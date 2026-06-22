"""Central assumptions for the Yeongnam 100MW BESS NPV model.

Every value here is a PLACEHOLDER for a portfolio prototype. Replace the
figures marked `# TODO` with numbers from your own data / vendor quotes
before treating any output as a real investment recommendation.

Units are encoded in each key name on purpose: the most common (and most
expensive) modelling bug is silently mixing MW with MWh, or KRW/kWh with
KRW/MWh. Keeping units in the name makes those mistakes visible at the
call site.
"""


def get_assumptions() -> dict:
    a = {
        # --- BESS technical spec ---
        "power_mw": 100,                  # rated power
        "duration_h": 4,                  # hours of storage at rated power
        "round_trip_efficiency": 0.86,    # AC-to-AC; energy out / energy in
        "cycles_per_day": 1,              # one charge + discharge per day
        "operating_days_per_year": 350,   # ~15 days/yr reserved for maintenance
        "annual_degradation": 0.02,       # usable-capacity fade per year

        # --- Financial spec ---            # TODO: replace with real quotes
        "capex_per_kwh_krw": 400_000,     # turnkey installed cost per kWh
        "om_pct_of_capex_per_year": 0.02, # fixed O&M as a share of capex
        "discount_rate": 0.07,            # WACC / hurdle rate
        "project_life_years": 15,

        # --- Solar growth scenario (this is what reshapes the price curve) ---
        "solar_growth_pct": 0.30,         # assumed % increase in solar generation

        # --- Hour-of-day solar elasticities on log(SMP) ---
        # These come from the working-paper regression: log(SMP) on log(Solar).
        # A value of -0.0058 means "+1% solar -> -0.58% SMP" at that hour.
        # Anchors are YOUR hour-specific estimates; every other hour falls back
        # to the IV average. NOTE: the +0.0496 sign at hour 13 contradicts the
        # usual "solar depresses midday price" intuition -- verify it against
        # the regression output before drawing business conclusions.
        "elasticity_iv_average": -0.0058,
        "elasticity_anchors": {13: 0.0496, 24: -0.0748},
    }

    # Derived quantities: never hand-type a number you can compute from others.
    a["energy_mwh"] = a["power_mw"] * a["duration_h"]
    return a
