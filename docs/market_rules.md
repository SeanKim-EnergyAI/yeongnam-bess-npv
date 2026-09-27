# Market rules — 2026 mainland ESS central contract market (case B sources)

All facts below were read directly from source files supplied by the author
(upload or Google Drive) and read on 2026-09-27. **The source files are not in
this repository.** The paths `docs/sources/…` below name where the files go when
downloaded; see [source_manifest.md](source_manifest.md) for download locations,
versions, page mappings and SHA-256.

Two kinds of access are kept apart:

- **Direct URL access failed.** kpx.or.kr, epsis.kpx.or.kr, atb.nlr.gov,
  data.openei.org and law.go.kr were blocked from this environment.
- **Supplied files were read.** The notice, the operation rules, the KEC
  excerpts, the ATB workbook, the ATB web-text export and the ATB printouts were
  read in full or at the pages listed in §0.

Anything not in those files is marked **unconfirmed**. "Not obtained" means the
file was not found or not reachable here; it is **not** a finding that the
document does not exist. Page references use the
form **p.N / PDF M**: N is the printed page number and M is the PDF page index.
No secondary sources are cited as fact. Summaries passed on from other AI tools or news were used only as leads to check, never as sources.

## 0. What was actually read

"Read directly" below means the file itself was opened and read in this
project. Anything else is unconfirmed. ATB **dashboard printouts** (single-page
chart and table exports) are kept separate from the ATB **web page text export**
and the ATB **Excel workbook**. All three were read by 2026-09-27; they are not mixed.

| File | Type | Pages read | Confirmed directly | Not confirmed from this file |
|---|---|---|---|---|
| `kpx_notice_2026-05_ess_central_contract_mainland.pdf` | KPX official notice (PDF, 34 pp.) | All 34 PDF pages. Formula pages 24, 28, 29 were also rendered as images to read the symbols. | Bid range, 송전단 6 h definition, KRW/kW-h unit, charging/discharge not settled, daily settlement and 이행률 formula, 15-yr term, fixed price, performance requirements, price adjustment, late-completion table, deposit, eligible substations, evaluation, KEC 512.1.2 quotation (§2) | 이행률 for hours with no dispatch instruction and how hourly 최대전력저장량 is set: **not defined in this document**, later found in the operation rules (§5). Fee rate. |
| `atb2024_battery_cost_components.pdf` | ATB dashboard printout (1 p.) | 1 | "Base 60MW 240MWh", column "2023": $1,906.95/kW, $476.74/kWh; cost-component legend | Dollar-year, scenario, projection year, usable/nameplate basis, 6-hour value, workbook cell |
| `atb2024_battery_capex_inclusions.pdf` | ATB dashboard printout (1 p.) | 1 | Items included in CAPEX (grid connection, land, battery-specific items) | Values per item |
| `atb2024_battery_om_inclusions.pdf` | ATB dashboard printout (1 p.) | 1 | "Battery augmentation" listed under fixed O&M costs (battery-specific) | Share of O&M that is augmentation |
| `atb2024_battery_tech_summary.pdf` | ATB dashboard printout (1 p.) | 1 | "data updated: 02/26/2025 v4.109"; CAPEX, fixed O&M and OCC trends by scenario; "the year represents the commercial online date" | Numeric values (chart only). Now superseded by the workbook. |
| `ATB_2024_v3_Workbook.xlsx` | ATB official workbook (file "2024 v3"; metadata modified 2025-02-14) | Sheet "Utility-Scale Battery Storage" rows 1–207 (formulas and cached values); "Preface and Contents" | 2022$ (D10, D67); base year 2022 (G9); energy/power costs (rows 19–27); OCC by duration and year (rows 104–118, e.g. H108 4-h, H111 6-h); ATB CAPEX = (OCC + GCC) × CFF (rows 70–84); GCC $100/kW (rows 155–164); FOM = 0.025 × OCC (rows 121–135); RTE 0.85 (rows 172–186) | Share of FOM that is augmentation; any Korean cost |
| `ATB_2024_battery_webtext.pdf` | User-prepared text export of the ATB web page (3 pp.), **not a publisher PDF**; charts and tables not captured | 3 | "240 MWh usable"; "in 2022$"; power/energy cost equation; FOM 2.5% of $/kW capital cost, includes augmentation, rated capacity over the 15-year life; RTE 85%; about one cycle per day; scenario definitions | Tables and figures on the page |
| `KPX_rules_20260725.pdf` (full file via Google Drive; 1,326 PDF pp.; cover "전력시장운영규칙 2026. 7."; PDF metadata created 2026-07-24; SHA-256 624c4f94…). Cited pages are kept in `docs/sources/KPX_rules_20260725_excerpt.pdf` (36 pp.). | KPX market operation rules (official, HWP→PDF) | 제15장 in full (PDF 264–276), 별표1 variable definitions, 별표2 Ⅰ.18, 별표4 6.6, 별표8 5.16/7.1.15/7.8.1, 별표9 5.14/7.4, 별표13 8.1.1.5, plus full-text keyword search of all pages | See §5 | See §5 |
| `KEC_official_attachment.pdf` (Google Drive, 23.2 MB) + user excerpt `KEC_2025-052_pp520-526_excerpt.pdf` (7 pp., printed 520–526) | KEC 한국전기설비규정 | Excerpt read in full (§6). From the full file, only a partial text extract was obtainable: the Drive tool refuses binary downloads above 10 MB, and its text export stops around printed p.50 (chapter 1). Read: cover and table of contents. | Cover: "기후에너지환경부 공고 제2025-052호", dated 2025-10-01, 10th revision; TOC: "512 이차전지 용량 및 종류에 따른 시설 … 523", "512.1 리튬계·나트륨계 이차전지의 시설 … 523" | Which parts 2025-052 amended (see §6) |
| `KEC_2025-052_cover_and_addenda_excerpt.pdf` (4 pp.; user excerpt, text not edited; per the user = PDF pp.1, 1205, 1206, 1207 of `KEC_official_attachment.pdf`; printed 부칙 pp.1175–1177; SHA-256 9d72b676…) | KEC 한국전기설비규정 cover + 부칙 | All 4 pages | Revision history on the cover (제정 2018-103 … 제10차 2025-052); 801 재검토기한; every 부칙 from 2018-103 to 2025-052 (§6a) | Whether the 2025-052 부칙 continues after printed p.1177 (excerpt ends there); which provisions 2025-052 amended |
| `docs/research_notes/2026-09-27_public_search_memo.md` | **Research memo by the author's investigator, not an official document** | All | Nothing official by itself. Used as leads (§7) | Everything it points to by URL only (kpx.or.kr is blocked here) |

