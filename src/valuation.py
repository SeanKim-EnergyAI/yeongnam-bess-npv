"""Investment metrics: NPV, IRR, simple payback.

numpy_financial.npv treats the first array element as a t=0 (undiscounted)
cash flow, which matches our convention of putting capex in year 0.
"""

import numpy_financial as npf
import pandas as pd


def compute_npv(net_cashflow: pd.Series, discount_rate: float) -> float:
    return npf.npv(discount_rate, net_cashflow.values)


def compute_irr(net_cashflow: pd.Series) -> float:
    return npf.irr(net_cashflow.values)


def compute_payback_year(net_cashflow: pd.Series):
    cumulative = net_cashflow.cumsum()
    recovered = cumulative[cumulative > 0]
    return int(recovered.index[0]) if len(recovered) else None


def summarize(cashflows_df: pd.DataFrame, discount_rate: float) -> dict:
    cf = cashflows_df["net_cashflow_krw"]
    return {
        "npv_krw": compute_npv(cf, discount_rate),
        "irr": compute_irr(cf),
        "payback_year": compute_payback_year(cf),
    }
