"""Audit tables: isolate each change so data-range, dispatch-method and
definition effects are never mixed in one number.

Writes:
    outputs/audit_cycle_cap.csv          delivered- vs internal-energy cycle cap (same LP, same days)
    outputs/audit_engine_comparison.csv  heuristic vs daily-reset LP vs continuous-SOC LP (same 364 days)
    outputs/audit_npv_bridge.csv         legacy headline -> baseline, one change per step

"Arbitrage profit" everywhere = discharge revenue - charging cost (SMP x metered
MWh), BEFORE fixed O&M, degradation and capex.

Run from the project root:
    python3 run_audit.py
"""

import math
import os

import pandas as pd

from src.arbitrage import daily_arbitrage_revenue
from src.assumptions import get_assumptions
from src.cashflow import build_cashflows
from src.daily_arbitrage import load_hourly_series
from src.data_checks import complete_days
from src.optimize_dispatch import check_dispatch, optimize_daily_dispatch
from src.price_scenario import apply_solar_scenario, load_baseline_smp, load_elasticities
from src.valuation import compute_npv

HERE = os.path.dirname(os.path.abspath(__file__))
SERIES_PATH = os.path.join(HERE, "data", "smp_2024_hourly.csv")
BASE_PATH = os.path.join(HERE, "data", "baseline_smp_hourly.csv")
ELAST_PATH = os.path.join(HERE, "data", "elasticities.csv")
OUT_DIR = os.path.join(HERE, "outputs")
KRW_PER_USD = 1_350
NO_TRADE_KRW = 1.0       # |daily profit| below this = no trade


def usd_m(krw: float) -> float:
    return krw / KRW_PER_USD / 1e6


def finance(daily_mean_krw: float, a: dict) -> dict:
    cf = build_cashflows(daily_mean_krw, a)
    return {
        "annualisation": f"daily mean x {a['operating_days_per_year']} operating days",
        "yr1_arbitrage_profit_usd_m": round(usd_m(cf.loc[1, "gross_revenue_krw"]), 3),
        "yr1_fixed_om_usd_m": round(usd_m(cf.loc[1, "om_krw"]), 3),
        "yr1_net_cashflow_usd_m": round(usd_m(cf.loc[1, "net_cashflow_krw"]), 3),
        "npv_usd_m": round(usd_m(compute_npv(cf["net_cashflow_krw"], a["discount_rate"])), 2),
    }


def per_day(days: pd.DataFrame, fn) -> pd.Series:
    return pd.Series({d: fn(g.set_index("hour")["smp_krw_per_kwh"])
                      for d, g in days.groupby("date")}).sort_index()


def lp_day_stats(prices: pd.Series, a: dict, cap_basis: str) -> dict:
    r = optimize_daily_dispatch(prices, a, cap_basis=cap_basis)
    d = r["dispatch"]
    eff = math.sqrt(a["round_trip_efficiency"])
    return {"profit": r["net_revenue_krw"],
            "delivered_mwh": d["discharge_mw"].sum(),
            "internal_out_mwh": d["discharge_mw"].sum() / eff,
            "drawn_mwh": d["charge_mw"].sum()}


def cycle_cap_table(days: pd.DataFrame, a: dict) -> pd.DataFrame:
    res = {}
    for basis in ("delivered", "internal"):
        res[basis] = pd.DataFrame(per_day(days, lambda p: lp_day_stats(p, a, basis)).tolist(),
                                  index=sorted(days["date"].unique()))
    diff = (res["delivered"]["profit"] - res["internal"]["profit"]).abs() > NO_TRADE_KRW
    rows = []
    for basis, formula in (("delivered", "sum_h d[h] <= 400 MWh/day (bb253a4)"),
                           ("internal", "sum_h d[h]/sqrt(0.86) <= 400 MWh/day (audit choice)")):
        r = res[basis]
        rows.append({
            "cap_basis": basis, "constraint": formula, "days": len(r),
            "arbitrage_profit_sum_usd_m": round(usd_m(r["profit"].sum()), 4),
            "daily_mean_usd": round(r["profit"].mean() / KRW_PER_USD, 1),
            "no_trade_days": int((r["profit"].abs() < NO_TRADE_KRW).sum()),
            "max_internal_out_mwh_per_day": round(r["internal_out_mwh"].max(), 2),
            "max_delivered_mwh_per_day": round(r["delivered_mwh"].max(), 2),
            "max_equivalent_internal_cycles_per_day": round(r["internal_out_mwh"].max()
                                                            / a["energy_mwh"], 4),
            "days_differing_between_bases": int(diff.sum()),
            **finance(r["profit"].mean(), a),
        })
    t = pd.DataFrame(rows)
    t["daily_mean_change_vs_delivered_pct"] = round(
        (t["daily_mean_usd"] / t.loc[0, "daily_mean_usd"] - 1) * 100, 3)
    return t