Summaries from other AI tools were treated as leads only. Correction notices, briefing materials and the standard contract terms were **not obtained** in this project. This does not mean they do not exist (see §7 for what the research memo reports).

## 1. Sources

| Short name | File | Issuer / title | Issue date | Effective / version | Checked | Notes |
|---|---|---|---|---|---|---|
| **KPX notice** | `kpx_notice_2026-05_ess_central_contract_mainland.pdf` (34 PDF pages) | 한국전력거래소 공고 제2026-05호, "2026년 ESS 중앙계약시장(육지) 경쟁입찰 공고" | 2026-09-22 (PDF 1). Posted 2026-09-22 17:00 (p.2 / PDF 4). PDF metadata created 2026-09-22 16:49 KST. | Issued under 전력시장운영규칙 제15장 (PDF 1). No version number beyond the notice number. | 2026-09-27 | Official source URL: kpx.or.kr board 0042, list_no=78164, seq=1 |
| **ATB O&M inclusions** | `atb2024_battery_om_inclusions.pdf` (1 page) | NREL ATB, "Inclusions in O&M", Utility-Scale Battery Storage | not printed | ATB 2024 web page (per the user); printout generated 2026-09-27 | 2026-09-27 | Orange = battery-specific item; blue = all technologies (legend on the page) |
| **ATB CAPEX inclusions** | `atb2024_battery_capex_inclusions.pdf` (1 page) | NREL ATB, "Inclusions in CAPEX" | not printed | as above | 2026-09-27 | |
| **ATB cost components** | `atb2024_battery_cost_components.pdf` (1 page) | NREL ATB, capital costs by category | not printed | as above | 2026-09-27 | |
| **ATB tech summary** | `atb2024_battery_tech_summary.pdf` (1 page) | NREL ATB, Utility-Scale Battery Storage parameter projections | "data updated: 02/26/2025 v4.109" | Financials = R&D, cost recovery period 30 years, "No Credits" | 2026-09-27 | Chart only; no numeric labels on the data points |

**Direct links that could not be opened here (files later supplied and read).**
These two links were named on 2026-09-27. The hosts were blocked, so the links
were not retried. The documents themselves were then **supplied as files and
read**: the full operation rules (2026. 7.) via Google Drive (§0, §5), and the ATB
page as a text export plus the ATB 2024 v3 workbook (§0, §3). The table records
what was searched for.

| Source | Link given (not opened here) | What was needed | Sections / search terms |
|---|---|---|---|
| 전력시장운영규칙 (rules version in force for the 2026 notice) | kpx.or.kr board bid=0030, list_no=77795 | The attached rules PDF/HWP (full text, or at least 제15장 and the related 별표) | 제15장 "저탄소 전원 중앙계약시장"; 15.1.1 (중앙계약공급자); 15.2.3 (입찰자 등록); 15.2.5 (유효경쟁); 15.2.7 (계약 취소·해지); the settlement clause for "중앙계약전기저장장치"; search terms "이행률", "급전지시량", "공급가능용량", "최대전력저장량", "정산금", "거래수수료"; 별표13 (중앙급전전기저장장치 기준); 별표3 |
| NREL ATB 2024, Utility-Scale Battery Storage | atb.nlr.gov/electricity/2024/utility-scale_battery_storage | The page itself (print to PDF), or the ATB 2024 data CSV | "Base Year", "dollar year"; "round-trip efficiency"; "augmentation"; "usable" or "energy capacity"; "Fixed O&M" definition; the 6-hour CAPEX values |

Other unconfirmed sources:

