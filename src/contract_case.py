"""Case B - 2026 mainland ESS central contract market (KPX notice 2026-05).

Research hypothetical only: a 50 MW / 300 MWh (transmission-side, 송전단) ESS.
It is not an eligible project, has no site, and no award price is known.

Source: docs/sources/kpx_notice_2026-05_ess_central_contract_mainland.pdf
(한국전력거래소 공고 제2026-05호, dated 2026-09-22). "p.N / PDF M" below means
the printed page number N and the PDF page M.

Settlement in the notice (p.26 / PDF 28, "정산 및 결제"), settled monthly:

    daily settlement = sum_{t=1..24} contract_price_i * supply_capacity_{i,t} * perf_rate_{i,t}
    supply_capacity  = max_stored_energy_{i,t} / 6                       [kW]
    perf_rate_{i,t}  = 1 - { (shortfall_chg/instr_chg) * a + (shortfall_dis/instr_dis) * (1-a) }
    a                = instr_chg / (instr_chg + instr_dis);  each ratio capped at 1
    shortfall        = |dispatch instruction - metered value|

Units: contract_price is KRW/kW-h (p.14 / PDF 16, p.22 / PDF 24): a fixed charge
per kW of supply capacity per settled hour. It is NOT a price per kWh of energy
discharged. KRW/kW-h x kW x 1 h x perf_rate [-] = KRW for that hour.

Charging cost and discharge revenue are not settled (p.22 / PDF 24): the bid
price excludes charging cost, and "정산시 충전비용 및 방전수익은 미정산". So case B
has no SMP arbitrage term, and none is added.

Two calculation paths (keep them apart):
  1. Hourly notice formula: `hourly_performance_rate`, `daily_settlement_krw`.
     Implemented as written; raises where the notice leaves the rate undefined
     (an hour with no dispatch instruction). Not called by the break-even price.
  2. Annual simplification: `build_contract_cashflows`, `breakeven_contract_price`.
     Uses one HYPOTHETICAL effective payment factor f in every settled hour and
     supply capacity = contracted kW in every hour. f is not the notice's
     이행률; whether they coincide depends on rules not yet read.
See docs/contract_model_design.md for what the simplification omits.
"""

import math

import numpy as np
import pandas as pd

HOURS_PER_DAY = 24                 # notice: sum over t = 1..24
DAYS_PER_YEAR = 365                # leap days ignored (<0.3% of hours)
KWH_PER_MWH = 1_000
NOTICE_DURATION_H = 6              # p.22 / PDF 24; p.26 / PDF 28 ("÷ 6")
BID_RANGE_MW = (10, 100)           # exclusive bounds, 1 MW steps; p.1 / PDF 3, p.22 / PDF 24


# NREL ATB 2024 v3 workbook (docs/sources/ATB_2024_v3_Workbook.xlsx), sheet
# "Utility-Scale Battery Storage". All values 2022$ (cells D10, D67); year columns
# are projection years (2022 = base year, G9). Overnight capital cost (OCC, $/kW)
# = energy $/kWh (rows 19-21) x hours + power $/kW (rows 25-27). OCC EXCLUDES grid
# connection (GCC, $100/kW, rows 155-164) and construction financing; ATB "CAPEX"
# (rows 70-84) = (OCC + GCC) x CFF. Cached values match the formulas.
ATB_OCC_CASES = {
    # key: (OCC $/kW, hours, cell, note)
    "legacy_4h_2023": (1906.96, 4, "H108", "4Hr Moderate, 2023; = dashboard $1,906.95/kW, $476.74/kWh"),
    "6h_2023": (2680.79864712, 6, "H111", "6Hr Moderate, 2023 (same in all scenarios in 2023)"),
    "6h_2029_moderate": (1867.549873504914, 6, "N111", "6Hr Moderate, 2029 projection"),
}


def atb_occ_usd_per_kwh(case: str) -> float:
    """ATB OCC for `case` expressed per kWh of rated (usable) energy."""
    occ_kw, hours, _, _ = ATB_OCC_CASES[case]
    return occ_kw / hours


