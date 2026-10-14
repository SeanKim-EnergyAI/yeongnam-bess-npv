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
         throughput cap (see below)

Conventions (see docs/model_audit.md):
  - charge/discharge are grid-side (metered) MW; each hour is 1 h, so MW = MWh.
  - energy_mwh (400) is the INTERNAL usable storage (SOC upper bound). One full
    cycle therefore draws energy/eff (~431 MWh) and delivers energy*eff (~371 MWh).
  - Throughput cap, per 24-hour block b (cap_window="per_day") or summed over
    the whole horizon (cap_window="pooled"; diagnostic only):
      cap_basis="internal" (default, modelling choice made in the audit):
          sum_{h in b} discharge[h] / eff <= energy_mwh * cycles_per_day
      cap_basis="delivered" (definition used before the audit, commit bb253a4):
          sum_{h in b} discharge[h]       <= energy_mwh * cycles_per_day
    For a single 24-hour day the two windows are identical.
  - Doing nothing is always feasible (all flows = 0), so the optimum is >= 0.
  - Perfect foresight over the horizon passed in (one day in the baseline).
"""

import math

import pandas as pd
import pulp

KWH_PER_MWH = 1_000


def optimize_daily_dispatch(prices: pd.Series, assumptions: dict,
                            cap_basis: str = "internal",
                            cap_window: str = "per_day") -> dict:
    if cap_basis not in ("internal", "delivered"):
        raise ValueError(f"unknown cap_basis {cap_basis!r}")
    if cap_window not in ("per_day", "pooled"):
        raise ValueError(f"unknown cap_window {cap_window!r}")
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
    # Throughput cap; a trailing partial block (< 24 h) still gets a full day's cap
    per_block = energy * assumptions["cycles_per_day"]
    scale = 1 / eff if cap_basis == "internal" else 1.0
    blocks = [hours[i:i + 24] for i in range(0, len(hours), 24)]
    if cap_window == "pooled":
        model += (pulp.lpSum(discharge[h] * scale for h in hours)
                  <= per_block * len(blocks))
    else:
        for b in blocks:
            model += pulp.lpSum(discharge[h] * scale for h in b) <= per_block

    model.solve(pulp.PULP_CBC_CMD(msg=False))
    status = pulp.LpStatus[model.status]
    if status != "Optimal":
        raise RuntimeError(f"Dispatch LP not solved to optimality: {status}")

    dispatch = pd.DataFrame({
        "price_smp": prices,
        "charge_mw": [charge[h].value() for h in hours],
        "discharge_mw": [discharge[h].value() for h in hours],
        "soc_mwh": [soc[h].value() for h in hours],
    }, index=hours)

    return {
        "status": status,
        "net_revenue_krw": pulp.value(model.objective),
        "dispatch": dispatch,
    }


def check_dispatch(dispatch: pd.DataFrame, assumptions: dict, tol: float = 1e-6) -> dict:
    """Independently re-check a solved schedule against the battery constraints.

    Returns the worst violation of each constraint (0 = satisfied) plus the
    largest simultaneous charge+discharge overlap, min(charge, discharge), in MW.
    """
    power = assumptions["power_mw"]
    energy = assumptions["energy_mwh"]
    eff = math.sqrt(assumptions["round_trip_efficiency"])
    c, d = dispatch["charge_mw"], dispatch["discharge_mw"]
    soc_rebuilt = (eff * c - d / eff).cumsum()          # start empty
    return {
        "power_violation_mw": max(0.0, c.max() - power, d.max() - power,
                                  -c.min(), -d.min()),
        "soc_violation_mwh": max(0.0, soc_rebuilt.max() - energy, -soc_rebuilt.min()),
        "soc_balance_error_mwh": float((soc_rebuilt - dispatch["soc_mwh"]).abs().max()),
        "end_soc_mwh": float(soc_rebuilt.iloc[-1]),
        "simultaneous_mw": float(pd.concat([c, d], axis=1).min(axis=1).max()),
    }
