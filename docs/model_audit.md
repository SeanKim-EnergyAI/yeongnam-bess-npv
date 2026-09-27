# Model audit — Korean SMP BESS arbitrage baseline (review round 1)

**Status:** first-round review. This is not a final verification: several items
are still open because the raw data is not in this repository (§4).
**Goal:** a reproducible, explainable arbitrage baseline. The audit does not aim
to change the investment conclusion or to make NPV positive.
**Conventions:** KRW-native. USD figures use a fixed reporting FX rate of
1,350 KRW/USD. "Arbitrage profit" always means discharge revenue minus
charging cost at SMP. It is measured **before** fixed O&M, degradation and capex.

Evidence tags: **[run]** = checked by executing code in this repo on 2026-09-27;
**[review]** = judged from reading code or data only, not executed.

## 0. Starting state

| Item | Value |
|---|---|
| Branch | `claude/bess-policy-lens-v09-nvpnt3`. No `v0.9-policy-lens` branch exists locally or on the remote. |
| Audited commit | `bb253a4`. The working tree was clean at the start of the audit. |
| Pre-audit outputs | archived outside the repo. `run_baseline.py` and `run_audit.py` recompute the legacy numbers from code. **[run]**: −$142.46M and −$134.18M, matching the archived logs. |
| Environment | Python 3.11.15, pandas 3.0.6, numpy 2.4.6, PuLP 3.3.2 (bundled CBC), numpy-financial 1.0.0, matplotlib 3.11.2, pytest 9.1.1 |

Line references are to `bb253a4` unless marked *(now)*.

## 1. Test and script results **[run]**

| Command | Result |
|---|---|
| `python3 -m pytest tests/test_model.py -v` | **14 collected, 14 passed, 0 failed, 0 skipped.** The only warnings are PuLP's deprecation notice for `PULP_CBC_CMD`. |
| `python3 run_baseline.py` | exit 0 |
| `python3 run_audit.py` | exit 0 |
| `python3 run_analytics.py` | exit 0 |
| `python3 run_phase4.py` | exit 0 |
| `python3 run_phase3.py` | exit 0 |
| `python3 -m pytest tests/ -v` (A + B) | **30 passed** (A 14, B 16), 0 failed, 0 skipped |
| `python3 run_contract_case.py` | exit 0 (case B; see `docs/contract_model_design.md`) |
| `./run_all.sh` | exit 0 (runs all of the above in order) |

Tests in `tests/test_model.py`:

- **Hand calculation.** 50 → 100 KRW/kWh, 10 MW / 10 MWh, RTE 0.81. Expected profit 310,000 KRW; the LP matches.
- **Constant price.** No trade.
- **Spread below losses** (10% spread vs 14% losses). No trade.
- **Real day (2024-01-15).** No power, SOC, end-SOC, simultaneous-flow or cap violation.
- **Two-peak day.** Internal throughput is capped at exactly 400 MWh.
- **Solver failure.** An infeasible LP raises an error.
- **Legacy heuristic.** It needs a 116 MW charge rate and books a forced loss at a flat price.
- **Break-even re-substitution** at 3 revenue levels.
- **Cash-flow units.**
- **Log-log elasticity arithmetic.**
- **Real-series coverage.**
- **Removal of partial/duplicate days.**

## 2. Calculation path **[review]**, confirmed by **[run]**

```
data/smp_2024_hourly.csv ─ src/data_checks (validate; keep complete days, no filling)
  ─ src/daily_arbitrage.daily_lp_series ─ src/optimize_dispatch (LP per day)
  ─ mean daily profit × operating_days_per_year ─ src/cashflow ─ src/valuation (NPV)
  ─ src/breakeven (closed form; re-substituted in run_baseline / tests)
Exploratory only: data/baseline_smp_hourly.csv (hour-of-day mean) × src/price_scenario → run_phase3
```

