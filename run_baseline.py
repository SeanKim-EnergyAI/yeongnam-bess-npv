"""Baseline - reproducible arbitrage NPV on observed 2024 SMP.

Pipeline (the headline):
    data/smp_2024_hourly.csv -> completeness checks -> keep complete days only
    -> LP dispatch per day (SOC empty at each midnight, perfect foresight)
    -> mean daily net revenue x operating_days_per_year -> cash flows -> NPV
    -> closed-form break-even levers, each re-substituted to check NPV = 0

Also writes a before/after table that reproduces the legacy headline method
(heuristic, hour-of-day mean day, +30% solar scenario) next to the baseline.
2024 prices are repeated for every project year: this is a what-if screen on
one historical year, not a price forecast.

Run from the project root:
    python3 run_baseline.py
"""

import json
import os

import pandas as pd

from src.arbitrage import daily_arbitrage_revenue
from src.assumptions import get_assumptions
from src.breakeven import (annuity_factor, breakeven_capex_per_kwh,
                           breakeven_daily_revenue_multiplier,
                           stacked_revenue_needed_per_kw_year)
from src.cashflow import build_cashflows
from src.daily_arbitrage import daily_lp_series, load_hourly_series
from src.data_checks import complete_days, validate_hourly_series
from src.optimize_dispatch import check_dispatch, optimize_daily_dispatch
from src.price_scenario import (apply_solar_scenario, load_baseline_smp,
                                load_elasticities)
from src.valuation import compute_npv

HERE = os.path.dirname(os.path.abspath(__file__))
SERIES_PATH = os.path.join(HERE, "data", "smp_2024_hourly.csv")
BASE_PATH = os.path.join(HERE, "data", "baseline_smp_hourly.csv")
ELAST_PATH = os.path.join(HERE, "data", "elasticities.csv")
OUT_DIR = os.path.join(HERE, "outputs")
KRW_PER_USD = 1_350      # reporting FX only; the model is KRW-native
TOL_KRW = 1.0            # break-even re-substitution tolerance (|NPV| in KRW)


def usd_m(krw: float) -> float:
    return krw / KRW_PER_USD / 1e6


def npv_krw(daily_net_krw: float, a: dict) -> float:
    return compute_npv(build_cashflows(daily_net_krw, a)["net_cashflow_krw"],
                       a["discount_rate"])


def case_row(name: str, period: str, days: int, engine: str, prices: str,
             daily_net_krw: float, a: dict) -> dict:
    cf = build_cashflows(daily_net_krw, a)
    npv = compute_npv(cf["net_cashflow_krw"], a["discount_rate"])
    return {
        "case": name,
        "analysis_period": period,
        "days_used": days,
        "dispatch_engine": engine,
        "price_basis": prices,
        "revenue_days_per_year": a["operating_days_per_year"],
        "daily_net_usd": round(daily_net_krw / KRW_PER_USD),
        "yr1_arbitrage_gross_margin_usd_m": round(usd_m(cf.loc[1, "gross_revenue_krw"]), 2),
        "yr1_om_usd_m": round(usd_m(cf.loc[1, "om_krw"]), 2),
        "yr1_net_cashflow_usd_m": round(usd_m(cf.loc[1, "net_cashflow_krw"]), 2),
        "npv_usd_m": round(usd_m(npv), 1),
        "breakeven_capex_usd_per_kwh": round(breakeven_capex_per_kwh(daily_net_krw, a)
                                             / KRW_PER_USD, 1),
        "stacked_revenue_needed_usd_per_kw_yr": round(
            stacked_revenue_needed_per_kw_year(npv, a) / KRW_PER_USD, 1),
    }


def breakeven_checks(daily_net_krw: float, a: dict) -> pd.DataFrame:
    """Plug each closed-form break-even back into the cash-flow model."""
    npv0 = npv_krw(daily_net_krw, a)
    be_capex = breakeven_capex_per_kwh(daily_net_krw, a)
    mult = breakeven_daily_revenue_multiplier(daily_net_krw, a)
    stack_kw_yr = stacked_revenue_needed_per_kw_year(npv0, a)

    npv_capex = npv_krw(daily_net_krw, dict(a, capex_per_kwh_krw=be_capex))
    npv_mult = npv_krw(daily_net_krw * mult, a)
    cf = build_cashflows(daily_net_krw, a)["net_cashflow_krw"].copy()
    cf.loc[1:] += stack_kw_yr * a["power_mw"] * 1_000        # constant extra revenue
    npv_stack = compute_npv(cf, a["discount_rate"])
    rows = [
        ("capex_krw_per_kwh", be_capex, npv_capex),
        ("daily_revenue_multiplier", mult, npv_mult),
        ("stacked_revenue_krw_per_kw_yr", stack_kw_yr, npv_stack),
    ]
    return pd.DataFrame([{"lever": k, "breakeven_value": v, "npv_after_substitution_krw": n,
                          "passes_abs_tol_1_krw": abs(n) < TOL_KRW} for k, v, n in rows])


