# Case B — central contract market model (minimal version, implemented; results CONDITIONAL)

Code: `src/contract_case.py`, `run_contract_case.py`, `tests/test_contract.py`.
Sources and page references: `docs/market_rules.md` (KPX notice 제2026-05호, ATB 2024 printouts).

**Scope.** A hypothetical 50 MW / 300 MWh (송전단) ESS under the 2026 mainland
central-contract settlement formula. The only question it answers: *given the
stated cost, performance and delivery assumptions, what contract price
(KRW/kW-h) makes NPV = 0, and how sensitive is it to CAPEX and the performance
rate?*

**No award price is known.** Nothing here says whether a real project would win
a bid or be profitable.

## 1. Roles of A and B

| | A. SMP arbitrage baseline | B. Central contract market |
|---|---|---|
| Asset | 100 MW / 400 MWh **internal**, 4 h (research example) | 50 MW / 300 MWh **at 송전단**, 6 h (research example) |
| Revenue | SMP spread from self-scheduled LP dispatch on 2024 prices | Contract price × 공급가능용량 × 이행률, summed over 24 h per day |
| Charging energy | Bought at SMP | **Not settled** (notice p.22 / PDF 24) |
| Time basis | 2024 prices repeated for 15 years | Notice 2026; COD by Feb 2029; 15-year trading period |
| Output | NPV at assumed costs (−$136.2M) | Break-even contract price p* and its sensitivity |

**A's arbitrage profit is never added to B.** The notice excludes charging cost
from the bid price and does not settle charging cost or discharge revenue.

## 2. Corrections to the previous design (2026-09-27, before the notice was read)

| Previous design | Correction | Basis |
|---|---|---|
| Example facility 100 MW | **Not eligible.** Bids must be > 10 MW and < 100 MW in 1 MW steps. Now 50 MW / 300 MWh. | p.1 / PDF 3; p.22 / PDF 24 |
| "Charging-cost switch" and a cash flow that could include charging cost | **Removed.** Charging cost and discharge revenue are not settled. | p.22 / PDF 24 |
| Price unit left open | Unit is KRW/kW-h: per kW of 공급가능용량 per settled hour, not per kWh discharged | p.14 / PDF 16; p.22 / PDF 24; p.26 / PDF 28 |
| Oversizing vs augmentation as a free choice; "ATB O&M may include augmentation" | ATB O&M **does** include "Battery augmentation". The base case therefore holds capacity through O&M, with no separate degradation haircut or augmentation capex. The notice quotes KEC 512.1.2 as saying design capacity must not be added mid-operation "to extend 보증수명", but that sentence is not in the KEC 2025-052 text of 512.1.2, which states only the capacity and operation duties. Whether ATB-style augmentation (adding capacity to make up degradation) falls under that sentence remains **undecided** (§7a; `market_rules.md` §6b). | ATB O&M inclusions; p.23 / PDF 25 |
| Contract term "~15 yr, unverified" | 15-year trading period from COD; price fixed for the term with no inflation indexation | p.25 / PDF 27 |
| Sensitivity for r with thresholds "per notice" | The notice's 이행률 is a continuous formula, not thresholds. The score-based price adjustment is a separate mechanism. | p.26 / PDF 28 |

## 3. Facility, energy and capacity variables

| Variable | Value | Definition |
|---|---|---|
| `contract_power_kw` P | 50,000 kW | 송전단 최대 방전용량 (hypothetical) |
| `deliverable_energy_kwh` E_del | P × 6 h = 300,000 kWh | 송전단 최대 전력저장량; the contract quantity |
| `supply_capacity_kw` | E_del ÷ 6 = 50,000 kW | 공급가능용량, as in the notice formula |
| `internal_nameplate_kwh` (illustrative) | E_del / (√RTE · (1 − aux)) / SOC_window = 323,498 kWh at RTE 0.86, aux 0, window 1.0 | Internal battery energy needed to deliver E_del at the meter |

How the internal-capacity terms work:

- √RTE is the one-way battery→meter efficiency.
- Auxiliary load reduces the energy that reaches the 송전단.
- Only the SOC window of the nameplate energy is usable.
- All three raise the required internal nameplate energy.

