"""Phase 3 - Yeongnam 100MW BESS NPV.

Pipeline:
    assumptions -> price scenario -> daily arbitrage -> cash flows -> NPV / IRR

Run from the project root:
    python3 run_phase3.py
"""

import os

import matplotlib
matplotlib.use("Agg")            # headless: write PNGs, don't open a window
import matplotlib.pyplot as plt
import pandas as pd

from src.assumptions import get_assumptions
from src.price_scenario import (load_baseline_smp, build_hourly_elasticities,
                                apply_solar_scenario)
from src.arbitrage import daily_arbitrage_revenue
from src.cashflow import build_cashflows
from src.valuation import summarize

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "data", "baseline_smp_hourly.csv")
OUT_DIR = os.path.join(HERE, "outputs")

EOK = 1e8  # 1 억 = 100,000,000 KRW -> report large won figures in 억 (oeok)


def run_pipeline(assumptions: dict) -> dict:
    """One full pass; returns every intermediate object for inspection."""
    baseline = load_baseline_smp(DATA_PATH)
    elasticities = build_hourly_elasticities(
        assumptions["elasticity_anchors"],
        assumptions["elasticity_iv_average"],
        baseline.index,
    )
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
    price = result["price"]
    arb = result["arbitrage"]
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
