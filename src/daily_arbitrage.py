"""Day-by-day arbitrage over the full 2024 year.

Phase 3 dispatches on the hour-of-day *average* price curve. This re-runs the
same dispatch on each of the ~365 actual daily curves, so we can see the
distribution and seasonality of arbitrage value and check whether averaging hid
anything. Uses observed 2024 SMP (no solar scenario).
"""

import pandas as pd

from src.arbitrage import daily_arbitrage_revenue


def load_hourly_series(csv_path: str) -> pd.DataFrame:
    """Long national SMP series: columns date (datetime), hour, smp_krw_per_kwh."""
    return pd.read_csv(csv_path, parse_dates=["date"])


def _one_day_net(day_df: pd.DataFrame, assumptions: dict) -> float:
    prices = day_df.set_index("hour")["smp_krw_per_kwh"]
    return daily_arbitrage_revenue(prices, assumptions)["net_revenue_krw"]


def daily_arbitrage_series(hourly: pd.DataFrame, assumptions: dict) -> pd.Series:
    """Net arbitrage revenue (KRW) for every calendar day, indexed by date."""
    nets = {day: _one_day_net(g, assumptions)
            for day, g in hourly.groupby("date")}
    return pd.Series(nets, name="daily_net_krw").sort_index()


def monthly_mean(daily_net: pd.Series) -> pd.Series:
    """Average daily arbitrage revenue by calendar month (1-12)."""
    return daily_net.groupby(daily_net.index.month).mean().rename_axis("month")
