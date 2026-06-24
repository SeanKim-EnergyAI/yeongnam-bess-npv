# Interview Narrative & Q&A

Personalize every line below — these are drafts in *my* voice, not a script to
memorize. The goal is to sound like I built it and interrogated it, because I did.

---

## One sentence
"I turned my paper's own 2024 data and causal estimates into an NPV model for a
100MW battery, and found that arbitrage alone doesn't pay for it — robustly."

---

## 90-second version
> My undergraduate research used an instrumental-variables design to estimate how
> solar generation moves Korea's wholesale price, the SMP. For the business side I
> built the battery model on the *same 2024 panel*, and two things jumped out.
> First, Korea has no California-style midday price dip yet — the cheapest hours
> are pre-dawn, when solar is zero — so the battery charges at 3am and discharges
> into the expensive daytime. Second, my hourly estimates show solar slightly
> *raises* daytime prices, an intraday-absorption pattern, so more solar actually
> nudges arbitrage revenue up here, opposite to the textbook story.
>
> But on arbitrage alone the NPV is about −$140M and never recovers the
> capex. The striking part is the robustness: across every elasticity scenario —
> the contested sign, the regional estimate, a flat average — NPV moves less than
> 2%. So the econometric debate is real for the paper but immaterial to the
> investment; capex is what dominates. To break even, capex would have to fall
> ~7x or the project would need ancillary and capacity revenue stacked on top.

## 3-minute version (structure)
1. **Context (30s)** — the paper, the IV strategy, the elasticity result (~−0.6%
   SMP per +1% solar).
2. **Translation (45s)** — the one equation: `scenario = baseline * (1+g)^β` by
   hour; why hour-specific elasticities matter (uniform elasticity *shrinks* the
   spread, only heterogeneous ones widen it).
3. **Model (45s)** — dispatch rule, round-trip efficiency, cash flow with
   degradation, NPV/IRR via numpy_financial.
4. **Result + insight (45s)** — negative NPV; sensitivity to capex and solar
   growth; the "arbitrage alone isn't enough" conclusion.
5. **Limitations + next (15s)** — perfect-foresight dispatch, placeholder costs,
   the sign puzzle, and stacked-revenue extension.

## 5-minute version
Same spine as the 3-minute, but add: the data (2024 hourly panel, 16 regions),
why demand specification was the hard identification issue, the exact units
discipline (MW vs MWh, KRW/kWh vs KRW/MWh), and walk one sensitivity table aloud.

---

## Anticipated questions (and strong answers)

**"Walk me through how a regression coefficient became a dollar figure."**
A log-log coefficient is an elasticity. I apply it as a power of the solar growth
factor — `baseline * (1+g)^β` — so each hour's price moves by its own percentage,
reshaping the curve. The reshaped spread drives arbitrage revenue, which flows
into the cash-flow and NPV calc.

**"The NPV is negative — so it's a bad project?"**
On *energy arbitrage alone*, yes — and that matches reality: utility batteries
rarely pencil out on arbitrage by itself. I quantified the gap with closed-form
break-even levers: capex would need to fall ~7x (to ~$47/kWh), or daily
arbitrage be ~7x larger, or ~$156/kW-yr of stacked capacity/ancillary
revenue. So the project isn't "bad" — it's "arbitrage-only is insufficient, and
here's exactly how much more is needed."

**"How sensitive is the conclusion to your contested hourly coefficients?"**
I ran four elasticity scenarios — the national HTE, a conservative version that
zeros the weakly-identified night hours, the stronger Yeongnam regional estimate,
and a flat average — and NPV stays within ~2%. So the econometric debate is an
important academic question but immaterial to the investment call; capex
dominates. I like that the model lets me *say that with a number*.

**"Your 1pm elasticity is positive — doesn't solar lower midday prices?"**
In Korea's single-price market it doesn't, yet — that positive daytime effect is
my paper's "intraday absorption" finding, and the raw 2024 data backs it: midday
is part of an expensive plateau, not a dip. It's still a contested result, which
is why I treat it carefully. But the key point for the business case is that I
*tested* whether it matters: flipping or removing it changes NPV by under 2%.

**"Biggest simplification?"**
Perfect foresight — both the heuristic and the LP assume the day's prices are
known in advance; I don't model forecast error. The LP *does* enforce
state-of-charge and power limits, which actually revealed that my heuristic was
over-optimistic. Real dispatch would run on a price forecast, which can only
lower captured value — fine for a go/no-go screen.

**"Walk me through the optimization model."**
It's a linear program over a representative day. The decision variables are
hourly charge, discharge, and state of charge; the objective maximizes
Σ price·(discharge − charge). Constraints: power limits on charge and discharge,
capacity on state of charge, an SOC-balance equation with round-trip efficiency
linking the hours, start and end empty, and a one-cycle-per-day throughput cap —
solved with PuLP/CBC. The telling result: the LP came in ~8% *below* my
heuristic, which exposed that the heuristic was buying a full cycle's energy in
four hours, over the power limit. So the LP both tightened the model and removed
an optimistic bias.

**"Korea has a single national SMP — does arbitrage even make sense?"**
Right — there's no locational price in Korea, so this is *temporal* arbitrage on
the national SMP's intraday spread (~96 KRW/kWh pre-dawn vs ~142 midday), not a
regional price difference. Yeongnam enters as the asset's location and the solar
region that drives the price scenario. And because it's a single-buyer market
where standalone merchant arbitrage is limited, I treat the model as an
upper-bound screen of temporal value — which is exactly why a negative
arbitrage-only NPV is a conservative, credible result, consistent with Korean
storage relying on REC and ancillary revenue.

**"You modeled an average day — isn't that a big simplification?"**
I tested it rather than assumed it. I backtested the dispatch on all 366 actual
2024 daily curves, and the mean came out 43% *higher* than the average-day
estimate — because individual days have wider spreads than the smoothed average
(a Jensen's-inequality effect). Daily profit is volatile and seasonal (winter
roughly 2.5× summer, some days even negative). The point: even giving arbitrage
that 43% benefit of the doubt, NPV stays around −$134M — so the conclusion isn't
an artifact of the shortcut. I also turned it into a break-even map (capex vs
stacked revenue) so a developer or regulator can read off what it would take.

**"What would you do with more time?"**
Plug in real KPX 2024 prices and vendor capex, add a revenue-stacking layer,
replace perfect foresight with a forecast-based dispatch, and run a Monte Carlo
over price spreads.

**"Why Python, coming from R?"**
The analysis was in R; I rebuilt the business extension in Python to make it a
clean, modular, reproducible pipeline — pure functions per stage, units encoded
in names, and a single orchestrator that re-runs sensitivities by swapping one
assumption.

---

## Delivery tips (esp. Kira async video)
- Lead with the *result*, then explain the *how*. Interviewers remember the hook.
- Use the 30-second think time to pick: context → method → result → caveat.
- Always end an answer on insight or a limitation — it signals maturity.
- It's fine to say "the numbers are placeholders; the method is what I'm showing."
