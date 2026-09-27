"""Case B - CONDITIONAL break-even contract price for a hypothetical 50 MW / 300 MWh
(송전단) ESS under the 2026 mainland ESS central contract market.

The result is conditional: it uses the annual simplification in
src/contract_case.py (a hypothetical effective payment factor f in all 8,760
hours; supply capacity held at the contracted kW). Two settlement definitions in
the notice are still unconfirmed, so this is not a verified market-rule result,
and no award price is known.

Writes:
    outputs/contract_breakdown.csv         step-by-step derivation of p*, with code locations
    outputs/contract_cashflows_base.csv    annual cash flows at the base-case p*
    outputs/contract_sensitivity_oneway.csv  CAPEX, f, O&M varied one at a time (hypothetical)
    outputs/contract_breakeven_grid.csv    CAPEX x f grid, O&M held at base (hypothetical)
    figures/contract_breakeven_sensitivity.png

Inputs: src/contract_case.py:get_contract_assumptions()

Run from the project root:
    python3 run_contract_case.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.contract_case import (ATB_OCC_CASES, annual_fixed_om_krw, base_capex_krw, breakeven_contract_price,
                               build_contract_cashflows, capex_krw, contract_npv,
                               deliverable_energy_kwh, get_contract_assumptions,
                               internal_nameplate_kwh, settled_kw_hours_per_year,
                               supply_capacity_kw)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "outputs")
FIG_DIR = os.path.join(HERE, "figures")
SRC = "src/contract_case.py"
CONDITIONAL = "CONDITIONAL (rules-based settlement; assumed EOSE, f and US 2022$ cost)"

# Hypothetical sensitivity values: NOT an official range, forecast or operating data
CAPEX_MULTIPLIERS = [0.75, 1.00, 1.25]
PAYMENT_FACTORS = [1.00, 0.95, 0.90]
OM_MULTIPLIERS = [0.75, 1.00, 1.25]      # total fixed O&M incl. augmentation (not augmentation alone)

# Ordinal single-hue ramp (validated: light->dark, light end >= 2:1 on white)
F_COLORS = {1.00: "#86b6ef", 0.95: "#2a78d6", 0.90: "#104281"}
INK, INK_2, GRID = "#0b0b0b", "#52514e", "#e6e5e0"


def breakdown(a: dict) -> pd.DataFrame:
    p = breakeven_contract_price(a)
    cf = build_contract_cashflows(p, a)
    df = cf["discount_factor"]
    pv_cost = cf["capex_krw"].sum() + (cf["fixed_om_incl_augmentation_krw"] * df).sum()
    pv_q = settled_kw_hours_per_year(a) * a["effective_payment_factor"] * df.loc[1:].sum()
    cfg = f"{SRC}:get_contract_assumptions"
    rows = [
        ("Contract power", a["contract_power_kw"] / 1_000, "MW", "hypothetical (bid range 10-100 MW, notice p.22/PDF 24)", cfg),
        ("Contract power", a["contract_power_kw"], "kW", "x 1,000 (MW -> kW)", cfg),
        ("Deliverable energy (송전단)", deliverable_energy_kwh(a) / 1_000, "MWh", "P x 6 h", f"{SRC}:deliverable_energy_kwh"),
        ("Deliverable energy (송전단)", deliverable_energy_kwh(a), "kWh", "x 1,000 (MWh -> kWh)", f"{SRC}:deliverable_energy_kwh"),
        ("Internal nameplate (illustrative, NOT in cost)", internal_nameplate_kwh(a), "kWh",
         "E / (sqrt(0.86) x (1-0)) / 1.0", f"{SRC}:internal_nameplate_kwh"),
        ("CAPEX unit cost", a["capex_usd_per_kwh"], "USD/kWh (2022$)",
         f"ATB 2024 v3 workbook, 'Utility-Scale Battery Storage'!{ATB_OCC_CASES[a['cost_case']][2]} "
         f"/ {ATB_OCC_CASES[a['cost_case']][1]} h: {ATB_OCC_CASES[a['cost_case']][3]} (OCC; excl. GCC and construction finance)", cfg),
        ("FX", a["krw_per_usd"], "KRW/USD", "research assumption, applied once", cfg),
        ("OCC-based initial investment (not total project cost)", capex_krw(a), "KRW", f"{a['capex_usd_per_kwh']:.4f} x 1,350 x 300,000", f"{SRC}:capex_krw"),
        ("Annual fixed O&M", annual_fixed_om_krw(a), "KRW/yr", "0.025 x OCC-based CAPEX (ATB formula H125/H128); INCLUDES augmentation", f"{SRC}:annual_fixed_om_krw"),
        ("Trading period", a["trading_years"], "yr", "notice p.25/PDF 27", cfg),
        ("Discount rate", a["discount_rate"], "-", "research assumption, NOMINAL (price fixed, no indexation)", cfg),
        ("Annuity factor sum DF_1..15", df.loc[1:].sum(), "-", "sum 1.07^-y", f"{SRC}:build_contract_cashflows"),
        ("Settled hours per year", 24 * 365, "h", "annual simplification (24 h x 365 d); NOT a confirmed rule", f"{SRC}:settled_kw_hours_per_year"),
        ("Supply capacity", supply_capacity_kw(a), "kW", "300,000 kWh / 6, held constant (not SOC)", f"{SRC}:supply_capacity_kw"),
        ("Effective payment factor f", a["effective_payment_factor"], "-", "hypothetical; not the notice 이행률", cfg),
        ("Settled quantity per year Q x f", settled_kw_hours_per_year(a) * a["effective_payment_factor"], "kW-h/yr", "50,000 kW x 8,760 h x f", f"{SRC}:settled_kw_hours_per_year"),
        ("PV of costs (CAPEX + PV O&M)", pv_cost, "KRW", f"{capex_krw(a)/1e9:.3f} bn + {annual_fixed_om_krw(a)/1e9:.3f} bn x {df.loc[1:].sum():.4f}", f"{SRC}:breakeven_contract_price"),
        ("PV of settled quantity", pv_q, "kW-h", "438,000,000 x 9.1079", f"{SRC}:breakeven_contract_price"),
        ("Break-even price p* = PV costs / PV quantity", p, "KRW/kW-h", CONDITIONAL, f"{SRC}:breakeven_contract_price"),
        ("Annual contract payment at p*", cf.loc[1, "contract_payment_krw"], "KRW/yr", "p* x Q x f", f"{SRC}:build_contract_cashflows"),
        ("Annual net cash flow at p*", cf.loc[1, "net_cashflow_krw"], "KRW/yr", "payment - O&M", f"{SRC}:build_contract_cashflows"),
        ("NPV at p* (re-substitution)", contract_npv(p, a), "KRW", "should be ~0", f"{SRC}:contract_npv"),
    ]
    return pd.DataFrame(rows, columns=["item", "value", "unit", "derivation / source", "code"])


def cost_update() -> pd.DataFrame:
    """Legacy -> duration change (same year, same OCC definition); 2029 kept separate."""
    rows, p_legacy = [], None
    for case, label in (("legacy_4h_2023", "PRIOR (reproduction): 4-h OCC applied to 6-h asset"),
                        ("6h_2023", "COST UPDATE (new base): 6-h OCC, same 2023 column"),
                        ("6h_2029_moderate", "SEPARATE scenario: 6-h OCC, 2029 Moderate projection")):
        a = get_contract_assumptions(case)
        p = breakeven_contract_price(a)
        p_legacy = p if p_legacy is None else p_legacy
        occ, hours, cell, note = ATB_OCC_CASES[case]
        rows.append({"case": label, "atb_cell": cell, "atb_occ_usd_per_kw": round(occ, 4),
                     "hours_in_atb_value": hours, "capex_usd_per_kwh_2022usd": round(occ / hours, 4),
                     "capex_krw_bn": round(capex_krw(a) / 1e9, 3),
                     "fixed_om_krw_bn_per_yr": round(annual_fixed_om_krw(a) / 1e9, 3),
                     "breakeven_price_krw_per_kw_h": round(p, 4),
                     "change_vs_prior_pct": round((p / p_legacy - 1) * 100, 2),
                     "held_constant": "f=1.00, 8,760 h, 7% nominal, FX 1,350, 15 yr",
                     "status": CONDITIONAL})
    return pd.DataFrame(rows)


def oneway(a: dict) -> pd.DataFrame:
    p0 = breakeven_contract_price(a)
    rows = []
    for key, values in (("capex_multiplier", CAPEX_MULTIPLIERS),
                        ("effective_payment_factor", PAYMENT_FACTORS),
                        ("om_multiplier", OM_MULTIPLIERS)):
        for v in values:
            aa = dict(a, **{key: v})
            p = breakeven_contract_price(aa)
            rows.append({"varied": key, "value": v,
                         "capex_krw_bn": round(capex_krw(aa) / 1e9, 3),
                         "fixed_om_krw_bn_per_yr": round(annual_fixed_om_krw(aa) / 1e9, 3),
                         "breakeven_price_krw_per_kw_h": round(p, 3),
                         "change_vs_base_pct": round((p / p0 - 1) * 100, 2),
                         "npv_at_breakeven_krw": contract_npv(p, aa),
                         "status": CONDITIONAL})
    return pd.DataFrame(rows)


def grid(a: dict) -> pd.DataFrame:
    rows = []
    for m in CAPEX_MULTIPLIERS:
        for f in PAYMENT_FACTORS:
            aa = dict(a, capex_multiplier=m, effective_payment_factor=f)
            p = breakeven_contract_price(aa)
            rows.append({"capex_multiplier": m, "effective_payment_factor": f,
                         "capex_krw_bn": round(capex_krw(aa) / 1e9, 2),
                         "breakeven_price_krw_per_kw_h": round(p, 3),
                         "npv_at_breakeven_krw": contract_npv(p, aa)})
    return pd.DataFrame(rows)


def plot_grid(g: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=150)
    fig.patch.set_facecolor("white")
    for f in PAYMENT_FACTORS:
        s = g[g["effective_payment_factor"] == f]
        ax.plot(s["capex_multiplier"], s["breakeven_price_krw_per_kw_h"], color=F_COLORS[f],
                linewidth=2, marker="o", markersize=7, markeredgecolor="white",
                markeredgewidth=1.5, label=f"hypothetical payment factor f = {f:.2f}")
        last = s.iloc[-1]
        ax.annotate(f"f = {f:.2f}: {last['breakeven_price_krw_per_kw_h']:.1f}",
                    (last["capex_multiplier"], last["breakeven_price_krw_per_kw_h"]),
                    xytext=(8, 0), textcoords="offset points", va="center",
                    fontsize=8.5, color=INK_2)
    ax.set_xticks(CAPEX_MULTIPLIERS)
    ax.set_xticklabels([f"{m:.2f}x" for m in CAPEX_MULTIPLIERS])
    ax.set_xlim(0.70, 1.42)
    ax.set_xlabel("CAPEX multiplier (O&M held at base; hypothetical)", color=INK_2)
    ax.set_ylabel("Break-even contract price (KRW/kW-h)", color=INK_2)
    ax.set_title("Case B: CONDITIONAL break-even contract price, 50 MW / 300 MWh hypothetical ESS\n"
                 "Assumed availability, payment factor and US cost - illustrative, not an award price",
                 fontsize=9.5, color=INK, loc="left")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#b5b4ae")
    ax.tick_params(colors=INK_2)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left", labelcolor=INK_2)
    os.makedirs(FIG_DIR, exist_ok=True)
    path = os.path.join(FIG_DIR, "contract_breakeven_sensitivity.png")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)
    return path


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    a = get_contract_assumptions()
    p = breakeven_contract_price(a)
    cf = build_contract_cashflows(p, a)
    b, o, g, c = breakdown(a), oneway(a), grid(a), cost_update()
    assert o["npv_at_breakeven_krw"].abs().max() < 1.0 and g["npv_at_breakeven_krw"].abs().max() < 1.0

    # Hand check of the PRIOR result: 59.42 x 50,000 kW x 8,760 h (legacy cost case, f = 1)
    al = get_contract_assumptions("legacy_4h_2023")
    pl = breakeven_contract_price(al)
    hand = 59.42 * 50_000 * 8_760
    model = build_contract_cashflows(pl, al).loc[1, "contract_payment_krw"]
    rounding = (pl - 59.42) * 50_000 * 8_760

    b.to_csv(os.path.join(OUT_DIR, "contract_breakdown.csv"), index=False)
    c.to_csv(os.path.join(OUT_DIR, "contract_cost_update.csv"), index=False)
    cf.to_csv(os.path.join(OUT_DIR, "contract_cashflows_base.csv"))
    o.to_csv(os.path.join(OUT_DIR, "contract_sensitivity_oneway.csv"), index=False)
    g.to_csv(os.path.join(OUT_DIR, "contract_breakeven_grid.csv"), index=False)
    fig = plot_grid(g)

    with pd.option_context("display.width", 220, "display.max_colwidth", 60,
                           "display.float_format", "{:,.4f}".format):
        print("=" * 76)
        print("CASE B - " + CONDITIONAL)
        print("=" * 76)
        print(b.drop(columns="code").to_string(index=False))
        print("\nCost update (other inputs held constant):")
        print(c.drop(columns=["held_constant", "status"]).to_string(index=False))
        print(f"\nHand check (prior case) 59.42 x 50,000 x 8,760 = {hand:,.0f} KRW")
        print(f"Model annual payment at prior p* = {model:,.2f} KRW")
        print(f"Difference {model - hand:,.2f} KRW = (p* - 59.42) x 438,000,000 = {rounding:,.2f} "
              "-> rounding of p* only")
        print("\nOne-way sensitivities (hypothetical):")
        print(o.drop(columns=["npv_at_breakeven_krw", "status"]).to_string(index=False))
        print("\nCAPEX x f grid, O&M at base (hypothetical):")
        print(g.pivot(index="capex_multiplier", columns="effective_payment_factor",
                      values="breakeven_price_krw_per_kw_h").to_string())
    print(f"\nWrote outputs/contract_*.csv and {os.path.relpath(fig, HERE)}")


if __name__ == "__main__":
    main()