def engine_table(days: pd.DataFrame, a: dict) -> pd.DataFrame:
    n = days["date"].nunique()
    heur = per_day(days, lambda p: daily_arbitrage_revenue(p, a)["net_revenue_krw"])
    lp = per_day(days, lambda p: optimize_daily_dispatch(p, a)["net_revenue_krw"])
    prices = days.reset_index(drop=True)["smp_krw_per_kwh"]
    cont = {w: optimize_daily_dispatch(prices, a, cap_window=w) for w in ("per_day", "pooled")}

    def row(name, feasible, soc, cap, total, daily=None):
        mean = total / n
        r = {"case": name, "feasible_schedule": feasible, "soc_boundary": soc,
             "cycle_cap": cap, "days": n,
             "arbitrage_profit_sum_usd_m": round(usd_m(total), 4),
             "daily_mean_usd": round(mean / KRW_PER_USD, 1),
             "vs_daily_reset_lp_pct": round((total / lp.sum() - 1) * 100, 2),
             "no_trade_days": int((daily.abs() < NO_TRADE_KRW).sum()) if daily is not None else "n/a (one horizon)",
             "loss_days": int((daily < -NO_TRADE_KRW).sum()) if daily is not None else "n/a"}
        r.update(finance(mean, a))
        return r

    rows = [
        row("legacy heuristic", "no (116 MW charge, ignores hour order)", "none modelled",
            "exactly 4 h in / 4 h out every day", heur.sum(), heur),
        row("daily-reset LP (BASELINE)", "yes", "0 at start and end of every day",
            "internal, per day", lp.sum(), lp),
        row("continuous-SOC LP, per-day cap (diagnostic)", "yes",
            "0 at 2024-01-02 h1 start and 2024-12-30 h24 end only",
            "internal, per 24-h block", cont["per_day"]["net_revenue_krw"]),
        row("continuous-SOC LP, pooled cap (diagnostic)", "yes",
            "0 at 2024-01-02 h1 start and 2024-12-30 h24 end only",
            "internal, 364 cycles pooled over period", cont["pooled"]["net_revenue_krw"]),
    ]
    for w in ("per_day", "pooled"):
        c = check_dispatch(cont[w]["dispatch"], a)
        assert c["power_violation_mw"] < 1e-6 and c["soc_violation_mwh"] < 1e-4, c
    return pd.DataFrame(rows)


def bridge_table(hourly: pd.DataFrame, days: pd.DataFrame, a: dict) -> pd.DataFrame:
    heur = lambda p: daily_arbitrage_revenue(p, a)["net_revenue_krw"]
    rep = load_baseline_smp(BASE_PATH)
    rep_scn = apply_solar_scenario(rep, load_elasticities(ELAST_PATH),
                                   a["exploratory_solar_growth_pct"])["scenario_smp"]
    all_dates = per_day(hourly, heur)
    steps = [
        ("0 legacy headline (bb253a4 run_phase3)", "-", heur(rep_scn)),
        ("1 drop +30% solar scenario", "scenario scope", heur(rep)),
        ("2 average day -> each observed date (366 dates)", "method: averaging", all_dates.mean()),
        ("3 drop 2 incomplete dates (364 days)", "data range", per_day(days, heur).mean()),
        ("4 heuristic -> LP, legacy delivered-energy cap", "dispatch method",
         per_day(days, lambda p: optimize_daily_dispatch(p, a, cap_basis="delivered")
                 ["net_revenue_krw"]).mean()),
        ("5 cap on internal energy (baseline)", "definition choice",
         per_day(days, lambda p: optimize_daily_dispatch(p, a)["net_revenue_krw"]).mean()),
    ]
    rows, prev = [], None
    for name, kind, daily in steps:
        f = finance(daily, a)
        rows.append({"step": name, "change_type": kind,
                     "daily_mean_usd": round(daily / KRW_PER_USD, 1),
                     "npv_usd_m": f["npv_usd_m"],
                     "delta_npv_usd_m": None if prev is None else round(f["npv_usd_m"] - prev, 2)})
        prev = f["npv_usd_m"]
    return pd.DataFrame(rows)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    a = get_assumptions()
    hourly = load_hourly_series(SERIES_PATH)
    days = complete_days(hourly)
    tables = {
        "audit_cycle_cap.csv": cycle_cap_table(days, a),
        "audit_engine_comparison.csv": engine_table(days, a),
        "audit_npv_bridge.csv": bridge_table(hourly, days, a),
    }
    with pd.option_context("display.width", 250, "display.max_columns", 30,
                           "display.max_colwidth", 48):
        for name, t in tables.items():
            t.to_csv(os.path.join(OUT_DIR, name), index=False)
            print(f"\n== {name}\n{t.to_string(index=False)}")


if __name__ == "__main__":
    main()
