"""Checks for case B (central contract market settlement and break-even price).

Run from the project root:  python3 -m pytest -q
"""

import pytest

from src.contract_case import (annual_fixed_om_krw, breakeven_contract_price, capex_krw,
                               contract_npv,
                               daily_settlement_krw, deliverable_energy_kwh,
                               get_contract_assumptions, hourly_performance_rate,
                               settled_kw_hours_per_year, supply_capacity_kw)


def test_units_and_notice_quantities():
    a = get_contract_assumptions()
    assert deliverable_energy_kwh(a) == 300_000                  # 50 MW x 6 h at 송전단
    assert supply_capacity_kw(a) == 50_000                       # 최대전력저장량 / 6
    assert settled_kw_hours_per_year(a) == 50_000 * 24 * 365     # kW x h
    assert capex_krw(a) == pytest.approx(2680.79864712 / 6 * 1_350 * 300_000)   # ATB H111 / 6 h
    legacy = get_contract_assumptions("legacy_4h_2023")
    assert capex_krw(legacy) == pytest.approx(476.74 * 1_350 * 300_000)


def test_bid_range_is_enforced():
    a = get_contract_assumptions()
    for bad_kw in (10_000, 100_000, 50_500):                     # bounds exclusive; 1 MW steps
        with pytest.raises(ValueError):
            contract_npv(10.0, dict(a, contract_power_kw=bad_kw))


def test_daily_settlement_hand_calculation():
    # 10 KRW/kW-h x 50,000 kW x 24 h x 0.95 = 11,400,000 KRW/day
    assert daily_settlement_krw(10.0, [50_000] * 24, [0.95] * 24) == pytest.approx(11_400_000)


def test_hourly_performance_rate_follows_notice_formula():
    # discharge-only instruction, 10% shortfall -> 0.90
    assert hourly_performance_rate(0, 0, 100, 90) == pytest.approx(0.90)
    # alpha = 30/(30+70) = 0.3: 1 - (0.2*0.3 + 0.1*0.7) = 0.87
    assert hourly_performance_rate(30, 24, 70, 63) == pytest.approx(0.87)
    # shortfall above the instruction is capped at a ratio of 1
    assert hourly_performance_rate(0, 0, 100, 350) == pytest.approx(0.0)
    with pytest.raises(ValueError):                              # undefined in the notice
        hourly_performance_rate(0, 0, 0, 0)


def test_breakeven_hand_calculation_one_year():
    a = dict(get_contract_assumptions(), trading_years=1, fixed_om_pct_of_capex=0.0)
    expected = capex_krw(a) * 1.07 / settled_kw_hours_per_year(a)
    assert breakeven_contract_price(a) == pytest.approx(expected, rel=1e-12)


@pytest.mark.parametrize("m,r", [(0.75, 1.0), (1.0, 0.95), (1.25, 0.90)])
def test_breakeven_resubstitution(m, r):
    a = dict(get_contract_assumptions(), capex_multiplier=m, effective_payment_factor=r)
    assert contract_npv(breakeven_contract_price(a), a) == pytest.approx(0, abs=1.0)


def test_direction_of_effects():
    a = get_contract_assumptions()
    p0 = breakeven_contract_price(a)
    assert breakeven_contract_price(dict(a, capex_multiplier=1.25)) > p0
    assert breakeven_contract_price(dict(a, effective_payment_factor=0.90)) > p0
    # at a fixed price, a lower payment factor lowers NPV
    assert contract_npv(p0, dict(a, effective_payment_factor=0.90)) < contract_npv(p0, a)


@pytest.mark.parametrize("f", [0.95, 0.90])
def test_payment_factor_scales_breakeven_as_one_over_f(f):
    # Arithmetic check of the annual simplification, not a penalty rule.
    a = get_contract_assumptions()
    p0 = breakeven_contract_price(a)
    assert breakeven_contract_price(dict(a, effective_payment_factor=f)) == pytest.approx(p0 / f, rel=1e-12)


def test_capex_multiplier_does_not_change_om():
    a = get_contract_assumptions()
    assert annual_fixed_om_krw(dict(a, capex_multiplier=1.25)) == annual_fixed_om_krw(a)
    assert annual_fixed_om_krw(dict(a, om_multiplier=1.25)) == pytest.approx(1.25 * annual_fixed_om_krw(a))


def test_annual_payment_matches_hand_calculation():
    # 59.42 x 50,000 kW x 8,760 h; residual is only the rounding of p* (legacy cost case)
    a = get_contract_assumptions("legacy_4h_2023")
    p = breakeven_contract_price(a)
    from src.contract_case import build_contract_cashflows
    pay = build_contract_cashflows(p, a).loc[1, "contract_payment_krw"]
    assert pay - 59.42 * 50_000 * 8_760 == pytest.approx((p - 59.42) * 50_000 * 8_760, abs=1e-3)


def test_cost_cases_reproduce_legacy_and_atb_arithmetic():
    # Legacy 476.74 $/kWh reproduces the earlier p*; 6 h value is ATB H111 = G20*6 + G26.
    assert breakeven_contract_price(get_contract_assumptions("legacy_4h_2023")) == pytest.approx(59.4203, abs=5e-5)
    from src.contract_case import atb_occ_usd_per_kwh
    assert atb_occ_usd_per_kwh("6h_2023") * 6 == pytest.approx(386.91932356 * 6 + 359.28270576)


def test_hourly_efr_rules_cases():
    # 별표2 Ⅰ.18 of the operation rules (2026.7). RA = 300 MWh -> ε = 1.5 MWh.
    from src.contract_case import efr_tolerance_mwh, hourly_efr_rules
    assert efr_tolerance_mwh(300) == pytest.approx(1.5)
    assert efr_tolerance_mwh(1) == pytest.approx(0.05)           # lower bound
    assert efr_tolerance_mwh(5000) == pytest.approx(5.0)         # upper bound
    assert hourly_efr_rules(50, 45, 0, 0, 50, 300) == pytest.approx(0.90)
    assert hourly_efr_rules(50, 49, 0, 0, 50, 300) == 1.0        # within ε
    # no dispatch instruction: idle within ε -> 1; 5 MWh unscheduled output -> 1 - 5/50
    assert hourly_efr_rules(0, -0.2, 0.0, 0.2, 50, 300) == 1.0
    assert hourly_efr_rules(0, 5, 5, 0.2, 50, 300) == pytest.approx(0.90)


def test_hourly_settlement_rules_hand_calculation():
    # (55 - 0) KRW/kW-h x 300 MWh / 6 h x 1.0 x 1000 = 2,750,000 KRW for the hour
    from src.contract_case import hourly_settlement_rules_krw
    assert hourly_settlement_rules_krw(55, 0, 300, 6, 1.0) == pytest.approx(2_750_000)