def get_contract_assumptions(cost_case: str = "6h_2023") -> dict:
    """Case-B inputs. Every value is either from a cited source or a labelled research assumption."""
    a = {
        # --- Hypothetical facility (research example, not a real project) ---
        "contract_power_kw": 50_000,         # 송전단 최대 방전용량; inside the 10-100 MW bid range
        "duration_h": NOTICE_DURATION_H,     # 6 h at the transmission-side meter (notice)

        # --- Internal battery sizing: ILLUSTRATIVE ONLY, does not enter cost ---
        # Unverified placeholders, used only to show how internal capacity relates to
        # the 송전단 requirement.
        "rte_illustrative": 0.86,            # same placeholder as case A
        "aux_share_illustrative": 0.0,       # auxiliary load as a share of discharged energy
        "soc_window_illustrative": 1.0,      # usable SOC range as a share of nameplate

        # --- Cost (US reference, 2022$, comparison only; NOT a Korean quote) ---
        # Default "6h_2023": ATB 6-hour OCC, 2023 column (H111) / 6 h = 446.80 $/kWh.
        # "legacy_4h_2023" (476.74 $/kWh, 4-hour H108) reproduces the earlier 59.4203.
        # ATB energy is stated as usable (web text); applied to 송전단 deliverable kWh.
        "cost_case": cost_case,
        "capex_usd_per_kwh": atb_occ_usd_per_kwh(cost_case),
        # Research assumption, same as case A; not a sourced forecast.
        "krw_per_usd": 1_350,
        # ATB fixed O&M = 0.025 x OCC (workbook formulas H125/H128); it includes
        # battery augmentation so the system keeps rated capacity for its 15-year
        # life (ATB web text). Applied to OCC-based capex, so it follows the cost case.
        "fixed_om_pct_of_capex": 0.025,
        # 0 = O&M held flat in nominal KRW (omits cost inflation; stated assumption).
        "om_escalation": 0.0,

        # --- Contract and finance ---
        "trading_years": 15,                 # 거래기간 15년 from COD (p.25 / PDF 27)
        # Contract price is fixed for the whole term, no inflation indexation
        # (p.25 / PDF 27), so the model runs in NOMINAL KRW.
        "discount_rate": 0.07,               # research assumption, NOT a verified Korean WACC
        # Hypothetical effective payment factor f (share of the full 24 h x kW x price
        # payment actually received). NOT the notice's 이행률 and NOT observed.
        "effective_payment_factor": 1.0,
        "capex_multiplier": 1.0,             # hypothetical; scales capex only
        "om_multiplier": 1.0,                # hypothetical; scales total fixed O&M (augmentation included)
    }
    return a


# --- Quantities -------------------------------------------------------------

def deliverable_energy_kwh(a: dict) -> float:
    """최대 전력저장량: energy deliverable at the 송전단 over `duration_h` at full power."""
    return a["contract_power_kw"] * a["duration_h"]


def supply_capacity_kw(a: dict) -> float:
    """공급가능용량 = 최대전력저장량 / 6 (notice p.26 / PDF 28)."""
    return deliverable_energy_kwh(a) / NOTICE_DURATION_H


def internal_nameplate_kwh(a: dict) -> float:
    """Illustrative internal battery energy needed to deliver the 송전단 energy.

    battery -> meter losses:  one-way efficiency sqrt(RTE), then auxiliary load;
    only `soc_window` of nameplate is usable. Not used for cost: the capex basis
    below is the deliverable energy, so efficiency is never applied to cost twice.
    """
    one_way = math.sqrt(a["rte_illustrative"]) * (1 - a["aux_share_illustrative"])
    return deliverable_energy_kwh(a) / one_way / a["soc_window_illustrative"]


def base_capex_krw(a: dict) -> float:
    """ATB $/kWh x KRW/USD (applied once) x 송전단 deliverable kWh; no multiplier."""
    return a["capex_usd_per_kwh"] * a["krw_per_usd"] * deliverable_energy_kwh(a)