- Any 정정공고 (correction notice) issued after 2026-09-22. Not obtained. The research memo's limited search found none within its stated scope (§7); this is not a finding that none exists.
- The briefing notice list_no=78169. The briefing itself is scheduled for 2026-09-30, a future event as of 2026-09-27 (§7). No slides or Q&A exist yet to read.
- The standard contract terms (표준계약조건 / 계약서) for this notice. Not obtained in the public search (§7); not a finding that they are unpublished.
- KEPCO 송배전용 전기설비 이용규정. (KEC 512.1.2 and the KEC 부칙 have since been read, §6.)
- EPSIS: source, units and hour definition of the case-A SMP data.

## 2. Confirmed facts and how the model uses them

| Item | Confirmed fact (paraphrase; key terms quoted) | Document · page · section | Difference from earlier design/model | How case B reflects it | Unconfirmed |
|---|---|---|---|---|---|
| **Bid size** | Bids are "10MW(60MWh) 초과 100MW(600MWh) 미만", in 1 MW (6 MWh) increments. Total auctioned: 1,100 MW / 6,600 MWh. | KPX notice p.1 / PDF 3 (Ⅰ.1 비고); p.22 / PDF 24 (Ⅳ.1 note); p.13 / PDF 15 (quantity adjustment uses the same unit) | The earlier design proposed **100 MW**, which is **outside** the range: the upper bound is exclusive. | Hypothetical **50 MW / 300 MWh**. The code rejects sizes outside (10, 100) MW or off 1 MW steps. | — |
| **6-hour, transmission-side (송전단) definition** | Quantities are "송전단기준 최대방전용량(MW) 및 최대전력저장량(MWh)". 최대 방전용량 = the 송전단 maximum discharge power that can be held "거래기간 동안 안정적인 운전 상태를 유지하면서". 최대 전력저장량 = the 송전단 energy that can be discharged for **6 hours** at 최대 방전용량 "거래기간 동안". 공급가능용량 = 최대방전용량 (kW) that must be deliverable "6시간 동안 연속으로". Maximum charging time is ≤ 7.5 h (lithium) at 최대 전력저장량. | p.1 / PDF 3; p.14 / PDF 16 (Ⅲ.5); p.22 / PDF 24 (Ⅳ.1); p.26 / PDF 28 (settlement notes) | Case A's 400 MWh is **internal** storage and 4 h. | The 송전단 deliverable energy (300,000 kWh) is the contract quantity. Internal battery energy is a separate, illustrative variable (§3). | How "거래기간 동안" is tested and enforced year by year (operation rules) |
| **Charging cost / discharge revenue** | The bid price is a unit fixed cost "총 사업비(투자비, 운영비 등)… 공급가능용량으로 환산"; "단, 총사업비 산정시 충전비용 제외 → 정산시 충전비용 및 방전수익은 미정산되어 대금결제 미발생". Operating cost "설비 운영 및 조정, 유지보수에 관련하여 발생하는 모든 비용을 포함". | p.22 / PDF 24 (Ⅳ.3 입찰가격) | The earlier design had a "charging-cost switch" and a formula that could include charging cost. **Removed**: charging cost and discharge revenue are not settled. | No charging-cost and no SMP-revenue terms. **Case A's arbitrage profit is never added.** | Treatment of auxiliary (소내) power purchases; 거래수수료 applicable rate (base confirmed in the rules, §5) |
| **Settlement formula** | Monthly settlement. Daily settlement = **Σ_{t=1}^{24} (계약가격_i × 공급가능용량_{i,t} × 이행률_{i,t})**. 공급가능용량 = 최대전력저장량_{i,t} ÷ 6. 이행률_{i,t} = 1 − {(미이행량(충전)/급전지시량(충전))·α + (미이행량(방전)/급전지시량(방전))·(1−α)}, with α = 급전지시량(충전) / (급전지시량(충전) + 급전지시량(방전)). Each ratio is capped at 1. 미이행량 = \|급전지시량 − 계량값\|. A transaction fee is charged per the operation rules. | p.26 / PDF 28 (Ⅴ.1 정산 및 결제) | The earlier design left the unit and quantity open. | Implemented as written for one hour (`hourly_performance_rate`) and one day (`daily_settlement_krw`). The annual model uses a constant r (§4). | Not defined in the notice but **found in the operation rules** (§5): 이행률 for an hour with no dispatch instruction (EFR case ii) and the hourly EOSE bid. Still open: treatment of EOSE bid below the contracted amount (C); applicable fee rate. |
| **Unit 원/kW-h** | Bid price is "공급가능용량 기준 단위 고정비(원/kW-h)". | p.14 / PDF 16 (Ⅲ.5); p.22 / PDF 24 (Ⅳ.3) | — | KRW per kW of 공급가능용량 per settled hour: KRW/kW-h × kW × h = KRW. **Not** KRW per kWh discharged. | — |
| **Contract term** | 계약기간 = 사업 준비기간 + 거래기간 (15 years). 거래기간 = 15 years including the COD day. Completion deadline February 2029. The contract is signed within 1 month of the generation business licence. | p.25 / PDF 27 (Ⅴ.1) | The earlier design had "~15 yr, unverified". | 15 settlement years from COD. Capex at year 0 = COD; no construction-period cash flows. | — |
| **Price fixed, no indexation** | 계약가격 = the bid price, "계약기간 동안 불변(물가상승률 등 인플레이션 영향 미 고려)". "고정계약 방식". | p.25 / PDF 27 (Ⅴ.1) | Real vs nominal was undefined. | The model runs in **nominal KRW**: flat nominal payment, 7% treated as a nominal rate. O&M escalation defaults to 0% (stated omission). | — |
| **Performance / technical requirements** | Charge/discharge "383 Cycle/년 이상", 5,745 cycles over 15 years. 보증수명 "15년간 70% 이상". 운전효율 "15년간 65% 이상". Plant starts and stops on EMS On/Off signals, under remote control. | p.5 / PDF 7 (Ⅱ.1) | — | Not modelled as revenue. Cost assumption: ATB O&M, which includes augmentation (§3). | Actual dispatch frequency and pattern |
| **Operating efficiency definition** | [방전전력량 ÷ 충전전력량] × 100%. Charging energy includes 소내 소비전력량. Scored on the minimum of the yearly averages; bands from ≥ 85% to 65%. | p.19 / PDF 21 (Ⅲ.6, 4.2); p.16 / PDF 18 | — | Not used in cash flow, since charging energy is not settled. | — |
| **보증수명 (EOL) and augmentation** | 보증수명 = remaining capacity as a share of the "최초 설계용량" at contract end (%). The notice quotes KEC 512.1.2 as reference: "BESS 이차전지의 최초 설계용량이 보증수명까지 소유자가 요구하는 용량을 만족하도록 하여야 하며 **운영 중간에 보증수명의 연장목적으로 설계 용량을 추가하지 않아야 함**". Scoring bands from ≥ 90% to 70% EOL. | p.23 / PDF 25 (Ⅳ.4); p.16 / PDF 18 | Earlier text implied augmentation is freely available. **It may be restricted.** | Base case keeps capacity through ATB O&M (includes augmentation), as the research brief specified. Whether that is compatible with the notice sentence is **not resolved**; the four capacity practices are separated in §6b. | Whether the notice sentence covers adding capacity to make up degradation, or same-capacity replacement; how 보증수명 is measured once capacity is added or replaced |
| **Contract price adjustment** | Triggers: 자기자본비율 below 15% at completion; 보증수명 or 운전효율 falling below the score used at bid ("연도별 도래기간"); 신용등급 on transfer; failure of equipment requirements. Adjusted price = 최저 입찰가격 × 50 / (기존 총평가점수(가격+비가격) − 변경된 비가격평가점수). The original price is restored if 보증수명 or 운전효율 recover. | p.26 / PDF 28 (Ⅴ.1 계약가격 조정) | — | **Not modelled.** It needs the lowest bid price and scores, which are unknown. Base case assumes no trigger. | — |
| **Late completion** | Delay N ≤ 30 days: trading period stays 15 years; for the first N days the price is 낙찰계약가격 × (15년 − N일) / 거래기간, and the full price applies afterwards. N > 30 days: trading period becomes 15 years − N days (deducted at the end), at the full price. N > 2 years: contract termination. | p.27 / PDF 29 (Ⅴ.2 준공지연 페널티 table) | — | **Not modelled** (on-time COD assumed). | — |
| **Performance deposit** | 입찰가격 × 1년 충·방전량 (383 cycles × contract quantity) × 10%. Paid at contract and refunded within 7 business days after COD. | p.29 / PDF 31 (Ⅵ.1) | — | **Not modelled**: refundable, and the timing effect is small. Note the notice multiplies a KRW/kW-h price by an energy quantity here. The model does not reinterpret that. | — |
| **Location and grid** | Connection is limited to KEPCO 계통관리변전소 / switching stations and substations with recognised ESS need, listed by region. Listed regions: 전남·광주, 전북, 대전·세종·충남 일부, 충북 일부, 강원 일부, 경북 일부 (e.g. 신영주, 안동, 영주, 울진, 의성, 상주). 22.9 kV requires a dedicated line. Connection-equipment costs must be considered. Meters are installed at both 송전단 and 발전단. | p.1 / PDF 3; p.10–11 / PDF 12–13 (Ⅱ.3) | The repository name refers to Yeongnam; case A models no site or regional price. Among Yeongnam provinces, **only some 경북 substations** appear in the list; **no 경남, 부산, 대구 or 울산** substations do. | Case B has no site. ATB CAPEX includes grid-connection items (§3), but the actual Korean connection cost is unknown. | Eligibility of any specific site |
| **Parallel SMP arbitrage** | Charging cost and discharge revenue are not settled (p.22 / PDF 24). "타 제도와 이중 참여 불가"; equipment traded in RPS or other schemes or subsidised cannot bid (p.5 / PDF 7). After the contract ends, no contract payment or 용량요금 (if in the spot market) is paid (p.1 / PDF 3). | as cited | — | **A and B are separate cases.** No arbitrage in B. | Any rule in the operation rules allowing energy trading during the contract |
| **Evaluation** | Price 50 points: [최저 입찰가격 ÷ 해당 입찰가격] × 50. Non-price 50 points. The cap price (상한가격) is **not disclosed**; it is "표준 ESS 총괄원가 기반 균등화원가(LCOS)". | p.13–14 / PDF 15–16; p.30 / PDF 32 | — | Win probability and the cap price are **not modelled**. The break-even price is not compared with any award price. | Cap price; award prices |
| **After contract** | No payment. Decommissioning requires domestic disposal of used batteries, with a separate contract 1 year before the end. | p.1 / PDF 3 | — | No residual value and no decommissioning cost (stated omission). | Disposal cost |