def legacy_full_year_heuristic(hourly: pd.DataFrame, a: dict) -> float:
    """Legacy method as shipped in bb253a4: heuristic on all 366 dates, incl. partial ones."""
    nets = [daily_arbitrage_revenue(g.set_index("hour")["smp_krw_per_kwh"], a)["net_revenue_krw"]
            for _, g in hourly.groupby("date")]
    return sum(nets) / len(nets)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    a = get_assumptions()
    hourly = load_hourly_series(SERIES_PATH)

    # --- B. data validation (report only; nothing is filled or shifted) ---
    report = validate_hourly_series(hourly)
    pd.Series({k: json.dumps(v) if isinstance(v, (dict, list)) else v
               for k, v in report.items()}, name="value").rename_axis("check") \
        .to_csv(os.path.join(OUT_DIR, "data_validation.csv"))

    # --- C. baseline: LP per complete day ---
    lp = daily_lp_series(hourly, a)
    lp.rename_axis("date").to_csv(os.path.join(OUT_DIR, "baseline_daily_lp.csv"))
    worst = lp[["power_violation_mw", "soc_violation_mwh", "simultaneous_mw"]].max()
    assert (worst < 1e-4).all(), f"constraint check failed: {worst.to_dict()}"
    days = len(lp)
    period = f"{lp.index.min().date()}..{lp.index.max().date()}"
    mean_daily = lp["daily_net_krw"].mean()
    period_sum = lp["daily_net_krw"].sum()

    cf = build_cashflows(mean_daily, a)
    cf.to_csv(os.path.join(OUT_DIR, "baseline_cashflows.csv"))

    # Diagnostic: one LP across all contiguous complete days (no midnight reset,
    # per-24-h cycle cap kept). Pooled-cap variant: run_audit.py.
    cont_prices = complete_days(hourly).reset_index(drop=True)["smp_krw_per_kwh"]
    cont = optimize_daily_dispatch(cont_prices, a)
    cont_check = check_dispatch(cont["dispatch"], a)
    cont_daily = cont["net_revenue_krw"] / days

    # --- Before / after table ---
    rep_scn = apply_solar_scenario(load_baseline_smp(BASE_PATH), load_elasticities(ELAST_PATH),
                                   a["exploratory_solar_growth_pct"])["scenario_smp"]
    legacy_rep = daily_arbitrage_revenue(rep_scn, a)["net_revenue_krw"]
    legacy_fy = legacy_full_year_heuristic(hourly, a)
    all_dates = f"{hourly['date'].min().date()}..{hourly['date'].max().date()}"
    rows = [
        case_row("BEFORE: legacy headline (run_phase3 @ bb253a4)", "hour-of-day mean of 2024",
                 1, "heuristic (infeasible)", "+30% solar scenario (exploratory)", legacy_rep, a),
        case_row("BEFORE: legacy full-year (run_analytics @ bb253a4)", all_dates,
                 hourly["date"].nunique(), "heuristic (infeasible)",
                 "observed, incl. 2 partial dates", legacy_fy, a),
        case_row("AFTER: baseline", period, days, "LP per day",
                 "observed, complete days", mean_daily, a),
        case_row("AFTER diag: actual-period sum as year-1", period, days, "LP per day",
                 "observed, complete days", period_sum / days,
                 dict(a, operating_days_per_year=days)),
        case_row("AFTER diag: continuous SOC, per-day cap", period, days,
                 "LP whole period", "observed, complete days", cont_daily, a),
    ]
    table = pd.DataFrame(rows)
    table.to_csv(os.path.join(OUT_DIR, "before_after_comparison.csv"), index=False)

    checks = breakeven_checks(mean_daily, a)
    checks.to_csv(os.path.join(OUT_DIR, "breakeven_check.csv"), index=False)

    # --- Console summary ---
    npv = compute_npv(cf["net_cashflow_krw"], a["discount_rate"])
    print("=" * 70)
    print("BASELINE - LP per complete day, observed 2024 SMP (not a forecast)")
    print("=" * 70)
    print(f"Rows {report['rows']} | dates {report['dates_present']} | complete "
          f"{report['complete_dates']} | expected hours {report['expected_hours_in_year']}")
    print(f"Incomplete dates excluded: {list(report['incomplete_dates_missing_hours'])}")
    print(f"Zero-price hours kept as observed: {report['zero_price_hours']}")
    print(f"Period {period} ({days} days) | LP no-trade days "
          f"{(lp['daily_net_krw'].abs() < 1).sum()} | max simultaneous flow "
          f"{lp['simultaneous_mw'].max():.2e} MW")
    print("Arbitrage profit = discharge revenue - charging cost, before fixed O&M.")
    print(f"Mean daily profit   : ${mean_daily/KRW_PER_USD:>12,.0f}")
    print(f"Annualised (yr 1)   : ${usd_m(cf.loc[1, 'gross_revenue_krw']):>12,.2f}M "
          f"(mean x {a['operating_days_per_year']} operating days)")
    print(f"Analysis-period sum : ${usd_m(period_sum):>12,.2f}M ({days} complete days; "
          "not a full calendar year)")
    print(f"Year-1 O&M          : ${usd_m(cf.loc[1, 'om_krw']):>12,.2f}M")
    print(f"NPV @ {a['discount_rate']:.0%}           : ${usd_m(npv):>12,.1f}M")
    print(f"Contin. SOC (diag)  : ${cont_daily/KRW_PER_USD:>12,.0f}/day "
          f"({(cont_daily/mean_daily-1)*100:+.1f}%), check {cont_check['soc_violation_mwh']:.1e}")
    print("-" * 70)
    print("Break-even re-substitution (NPV should be ~0):")
    print(checks.to_string(index=False))
    print("-" * 70)
    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(table.drop(columns=["analysis_period", "price_basis"]).to_string(index=False))
    print(f"\nWrote CSVs to {OUT_DIR}")


if __name__ == "__main__":
    main()
