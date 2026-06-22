"""Project cash flows: year-0 capex, then annual arbitrage net of O&M.

Year 0   = -capex
Year t>0 = daily_net * operating_days * (1 - degradation)^(t-1)  -  O&M
"""

import numpy as np
import pandas as pd

KWH_PER_MWH = 1_000


def build_cashflows(daily_net_revenue_krw: float, assumptions: dict) -> pd.DataFrame:
    life = assumptions["project_life_years"]
    days = assumptions["operating_days_per_year"]
    degradation = assumptions["annual_degradation"]

    capex = (assumptions["capex_per_kwh_krw"]
             * assumptions["energy_mwh"] * KWH_PER_MWH)
    annual_om = capex * assumptions["om_pct_of_capex_per_year"]

    years = np.arange(0, life + 1)
    # capacity fades over time, so revenue scales by (1 - deg)^(t-1) for t >= 1
    keep_factor = np.where(years == 0, 0.0, (1 - degradation) ** (years - 1))

    gross_revenue = daily_net_revenue_krw * days * keep_factor
    om = np.where(years == 0, 0.0, annual_om)
    capex_flow = np.where(years == 0, capex, 0.0)
    net_cashflow = gross_revenue - om - capex_flow

    return pd.DataFrame({
        "year": years,
        "gross_revenue_krw": gross_revenue,
        "om_krw": om,
        "capex_krw": capex_flow,
        "net_cashflow_krw": net_cashflow,
    }).set_index("year")