## 3. NREL ATB facts used for cost

| Item | Confirmed fact | Source file | How case B uses it | Unconfirmed |
|---|---|---|---|---|
| Dollar-year | **2022$** | Workbook D10, D67; web text | All ATB $ values are 2022$; converted at FX 1,350 without inflation to a 2029 COD | Conversion to nominal 2029 KRW (author decision) |
| Year columns | Projection years 2022–2050; 2022 = base year. The dashboard notes that the year "represents the commercial online date". | Workbook G9, rows 18/69; tech-summary printout | The "2023" column is used for the cost update. The 2029 column is used only as a separate scenario. | — |
| 476.74 $/kWh source | 4-h OCC 2023 = 1,906.96 $/kW (H108 `=G20*4+G26`), ÷ 4 | Workbook; matches dashboard $1,906.95 | Prior input; reproduction only (p* 59.4203) | — |
| 6-hour cost | 6-h OCC 2023 = 2,680.80 $/kW (H111 `=G20*6+G26`) = 446.80 $/kWh; 2029 Moderate 1,867.55 $/kW (N111) | Workbook | **New base** 446.80 $/kWh × 300,000 kWh × 1,350 = 180.95 bn KRW | — |
| Scenario | 2022–2023 identical across Advanced / Moderate / Conservative | Workbook rows 19–27 | Scenario choice does not matter for 2023; the 2029 scenario uses Moderate | — |
| Capacity basis | "240-megawatt hour [MWh] usable" | Web text (Figure 1 caption) | ATB kWh treated as usable, applied to 송전단 deliverable kWh | Whether ATB's usable basis equals the KPX 송전단 basis (not stated) |
| OCC vs CAPEX | OCC excludes GCC ($100/kW, US placeholder) and construction financing; ATB CAPEX = (OCC + GCC) × CFF. For the 6-h 2023 row only, CAPEX is 7.5% above OCC (H77 = 2,882.41); the ratio is specific to that row and is not a Korean cost estimate. | Workbook rows 70–118, 155–164, 206 | Model uses **OCC**. An earlier note calling it "all-in including grid connection" was **incorrect**. | Whether to include GCC and construction finance (author decision; Korean connection cost differs) |
| Total vs pack | OCC = energy (battery) + power (BOS) components; the total system, not the pack alone | Workbook row 29; web text | Used once as the total | — |
| **O&M and augmentation** | FOM = 0.025 × OCC (H125, H128), constant over years; "include battery augmentation costs, which enables the system to operate at its rated capacity throughout its 15-year lifetime"; "Battery augmentation" listed in O&M inclusions | Workbook; web text p.3; O&M-inclusions printout | O&M = 0.025 × OCC-based capex; capacity held constant; no separate augmentation or degradation line | Augmentation share of FOM (no split given) |
| RTE / cycling | RTE 0.85; costs based on about one cycle per day | Workbook H176/H179; web text | Not used in B's cost; the notice requires ≥ 383 cycles/yr | Whether ATB's augmentation assumption holds at the notice's cycling |

