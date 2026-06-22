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

## Method
1. Translate elasticity → price scenario: `scenario = baseline × (1+g)^elasticity`
2. Dispatch: charge the cheapest 4 h, discharge the dearest 4 h (efficiency-adjusted)
3. Annual cash flows (capex, O&M, degradation) → NPV / IRR
4. Closed-form break-even + 4-scenario elasticity robustness + sensitivities
5. **LP optimization** of dispatch (PuLP) under power, capacity, state-of-charge, and cycle constraints

## Key findings
1. **No Korean "duck curve" yet** — the cheapest hours are pre-dawn (03–05h), not
   midday, so the battery charges at 3am and discharges into the daytime peak.
2. **More solar slightly *raises* the spread** (my paper's intraday-absorption
   pattern) — the opposite of the textbook merit-order story.
3. **Arbitrage-only NPV ≈ −1,923억 KRW; IRR undefined.** Robust within ~2% across
   every elasticity scenario → the econometric debate is immaterial to the
   investment; **capex dominates.**
4. Break-even needs capex ~7x lower or ~211,000 KRW/kW-yr of stacked
   capacity/ancillary revenue.
5. An **LP dispatch optimizer** shows the heuristic *overstates* revenue ~8% by
   ignoring the charging power limit; the feasible optimum confirms the result.

## Figures
`outputs/price_curve.png` (SMP, solar, dispatch) · `outputs/cashflows.png`
(annual cash flow) · `outputs/lp_dispatch.png` (LP-optimal schedule)

## Limitations
Dispatch assumes perfect foresight of prices (both the heuristic and the LP);
single national price; capex is literature-based; the positive daytime elasticity
is the paper's own contested result, so the *mechanism* is treated as tentative
(the *robustness* is not).

## Future work
- Revenue stacking (capacity / ancillary) and PPA structures.
- Yeongnam-specific hourly elasticities.
- Multi-day / seasonal dispatch and price-forecast uncertainty (replace perfect foresight).
