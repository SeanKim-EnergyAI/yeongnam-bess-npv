# Yeongnam 100MW BESS — Arbitrage NPV

**Translating an econometric result into an investment decision.**
My working paper estimates the elasticity of Korea's System Marginal Price (SMP)
to solar generation. This project asks the business question that follows:
**is a 100MW / 4h battery in the Yeongnam region worth building on price
arbitrage alone?**

> ⚠️ Portfolio prototype. Financial inputs and the baseline price curve are
> stylized placeholders (see [Caveats](#caveats)); the *method* is the point.

## TL;DR result

| Metric | Value |
|---|---|
| System | 100 MW / 4 h (400 MWh) |
| Daily arbitrage spread | ~46 KRW/kWh (charge ≈100, discharge ≈146) |
| Daily net revenue | ~0.12억 KRW |
| Capex | ~1,600억 KRW |
| **NPV @ 7%** | **≈ −1,553억 KRW** |
| IRR | ≈ −39% |

**Energy arbitrage alone does not justify the capex** — a realistic, defensible
finding. The value of the project is quantifying *how far* it misses and *which
levers* (capex, price spread, stacked revenue) would close the gap.

![Hourly SMP and BESS dispatch](outputs/price_curve.png)

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
| `src/price_scenario.py` | Reshape baseline SMP via hourly elasticities |
| `src/arbitrage.py`      | Pick charge/discharge hours, daily net revenue |
| `src/cashflow.py`       | Capex, O&M, degradation -> annual cash flows |
| `src/valuation.py`      | NPV, IRR, payback |
| `run_phase3.py`         | Orchestrate, print summary, sensitivities, plots |

## Run

```bash
pip install -r requirements.txt
python3 run_phase3.py
```

Console prints a summary + two sensitivity tables; PNGs are written to `outputs/`.

## Caveats

- Financial inputs in `assumptions.py` are placeholders (`# TODO`).
- `data/baseline_smp_hourly.csv` is a stylized duck-curve, not 2024 KPX data.
- The hour-13 elasticity sign (`+0.0496`) contradicts the usual "solar lowers
  midday price" intuition and must be reconciled with the regression output.
- Energy-arbitrage-only economics ignore capacity / ancillary-service revenue,
  which real BESS projects stack on top.

## Context

Business extension of a working paper, *"Does Solar Generation Lower the Korean
SMP?"* (IV / 2SLS on a 2024 hourly regional panel). This repo is the "academic
result → business case" layer.
