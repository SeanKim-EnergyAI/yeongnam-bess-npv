# Interview Narrative & Q&A

Personalize every line below — these are drafts in *my* voice, not a script to
memorize. The goal is to sound like I built it and interrogated it, because I did.

---

## One sentence
"I turned my paper's estimate of how solar affects electricity prices into an
NPV model for a 100MW battery, and found that arbitrage alone doesn't pay for it."

---

## 90-second version
> My undergraduate research used an instrumental-variables design to estimate the
> causal effect of solar generation on Korea's wholesale electricity price, the
> SMP. That result is an *elasticity*, so I wanted to translate it into a real
> business decision. I built a Python model where a percentage increase in solar
> reshapes the 24-hour price curve through each hour's elasticity. A 100MW / 4h
> battery then charges in the cheapest hours and discharges in the most expensive
> ones, and that price spread is the revenue. I extended the daily profit into
> annual cash flows with capex, O&M, and battery degradation, and computed NPV
> and IRR.
>
> The interesting part: on energy arbitrage alone the NPV is negative. That's not
> a failure — it quantifies an industry reality, that batteries need to stack
> capacity and ancillary-service revenue on top of arbitrage. I also flagged that
> one of my hourly coefficients has a counter-intuitive sign, so I treated the
> numbers skeptically rather than just plugging them in.

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
break-even levers: capex would need to fall ~5x (to ~78,000 KRW/kWh), or daily
arbitrage be ~5x larger, or ~167,000 KRW/kW-yr of stacked capacity/ancillary
revenue. So the project isn't "bad" — it's "arbitrage-only is insufficient, and
here's exactly how much more is needed."

**"How sensitive is the conclusion to that contested hour-13 coefficient?"**
I ran it three ways — as-estimated, with the sign flipped, and with a uniform
average elasticity — and NPV moved less than 0.5%. So the contested sign is an
important academic question but immaterial to the investment call; capex and the
overall spread dominate. I like that the model lets me *say that with a number*
rather than hand-wave.

**"Your 1pm elasticity is positive — doesn't solar lower midday prices?"**
That's exactly the sign I'm skeptical of. It may be an artifact of the omitted
base hour in the interaction, a demand-control issue, or a definitional one. I
didn't want to build a business case on a coefficient I couldn't defend, so I
flagged it as something to reconcile against the regression before trusting it.

**"Biggest simplification?"**
Perfect-foresight dispatch — I assume the day's prices are known and ignore
state-of-charge and ramping constraints beyond the duration. It gives an upper
bound on arbitrage value, which is the right direction for a go/no-go screen.

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