def capex_krw(a: dict) -> float:
    """Capex including the hypothetical CAPEX multiplier."""
    return base_capex_krw(a) * a["capex_multiplier"]


def annual_fixed_om_krw(a: dict) -> float:
    """Fixed O&M incl. augmentation (per ATB inclusions), set from BASE capex.

    Tied to base capex, so the CAPEX multiplier gives a one-variable CAPEX
    sensitivity with O&M held fixed. (Earlier versions scaled O&M with the
    multiplier, i.e. a joint CAPEX+O&M scenario.) O&M has its own multiplier.
    """
    return base_capex_krw(a) * a["fixed_om_pct_of_capex"] * a["om_multiplier"]


def settled_kw_hours_per_year(a: dict) -> float:
    """kW x settled hours per year (24 h x 365 d), before the performance rate."""
    return supply_capacity_kw(a) * HOURS_PER_DAY * DAYS_PER_YEAR


def check_bid_range(a: dict) -> None:
    mw = a["contract_power_kw"] / 1_000
    lo, hi = BID_RANGE_MW
    if not (lo < mw < hi and float(mw).is_integer()):
        raise ValueError(f"{mw} MW is outside the notice bid range ({lo}, {hi}) MW in 1 MW steps")


# --- Settlement formula (notice, p.26 / PDF 28) -----------------------------

def hourly_performance_rate(instr_charge_kwh: float, metered_charge_kwh: float,
                            instr_discharge_kwh: float, metered_discharge_kwh: float) -> float:
    """이행률_{i,t} exactly as written in the notice.

    Raises when both instructions are zero: the NOTICE does not define that case.
    The operation rules do; see `hourly_efr_rules`.
    """
    total = instr_charge_kwh + instr_discharge_kwh
    if total <= 0:
        raise ValueError("performance rate undefined in the notice when no dispatch instruction")
    alpha = instr_charge_kwh / total

    def ratio(instr, metered):
        if instr <= 0:
            return 0.0                       # the term is weighted by 0 anyway
        return min(abs(instr - metered) / instr, 1.0)

    return 1 - (ratio(instr_charge_kwh, metered_charge_kwh) * alpha
                + ratio(instr_discharge_kwh, metered_discharge_kwh) * (1 - alpha))


def daily_settlement_krw(price_krw_per_kw_h: float, supply_kw_by_hour, perf_by_hour) -> float:
    """sum_{t=1..24} price x supply_capacity_t x perf_rate_t."""
    s, r = np.asarray(supply_kw_by_hour, float), np.asarray(perf_by_hour, float)
    if s.shape != (HOURS_PER_DAY,) or r.shape != (HOURS_PER_DAY,):
        raise ValueError("need 24 hourly values")
    return float(price_krw_per_kw_h * (s * r).sum())


# --- Settlement per the operation rules --------------------------------------
# 전력시장운영규칙 (2026. 7. edition, docs/sources/KPX_rules_20260725_excerpt.pdf),
# 별표2 Ⅰ.18 "중앙계약시장 계약용량에 대한 정산" (printed pp.531-532 / PDF 549-550),
# variables per 별표1 (printed pp.403-407, 430, 441-442). Hourly quantities in MWh.

def efr_tolerance_mwh(ra_mwh: float) -> float:
    """허용오차 ε = RA x 0.005, bounded to [0.05, 5] MWh (RA: 변경 공급가능용량)."""
    return min(max(abs(ra_mwh) * 0.005, 0.05), 5.0)