## 4. Timing gaps

| Element | Period |
|---|---|
| Case A price data | 2024 SMP, 364 complete days |
| Case B market rules | notice dated 2026-09-22 |
| Case B cost basis | ATB 2022$, 2023 projection column (6-hour OCC) |
| Case B operation | COD by Feb 2029; 15-year trading period ≈ 2029–2044 |

A and B differ in size, duration, time period, revenue mechanism and cost basis
all at once. The comparison is a case comparison, not a causal estimate.


## 5. Operation rules (전력시장운영규칙, 2026. 7.) — review of the open settlement items

Page references are **printed page / PDF page** of the full rules file. The same
pages are in the excerpt PDF. Classification:

- **A** = explicit in the text
- **B** = needs a contract, detailed regulation or KPX decision
- **C** = not found in the parts reviewed; this is not a claim that no rule exists

| Item | Class | What the text says | Where |
|---|---|---|---|
| Settlement formula | A | TECP_i,t = (TECF_i × EOSE_i,t / EMOT_i) × EFR_i,t × 1000 [KRW], with TECF = EACF − ENPP (contract price minus penalty price; ENPP = 0 unless a 거래지연 or 비가격평가 불충족 penalty applies) | 별표2 Ⅰ.18, 531 / 549; 제15.4.1.1조 (settlement per 별표2 and 별표8), 252 / 270 |
| **Performance rate when there is no dispatch instruction** | **A** | EFR (시간당 급전지시 이행률). (i) \|SET_POINT\| ≠ 0: Max[1 − \|SET_POINT − MGO\| / \|SET_POINT\|, 0], and 1 if within ε. (ii) **\|SET_POINT\| = 0: Max{1 − \|EGMO\| ÷ ECD, 0}; = 1 if \|\|EAP\| − \|MGO\|\| ≤ ε and \|EGMO\| ≤ ε** (<개정 2026.7.24.>). ε = ±RA × 0.005, min 0.05 MWh, max 5 MWh; RA = 변경 공급가능용량 (MWh). | 별표2 Ⅰ.18, 531–532 / 549–550; 별표1 RA, 430 / 448 |
| Settled hours | A | Settlement is per 거래시간 t, and case (ii) explicitly covers hours without an instruction, so every hour is settled. (The notice writes the daily sum as Σ_{t=1..24}.) | same |
| Hourly capacity term (공급가능용량 / 방전가능전력량) | A | The supplier **bids**, for each of the 24 hours: 공급가능용량 = 송전단 hourly maximum discharge (MW), which "must match the approved maintenance plan"; 방전가능전력량 (EOSE) = 송전단 energy deliverable over the maximum operating time (MWh), which cannot be bid when 공급가능용량 = 0; and 소내전력량. EMOT = the notice's maximum operating time. Changes are allowed until 17:30 the day before, except for force majeure or a serious failure. | 별표4 6.6.1–6.6.4, 588–589 / 606–607; 별표1 EOSE/EMOT, 406–407 / 424–425; forms 별지 31-10, 33-9 |
| Outages and maintenance | A (mechanism) / B (detail) | Planned maintenance must be reflected in the hourly bid capacity, and EOSE cannot be bid when capacity is 0, so maintenance hours lower EOSE and therefore payment. The general pre-settlement adjustment for generators that fail to re-bid (별표8 7.3.2.1) is **not stated** to apply to 중앙계약 ESS. | 별표4 6.6.2.1, 6.6.3.2; 별표8 7.3.2.1, 631 / 649 |
| Capacity loss from degradation vs the contracted amount | C | No clause found that states how a bid EOSE below the contracted 최대전력저장량 is treated, beyond the formula scaling payment by EOSE. Searched "열화", "정격용량", "성능시험" and "방전가능전력량" on 중앙계약 pages; reviewed 제15장, 별표2 Ⅰ.18, 별표4 6.6 and 별표9 7.4. The notice's 보증수명 price adjustment (notice p.26 / PDF 28) is a separate mechanism. | — |
| Transaction fee | A (base) / B (rate) | The fee = each member's traded quantity × a rate **"전력거래소가 별도로 정하는"**; for 중앙계약 ESS the base is the **discharge metered value** (confirmed). The rate applicable to this ESS is not confirmed. Rounding rules for the settlement amounts are also specified. | 별표8 7.8.1, 634 / 652; 7.1.4, 7.1.15, 629–630 / 647–648 |
| Operating cycle | A | 1 운전주기 = cumulative discharge equal to the contracted 최대전력저장량; the day-ahead schedule is constrained to 1 cycle/day, or up to 2 cycles/day if the system needs it. | 별표9 5.14, 652 / 670; 7.4, 657 / 675 |

