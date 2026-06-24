"""Phase 3.5 - Full-year arbitrage distribution and a break-even decision map.

Two questions a business reader asks:
  1. The headline used an *average* day -- does real daily volatility change it?
  2. What cost / policy-support combination would actually make this investable?

Run from the project root:
    python3 run_analytics.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.assumptions import get_assumptions
from src.price_scenario import load_baseline_smp
from src.arbitrage import daily_arbitrage_revenue
from src.daily_arbitrage import load_hourly_series, daily_arbitrage_series, monthly_mean
from src.cashflow import build_cashflows
from src.valuation import summarize
from src.breakeven import annuity_factor

HERE = os.path.dirname(os.path.abspath(__file__))
SERIES_PATH = os.path.join(HERE, "data", "smp_2024_hourly.csv")
BASE_PATH = os.path.join(HERE, "data", "baseline_smp_hourly.csv")
OUT_DIR = os.path.join(HERE, "outputs")
KRW_PER_USD = 1_350


def npv_krw(daily_net_krw: float, a: dict) -> float:
    return summarize(build_cashflows(daily_net_krw, a), a["discount_rate"])["npv_krw"]


def plot_distribution(daily_usd, monthly_usd) -> str:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
    ax1.hist(daily_usd, bins=40, color="tab:blue", alpha=0.8)
    ax1.axvline(daily_usd.mean(), color="black", linestyle="--",
                label=f"mean ${daily_usd.mean():,.0f}")
    ax1.axvline(daily_usd.median(), color="tab:red", linestyle=":",
                label=f"median ${daily_usd.median():,.0f}")
    ax1.set_xlabel("Daily arbitrage profit (USD)"); ax1.set_ylabel("Days")
    ax1.set_title("Distribution of daily arbitrage (2024)"); ax1.legend()

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    ax2.bar([months[m - 1] for m in monthly_usd.index], monthly_usd.values,
            color="tab:green", alpha=0.8)
    ax2.set_ylabel("Avg daily profit (USD)"); ax2.set_title("Seasonality by month")
    ax2.tick_params(axis="x", rotation=45)
    path = os.path.join(OUT_DIR, "analytics_distribution.png")
    fig.tight_layout(); fig.savefig(path, dpi=120); plt.close(fig)
    return path


def plot_breakeven_frontier(daily_net_krw: float, a: dict) -> str:
    capex_usd = np.linspace(80, 400, 60)                 # $/kWh
    stack_usd = np.linspace(0, 220, 60)                  # $/kW-yr
    A = annuity_factor(a)
    power_kw = a["power_mw"] * 1_000
    npv_grid = np.zeros((len(stack_usd), len(capex_usd)))
    for j, cx in enumerate(capex_usd):
        aa = dict(a); aa["capex_per_kwh_krw"] = cx * KRW_PER_USD
        base = npv_krw(daily_net_krw, aa)
        for i, st in enumerate(stack_usd):
            stack_pv = st * KRW_PER_USD * power_kw * A
            npv_grid[i, j] = (base + stack_pv) / KRW_PER_USD / 1e6   # $M

    fig, ax = plt.subplots(figsize=(7.5, 5))
    cf = ax.contourf(capex_usd, stack_usd, npv_grid, levels=20, cmap="RdYlGn")
    ax.contour(capex_usd, stack_usd, npv_grid, levels=[0], colors="black", linewidths=2)
    ax.clabel(ax.contour(capex_usd, stack_usd, npv_grid, levels=[0],
                         colors="black"), fmt="NPV = 0")
    ax.scatter([350], [0], color="black", zorder=5)
    ax.annotate("today\n($350/kWh, no stack)", (350, 0),
                textcoords="offset points", xytext=(-95, 12))
    fig.colorbar(cf, label="NPV (M USD)")
    ax.set_xlabel("Battery capex ($/kWh)")
    ax.set_ylabel("Stacked revenue ($/kW-yr)")
    ax.set_title("Break-even frontier: when does the BESS become investable?")
    path = os.path.join(OUT_DIR, "analytics_breakeven_frontier.png")
    fig.tight_layout(); fig.savefig(path, dpi=120); plt.close(fig)
    return path


def main() -> None:
    a = get_assumptions()
    hourly = load_hourly_series(SERIES_PATH)
    daily = daily_arbitrage_series(hourly, a)
    daily_usd = daily / KRW_PER_USD

    # Representative-day dispatch (Phase 3 basis) vs the mean of real daily dispatch
    rep_daily = daily_arbitrage_revenue(load_baseline_smp(BASE_PATH), a)["net_revenue_krw"]
    real_mean = daily.mean()
    uplift = (real_mean / rep_daily - 1) * 100

    print("=" * 64)
    print("PHASE 3.5 - Full-year arbitrage (observed 2024 SMP, %d days)" % len(daily))
    print("=" * 64)
    print("Daily arbitrage profit (USD):")
    print(f"  mean ${daily_usd.mean():,.0f} | median ${daily_usd.median():,.0f} | "
          f"std ${daily_usd.std():,.0f}")
    print(f"  P10 ${daily_usd.quantile(.10):,.0f} | P90 ${daily_usd.quantile(.90):,.0f} | "
          f"min ${daily_usd.min():,.0f} | max ${daily_usd.max():,.0f}")
    print("-" * 64)
    print(f"Representative-day dispatch : ${rep_daily/KRW_PER_USD:,.0f}/day")
    print(f"Real per-day dispatch (mean): ${real_mean/KRW_PER_USD:,.0f}/day  ({uplift:+.1f}%)")
    print(f"  -> averaging the curve UNDERSTATED daily value by {uplift:.0f}%")
    print("-" * 64)
    print(f"NPV @ representative day : ${npv_krw(rep_daily, a)/KRW_PER_USD/1e6:>8,.1f}M")
    print(f"NPV @ real daily mean    : ${npv_krw(real_mean, a)/KRW_PER_USD/1e6:>8,.1f}M")
    print("  -> conclusion unchanged: arbitrage alone is deeply negative")

    mm = monthly_mean(daily) / KRW_PER_USD
    print(f"\nSeasonality: best month {int(mm.idxmax())} (${mm.max():,.0f}/day), "
          f"worst month {int(mm.idxmin())} (${mm.min():,.0f}/day)")

    p1 = plot_distribution(daily_usd, mm)
    p2 = plot_breakeven_frontier(real_mean, a)
    print(f"\nSaved plots:\n  {p1}\n  {p2}")


if __name__ == "__main__":
    main()
