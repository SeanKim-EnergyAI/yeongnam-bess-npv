"""Phase 3 - Yeongnam 100MW BESS NPV.

Pipeline:
    real 2024 SMP + hourly IV elasticities -> price scenario
    -> daily arbitrage -> cash flows -> NPV / IRR

plus break-even levers and elasticity-scenario robustness.

Run from the project root:
    python3 run_phase3.py

The analysis is KRW-native; results are reported in USD (FX below) for an
international reader. Battery capex is the only non-market input.
"""

import os

import matplotlib
matplotlib.use("Agg")            # headless: write PNGs, don't open a window
import matplotlib.pyplot as plt
import pandas as pd

from src.assumptions import get_assumptions
from src.price_scenario import (load_baseline_smp, load_elasticities,
                                load_solar_profile, apply_solar_scenario)
from src.arbitrage import daily_arbitrage_revenue
from src.cashflow import build_cashflows
from src.valuation import summarize
from src.breakeven import (breakeven_capex_per_kwh,
                           breakeven_daily_revenue_multiplier,
                           stacked_revenue_needed_per_kw_year)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "data", "baseline_smp_hourly.csv")
ELAST_PATH = os.path.join(HERE, "data", "elasticities.csv")
SOLAR_PATH = os.path.join(HERE, "data", "solar_profile_hourly.csv")
OUT_DIR = os.path.join(HERE, "outputs")

KRW_PER_USD = 1_350      # reporting FX (2024 average ~1,360)


def usd_m(krw: float) -> float:
    return krw / KRW_PER_USD / 1e6


def run_pipeline(assumptions: dict, elasticities=None) -> dict:
    """One full pass. Pass `elasticities` to override the CSV (for scenarios)."""
    baseline = load_baseline_smp(DATA_PATH)
    if elasticities is None:
        elasticities = load_elasticities(ELAST_PATH)
    price = apply_solar_scenario(baseline, elasticities,
                                 assumptions["solar_growth_pct"])
    arbitrage = daily_arbitrage_revenue(price["scenario_smp"], assumptions)
    cashflows = build_cashflows(arbitrage["net_revenue_krw"], assumptions)
    metrics = summarize(cashflows, assumptions["discount_rate"])
    return {"price": price, "arbitrage": arbitrage,
            "cashflows": cashflows, "metrics": metrics}


def print_summary(assumptions: dict, result: dict) -> None:
    arb, m = result["arbitrage"], result["metrics"]
    base = result["price"]["baseline_smp"]
    print("=" * 64)
    print("PHASE 3 - Yeongnam 100MW BESS  |  arbitrage NPV (real 2024 data)")
    print("=" * 64)
    print(f"System            : {assumptions['power_mw']} MW / "
          f"{assumptions['duration_h']} h  = {assumptions['energy_mwh']} MWh")
    print(f"Baseline SMP      : mean {base.mean():.1f} KRW/kWh "
          f"(min h{int(base.idxmin())}={base.min():.0f}, max h{int(base.idxmax())}={base.max():.0f})")
    print(f"Solar scenario    : +{assumptions['solar_growth_pct']:.0%} generation")
    print(f"Charge hours      : {sorted(arb['charge_hours'])}  (pre-dawn, solar~0)")
    print(f"Discharge hours   : {sorted(arb['discharge_hours'])}")
    print(f"Avg charge price  : {arb['avg_charge_price_krw_per_mwh']:>12,.0f} KRW/MWh")
    print(f"Avg discharge px  : {arb['avg_discharge_price_krw_per_mwh']:>12,.0f} KRW/MWh")
    print(f"Daily net revenue : {arb['net_revenue_krw']/KRW_PER_USD:>12,.0f} USD")
    print("-" * 64)
    irr = m["irr"]
    print(f"NPV  (@{assumptions['discount_rate']:.0%}) : {usd_m(m['npv_krw']):>12,.1f} M USD")
    print(f"IRR               : {irr:>12.2%}" if irr == irr else
          f"IRR               :          n/a (never recovers capex)")
    print(f"Payback year      : {m['payback_year']}")
    print("=" * 64)


def print_breakeven(assumptions: dict, result: dict) -> None:
    daily = result["arbitrage"]["net_revenue_krw"]
    npv = result["metrics"]["npv_krw"]
    be_capex = breakeven_capex_per_kwh(daily, assumptions)
    mult = breakeven_daily_revenue_multiplier(daily, assumptions)
    stack = stacked_revenue_needed_per_kw_year(npv, assumptions)
    print("\nBreak-even levers (what would make NPV = 0):")
    print(f"  Capex must fall to        : ${be_capex/KRW_PER_USD:>6,.0f}/kWh "
          f"(now ${assumptions['capex_per_kwh_krw']/KRW_PER_USD:,.0f})")
    print(f"  Daily arbitrage must be   : {mult:>6.1f} x  larger")
    print(f"  OR stacked revenue of     : ${stack/KRW_PER_USD:>6,.0f}/kW-yr "
          f"(capacity / ancillary)")


