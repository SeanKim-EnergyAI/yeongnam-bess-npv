"""Day-by-day arbitrage over the observed 2024 series.

Phase 3 dispatches on the hour-of-day *average* price curve. This re-runs the
dispatch on each actual daily curve, so we can see the distribution and
seasonality of arbitrage value. Uses observed 2024 SMP (no solar scenario).

`daily_lp_series` is the baseline engine: the same LP as the representative day
(src/optimize_dispatch.py), solved once per complete day with SOC reset to empty
at each midnight. `daily_arbitrage_series` keeps the legacy cheapest/dearest-hour
heuristic for comparison only; it ignores hour order and the power limit on
charging, so it is not a feasible schedule.
"""

import pandas as pd

from src.arbitrage import daily_arbitrage_revenue
from src.data_checks import HOURS_PER_DAY, complete_days
from src.optimize_dispatch import check_dispatch, optimize_daily_dispatch


def load_hourly_series(csv_path: str) -> pd.DataFrame:
    """Long national SMP series: columns date (datetime), hour, smp_krw_per_kwh."""
    return pd.read_csv(csv_path, parse_dates=["date"])


def _one_day_net(day_df: pd.DataFrame, assumptions: dict) -> float:
    prices = day_df.set_index("hour")["smp_krw_per_kwh"]
    return daily_arbitrage_revenue(prices, assumptions)["net_revenue_krw"]


def daily_arbitrage_series(hourly: pd.DataFrame, assumptions: dict) -> pd.Series:
    """LEGACY heuristic net revenue (KRW) per complete day, indexed by date."""
    nets = {day: _one_day_net(g, assumptions)
            for day, g in complete_days(hourly).groupby("date")}
    return pd.Series(nets, name="daily_net_krw").sort_index()


def daily_lp_series(hourly: pd.DataFrame, assumptions: dict) -> pd.DataFrame:
    """LP dispatch for every complete day: net revenue plus constraint checks.

    Days missing any hour are skipped, never filled.
    """
    rows = {}
    for day, g in complete_days(hourly).groupby("date"):
        prices = g.set_index("hour")["smp_krw_per_kwh"]
        assert len(prices) == HOURS_PER_DAY
        lp = optimize_daily_dispatch(prices, assumptions)
        d = lp["dispatch"]
        rows[day] = {
            "daily_net_krw": lp["net_revenue_krw"],
            "charge_mwh": d["charge_mw"].sum(),
            "discharge_mwh": d["discharge_mw"].sum(),
            **check_dispatch(d, assumptions),
        }
    return pd.DataFrame.from_dict(rows, orient="index").sort_index()


def monthly_mean(daily_net: pd.Series) -> pd.Series:
    """Average daily arbitrage revenue by calendar month (1-12)."""
    return daily_net.groupby(daily_net.index.month).mean().rename_axis("month")
