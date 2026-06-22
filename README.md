# Yeongnam 100MW BESS — Arbitrage NPV

**Turning a causal estimate into an investment decision.** My working paper
estimates how solar generation moves Korea's System Marginal Price (SMP). This
project asks the business question that follows: **is a 100MW / 4h battery in the
Yeongnam region worth building on price arbitrage alone?**

Built entirely on the paper's own 2024 data — the same 140,138-observation panel
behind the regression — not stylized inputs.

## Two findings that survive the real data

**1. Korea has no "duck curve" yet — so the battery charges pre-dawn, not midday.**
The cheapest hours in 2024 are 03–05h (~96 KRW/kWh), when solar output is zero;
midday and evening sit on a broad expensive plateau (~134–142). The solar-driven
midday price dip that BESS arbitrage relies on in California has not emerged in
Korea's single-price market.

**2. More solar slightly *raises* the spread here — the opposite of the naive story.**
My paper's hourly estimates show a positive solar effect on *daytime* SMP (the
"intraday absorption pattern"). Because the battery discharges into those
daytime-peak hours, growing solar nudges its revenue *up*, not down. But the
effect is second-order.

![Korea 2024 SMP, solar, and dispatch](outputs/price_curve.png)

## TL;DR result

| Metric | Value |
|---|---|
| System | 100 MW / 4 h (400 MWh) |
| Baseline SMP (real 2024) | mean 125.5 KRW/kWh, min h4 = 96, max h10 = 142 |
| Dispatch | charge 03–06h (~98), discharge daytime peak (~141) |
| Arbitrage spread | ~42 KRW/kWh |
| Daily net revenue | ~0.11억 KRW |
| Capex | ~1,600억 KRW |
| **NPV @ 7%** | **≈ −1,592억 KRW** |
| IRR | undefined (cash flows never recover capex) |

**Energy arbitrage alone does not justify the capex** — a robust, defensible
finding. The contribution is quantifying *how far* it misses and *which levers*
would close it.

## Break-even levers (what would make NPV = 0)

| Lever | Required | vs. now |
|---|---|---|
| Capex | ~63,000 KRW/kWh | ~6x below market (~400,000) |
| Daily arbitrage | ~6.3x larger | spread far beyond the data |
| Stacked revenue | ~175,000 KRW/kW-yr | capacity / ancillary on top |

## Robustness: the econometric debate is immaterial to the investment

My paper flags that the hourly solar sign is contested (the daytime effect is
positive, against intuition). The model quantifies how much that matters:

| Elasticity scenario | NPV |
|---|---|
| as-estimated (national HTE) | −1,592억 |
| solar-hours only (night = 0) | −1,595억 |
| Yeongnam intensity (×2.3)    | −1,574억 |
| flat IV average (−0.0058)    | −1,605억 |

All within ~2%. **The contested sign matters for the paper, not for the business
call** — capex dominates. Even halving capex to 150,000 KRW/kWh leaves NPV at
−410억.

## How it works

```
real 2024 SMP + hourly IV elasticities  ->  price scenario  ->  daily arbitrage
   ->  cash flows (capex, O&M, degradation)  ->  NPV / IRR  ->  break-even
```

The bridge from academics to business is one equation:

```
scenario_SMP[h] = baseline_SMP[h] * (1 + solar_growth) ** elasticity[h]
```

| Module | Responsibility |
|---|---|
| `scripts/build_inputs_from_panel.py` | Derive real hourly inputs from the research panel |
| `src/assumptions.py`    | All inputs in one place, units in the key names |
| `src/price_scenario.py` | Reshape baseline SMP via hourly elasticities |
| `src/arbitrage.py`      | Pick charge/discharge hours, daily net revenue |
| `src/cashflow.py`       | Capex, O&M, degradation -> annual cash flows |
| `src/valuation.py`      | NPV, IRR, payback |
| `src/breakeven.py`      | Closed-form break-even capex / arbitrage / stacking |
| `run_phase3.py`         | Orchestrate: summary, break-even, robustness, plots |

## Run

```bash
pip install -r requirements.txt
python3 run_phase3.py                       # uses the committed real-data inputs
```

To regenerate the inputs from the raw research files:

```bash
python3 scripts/build_inputs_from_panel.py \
    --panel ".../panel_v4_main.csv" --hte ".../v4_phase2_hte.csv"
```

## Data

| Input | Source |
|---|---|
| `data/baseline_smp_hourly.csv` | National hour-of-day mean SMP, 2024 mainland panel (N=140,138) |
| `data/solar_profile_hourly.csv` | National hour-of-day mean solar generation, same panel |
| `data/elasticities.csv` | Hourly log(SMP)~log(Solar) IV coefficients (Phase 2 HTE) |

Only these small aggregates live here; the raw panel stays in the research repo.
The one remaining placeholder is battery capex (~$300/kWh, BNEF range) in
`assumptions.py` — and the break-even table shows the conclusion holds across it.

## Context

Business extension of the working paper *"Does Solar Generation Lower the Korean
SMP?"* (IV / 2SLS, 2024 hourly panel, 16 mainland regions, first-stage F = 27,351;
national effect −0.58%, Yeongnam −1.35%). This repo is the "academic result →
business case" layer.