**Notice vs rules on 이행률.**

- The notice (p.26 / PDF 28) writes the rate as an α-weighted average of the charge and discharge shortfalls, and leaves the no-instruction case undefined.
- The rules write it on the single 60-minute average SET_POINT, add the tolerance ε, and define the no-instruction case.
- For an hour with an instruction in only one direction, the two forms coincide apart from ε.
- Code keeps both: `hourly_performance_rate` (notice form; raises for no instruction) and `hourly_efr_rules` (rules form).
- Which text governs a signed contract is a contract matter (B).

**Effect on the annual model.**

- With EOSE_t equal to the contracted 300 MWh and EFR_t = 1 in every hour, the rules give payment = p × 300,000 kWh / 6 h × 8,760 h. That is exactly the annual model at f = 1, so **p\* = 55.6886 is unchanged**.
- The hypothetical factor f can now be read as the hour-average of (EOSE_t / contracted EOSE) × EFR_t.
- It stays hypothetical: no dispatch or metering data exists for the hypothetical plant.

## 6. KEC 512.1.2 — review

Sources:

- Cover: Drive text extract, a cover image supplied by the user, and page 1 of `docs/sources/KEC_2025-052_cover_and_addenda_excerpt.pdf`.
- Body: `docs/sources/KEC_2025-052_pp520-526_excerpt.pdf`, supplied by the user. It holds 7 pages, printed pp.520–526, which the user identified as PDF pp.550–556 of `KEC_official_attachment.pdf`.
- 부칙: `docs/sources/KEC_2025-052_cover_and_addenda_excerpt.pdf`, printed pp.1175–1177 (§6a).

