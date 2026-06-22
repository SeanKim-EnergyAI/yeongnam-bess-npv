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

        # --- Financial spec ---
        # Battery capex: a 4-hour utility-scale Li-ion system runs ~$300-400/kWh
        # installed in 2024 (NREL ATB 2024; Lazard LCOS v9). Midpoint ~$350/kWh
        # at ~1,350 KRW/USD ~= 470,000 KRW/kWh. The break-even table shows the
        # negative-NPV conclusion holds across this whole range.
        "capex_per_kwh_krw": 470_000,     # installed cost per kWh (sourced midpoint)
        "om_pct_of_capex_per_year": 0.02, # fixed O&M as a share of capex
        "discount_rate": 0.07,            # WACC / hurdle rate
        "project_life_years": 15,

        # --- Solar growth scenario (this reshapes the price curve) ---
        "solar_growth_pct": 0.30,         # assumed % increase in solar generation

        # --- Elasticity context (the hourly vector lives in data/elasticities.csv) ---
        # From the working paper: IV regression of log(SMP) on log(Solar).
        # -0.0058 means "+1% solar -> -0.58% SMP" on the national average.
        "elasticity_iv_average": -0.0058,      # national mainland, Phase 1 main spec
        "elasticity_zonal_yeongnam": -0.0135,  # Yeongnam, Phase 2B (~2.3x stronger)
        # Hours below this solar generation (MWh) are treated as non-solar: their
        # IV coefficients are weakly identified and zeroed in the conservative run.
        "solar_active_threshold_mwh": 50,
    }

    # Derived quantities: never hand-type a number you can compute from others.
    a["energy_mwh"] = a["power_mw"] * a["duration_h"]
    return a