**Cost basis.** Capex is ATB $/kWh × **E_del**, not × internal nameplate.
Efficiency and SOC margins are therefore not applied to cost a second time. The
ATB printouts do not say whether their $/kWh is per usable or per nameplate kWh
(unconfirmed). This choice treats ATB's "240 MWh" as analogous to deliverable
energy.

## 4. Cost source trace and finance basis

### 4.1 Cost source — traced to the ATB 2024 v3 workbook

Sources, read directly:

- (Source files are not in this repository; see [source_manifest.md](source_manifest.md).)
- `docs/sources/ATB_2024_v3_Workbook.xlsx` ("ATB 2024 v3" file; workbook metadata modified 2025-02-14; errata list in "Preface and Contents")
- `docs/sources/ATB_2024_battery_webtext.pdf`: a user-prepared **text export** of the ATB web page dated 2026-09-27. It is not a publisher PDF, and the page's charts and tables are not captured.
- The earlier dashboard printouts, whose tech-summary printout is stamped "data updated 02/26/2025 v4.109". That stamp belongs to the web dashboard and is kept separate from the workbook file.

Excel cells were read twice: once for formulas and once for cached values. The cached values match a direct recomputation of the formulas, so no stale value was found.

| Field | Value | Workbook location (sheet "Utility-Scale Battery Storage") / web text |
|---|---|---|
| Dollar-year | **2022$** | D10 "All values are given in 2022 U.S. dollars"; D67; web text "is in 2022$" |
| Base year | 2022 | G9 |
| Year columns | Projection years 2022–2050. Web text: "Three projections for 2022 to 2050"; the dashboard notes the year "represents the commercial online date". | header rows 18, 24, 69 |
| Representative plant | 60 MW, 240 MWh (4 h); web text: "240-megawatt hour [MWh] **usable**" | D12; web text Figure 1 caption |
| Scenario | 2022–2023 values are identical in Advanced / Moderate / Conservative; they diverge from 2024 | rows 19–21, 25–27 |
| Energy cost (2023) | 386.91932356 $/kWh | G20 (Moderate) |
| Power cost (2023) | 359.28270576 $/kW | G26 |
| **4-h OCC (2023)** | **1,906.96 $/kW = energy × 4 + power**, i.e. **476.74 $/kWh**. This is the source of the previous input (the dashboard showed 1,906.95). | H108 `=G20*4+G26` |
| **6-h OCC (2023)** | **2,680.79864712 $/kW = energy × 6 + power**, i.e. **446.7998 $/kWh** | H111 `=G20*6+G26` |
| 6-h OCC (2029, Moderate) | 1,867.549873504914 $/kW, i.e. 311.2583 $/kWh | N111 `=M20*6+M26` |
| ATB "CAPEX" definition | (OCC + GCC) × CFF. 6-h 2023 = 2,882.41 $/kW, 7.5% above OCC **for this row only** (6-h, 2023 column, this workbook's US $100/kW GCC and its CFF). The ratio differs by year and duration. **It is not an estimate of Korean connection or financing costs.** | H77 `=(H111+H162)*H$207`; H162; row 206 |
| Fixed O&M | 0.025 × OCC. 4-h 2023 = 47.674 $/kW-yr; 6-h 2023 = 67.020 $/kW-yr. Web text: it "include[s] battery augmentation costs, which enables the system to operate at its rated capacity throughout its 15-year lifetime". FOM is constant over years. | H125 `=0.025*H108`, H128 `=0.025*H111`; web text p.3 |
| Total vs battery pack | OCC is the total system cost: energy (battery-related) plus power (BOS) components. It is not the pack cost alone. | row 29 equation; web text p.2 |
| RTE | 0.85 | H176, H179; web text |

**What was wrong before.**

- The previous input applied the **4-hour** OCC per kWh to a 6-hour asset.
- Earlier docs said the input was "all-in capex including grid connection". That is incorrect: **OCC excludes GCC ($100/kW) and construction financing**, which ATB adds only in its CAPEX rows.
- The model keeps the OCC definition, which is what the previous result used, so as not to mix a definition change into the duration change. The ATB-CAPEX gap is recorded here and is **not applied**.
- **Naming.** The model's initial cost is therefore an **"OCC-based initial investment"**, not a total project cost (총사업비).

**Cost scope: what the source covers vs what this study uses.**

| Cost item | In ATB source? | In this study's initial investment / cash flow? |
|---|---|---|
| Battery energy + power (BOS) components, installation, EPC, owner's costs | Yes, in OCC | **Included** (OCC, US 2022$) |
| Grid connection (GCC) | ATB CAPEX adds a US $100/kW placeholder | **Excluded.** The Korean cost (KEPCO 접속설비, 무효전력 보상설비 etc.; notice p.1/PDF 3) is unknown. |
| Construction financing | ATB CAPEX applies its CFF | **Excluded** (capex placed at COD) |
| Fixed O&M incl. augmentation | Yes (0.025 × OCC) | **Included** |
| Charging energy | — | Excluded (not settled per notice) |
| Transaction fee (거래수수료) | — | Excluded (rate in the operation rules, not read) |
| Performance deposit, late-completion penalty, price adjustment | — | Excluded (refundable / assumed not triggered) |
| Income tax, debt costs, residual value, battery disposal | — | Excluded (scope) |


**Cost update (other inputs held constant: f = 1.00, 8,760 h, 7% nominal, FX 1,350, 15 years).** Source: `outputs/contract_cost_update.csv`.

| Case | ATB cell | $/kWh (2022$) | CAPEX (KRW bn) | Fixed O&M (KRW bn/yr) | p* (KRW/kW-h) ⚠ conditional |
|---|---|---|---|---|---|
| Prior (reproduction): 4-h OCC applied to 6-h asset | H108 / 4 | 476.74 | 193.080 | 4.827 | **59.4203** |
| **Cost update (new base): 6-h OCC, same 2023 column** | H111 / 6 | 446.80 | 180.954 | 4.524 | **55.6886** (−6.28%) |
| Separate scenario: 6-h OCC, 2029 Moderate | N111 / 6 | 311.26 | 126.060 | 3.151 | 38.7949 (−34.7%) |

- **How CAPEX and O&M were updated.** CAPEX = $/kWh × 300,000 kWh × 1,350. O&M is re-derived as 0.025 × the new OCC-based CAPEX, following the ATB formula. Re-deriving O&M from the new base cost is a different analysis from the ±25% total-fixed-O&M sensitivity in §7, which varies O&M around that base.
- **The 2029 row is a separate scenario.** Relative to the new base it changes only the cost year. It is not the base because the dollar-year and escalation questions in §4.2 are unresolved, and it should not be read together with the duration change.

### 4.2 Finance basis

| Element | Model setting | Nature |
|---|---|---|
| Valuation point | Year 0 = commercial operation date (COD). All PVs are at COD. | Modelling choice |
| Construction spend | All capex at year 0; no construction-period flows. ATB's own construction finance factor is not applied (OCC basis). | Simplification |
| Cost basis | ATB 2022$, 2023 projection column. No conversion from 2022$ to nominal KRW at a 2029 COD. | Simplification. Ignoring inflation from 2022 to 2029 understates nominal cost; ignoring ATB's projected decline (the 2029 row) overstates it. **The net direction is not determined.** |
| FX 1,350 KRW/USD | **Research assumption**, not an observed or sourced rate; applied once | Assumption |
| Contract revenue | Fixed in nominal KRW for 15 years, no indexation | **Confirmed** (notice p.25 / PDF 27) |
| Fixed O&M | 0.025 × OCC-based CAPEX; flat in nominal KRW (0% escalation) | ATB formula (**confirmed**); 0% escalation is an assumption |
| Discount rate 7% | Treated as nominal, not a verified Korean WACC. (The ATB workbook also lists a 7% nominal "interest rate" in its financial assumptions, rows 50–52. That is ATB's US debt-rate input and is **not** used as a source for this rate.) | Research assumption |
| Tax, debt, residual value, disposal | Excluded | Scope limit |

Case B remains an **educational scenario**: a US reference cost (2022$)
converted at an assumed FX. It is not a Korean project quote.

## 5. Settlement: notice → implementation — two separate calculation paths

Notice (p.26 / PDF 28), settled monthly:

```
daily settlement  = Σ_{t=1..24} price_i × supply_capacity_{i,t} × perf_rate_{i,t}
supply_capacity   = max_stored_energy_{i,t} / 6
perf_rate_{i,t}   = 1 − { (dev_chg/instr_chg)·α + (dev_dis/instr_dis)·(1−α) },
α = instr_chg / (instr_chg + instr_dis),  each ratio capped at 1,  dev = |instr − metered|
```

**Path 1 — hourly notice formula** (`hourly_performance_rate`, `daily_settlement_krw`).

- Implemented as written.
- For an hour with no dispatch instruction the notice gives 0/0, so the function **raises an error**. It does not guess.
- Tests check it against hand examples. **Passing those tests does not confirm the market rule**: it only shows the code matches the notice text for hours where that text is defined.

**Path 2 — annual simplification** (`build_contract_cashflows`, `breakeven_contract_price`).

- One **hypothetical effective payment factor f** applies in every one of 24 × 365 hours.
- supply_capacity is held at the contracted kW every hour.
- **Path 2 does not call Path 1.** So the break-even result (prior 59.42, new base 55.69) is computable even though Path 1 raises for no-instruction hours. The success of Path 2 is **not** a validation of the hourly settlement rule.

f is **not** the notice's 이행률. They coincide only if (a) every hour is settled and (b) the realised 이행률 averages to f with capacity at the contracted level. Neither (a) nor (b) is confirmed.

**The two formerly open definitions, after reading the operation rules (2026. 7.; `docs/market_rules.md` §5).**

| | (1) Rate in an hour with no dispatch instruction | (2) Hourly capacity term |
|---|---|---|
| Rule text (class A) | 별표2 Ⅰ.18 (ii): EFR = Max{1 − \|EGMO\| ÷ ECD, 0}; = 1 if idle within tolerance ε. Every hour is settled. | TECP uses EOSE_i,t / EMOT: the supplier's hourly **bid** 방전가능전력량 at the 송전단 (별표4 6.6.3), consistent with the approved maintenance plan |
| Code | `hourly_efr_rules` implements (i) and (ii). The notice-form `hourly_performance_rate` is unchanged and still raises for no instruction, because the notice does not define that case. | `hourly_settlement_rules_krw` implements TECP_i,t |
| Annual model | **Unchanged.** With EOSE_t = contracted 300 MWh and EFR_t = 1 in all 8,760 hours, the rules' payment equals the annual model at f = 1, so p* = 55.6886. f is now read as the hour-average of (EOSE_t / contract) × EFR_t. It remains hypothetical. | Unchanged. Capacity is held at the contract level (O&M includes augmentation). |
| Still open | Actual dispatch and idle patterns (data, not rules). Which text governs the signed contract: the notice's α form or the rules' net form (identical when an hour has one direction). | How a bid EOSE below the contracted amount is treated beyond proportional payment (C); fee **rate** (B, set separately by KPX) |

The annual path (`breakeven_contract_price`) still does not call either hourly
function. The hourly functions reproduce the rule text; they are not fed with
dispatch data.

**Do not double count.**

- A capacity shortfall lowers supply_capacity, which is definition (2).
- Non-compliance with instructions lowers 이행률, which is definition (1) or f.
- The model holds capacity constant and varies only f, so a capacity loss is never also counted as a lower f.

## 6. Break-even derivation — new base (6-h OCC, 2023) ⚠ conditional

All inputs are in `src/contract_case.py:get_contract_assumptions()`, with default
`cost_case="6h_2023"`. The full table with code locations is
`outputs/contract_breakdown.csv`.

| Item | Value | Derivation / status |
|---|---|---|
| Contract power | 50 MW = 50,000 kW | hypothetical |
| Deliverable energy (송전단) | 300 MWh = 300,000 kWh | P × 6 h |
| CAPEX unit cost | 446.7998 $/kWh (2022$) | ATB H111 / 6; OCC basis |
| OCC-based initial investment (not total project cost) | 180,953,908,680.6 KRW | 446.7998 × 1,350 × 300,000 |
| Annual fixed O&M (incl. augmentation) | 4,523,847,717 KRW/yr | 0.025 × CAPEX (ATB formula) |
| Σ DF_1..15 at 7% | 9.107914 | |
| Settled quantity | 438,000,000 kW-h/yr | 50,000 kW × 8,760 h × f (1.00); **annual simplification** |
| PV of costs | 222,156,724,659 KRW | 180.954 bn + 4.524 bn × 9.107914 |
| PV of settled quantity | 3,989,266,334 kW-h | 438,000,000 × 9.107914 |
| **p\*** | **55.6886 KRW/kW-h ⚠ conditional** | 222,156,724,659 ÷ 3,989,266,334 |
| Annual payment / net cash flow at p* | 24,391,614,209 / 19,867,766,492 KRW | |

**Prior result kept for reproduction.** With `get_contract_assumptions("legacy_4h_2023")`
(476.74 $/kWh), p* = 59.4203. The hand check
59.42 × 50,000 × 8,760 = 26,025,960,000 KRW differs from the model's
26,026,105,699 KRW only by the rounding of p* (145,699 KRW). A test covers this.

**Unit and double-counting checks** (unchanged; all pass):

- MW→kW and MWh→kWh are each converted once, and FX is applied once.
- "6" appears only in 공급가능용량 = 최대전력저장량 ÷ 6. Settled hours are 24 × 365.
- 공급가능용량 is the contracted kW, not the state of charge.
- Efficiency and SOC window enter only the illustrative internal capacity, never cost.
- OCC is the total system cost and is used once.
- Augmentation sits only in O&M.

## 7. Conditional sensitivities around the new base (hypothetical, one variable at a time)

Source: `outputs/contract_sensitivity_oneway.csv`. ⚠ All values are conditional.
The multipliers and factors are hypothetical, not forecasts or likelihoods.

| Varied | 0.75 or 1.00 | 1.00 or 0.95 | 1.25 or 0.90 |
|---|---|---|---|
| CAPEX multiplier (O&M held fixed; one-variable) | 0.75 → 44.35 (−20.4%) | 1.00 → 55.69 | 1.25 → 67.03 (+20.4%) |
| Hypothetical effective payment factor f | 1.00 → 55.69 | 0.95 → 58.62 (+5.3%) | 0.90 → 61.88 (+11.1%) |
| Total fixed O&M multiplier (augmentation included) | 0.75 → 53.11 (−4.6%) | 1.00 → 55.69 | 1.25 → 58.27 (+4.6%) |

- With costs fixed, p*(f) = p*(1)/f exactly. This is arithmetic in the annual simplification, not a reproduction of any penalty rule.
- CAPEX × f grid (O&M at base; `outputs/contract_breakeven_grid.csv`, `figures/contract_breakeven_sensitivity.png`):

| CAPEX \ f | 1.00 | 0.95 | 0.90 |
|---|---|---|---|
| 0.75 | 44.35 | 46.68 | 49.28 |
| 1.00 | 55.69 | 58.62 | 61.88 |
| 1.25 | 67.03 | 70.56 | 74.48 |

- Earlier versions reported CAPEX sensitivities around 59.42, first as a joint CAPEX+O&M scenario and then with O&M fixed. Those are superseded by the cost update. The percentage effects are unchanged because they do not depend on the cost level.

## 7a. KEC 512.1.2, the notice's 보증수명 sentence, and the cost assumption

Sources: KEC 2025-052 512.1.2 (printed p.523) and 부칙 (printed pp.1175–1177); notice p.22–23 / PDF 24–25 and p.26 / PDF 28. Details in `docs/market_rules.md` §6–§6b.

- KEC 512.1.2 ① requires rated discharge capacity over the warranty period; ② requires operation at or below it. It does not say how capacity is kept.
- The 2025-052 부칙 read: 제1조 "공고한 날부터 시행". No 경과조치 appears in the excerpt. Which edition governs a hypothetical project is **not determined**; earlier revisions tie it to permit application dates, and later revisions were not searched.
- The notice (p.23) quotes as KEC reference that design capacity must not be added mid-operation "보증수명의 연장목적으로", and (p.22) tells bidders to size quantities with KEC 512.1.2 in mind. This is not dismissed because the KEC body lacks it, and not read as a ban on all maintenance or replacement.

Four capacity practices (see `market_rules.md` §6b):

| Practice | Status from sources read |
|---|---|
| (a) initial design margin | consistent with the notice text; not modelled |
| (b) capacity added to make up degradation | not named in the notice or KEC; **ATB's augmentation is this** |
| (c) same-capacity battery replacement | not named in the notice; KEC 511.2.4 requires a replacement history |
| (d) capacity added to extend 보증수명 | the notice says "하지 않아야 함" |

What this means for case B:

- B's capacity-maintained assumption is **consistent with KEC 512.1.2 ①**.
- Its **contract conformity is unconfirmed**. Whether (b) counts as (d), and whether added capacity enters the yearly 보증수명 ratio (잔여용량 ÷ 최초 설계용량), are open.
- B is therefore a **financial scenario that assumes the cost of maintaining rated capacity**. p\* = 55.6886 is conditional on the cost and payment assumptions **and** on the unconfirmed contract conformity of the capacity-maintenance method. It is not the break-even of a biddable project.
- No switch to initial oversizing, and no assumed augmentation share removed from ATB O&M. No calculation changed.

## 8. What can and cannot be compared

**Comparable:**

- p* against an award price or the undisclosed cap price, *if one is published in KRW/kW-h for comparable terms*. Neither is available now.
- p* across the CAPEX × f grid, since everything else is held equal.

**Not comparable, or not to be read causally:**

- NPV(A) vs anything in B. A is 4 h / internal 400 MWh / 2024 prices / merchant. B is 6 h / 송전단 300 MWh / 2029+ / fixed payment. Size, duration, period, revenue mechanism and cost basis all differ, so the gap is not a policy effect.
- A's break-even "extra revenue" ($149.5/kW-yr ≈ 201,875 KRW/kW-yr, on top of arbitrage, 4 h asset) vs B's p* × 8,760 (487,832 KRW/kW-yr at the new base, no arbitrage, 6 h asset, ATB 2022$ OCC). The units can be matched, but the assets and cost bases differ.
- 4 h vs 6 h results. Most of the difference is duration-driven cost, not policy.
- A negative NPV in A. It is not evidence of a subsidy need, of social benefit, or of policy failure.
- KRW/kW-h contract prices vs KRW/kWh SMP.

## 9. Blocked items (need the named clause or data)

| Blocked variable | What is needed |
|---|---|
| 이행률 in hours with no dispatch instruction | **Resolved** (rules 별표2 Ⅰ.18 (ii), 2026.7.24. amendment); implemented in `hourly_efr_rules` |
| Hourly 최대전력저장량_{i,t}: declaration, testing, derating | Declaration **resolved** (bid EOSE, 별표4 6.6). Treatment of a bid below contract (degradation) and any capacity test: not found (C); contract needed |
| Augmentation vs initial oversizing | KEC 512.1.2 and the 2025-052 부칙 read (§7a). Still open: whether the notice's "보증수명의 연장목적으로 설계 용량을 추가하지 않아야 함" covers degradation make-up (b) or same-capacity replacement (c); how added capacity enters the yearly 보증수명 evaluation; which KEC edition governs the project; the contract's equipment-change terms (contract not obtained in the public search, `market_rules.md` §7). |
| Transaction fee | Base in the rules: discharge metered value (kWh), 별표8 7.8.1. A research memo reports a general KPX FAQ rate (거래량 × 0.1193원/kWh from 2025-09-01), not checked here and not confirmed for central-contract ESS. Not added to the model: its base is kWh, while the contract settles in kW-h, and the ESS chargeable quantity is unconfirmed. |
| A realistic effective payment factor f | Hourly dispatch-instruction and metering data from operating central-contract ESS (not public in this repo) |
| Korean capex and O&M | Korean project cost data or quotes; the ATB augmentation share of O&M (the workbook gives FOM only as 0.025 × OCC, with no split) |
| Cost definition and vintage | Whether to add a Korean connection and financing cost to OCC (the ATB US values are not Korean estimates), and how to move 2022$ to a 2029 nominal-KRW basis. These are author decisions. |