| Script | Role | Engine |
|---|---|---|
| `run_baseline.py` | Headline: data checks, per-day LP, NPV, break-even check, before/after table | LP per day |
| `run_audit.py` | Cap-definition, engine-comparison and NPV-bridge tables | LP, heuristic |
| `run_analytics.py` | Daily distribution figure, NPV = 0 frontier figure | LP per day |
| `run_phase4.py` / `run_phase3.py` | Representative day; exploratory solar scenarios | LP (+ heuristic for comparison) |
| `scripts/build_inputs_from_panel.py` | Rebuilds `data/*.csv` from the research panel. **Not run: the panel is not in the repo.** | — |

`src/arbitrage.py` (the heuristic) is no longer on the baseline path. It is kept
only to reproduce the legacy numbers.

## 3. Items verified and fixed

### 3.1 Data coverage **[run]**

| Check | Result |
|---|---|
| Rows | 8,760 |
| Dates present | 366 (2024-01-01 … 2024-12-31); no calendar date is absent |
| Expected hours for 2024 (leap year) | 8,784, so **24 hours are missing** |
| Dates with 24 hours | 364 |
| 2024-01-01 | hours 1–23 only; **hour 24 missing** |
| 2024-12-31 | **hour 24 only**; hours 1–23 missing |
| Duplicate (date, hour) rows | 0 |
| Hour values | exactly 1…24 |
| Null / negative prices | 0 / 0 |
| Zero prices | 6 hours: 2024-02-10 h12; 02-11 h13; 02-12 h13; 11-03 h13; 11-23 h13; 11-24 h13 |

**Where the two incomplete dates come from.** `build_inputs_from_panel.py`
performs no timestamp conversion **[review]**. It copies `date` and `hour` from
the panel and keeps one row per (date, hour). The (date, hour) values were
therefore created upstream, in the research project, which is not in this repo.
One candidate mechanism explains the pattern exactly:

- Build 8,760 hourly timestamps starting 2024-01-01 01:00, a count that assumes a 365-day year.
- Then map timestamp hour 0 to "hour 24" of the **same** calendar date.
- The series would end at 2024-12-31 00:00, which becomes "(12-31, 24)".
- 2024-01-01 would get no hour 24.
- Every "(D, 24)" row would actually be 00:00 of D, i.e. hour 24 of D−1.

That hypothesis predicts that "(D, 24)" behaves like a neighbour of (D−1, 23)
and (D, 1). The data says otherwise **[run]**:

| Pair | Adjacent under… | P(identical SMP) | median \|ΔSMP\| KRW/kWh |
|---|---|---|---|
| (D,h)–(D,h+1), h = 1…21 (control) | both readings | 15.5% | 2.38 |
| (D,22)–(D,23) (control) | both readings | 16.2% | 1.44 |
| **(D,23)–(D,24)** | labels as given | **14.8%** | **1.92** |
| (D−1,23)–(D,24) | shift hypothesis | 0.8% | 4.39 |
| (D,24)–(D,1) | shift hypothesis | 1.6% | 7.81 |
| (D,23)–(D+1,1) | shift hypothesis only | 0.0% | 10.60 |

**Conclusion.**

- The adjacency test is **supporting evidence only**. It does not establish the timestamp definition.
- In this file, hour 24 of each date behaves like the hour right after hour 23 of the same date. That is consistent with the labels as given, and less consistent with the one specific "hour 0 relabelled onto the same date" mechanism above.
- **The cause of the missing hours is unresolved.** They could be missing in the original KPX download, or dropped or mis-converted during panel construction. The hour convention (hour-ending KST) is an assumption.
- Resolving it needs the raw export and the panel-building code (§5, U1).

Nothing was filled, shifted or re-dated.

**Fix [run].** `src/data_checks.py` reports coverage and keeps only complete dates.

- The baseline uses the **364 complete dates 2024-01-02 … 2024-12-30**.
- This is **not** a complete 2024 calendar year, and results are never described as full-year 2024 performance.
- The actual profit sum over these 364 days and the annualised value (daily mean × 350) are reported separately (§3.4).

