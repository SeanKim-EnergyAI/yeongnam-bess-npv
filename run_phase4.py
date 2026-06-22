"""Phase 4 - LP optimization of battery dispatch.

Compares the heuristic dispatch (Phase 3) with an LP optimum on the same real
2024 price scenario, then values both. Run from the project root:

    python3 run_phase4.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.assumptions import get_assumptions
from src.price_scenario import load_baseline_smp, load_elasticities, apply_solar_scenario
from src.arbitrage import daily_arbitrage_revenue
from src.optimize_dispatch import optimize_daily_dispatch
from src.cashflow import build_cashflows
from src.valuation import summarize

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "data", "baseline_smp_hourly.csv")
ELAST_PATH = os.path.join(HERE, "data", "elasticities.csv")
OUT_DIR = os.path.join(HERE, "outputs")
EOK = 1e8


def npv_of(daily_net_krw: float, a: dict) -> float:
    return summarize(build_cashflows(daily_net_krw, a), a["discount_rate"])["npv_krw"]


def plot_dispatch(dispatch, a: dict) -> str:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(dispatch.index, dispatch["discharge_mw"], color="tab:red", label="discharge (MW)")
    ax.bar(dispatch.index, -dispatch["charge_mw"], color="tab:green", label="charge (MW)")
    ax.set_xlabel("Hour of day"); ax.set_ylabel("Power (MW)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax2 = ax.twinx()
    ax2.plot(dispatch.index, dispatch["soc_mwh"], color="tab:blue", marker="o",
             markersize=3, label="state of charge (MWh)")
    ax2.plot(dispatch.index, dispatch["price_smp"] * dispatch["soc_mwh"].max()
             / dispatch["price_smp"].max(), color="gray", linestyle=":", label="SMP (scaled)")
    ax2.set_ylabel("SOC (MWh)  /  SMP (scaled)")
    ax.set_title("LP-optimal battery dispatch (real 2024 prices)")
    ax.legend(loc="upper left"); ax2.legend(loc="upper right")
    path = os.path.join(OUT_DIR, "lp_dispatch.png")
    fig.tight_layout(); fig.savefig(path, dpi=120); plt.close(fig)
    return path


def main() -> None:
    a = get_assumptions()
    baseline = load_baseline_smp(DATA_PATH)
    elasticities = load_elasticities(ELAST_PATH)
    price = apply_solar_scenario(baseline, elasticities, a["solar_growth_pct"])["scenario_smp"]

    heuristic = daily_arbitrage_revenue(price, a)
    lp = optimize_daily_dispatch(price, a)

    h_daily, l_daily = heuristic["net_revenue_krw"], lp["net_revenue_krw"]
    uplift = (l_daily / h_daily - 1) * 100

    print("=" * 64)
    print("PHASE 4 - LP dispatch optimization vs heuristic")
    print("=" * 64)
    print(f"Solver status            : {lp['status']}")
    print(f"Heuristic daily revenue  : {h_daily/EOK:>10.4f} 억 KRW")
    print(f"LP-optimal daily revenue : {l_daily/EOK:>10.4f} 억 KRW  ({uplift:+.1f}%)")
    print(f"Heuristic NPV (@{a['discount_rate']:.0%})    : {npv_of(h_daily, a)/EOK:>10,.1f} 억 KRW")
    print(f"LP-optimal NPV (@{a['discount_rate']:.0%})   : {npv_of(l_daily, a)/EOK:>10,.1f} 억 KRW")
    print("-" * 64)
    d = lp["dispatch"].round(1)
    active = d[(d["charge_mw"] > 0.1) | (d["discharge_mw"] > 0.1)]
    print("Optimal schedule (active hours):")
    print(active[["price_smp", "charge_mw", "discharge_mw", "soc_mwh"]].to_string())

    p = plot_dispatch(lp["dispatch"], a)
    print(f"\nSaved plot: {p}")
    print("\nTakeaway: the heuristic OVERSTATES revenue ~8% -- it implicitly buys a")
    print("full cycle's charging energy in 4 hours, exceeding the power limit. The")
    print("LP charges over ~5 hours and delivers less than a full cycle when the")
    print("marginal charge hour costs more than the discharge, giving the feasible")
    print("optimum. The negative-NPV conclusion is unchanged.")


if __name__ == "__main__":
    main()
