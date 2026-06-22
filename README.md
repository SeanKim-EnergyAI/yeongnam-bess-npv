# Yeongnam 100MW BESS — Arbitrage NPV

**Translating an econometric result into an investment decision.**
My working paper estimates the elasticity of Korea's System Marginal Price (SMP)
to solar generation. This project asks the business question that follows:
**is a 100MW / 4h battery in the Yeongnam region worth building on price
arbitrage alone?**

> ⚠️ Portfolio prototype. The hourly baseline is calibrated to the KPX 2024
> mainland average (~126 KRW/kWh) but is **representative, not the raw series**;
> financial inputs are placeholders. The *method* is the deliverable. See
> [Data status](#data-status) for how to drop in real data.

## TL;DR result

| Metric | Value |
|---|---|
| System | 100 MW / 4 h (400 MWh) |
| Arbitrage spread | ~50 KRW/kWh (charge ≈107, discharge ≈156) |
| Daily net revenue | ~0.13억 KRW |
| Capex | ~1,600억 KRW |
| **NPV @ 7%** | **≈ −1,523억 KRW** |
| IRR | ≈ −27% |

**Energy arbitrage alone does not justify the capex** — a realistic, defensible
finding. The contribution is quantifying *how far* it misses and *which levers*
would close it.

![Hourly SMP and BESS dispatch](outputs/price_curve.png)

## Break-even levers (what would make NPV = 0)

| Lever | Required | vs. now |
|---|---|---|
| Capex | ~78,000 KRW/kWh | 5x below the assumed 400,000 |
| Daily arbitrage | ~5.1x larger | spread far beyond the duck curve |
| Stacked revenue | ~167,000 KRW/kW-yr | capacity / ancillary on top of arbitrage |

The takeaway lines up with industry reality: utility batteries don't pencil out
on arbitrage alone; they stack capacity and ancillary-service revenue.

## Sign-robustness (turning the open question into an answer)

My hour-13 elasticity has a counter-intuitive positive sign. Rather than hide
it, the model quantifies how much it matters:

| Elasticity scenario | NPV |
|---|---|
| as-estimated (h13 +) | −1,523억 |
| h13 sign flipped (−)  | −1,516억 |
| uniform IV average    | −1,520억 |

The investment conclusion moves <0.5%. **The contested sign matters for the
paper, not for the business call** — capex and the overall spread dominate.

## How it works

```
assumptions  ->  price scenario  ->  daily arbitrage  ->  cash flows  ->  NPV / IRR
 (units!)        log-log elastic.    cheapest/dearest     capex+O&M       numpy_financial
```

The bridge from academics to business is one equation:

```
scenario_SMP[h] = baseline_SMP[h] * (1 + solar_growth) ** elasticity[h]
```

A per-hour elasticity turns "+X% solar" into a per-hour % price move, reshaping
the daily curve and the arbitrage spread.

| Module | Responsibility |
|---|---|
| `src/assumptions.py`    | All inputs in one place, units in the key names |
| `src/data_prep.py`      | Build the real hour-of-day baseline from your panel CSV |
| `src/price_scenario.py` | Reshape baseline SMP via hourly elasticities |
| `src/arbitrage.py`      | Pick charge/discharge hours, daily net revenue |
| `src/cashflow.py`       | Capex, O&M, degradation -> annual cash flows |
| `src/valuation.py`      | NPV, IRR, payback |
| `src/breakeven.py`      | Closed-form break-even capex / revenue / stacking |
| `run_phase3.py`         | Orchestrate: summary, break-even, robustness, plots |

## Run

```bash
pip install -r requirements.txt
python3 run_phase3.py
```

## Data status

| Input | Current | How to make it real |
|---|---|---|
| `data/baseline_smp_hourly.csv` | Stylized, calibrated to KPX 2024 avg (~126) | `python3 -m src.data_prep your_panel.csv --smp-col smp --hour-col hour` |
| `data/elasticities.csv` | IV average + 2 anchors (13, 24) | Replace with your estimated hour-of-day coefficients |
| `src/assumptions.py` (costs) | Industry-plausible placeholders (`# TODO`) | Vendor quotes / project data |

## Context

Business extension of a working paper, *"Does Solar Generation Lower the Korean
SMP?"* (IV / 2SLS on a 2024 hourly regional panel, 16 regions). This repo is the
"academic result → business case" layer.