| Question | Finding | Class | Where (printed page) |
|---|---|---|---|
| Edition | 기후에너지환경부 공고 제2025-052호, 2025-10-01, "제10차 개정". It amends "중 일부" of 공고 제2024-749호 (2024-10-24). | A | cover |
| Obligation to secure rated capacity | 512.1.2 "이차전지 용량 및 운영" ①: "전기저장장치 이차전지 용량은 **수명보증기간 동안 정격방전용량**(전기저장장치 설치 시 소유자가 요구하는 이차전지의 용량)**이 확보되도록 하여야 한다**." Applies to lithium/sodium systems above 20 kWh (512.1.1). | A | 523 |
| Operating safety condition | 512.1.2 ②: "안전이 확보되도록 **정격방전용량 이하로 운영**하여야 한다." Also 512.1.4 ⑥: no charging beyond the rated maximum range, and no further charging after full charge. | A | 523–524 |
| Explicit permission or prohibition of capacity additions | **Not stated** in 512.1.2 or elsewhere in pp.520–526. The sentence the KPX notice quotes ("운영 중간에 보증수명의 연장목적으로 설계 용량을 추가하지 않아야 함", notice p.23 / PDF 25) **does not appear** in this edition's 512.1.2 text. 511.2.4 requires keeping a battery **replacement history (교체이력)**; this is a record-keeping duty, not a permission rule. | C | 520–526 |
| Contract approval for equipment changes | Not a KEC matter. Only transfer of contract rights needs committee approval (rules 제15.2.7조⑦); equipment changes depend on the contract (B), which was not obtained. | B | rules 250 / 268 |
| 부칙 of 2025-052 | Read (§6a): 제1조(시행일) "이 공고는 공고한 날부터 시행한다." | A | 1177 |
| Whether this edition applies to the hypothetical project | **Not determined** (§6a). | open | — |

### 6a. 부칙 (printed pp.1175–1177)

Two things are kept apart: what the 부칙 say (confirmed), and which edition would govern a hypothetical project (not determined).

**What the 부칙 say.**

| 부칙 | 시행일 | 경과조치 (transition rule) |
|---|---|---|
| 2018-103 (2018-03-09) | 2021-01-01 | none shown |
| 2020-738 (2020-12-31) | 2021-01-01 (522.3.2의 2: 2021-09-01) | Facilities already installed, or with 전기공사계획 인가(신고), 사업승인, 건축허가·신고 before 시행, "종전의 기준을 따를 수 있다" |
| 2021-36 (2021-01-19) | 공고한 날 | none shown |
| 2021-509 (2021-07-01) | 2022-01-01 | Same "따를 수 있다" rule, limited to listed 232/234 provisions |
| 2022-809 (2022-11-08) | 공고한 날; 245.3 1 라(2) from 2024-07-01; provisions of 245 that cite 511 and 512 take effect when 510 (전기저장장치) is amended and in force | Same "따를 수 있다" rule |
| 2023-364 (2023-04-17) | 공고한 날; two stated exceptions (245.3; 511.2.5 from 2023-10-19) | Same "따를 수 있다" rule; 제3조 special rule for reused batteries (511.2.5) |
| 2023-563 (2023-07-11) | 공고한 날 | Changes form: items for which 전기설비 공사계획 인가(신고), 사업승인, 건축허가(신고) etc. were **applied for or filed before 시행 "종전의 기준을 따른다"**; 제3조 repeals the 판단기준 |
| 2023-768 (2023-10-12), 2023-839 (2023-11-21), 2023-875 (2023-12-14), 2024-749 (2024-10-24) | 공고한 날, with listed exceptions (none of them 510–512) | Same "신청하거나 신고한 것 … 종전의 기준을 따른다" rule |
| **2025-052 (2025-10-01)** | **제1조: 공고한 날부터 시행** | **None within the excerpt.** The excerpt ends with 제1조 at the bottom of printed p.1177. Whether further articles follow on the next page cannot be seen from the excerpt. |

**What the 부칙 do not settle.**

- Which provisions 2025-052 amended, including whether 512.1.2 changed in this revision. The 부칙 do not list amended provisions.
- Which edition governs a hypothetical project. Earlier 경과조치 tie the edition to the date a 공사계획 인가(신고), 사업승인 or 건축허가 was applied for or filed. The hypothetical project has no such dates. Later revisions after 2025-052 may also exist and were not searched for.
- The earlier 경과조치 are not applied to 2025-052 by analogy.

This project therefore records 512.1.2 of the 2025-052 edition as **the text read**, not as the rule proven to govern the project.

### 6b. Notice p.23 wording and the ATB augmentation assumption

Notice text (p.23 / PDF 25, Ⅳ.4 보증수명; re-read from the uploaded excerpt, identical to the full notice):

- 보증수명 = "계약기간 동안 설비 경화･열화 등을 감안하여 산정한 **최초 설계용량 대비 잔여용량 비율**" (%, entered in the bid).
- "(참고) 보증수명 관련 한국전기설비규정 공고문 ∎ 이차전지 용량 및 운영(관련조항 512.1.2) * 보증수명(EOL): 이차전지 제조사가 BESS 사업자에게 경화･열화되는 것을 감안하여 BESS 설비의 보증기간까지의 이차전지 용량(BESS 이차전지의 **최초 설계용량이 보증수명까지 소유자가 요구하는 용량을 만족하도록 하여야 하며 운영 중간에 보증수명의 연장목적으로 설계 용량을 추가하지 않아야 함**)".

Related notice text:

