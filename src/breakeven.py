"""Closed-form break-even levers.

Arbitrage alone gives a negative NPV, so the useful questions are *how far off*
and *what closes the gap*. Each function below is solved analytically from the
same NPV identity the pipeline computes numerically:

    NPV = -capex + daily_net * K  -  om_pct * capex * A

where  A = sum_t 1/(1+r)^t                         (annuity factor)
       K = days * sum_t (1-deg)^(t-1) / (1+r)^t     (PV of revenue per daily KRW)
"""

import numpy as np

KWH_PER_MWH = 1_000


def _years(a: dict) -> np.ndarray:
    return np.arange(1, a["project_life_years"] + 1)


def annuity_factor(a: dict) -> float:
    y = _years(a)
    return float((1 / (1 + a["discount_rate"]) ** y).sum())


def revenue_pv_per_daily_krw(a: dict) -> float:
    """K: multiply by daily net revenue to get PV of lifetime gross revenue."""
    y = _years(a)
    df = 1 / (1 + a["discount_rate"]) ** y
    keep = (1 - a["annual_degradation"]) ** (y - 1)
    return float(a["operating_days_per_year"] * (keep * df).sum())


def _capex_total_krw(a: dict) -> float:
    return a["capex_per_kwh_krw"] * a["energy_mwh"] * KWH_PER_MWH


def breakeven_capex_per_kwh(daily_net_krw: float, a: dict) -> float:
    """Capex (KRW/kWh) at which NPV = 0, holding revenue fixed."""
    K, A = revenue_pv_per_daily_krw(a), annuity_factor(a)
    capex_total_be = daily_net_krw * K / (1 + a["om_pct_of_capex_per_year"] * A)
    return capex_total_be / (a["energy_mwh"] * KWH_PER_MWH)


def breakeven_daily_revenue_multiplier(daily_net_krw: float, a: dict) -> float:
    """How many times larger daily arbitrage must be for NPV = 0."""
    K, A = revenue_pv_per_daily_krw(a), annuity_factor(a)
    capex = _capex_total_krw(a)
    daily_be = capex * (1 + a["om_pct_of_capex_per_year"] * A) / K
    return daily_be / daily_net_krw


def stacked_revenue_needed_per_kw_year(npv_base_krw: float, a: dict) -> float:
    """Constant extra annual revenue (KRW/kW-yr) that lifts NPV to 0.

    Stands in for capacity-market / ancillary-service income a real BESS stacks
    on top of arbitrage. Positive when the base NPV is negative.
    """
    R = -npv_base_krw / annuity_factor(a)        # KRW per year, project-wide
    return R / (a["power_mw"] * 1_000)           # KRW per kW-year
