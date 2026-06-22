"""LP optimization of one day's battery dispatch (Phase 4).

src/arbitrage.py uses a heuristic: charge the cheapest hours, discharge the
dearest. That ignores a real constraint -- to *deliver* a full cycle you must
*draw* more than capacity (round-trip losses), which takes more than `duration`
hours at the power limit. This module replaces the heuristic with a linear
program that maximizes daily arbitrage profit subject to real battery physics:

    max  sum_h price[h] * (discharge[h] - charge[h])
    s.t. 0 <= charge[h], discharge[h] <= power_mw
         0 <= soc[h] <= energy_mwh
         soc[h] = soc[h-1] + eff*charge[h] - discharge[h]/eff
         soc starts and ends empty                 (closed daily cycle)
         sum_h discharge[h] <= energy_mwh * cycles_per_day
"""

import math

import pandas as pd
import pulp

KWH_PER_MWH = 1_000


def optimize_daily_dispatch(prices: pd.Series, assumptions: dict) -> dict:
    hours = list(prices.index)
    power = assumptions["power_mw"]
    energy = assumptions["energy_mwh"]
    eff = math.sqrt(assumptions["round_trip_efficiency"])   # split RTE over both legs
    price = prices * KWH_PER_MWH                             # KRW/kWh -> KRW/MWh

    model = pulp.LpProblem("battery_arbitrage", pulp.LpMaximize)
    charge = pulp.LpVariable.dicts("charge", hours, lowBound=0, upBound=power)
    discharge = pulp.LpVariable.dicts("discharge", hours, lowBound=0, upBound=power)
    soc = pulp.LpVariable.dicts("soc", hours, lowBound=0, upBound=energy)

    model += pulp.lpSum(price[h] * (discharge[h] - charge[h]) for h in hours)

    prev = 0                                                 # start empty
    for h in hours:
        model += soc[h] == prev + eff * charge[h] - discharge[h] / eff
        prev = soc[h]
    model += soc[hours[-1]] == 0                             # end empty
    model += (pulp.lpSum(discharge[h] for h in hours)
              <= energy * assumptions["cycles_per_day"])

    model.solve(pulp.PULP_CBC_CMD(msg=False))

    dispatch = pd.DataFrame({
        "price_smp": prices,
        "charge_mw": [charge[h].value() for h in hours],
        "discharge_mw": [discharge[h].value() for h in hours],
        "soc_mwh": [soc[h].value() for h in hours],
    }, index=hours)

    return {
        "status": pulp.LpStatus[model.status],
        "net_revenue_krw": pulp.value(model.objective),
        "dispatch": dispatch,
    }