**Regional de-duplication [review].** `build_inputs_from_panel.py:32,65` dropped
duplicates without comparing values. A guard `assert_same_within_date_hour` now
raises if `smp` or `solar_total` differ across regions for any (date, hour).
**It has not been executed**, because the panel is not available (§4).

### 3.2 Dispatch engine **[run]**

**Before.**

- The full-year script and the published headline used the heuristic (`arbitrage.py:16-18`, `daily_arbitrage.py:21`): the 4 cheapest hours in, the 4 dearest hours out.
- It ignores hour order. It needs 400/0.86 = 465 MWh drawn in 4 h, i.e. 116 MW against a 100 MW limit.
- It stores 431 MWh against a 400 MWh SOC bound.
- It always trades: 10 loss days in 2024.

**Now.**

- The same LP as the representative day is solved once per complete day.
- Solver status is checked: anything other than `Optimal` raises an error (`optimize_dispatch.py:47,57` previously ignored it).
- Every schedule is re-checked independently by `check_dispatch`: power, SOC range, SOC balance, end SOC and simultaneous flow.
- Across 364 days, the worst violations are 1e-12 MW (power) and 4.5e-7 MWh (SOC). Maximum simultaneous charge + discharge is **0 MW**.
- 7 days have no trade; there are no loss days.
- Simultaneous flows are never profitable with prices ≥ 0 and η < 1. They would pay only at negative prices, which do not occur in this data. A binary charge/discharge mode would be needed if they did.

### 3.3 Cycle / throughput limit — a **definition change**, not a bug fix

Symbols: d[h], c[h] = metered (grid-side) discharge and charge in MWh per hour;
η = √0.86 = 0.9274 per leg; E = 400 MWh.

SOC balance, unchanged: `soc[h] = soc[h−1] + η·c[h] − d[h]/η`, with
`0 ≤ soc ≤ E` and soc = 0 at the start and end of each day.

| | Constraint (per day) | What "1 cycle" means |
|---|---|---|
| Before (`bb253a4`) | Σ_h d[h] ≤ E · cycles_per_day | 400 MWh **delivered** at the meter |
| After (default) | Σ_h d[h] / η ≤ E · cycles_per_day | 400 MWh **withdrawn from internal SOC**, i.e. one full swing of the SOC range |

What the 400 MWh means:

- **E = 400 MWh is internal usable storage**, the SOC upper bound. It is not AC deliverable energy.
- One full SOC swing draws 400/η = 431.3 MWh and delivers 400·η = 370.9 MWh at the meter.
- Efficiency applies on both legs: η on charge (grid → SOC) and 1/η on discharge (SOC → grid).
- Auxiliary load and transformer losses are not modelled separately.

Why this is a choice, not a bug fix:

- Both definitions appear in practice: delivered-energy throughput and internal/nameplate full cycles.
- Under the old definition the cap never binds on a single full cycle (370.9 < 400 MWh). It allows up to 1.078 internal cycles per day.
- The audit chose the internal-energy definition so that "1 cycle" matches the SOC bound. The old definition remains available as `cap_basis="delivered"`.

Effect, same LP and the same 364 days (`outputs/audit_cycle_cap.csv`) **[run]**:

| cap_basis | Profit sum (364 d) | Daily mean | No-trade days | Max internal out / day | Max delivered / day | NPV |
|---|---|---|---|---|---|---|
| delivered (before) | $3.6496M | $10,026.3 | 7 | 431.33 MWh (1.078 cycles) | 400.00 MWh | −$136.07M |
| internal (after) | $3.6337M | $9,982.7 | 7 | 400.00 MWh (1.000 cycles) | 370.94 MWh | −$136.20M |
| Difference | | **−0.435%** | | 60 of 364 days differ | | −$0.13M |

### 3.4 Engine comparison on identical data and assumptions **[run]**

All rows use the same 364 complete days, the same prices, the internal-energy cap
(where applicable), annualisation = daily mean × 350, fixed O&M = 2% of capex,
2%/yr revenue fade, 15 years, 7% (`outputs/audit_engine_comparison.csv`).

