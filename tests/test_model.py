"""Behavioural checks for the dispatch, finance and data-validation code.

Run from the project root:  python3 -m pytest -q
"""

import math
import os

import numpy as np
import pandas as pd
import pytest

from src.arbitrage import daily_arbitrage_revenue
from src.assumptions import get_assumptions
from src.breakeven import (breakeven_capex_per_kwh, breakeven_daily_revenue_multiplier,
                           stacked_revenue_needed_per_kw_year)
from src.cashflow import build_cashflows
from src.data_checks import complete_days, validate_hourly_series
from src.daily_arbitrage import load_hourly_series
from src.optimize_dispatch import check_dispatch, optimize_daily_dispatch
from src.price_scenario import apply_solar_scenario
from src.valuation import compute_npv

HERE = os.path.dirname(os.path.abspath(__file__))
SERIES = os.path.join(HERE, "..", "data", "smp_2024_hourly.csv")


def small_battery(**kw) -> dict:
    a = {"power_mw": 10, "energy_mwh": 10, "round_trip_efficiency": 0.81,
         "cycles_per_day": 1}
    a.update(kw)
    return a


def npv_of(daily_krw: float, a: dict) -> float:
    return compute_npv(build_cashflows(daily_krw, a)["net_cashflow_krw"], a["discount_rate"])


# --- dispatch --------------------------------------------------------------

def test_hand_calculation_two_hours():
    # eff per leg = 0.9. Hour 1: charge 10 MW -> SOC 9 MWh. Hour 2: deliver
    # 9 * 0.9 = 8.1 MWh. Profit = 8.1 MWh * 100,000 - 10 MWh * 50,000 = 310,000 KRW.
    prices = pd.Series([50.0, 100.0], index=[1, 2])           # KRW/kWh
    r = optimize_daily_dispatch(prices, small_battery())
    assert r["status"] == "Optimal"
    assert r["net_revenue_krw"] == pytest.approx(310_000, rel=1e-6)
    assert r["dispatch"]["discharge_mw"].sum() == pytest.approx(8.1, rel=1e-6)


def test_constant_price_means_no_trade():
    prices = pd.Series(120.0, index=range(1, 25))
    r = optimize_daily_dispatch(prices, get_assumptions())
    d = r["dispatch"]
    assert r["net_revenue_krw"] == pytest.approx(0, abs=1e-3)
    assert d["charge_mw"].max() < 1e-6 and d["discharge_mw"].max() < 1e-6


def test_spread_below_losses_means_no_trade():
    # 100 -> 110 KRW/kWh is a 10% spread; losses are 14% (rte 0.86).
    prices = pd.Series([100.0] * 12 + [110.0] * 12, index=range(1, 25))
    r = optimize_daily_dispatch(prices, get_assumptions())
    assert r["net_revenue_krw"] == pytest.approx(0, abs=1e-3)


def test_real_day_respects_constraints():
    a = get_assumptions()
    day = complete_days(load_hourly_series(SERIES)).groupby("date").get_group(
        pd.Timestamp("2024-01-15"))
    r = optimize_daily_dispatch(day.set_index("hour")["smp_krw_per_kwh"], a)
    c = check_dispatch(r["dispatch"], a)
    assert c["power_violation_mw"] < 1e-6
    assert c["soc_violation_mwh"] < 1e-4
    assert abs(c["end_soc_mwh"]) < 1e-4
    assert c["simultaneous_mw"] < 1e-6
    internal_out = r["dispatch"]["discharge_mw"].sum() / math.sqrt(a["round_trip_efficiency"])
    assert internal_out <= a["energy_mwh"] * a["cycles_per_day"] + 1e-4


