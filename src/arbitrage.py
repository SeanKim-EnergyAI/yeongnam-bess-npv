"""LEGACY heuristic daily arbitrage -- kept only as a comparison to the LP.

Dispatch rule: each day, charge during the cheapest `duration_h` hours and
discharge during the most expensive `duration_h` hours. Round-trip losses
mean we must buy MORE energy than we sell, which is why charge energy is
divided by the efficiency.

Not a feasible schedule: it ignores hour order (may "discharge" before it
charges), draws energy/rte = 465 MWh in 4 h (116 MW > 100 MW limit), and always
trades even when the spread does not cover losses. The baseline uses
src/optimize_dispatch.py instead.
"""

import pandas as pd

KWH_PER_MWH = 1_000  # SMP is quoted in KRW/kWh; we settle energy in MWh


def select_dispatch_hours(prices: pd.Series, n_hours: int):
    """Return (charge_hours, discharge_hours): cheapest n to buy, dearest n to sell."""
    ranked = prices.sort_values()
    charge_hours = list(ranked.index[:n_hours])
    discharge_hours = list(ranked.index[-n_hours:])
    return charge_hours, discharge_hours


def daily_arbitrage_revenue(prices: pd.Series, assumptions: dict) -> dict:
    n = assumptions["duration_h"]
    rte = assumptions["round_trip_efficiency"]
    energy_mwh = assumptions["energy_mwh"]

    charge_hours, discharge_hours = select_dispatch_hours(prices, n)

    # KRW/kWh -> KRW/MWh so the MWh energy terms cancel cleanly
    avg_discharge_price = prices[discharge_hours].mean() * KWH_PER_MWH
    avg_charge_price = prices[charge_hours].mean() * KWH_PER_MWH

    discharge_revenue = energy_mwh * avg_discharge_price
    charge_energy_mwh = energy_mwh / rte               # over-buy to cover losses
    charge_cost = charge_energy_mwh * avg_charge_price
    net_revenue = discharge_revenue - charge_cost

    return {
        "charge_hours": charge_hours,
        "discharge_hours": discharge_hours,
        "avg_charge_price_krw_per_mwh": avg_charge_price,
        "avg_discharge_price_krw_per_mwh": avg_discharge_price,
        "discharge_revenue_krw": discharge_revenue,
        "charge_cost_krw": charge_cost,
        "net_revenue_krw": net_revenue,
    }
