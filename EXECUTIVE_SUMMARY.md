# Executive Summary — Does Battery Storage Pay Under Korea's Solar Transition?

*A business extension of the working paper "Does Solar Generation Lower the Korean SMP?"*

## Motivation — why Yeongnam

Yeongnam (including Busan) is Korea's industrial heartland, where firms are
directly exposed to wholesale power costs and, increasingly, to RE100 / PPA
pressure. My working paper finds solar's causal effect on the wholesale price
(SMP) is **strongest in Yeongnam: −1.35%, versus −0.58% nationally.** If solar is
reshaping regional prices, the natural decision question is whether storage can
monetize that shift — a live issue for developers and large consumers in the
region. This project turns the academic estimate into that investment question,
making "Busan" a concrete analytical object rather than an aspiration.

## Question
Is a 100 MW / 4 h battery in Yeongnam worth building on **energy arbitrage alone?**

## Data
- 2024 hourly panel, 16 mainland regions, **N = 140,138** (the working-paper dataset)
- National hour-of-day SMP and solar generation profile; hourly IV elasticities (HTE)
- Battery capex: NREL ATB 2024 / Lazard LCOS, ~$350/kWh
- Figures reported in USD at ~1,350 KRW/USD (2024 avg); analysis is KRW-native

## Method
1. Translate elasticity → price scenario: `scenario = baseline × (1+g)^elasticity`
2. Dispatch: charge the cheapest 4 h, discharge the dearest 4 h (efficiency-adjusted)
3. Annual cash flows (capex, O&M, degradation) → NPV / IRR
4. Closed-form break-even + 4-scenario elasticity robustness + sensitivities
5. **LP optimization** of dispatch (PuLP) under power, capacity, state-of-charge, and cycle constraints
6. **Full-year backtest** of all 366 daily price curves + a capex × stacked-revenue break-even frontier

## Key findings
1. **No Korean "duck curve" yet** — the cheapest hours are pre-dawn (03–05h), not
   midday, so the battery charges at 3am and discharges into the daytime peak.
2. **More solar slightly *raises* the spread** (my paper's intraday-absorption
   pattern) — the opposite of the textbook merit-order story.
3. **Arbitrage-only NPV ≈ −$142.5M; IRR undefined.** Robust within ~2% across
   every elasticity scenario → the econometric debate is immaterial to the
   investment; **capex dominates.**
4. Break-even needs capex ~7x lower (~$47/kWh) or ~$156/kW-yr of stacked
   capacity/ancillary revenue.
5. An **LP dispatch optimizer** shows the heuristic *overstates* revenue ~8% by
   ignoring the charging power limit; the feasible optimum confirms the result.
6. **Backtesting all 366 days** (vs the average day) raises arbitrage 43% — yet
   NPV stays −$134M; daily profit is volatile and seasonal (winter ≈ 2.5× summer).

## Figures
`outputs/price_curve.png` (SMP, solar, dispatch) · `outputs/cashflows.png` (cash
flow) · `outputs/lp_dispatch.png` (LP schedule) · `outputs/analytics_distribution.png`
(daily distribution + seasonality) · `outputs/analytics_breakeven_frontier.png`
(capex × stacked-revenue decision map)

## Limitations
- **Single-price market** → temporal (not locational) arbitrage on the national
  SMP; Yeongnam is the asset location and solar driver, not a regional price.
- **Single-buyer (CBP) market** → assumes SMP price-taker access; real Korean ESS
  stacks REC / frequency-regulation / peak-shaving, so this is an upper-bound
  screen and the negative result is conservative.
- **Perfect-foresight dispatch** (heuristic and LP); one representative day.
- **Energy arbitrage only** — no capacity / ancillary / REC revenue modeled.
- Positive daytime elasticity is the paper's own contested result (night
  coefficients weakly identified); robustness keeps NPV within ~2%. Capex is
  literature-based.

## Future work
- Revenue stacking (capacity / ancillary) and PPA structures.
- Yeongnam-specific hourly elasticities.
- Multi-day / seasonal dispatch and price-forecast uncertainty (replace perfect foresight).