| Case | Days | Profit sum (period) | Daily mean | vs daily-reset LP | No-trade days | Annualised yr-1 profit | Yr-1 fixed O&M | Yr-1 net | NPV |
|---|---|---|---|---|---|---|---|---|---|
| Legacy heuristic (infeasible) | 364 | $3.911M | $10,745 | +7.64% | 0 (10 loss days) | $3.761M | $2.785M | $0.976M | −$134.03M |
| **Daily-reset LP (baseline)** | 364 | **$3.634M** | **$9,983** | 0 | 7 | **$3.494M** | $2.785M | $0.709M | **−$136.20M** |
| Continuous-SOC LP, per-day cap (diagnostic) | 364 | $3.658M | $10,048 | **+0.65%** | n/a | $3.517M | $2.785M | $0.732M | −$136.01M |
| Continuous-SOC LP, pooled cap (diagnostic) | 364 | $3.747M | $10,295 | +3.13% | n/a | $3.603M | $2.785M | $0.818M | −$135.31M |

Settings for the continuous-SOC runs:

- One LP over 8,736 consecutive hours (2024-01-02 h1 … 2024-12-30 h24; the dates are verified contiguous).
- SOC = 0 before the first hour and at the last hour only.
- Same power, SOC bounds and η as the baseline.
- Cap per consecutive 24-hour block ("per-day"), or 364 × 400 MWh summed over the period ("pooled").

**Correction to my previous report.** I reported continuous SOC as "+3.1%". That
figure is the **pooled-cap** run, which relaxes two things at once. Removing the
midnight reset alone, with the per-day cap kept, is worth **+0.65%**.

### 3.5 NPV bridge — one change per step **[run]** (`outputs/audit_npv_bridge.csv`)

Every step uses the same finance assumptions (×350 days, O&M, fade, 7%).

| Step | Type of change | Daily mean | NPV | ΔNPV |
|---|---|---|---|---|
| 0 Legacy headline: heuristic, hour-of-day mean day, +30% solar | — | $7,784 | −$142.46M | |
| 1 Remove the +30% solar scenario | scenario scope | $7,468 | −$143.36M | −0.90 |
| 2 Average day → each observed date (366 dates, incl. 2 partial) | method: averaging | $10,691 | −$134.18M | +9.18 |
| 3 Drop the 2 incomplete dates (364 days) | data range | $10,745 | −$134.03M | +0.15 |
| 4 Heuristic → LP, legacy delivered-energy cap | dispatch method (feasibility) | $10,026 | −$136.07M | −2.04 |
| 5 Internal-energy cap (baseline) | definition choice | $9,983 | −$136.20M | −0.13 |

Step 2 is large because optimizing on averaged prices can only lower the optimum.
It is a property of averaging, not a new empirical finding.

### 3.6 Other verified items

- **Units [run].** KRW/kWh × 1,000 = KRW/MWh; × MWh = KRW. Capex: 470,000 KRW/kWh × 400,000 kWh = 188.0 bn KRW. The unit test checks this.
- **Break-even re-substitution [run].** Each closed-form lever plugged back into the cash-flow model gives |NPV| < 1 KRW:
  - capex 81,165 KRW/kWh (≈ $60.1/kWh)
  - revenue multiplier 5.79×
  - constant extra revenue 201,875 KRW/kW-yr (≈ $149.5/kW-yr)

  Results are in `outputs/breakeven_check.csv`.
- **Elasticity comment [run + review].** `assumptions.py:39` said a coefficient of −0.0058 means "+1% solar → −0.58% SMP". For a log-log coefficient, +1% solar gives exp(−0.0058 · ln 1.01) − 1 = −0.0058%. `price_scenario.py` already computed the log-log form, so **NPV was never affected**. Only the comment was fixed; the coefficients are unchanged.
- **Solar scenario scope.** The baseline now uses observed prices (`solar_growth_pct = 0`). The +30% case is `exploratory_solar_growth_pct` and is labeled exploratory everywhere. The "×2.3" row is relabeled "national HTE rescaled", because it is not a Yeongnam effect or a regional price.

