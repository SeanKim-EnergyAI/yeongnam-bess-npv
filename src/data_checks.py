"""Completeness checks for the hourly SMP series.

Row count alone does not prove a full year: 2024 is a leap year (366 days x 24 h
= 8,784 hours), and a file with 8,760 rows can still spread over 366 dates with
partial days at either end. These checks never fill or shift data; they only
report, and let callers keep complete days for the dispatch run.

Hour convention assumed: hour 1..24 is hour-ending local time (KST), so hour 24
is 23:00-24:00 of the stated date. This is the KPX publication convention but is
NOT verified against the raw panel (see docs/model_audit.md).
"""

import pandas as pd

HOURS_PER_DAY = 24


def validate_hourly_series(hourly: pd.DataFrame, year: int = 2024) -> dict:
    """Summarize row count, per-date coverage, duplicates and gaps."""
    per_date = hourly.groupby("date").size()
    calendar = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D")
    present = set(hourly["hour"].unique())
    incomplete = {}
    for day, n in per_date[per_date != HOURS_PER_DAY].items():
        have = set(hourly.loc[hourly["date"] == day, "hour"])
        incomplete[str(day.date())] = sorted(set(range(1, HOURS_PER_DAY + 1)) - have)
    price = hourly["smp_krw_per_kwh"]
    return {
        "rows": len(hourly),
        "calendar_days_in_year": len(calendar),
        "expected_hours_in_year": len(calendar) * HOURS_PER_DAY,
        "dates_present": int(per_date.size),
        "complete_dates": int((per_date == HOURS_PER_DAY).sum()),
        "incomplete_dates_missing_hours": incomplete,
        "missing_calendar_dates": [str(d.date()) for d in
                                   calendar.difference(pd.DatetimeIndex(per_date.index))],
        "duplicate_date_hour_rows": int(hourly.duplicated(["date", "hour"]).sum()),
        "hour_values_outside_1_24": sorted(h for h in present if not 1 <= h <= HOURS_PER_DAY),
        "null_prices": int(price.isna().sum()),
        "zero_price_hours": int((price == 0).sum()),
        "negative_price_hours": int((price < 0).sum()),
    }


def complete_days(hourly: pd.DataFrame) -> pd.DataFrame:
    """Keep only dates that carry all 24 hours exactly once (no imputation)."""
    counts = hourly.groupby("date")["hour"].agg(["size", "nunique"])
    ok = counts[(counts["size"] == HOURS_PER_DAY)
                & (counts["nunique"] == HOURS_PER_DAY)].index
    return hourly[hourly["date"].isin(ok)].sort_values(["date", "hour"])
