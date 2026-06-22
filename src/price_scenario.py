"""Build the 24-hour SMP price curve under a solar-growth scenario.

The econometrics give an ELASTICITY (log(SMP) on log(Solar)), not a price in
won. The translation from "academic coefficient" to "business price path" is:

    dlog(SMP)[h] = elasticity[h] * dlog(Solar)
    scenario_SMP[h] = baseline_SMP[h] * exp( dlog(SMP)[h] )

so a +30% solar scenario maps each hour's elasticity into a % move in that
hour's price, reshaping the daily curve (and the arbitrage spread).
"""

import numpy as np
import pandas as pd


def load_baseline_smp(csv_path: str) -> pd.Series:
    """Return a Series indexed by hour (1..24) of baseline SMP in KRW/kWh."""
    df = pd.read_csv(csv_path)
    return df.set_index("hour")["smp_krw_per_kwh"]


def build_hourly_elasticities(anchors: dict, default: float,
                              hours: pd.Index) -> pd.Series:
    """Full 24-hour elasticity vector: anchors where known, default elsewhere."""
    elasticities = pd.Series(default, index=hours, name="elasticity")
    for hour, value in anchors.items():
        elasticities.loc[hour] = value
    return elasticities


def apply_solar_scenario(baseline_smp: pd.Series, elasticities: pd.Series,
                         solar_growth_pct: float) -> pd.DataFrame:
    """Reshape the baseline curve given a % growth in solar generation."""
    dlog_solar = np.log1p(solar_growth_pct)          # log(1 + growth)
    dlog_smp = elasticities * dlog_solar
    scenario_smp = baseline_smp * np.exp(dlog_smp)
    return pd.DataFrame({
        "baseline_smp": baseline_smp,
        "elasticity": elasticities,
        "scenario_smp": scenario_smp,
    })