## 4. Assumption choices (made or kept, not verified)

| Item | Choice | Alternative |
|---|---|---|
| Cycle definition | 1 internal SOC swing per day (§3.3) | delivered-energy cap (`cap_basis="delivered"`) |
| SOC boundary | empty at every midnight | continuous (+0.65% with the same cap) |
| Foresight | perfect foresight within the day | forecast-based dispatch (not modelled) |
| Annualisation | daily mean × 350 operating days (assumes outage days are average days) | analysis-period sum ($3.634M over 364 days) |
| Incomplete dates | excluded | never filled |
| Zero-price hours | kept as observed | — |
| Degradation | 2%/yr revenue haircut; LP not re-solved; not linked to cycling | cycle-based fade and/or augmentation |
| Future prices | 2024 prices repeated for 15 years (a what-if, not a forecast) | price scenarios |
| Discount rate | 7%, real vs nominal unstated; prices and O&M flat in 2024 KRW. Consistency between the rate basis and the price basis is not checked (open) | a real rate with constant-KRW flows, or a nominal rate with escalated flows |

## 5. Unresolved — raw data needed

| ID | Issue | File and columns needed |
|---|---|---|
| U1 | Cause of the 24 missing hours; hour convention and time zone; whether the 6 zero-SMP hours are real | Original KPX/EPSIS hourly **mainland (육지) SMP** export for 2023-12-31 … 2025-01-01, as downloaded: date column, hour column (1–24 or 0–23, exactly as published), SMP value, unit label, and the file's region field. Plus the panel-building code that converted it. |
| U2 | Whether `smp` and `solar_total` are identical across regions | `panel_v4_main.csv` with columns `date`, `hour`, `region`, `smp`, `solar_total` (run `build_inputs_from_panel.py`) |
| U3 | Regression behind `elasticities.csv`, −0.0058 and −0.0135 | `v4_phase2_hte.csv` plus the estimation script and output: dependent and endogenous variables with units, instrument, controls/fixed effects, sample, standard errors, first stage |
| U4 | Capex source | exact table, year, scenario and value in NREL ATB 2024 / Lazard LCOS v9 (see `docs/market_rules.md` §ATB) |

## 6. Remaining limitations that affect results

- Perfect foresight overstates achievable arbitrage revenue. The LP result is an upper bound on arbitrage profit only for the same prices and operating constraints, not on a real project's total revenue. No forecast-error model exists.
- The midnight SOC reset understates revenue slightly (+0.65% with the same cap).
- Degradation is not linked to cycling. There is no augmentation, replacement, residual value or tax. O&M is flat while revenue fades, so net cash flow turns negative in years 13–15 and the model has no retirement option.
- The model is SMP arbitrage only, as a price-taker. No contract, capacity or ancillary revenue is modelled, and none should be added to this case (see `docs/market_rules.md`).
- 2024 prices (one year, 364 days) are applied to a 15-year life.
- Solar-scenario results rest on an unverified regression, so they are exploratory only.
- The pre-audit executive summary (−$142.5M, $47/kWh, $156/kW-yr, "366 days", "43%", "−0.58%/−1.35%") is archived unchanged at [archive/EXECUTIVE_SUMMARY_bb253a4.md](archive/EXECUTIVE_SUMMARY_bb253a4.md), with a table of which claims are superseded.

## 7. Reproduce

```bash
pip install -r requirements.txt
python3 -m pytest tests/ -v                # 30 tests (A 14, B 16)
python3 run_baseline.py                     # headline + data_validation, baseline_*, before_after, breakeven_check CSVs
python3 run_audit.py                        # audit_cycle_cap, audit_engine_comparison, audit_npv_bridge CSVs
python3 run_contract_case.py                # case B: contract_*.csv + figures/contract_breakeven_sensitivity.png
./run_all.sh                                # everything, in order
```

Output CSVs are in `outputs/`. They are deterministic given the committed `data/`
files and the PuLP/CBC version above.
