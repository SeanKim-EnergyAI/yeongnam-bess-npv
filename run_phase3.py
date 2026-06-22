"""Phase 3 - Yeongnam 100MW BESS NPV.

Pipeline:
    assumptions -> price scenario -> daily arbitrage -> cash flows -> NPV / IRR

plus break-even levers and an elasticity sign-robustness check.

Run from the project root:
    python3 run_phase3.py
"""

import os

import matplotlib
matplotlib.use("Agg")            # headless: write PNGs, don't open a window
import matplotlib.pyplot as plt
import pandas as pd

from src.assumptions import get_assumptions
from src.price_scenario import load_baseline_smp, load_elasticities, apply_solar_scenario
from src.arbitrage import daily_arbitrage_revenue
from src.cashflow import build_cashflows
from src.valuation import summarize
from src.breakeven import (breakeven_capex_per_kwh,
                           breakeven_daily_revenue_multiplier,
                           stacked_revenue_needed_per_kw_year)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "data", "baseline_smp_hourly.csv")
ELAST_PATH = os.path.join(HERE, "data", "elasticities.csv")
OUT_DIR = os.path.join(HERE, "outputs")

EOK = 1e8  # 1 억 = 100,000,000 KRW -> report large won figures in 억 (oeok)


def run_pipeline(assumptions: dict, elasticities=None) -> dict:
    """One full pass. Pass `elasticities` to override the CSV (used for scenarios)."""
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
    print("=" * 64)
    print("PHASE 3 - Yeongnam 100MW BESS  |  arbitrage NPV")
    print("=" * 64)
    print(f"System            : {assumptions['power_mw']} MW / "
          f"{assumptions['duration_h']} h  = {assumptions['energy_mwh']} MWh")
    print(f"Solar scenario    : +{assumptions['solar_growth_pct']:.0%} generation")
    print(f"Charge hours      : {sorted(arb['charge_hours'])}")
    print(f"Discharge hours   : {sorted(arb['discharge_hours'])}")
    print(f"Avg charge price  : {arb['avg_charge_price_krw_per_mwh']:>12,.0f} KRW/MWh")
    print(f"Avg discharge px  : {arb['avg_discharge_price_krw_per_mwh']:>12,.0f} KRW/MWh")
    print(f"Daily net revenue : {arb['net_revenue_krw']/EOK:>12.3f} 억 KRW")
    print("-" * 64)
    irr = m["irr"]
    print(f"NPV  (@{assumptions['discount_rate']:.0%}) : {m['npv_krw']/EOK:>12,.1f} 억 KRW")
    print(f"IRR               : {irr:>12.2%}" if irr == irr else
          f"IRR               :          n/a")
    print(f"Payback year      : {m['payback_year']}")
    print("=" * 64)


def print_breakeven(assumptions: dict, result: dict) -> None:
    daily = result["arbitrage"]["net_revenue_krw"]
    npv = result["metrics"]["npv_krw"]
    be_capex = breakeven_capex_per_kwh(daily, assumptions)
    mult = breakeven_daily_revenue_multiplier(daily, assumptions)
    stack = stacked_revenue_needed_per_kw_year(npv, assumptions)
    print("\nBreak-even levers (what would make NPV = 0):")
    print(f"  Capex must fall to        : {be_capex:>10,.0f} KRW/kWh "
          f"(now {assumptions['capex_per_kwh_krw']:,})")
    print(f"  Daily arbitrage must be   : {mult:>10.1f} x  larger")
    print(f"  OR stacked revenue of     : {stack:>10,.0f} KRW/kW-yr "
          f"(capacity / ancillary)")


def sign_robustness(assumptions: dict) -> pd.DataFrame:
    """How much does the contested hour-13 sign actually move the investment?"""
    base = load_elasticities(ELAST_PATH)
    flipped = base.copy()
    flipped.loc[13] = -abs(base.loc[13])                       # force intuitive (-)
    uniform = pd.Series(assumptions["elasticity_iv_average"],
                        index=base.index, name="elasticity")
    variants = {"as-estimated (h13 +)": base,
                "h13 flipped (-)": flipped,
                "uniform IV average": uniform}
    rows = []
    for name, el in variants.items():
        r = run_pipeline(assumptions, el)
        rows.append({"elasticity_scenario": name,
                     "daily_rev_eok": r["arbitrage"]["net_revenue_krw"] / EOK,
                     "npv_eok": r["metrics"]["npv_krw"] / EOK})
    return pd.DataFrame(rows)


def sensitivity(base_assumptions: dict, key: str, values: list) -> pd.DataFrame:
    """Re-run the whole pipeline while sweeping one assumption."""
    rows = []
    for v in values:
        a = dict(base_assumptions)
        a[key] = v
        m = run_pipeline(a)["metrics"]
        rows.append({key: v, "npv_eok": m["npv_krw"] / EOK, "irr": m["irr"]})
    return pd.DataFrame(rows)


def plot_price_curve(assumptions: dict, result: dict) -> str:
    price, arb = result["price"], result["arbitrage"]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(price.index, price["baseline_smp"], "--", label="Baseline SMP")
    ax.plot(price.index, price["scenario_smp"], "-",
            label=f"+{assumptions['solar_growth_pct']:.0%} solar scenario")
    ax.scatter(arb["charge_hours"], price.loc[arb["charge_hours"], "scenario_smp"],
               color="tab:green", zorder=5, label="charge")
    ax.scatter(arb["discharge_hours"], price.loc[arb["discharge_hours"], "scenario_smp"],
               color="tab:red", zorder=5, label="discharge")
    ax.set_xlabel("Hour of day"); ax.set_ylabel("SMP (KRW/kWh)")
    ax.set_title("Hourly SMP and BESS dispatch"); ax.legend()
    path = os.path.join(OUT_DIR, "price_curve.png")
    fig.tight_layout(); fig.savefig(path, dpi=120); plt.close(fig)
    return path


def plot_cashflows(result: dict) -> str:
    cf = result["cashflows"]["net_cashflow_krw"] / EOK
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(cf.index, cf.values, color=["tab:red" if x < 0 else "tab:blue" for x in cf])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Year"); ax.set_ylabel("Net cash flow (100M KRW)")
    ax.set_title("Annual net cash flow")
    path = os.path.join(OUT_DIR, "cashflows.png")
    fig.tight_layout(); fig.savefig(path, dpi=120); plt.close(fig)
    return path


def main() -> None:
    a = get_assumptions()
    result = run_pipeline(a)
    print_summary(a, result)
    print_breakeven(a, result)

    print("\nElasticity sign-robustness (does the contested h13 sign change the call?):")
    print(sign_robustness(a).to_string(index=False))

    print("\nSensitivity - solar growth:")
    print(sensitivity(a, "solar_growth_pct", [0.0, 0.25, 0.50, 1.00])
          .to_string(index=False))

    print("\nSensitivity - capex (KRW/kWh):")
    print(sensitivity(a, "capex_per_kwh_krw", [150_000, 250_000, 350_000, 450_000])
          .to_string(index=False))

    p1 = plot_price_curve(a, result)
    p2 = plot_cashflows(result)
    print(f"\nSaved plots:\n  {p1}\n  {p2}")


if __name__ == "__main__":
    main()