def elasticity_scenarios(assumptions: dict, base_el: pd.Series,
                         solar: pd.Series) -> pd.DataFrame:
    """Does the (contested) hourly elasticity pattern change the investment call?"""
    ratio = (assumptions["elasticity_zonal_yeongnam"]
             / assumptions["elasticity_iv_average"])
    active = solar >= assumptions["solar_active_threshold_mwh"]
    variants = {
        "as-estimated (national HTE)": base_el,
        "solar-hours only (night=0)": base_el.where(active, 0.0),
        f"Yeongnam intensity (x{ratio:.1f})": base_el * ratio,
        "flat IV average (-0.0058)": pd.Series(assumptions["elasticity_iv_average"],
                                               index=base_el.index),
    }
    rows = []
    for name, el in variants.items():
        r = run_pipeline(assumptions, el)
        rows.append({"elasticity_scenario": name,
                     "npv_M_usd": round(usd_m(r["metrics"]["npv_krw"]), 1)})
    return pd.DataFrame(rows)


def sensitivity(base_assumptions: dict, key: str, values: list) -> pd.DataFrame:
    """Re-run the whole pipeline while sweeping one assumption."""
    rows = []
    for v in values:
        a = dict(base_assumptions)
        a[key] = v
        m = run_pipeline(a)["metrics"]
        rows.append({key: v, "npv_M_usd": round(usd_m(m["npv_krw"]), 1),
                     "irr": m["irr"]})
    return pd.DataFrame(rows)


def plot_price_curve(assumptions: dict, result: dict, solar: pd.Series) -> str:
    price, arb = result["price"], result["arbitrage"]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax2 = ax.twinx()
    ax2.bar(solar.index, solar.values, width=0.8, color="gold", alpha=0.35,
            label="solar generation")
    ax2.set_ylabel("Solar generation (MWh)")
    ax.plot(price.index, price["baseline_smp"], "--", color="tab:blue",
            label="Baseline SMP (2024)")
    ax.plot(price.index, price["scenario_smp"], "-", color="tab:blue",
            label=f"+{assumptions['solar_growth_pct']:.0%} solar scenario")
    ax.scatter(arb["charge_hours"], price.loc[arb["charge_hours"], "scenario_smp"],
               color="tab:green", zorder=5, label="charge")
    ax.scatter(arb["discharge_hours"], price.loc[arb["discharge_hours"], "scenario_smp"],
               color="tab:red", zorder=5, label="discharge")
    ax.set_xlabel("Hour of day"); ax.set_ylabel("SMP (KRW/kWh)")
    ax.set_title("Korea 2024: SMP, solar, and BESS dispatch")
    ax.set_zorder(ax2.get_zorder() + 1); ax.patch.set_visible(False)
    ax.legend(loc="upper left"); ax2.legend(loc="upper right")
    path = os.path.join(OUT_DIR, "price_curve.png")
    fig.tight_layout(); fig.savefig(path, dpi=120); plt.close(fig)
    return path


def plot_cashflows(result: dict) -> str:
    cf = result["cashflows"]["net_cashflow_krw"] / KRW_PER_USD / 1e6
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(cf.index, cf.values, color=["tab:red" if x < 0 else "tab:blue" for x in cf])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Year"); ax.set_ylabel("Net cash flow (M USD)")
    ax.set_title("Annual net cash flow")
    path = os.path.join(OUT_DIR, "cashflows.png")
    fig.tight_layout(); fig.savefig(path, dpi=120); plt.close(fig)
    return path


def main() -> None:
    a = get_assumptions()
    solar = load_solar_profile(SOLAR_PATH)
    base_el = load_elasticities(ELAST_PATH)

    result = run_pipeline(a)
    print_summary(a, result)
    print_breakeven(a, result)

    print("\nElasticity-scenario robustness (does the hourly pattern change the call?):")
    print(elasticity_scenarios(a, base_el, solar).to_string(index=False))

    print("\nSensitivity - solar growth:")
    print(sensitivity(a, "solar_growth_pct", [0.0, 0.25, 0.50, 1.00])
          .to_string(index=False))

    print("\nSensitivity - capex (KRW/kWh):")
    print(sensitivity(a, "capex_per_kwh_krw", [150_000, 250_000, 350_000, 450_000])
          .to_string(index=False))

    p1 = plot_price_curve(a, result, solar)
    p2 = plot_cashflows(result)
    print(f"\nSaved plots:\n  {p1}\n  {p2}")


if __name__ == "__main__":
    main()