def hourly_efr_rules(set_point_mwh: float, mgo_mwh: float, egmo_mwh: float,
                     eap_mwh: float, ecd_mw: float, ra_mwh: float) -> float:
    """EFR_i,t, the hourly dispatch-compliance rate, exactly as in 별표2 Ⅰ.18.

    i)  |SET_POINT| != 0: Max[1 - |SET_POINT - MGO| / |SET_POINT|, 0];
        = 1 if |SET_POINT - MGO| <= ε.
    ii) |SET_POINT| == 0: Max{1 - |EGMO| / ECD, 0};
        = 1 if ||EAP| - |MGO|| <= ε and |EGMO| <= ε.  (<개정 2026.7.24.>)
    Sign conventions of SET_POINT/MGO are not restated in the clause; values are
    used as passed.
    """
    eps = efr_tolerance_mwh(ra_mwh)
    if set_point_mwh != 0:
        dev = abs(set_point_mwh - mgo_mwh)
        return 1.0 if dev <= eps else max(1 - dev / abs(set_point_mwh), 0.0)
    if abs(abs(eap_mwh) - abs(mgo_mwh)) <= eps and abs(egmo_mwh) <= eps:
        return 1.0
    return max(1 - abs(egmo_mwh) / ecd_mw, 0.0)


def hourly_settlement_rules_krw(eacf_krw_per_kw_h: float, enpp_krw_per_kw_h: float,
                                eose_mwh: float, emot_h: float, efr: float) -> float:
    """TECP_i,t = ((EACF - ENPP) x EOSE_i,t / EMOT_i) x EFR_i,t x 1000   [KRW].

    EOSE_i,t is the hourly BID 방전가능전력량 at the 송전단 (별표4 6.6.3); it must be
    consistent with the approved maintenance plan (별표4 6.6.2.1), so outages and
    capacity loss enter through EOSE, not through EFR.
    """
    return (eacf_krw_per_kw_h - enpp_krw_per_kw_h) * eose_mwh / emot_h * efr * 1000


# --- Cash flows and break-even ----------------------------------------------

def build_contract_cashflows(price_krw_per_kw_h: float, a: dict) -> pd.DataFrame:
    """Year 0 = capex at COD; years 1..T = contract payment - fixed O&M (nominal KRW).

    Supply capacity is held at the contracted kW every year because ATB fixed
    O&M includes battery augmentation (capacity maintained). There is no separate
    augmentation line and no degradation haircut.
    """
    check_bid_range(a)
    T = a["trading_years"]
    years = np.arange(0, T + 1)
    op = years >= 1
    capex = capex_krw(a)
    payment = np.where(op, price_krw_per_kw_h * settled_kw_hours_per_year(a)
                       * a["effective_payment_factor"], 0.0)
    om = np.where(op, annual_fixed_om_krw(a)
                  * (1 + a["om_escalation"]) ** np.maximum(years - 1, 0), 0.0)
    capex_flow = np.where(years == 0, capex, 0.0)
    df = pd.DataFrame({
        "year": years,
        "contract_payment_krw": payment,
        "fixed_om_incl_augmentation_krw": om,
        "capex_krw": capex_flow,
        "net_cashflow_krw": payment - om - capex_flow,
    }).set_index("year")
    df["discount_factor"] = 1 / (1 + a["discount_rate"]) ** df.index
    df["pv_net_cashflow_krw"] = df["net_cashflow_krw"] * df["discount_factor"]
    return df


def contract_npv(price_krw_per_kw_h: float, a: dict) -> float:
    return float(build_contract_cashflows(price_krw_per_kw_h, a)["pv_net_cashflow_krw"].sum())


def breakeven_contract_price(a: dict) -> float:
    """Contract price (KRW/kW-h) at which NPV = 0.

    NPV(p) = -CAPEX + sum_y DF_y (p * Q * f - OM_y)  is linear in p, so
    p* = (CAPEX + PV(OM)) / (f * PV(Q)), with Q = kW x 8,760 h per year.
    """
    cf = build_contract_cashflows(0.0, a)
    df = cf["discount_factor"]
    pv_cost = cf["capex_krw"].sum() + (cf["fixed_om_incl_augmentation_krw"] * df).sum()
    pv_q = (settled_kw_hours_per_year(a) * a["effective_payment_factor"] * df.loc[1:]).sum()
    return float(pv_cost / pv_q)