- p.22 / PDF 24 (Ⅳ.1): "입찰사업자는 한국전기설비규정(KEC) 512.1.2에 따른 이차전지 용량 및 운영기준을 고려하여 입찰물량(최대 방전용량, 최대 전력저장량) 산정 필요". Also: "최대 전력저장량을 기준으로 최대 충전 가능시간은 리튬전지 7.5h … 초과할 수 없음". How this charging-time limit relates to initial oversizing is not stated and is not interpreted here.
- p.22 / PDF 24 (Ⅳ.3): the bid price covers total project cost; 운영비 includes "설비 운영 및 조정, 유지보수에 관련하여 발생하는 모든 비용".
- p.26 / PDF 28: contract price is adjusted downward when the yearly 보증수명 value falls below the bid score, and returns to the original price "연도별 도래기간에 평가한 기준값이 입찰시점 기준값으로 회복될 경우".

Reading rules used here:

- The notice sentence is **not ignored** because KEC 2025-052 512.1.2 lacks it. The notice itself tells bidders to size quantities with it in mind.
- The sentence is **not generalized** into a ban on all maintenance or replacement. Its object is "보증수명의 연장목적으로 설계 용량을 추가".
- The KEC document the notice calls "공고문" was not identified. The sentence is not in the 512.1.2 body or in the 부칙 read.

Four capacity practices, kept apart:

| Practice | What the sources read say | Status |
|---|---|---|
| (a) Initial design margin (초기 설계용량의 여유) | The notice sentence expects "최초 설계용량" to meet the owner-required capacity until 보증수명. KEC ① requires rated capacity over the warranty period without saying how. 보증수명 is measured against 최초 설계용량. | Consistent with the notice text. Not modelled (no switch to oversizing). |
| (b) Adding capacity to make up degradation (열화 보충을 위한 용량 추가) | Not named in the notice or KEC text read. Whether it is the same act as (d) is not defined. | **Open**; this is where ATB sits |
| (c) Replacing batteries at the same capacity (동일 용량 교체) | Not named in the notice. KEC 511.2.4 requires a replacement history, which presumes replacement can occur, but gives no rule on it for this contract. | Not addressed by the sentence as written; contract terms not read |
| (d) Adding design capacity to extend 보증수명 (보증수명 연장 목적 설계용량 추가) | The notice says it "하지 않아야 함". | Stated in the notice (quoted as KEC reference) |

Where ATB's assumption falls:

- ATB web text: fixed O&M "include[s] battery augmentation costs, which enables the system to operate at its rated capacity throughout its 15-year lifetime". ATB O&M-inclusions printout: "Battery augmentation" under fixed costs, separate from "large component replacement" under replacement costs.
- So ATB describes **(b)**, adding capacity during operation to hold rated capacity. The ATB sources read do not say whether that capacity is added module by module, is sized at installation, or how much of the 2.5% it is.
- Whether (b) counts as (d) under the notice is **not answerable from the sources read**. Two unknowns decide it: the scope of "보증수명의 연장목적", and whether added capacity enters the 잔여용량 ÷ 최초 설계용량 ratio used for the yearly 보증수명 evaluation.

**Consequences for case B.**

- The "capacity maintained at the contracted level" assumption is **consistent with** KEC 512.1.2 ①.
- Its **conformity with the contract is unconfirmed**: the method ATB assumes (b) may or may not fall under the notice's restriction (d).
- p\* = 55.6886 is therefore conditional on two things: the cost and payment assumptions, and the unconfirmed contract conformity of the capacity-maintenance method.
- The model is **not switched** to oversizing, and no augmentation share is removed from ATB O&M.

## 7. Research memo leads (not official; `docs/research_notes/2026-09-27_public_search_memo.md`)

The memo is dated 2026-09-27 and labels itself an investigation memo, not an official document. Official sources it points to are listed apart from the investigator's reading. URL-only items could not be opened here (kpx.or.kr blocked).

| Topic | Official source pointed to | What the memo reports (investigator's search/interpretation) | How this project records it |
|---|---|---|---|
| Standard contract terms | kchps.kmos.kr (저탄소 중앙계약 플랫폼) | A complete contract file for the 2026 mainland ESS market was **not obtained in this public search**; the platform could not be accessed. The memo says non-publication was not confirmed. | "이번 공개 검색에서 원문 미확보". Not "비공개". |
| 정정공고 | KPX 공지사항 board bid=0042 | No correction for the 2026 mainland notice among the posts dated 2026-09-22~23 on **page 1** of the board, nor in a public search, as of 2026-09-27. | Search scope and date recorded. **No claim that no correction exists on any platform.** |
| 설명회 | Board post list_no=78169 | Scheduled 2026-09-30 14:00–15:30; the attachment is a 개최계획(안). | A **future event** as of 2026-09-27. The plan is not cited as slides or Q&A. |
| 거래수수료 | KPX FAQ board bid=0047, "전력거래수수료는 무엇입니까?" | General rate: 거래량 × 0.1193원/kWh from 2025-09-01. The memo says the chargeable quantity for central-contract ESS was not confirmed. | A **general fee rate**, not confirmed as the rate applied to this ESS. The **base** is confirmed separately: rules 별표8 7.8.1 names discharge metered values (kWh); the contract settles in kW-h (capacity × hours). The two units are not interchangeable. **Not added to the model; no size claim is made without a calculation on a confirmed base.** |
| Draft inquiry | Channel: the platform's inquiry channel (kchps.kmos.kr); the department contact is given in the briefing post (list_no=78169) | Unsent draft. | Not sent from this project. |