def test_cycle_cap_limits_two_peak_day():
    # Two cheap/dear pairs: without the cap the LP would cycle twice.
    p = [50.0] * 5 + [200.0] * 5 + [50.0] * 5 + [200.0] * 5 + [100.0] * 4
    a = get_assumptions()
    r = optimize_daily_dispatch(pd.Series(p, index=range(1, 25)), a)
    internal_out = r["dispatch"]["discharge_mw"].sum() / math.sqrt(a["round_trip_efficiency"])
    assert internal_out == pytest.approx(a["energy_mwh"], rel=1e-6)


def test_solver_failure_raises():
    with pytest.raises(RuntimeError):
        optimize_daily_dispatch(pd.Series([1.0, 2.0], index=[1, 2]),
                                small_battery(energy_mwh=-1))


def test_legacy_heuristic_exceeds_power_limit():
    # Documents why the heuristic is not the baseline.
    a = get_assumptions()
    implied_charge_mw = a["energy_mwh"] / a["round_trip_efficiency"] / a["duration_h"]
    assert implied_charge_mw > a["power_mw"]
    prices = pd.Series(120.0, index=range(1, 25))
    assert daily_arbitrage_revenue(prices, a)["net_revenue_krw"] < 0   # forced loss


# --- finance ---------------------------------------------------------------

@pytest.mark.parametrize("daily_krw", [5e6, 13.5e6, 40e6])
def test_breakeven_resubstitution(daily_krw):
    a = get_assumptions()
    be = breakeven_capex_per_kwh(daily_krw, a)
    assert npv_of(daily_krw, dict(a, capex_per_kwh_krw=be)) == pytest.approx(0, abs=1.0)
    m = breakeven_daily_revenue_multiplier(daily_krw, a)
    assert npv_of(daily_krw * m, a) == pytest.approx(0, abs=1.0)
    npv0 = npv_of(daily_krw, a)
    extra = stacked_revenue_needed_per_kw_year(npv0, a) * a["power_mw"] * 1_000
    cf = build_cashflows(daily_krw, a)["net_cashflow_krw"].copy()
    cf.loc[1:] += extra
    assert compute_npv(cf, a["discount_rate"]) == pytest.approx(0, abs=1.0)


def test_cashflow_units():
    a = get_assumptions()
    cf = build_cashflows(1e6, a)
    assert cf.loc[0, "capex_krw"] == pytest.approx(470_000 * 400 * 1_000)   # KRW/kWh * kWh
    assert cf.loc[1, "gross_revenue_krw"] == pytest.approx(1e6 * 350)
    assert cf.loc[2, "gross_revenue_krw"] == pytest.approx(1e6 * 350 * 0.98)


# --- price scenario --------------------------------------------------------

def test_log_log_elasticity_arithmetic():
    base = pd.Series([100.0], index=[1])
    out = apply_solar_scenario(base, pd.Series([-0.0058], index=[1]), 0.01)
    pct = out.loc[1, "scenario_smp"] / 100.0 - 1
    assert pct == pytest.approx(math.exp(-0.0058 * math.log(1.01)) - 1, rel=1e-9)
    assert abs(pct) < 1e-4            # ~ -0.0058 %, not -0.58 %


# --- data ------------------------------------------------------------------

def test_real_series_completeness():
    rep = validate_hourly_series(load_hourly_series(SERIES))
    assert rep["rows"] == 8760
    assert rep["expected_hours_in_year"] == 8784         # 2024 is a leap year
    assert rep["complete_dates"] == 364
    assert set(rep["incomplete_dates_missing_hours"]) == {"2024-01-01", "2024-12-31"}
    assert rep["duplicate_date_hour_rows"] == 0


def test_complete_days_drops_partial_and_duplicate_days():
    d = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01"] * 24 + ["2024-01-02"] * 23
                               + ["2024-01-03"] * 24),
        "hour": list(range(1, 25)) + list(range(1, 24)) + [1] + list(range(1, 24)),
        "smp_krw_per_kwh": np.arange(71.0),
    })
    kept = complete_days(d)
    assert list(kept["date"].unique()) == [pd.Timestamp("2024-01-01")]
