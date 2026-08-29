# Preliminary Experiments and Method Revision

## Status and scope

This document records the exploratory work found in `report_new`. It separates completed preliminary evidence from the paper-aligned experiment that has not yet produced usable rounds.

The completed evidence is a baseline, not a final replication or contribution claim. It is useful for diagnosing the behavior of the current agent loop and motivating the next experimental design.

## Current implementation

### Market

- Two firms choose prices simultaneously in each round.
- Prices are constrained to `[1.00, 3.00]`; marginal cost is `1.00`.
- Demand follows a differentiated-products regular-logit model with an outside option.
- The current calibration uses quality `2.0` and temperature `0.25`.
- These parameters reproduce the reported price benchmarks approximately: symmetric Nash `p_NE = 1.473` and standalone monopoly `p_M = 1.802`.
- The source paper does not disclose the underlying utility parameters, so this is a benchmark-level calibration rather than an exact structural reproduction.

### Agent state and observations

Each agent observes the full sequence of both firms' past prices and its own realized quantity and profit. It receives no analytical demand curve or counterfactual profit table. Its private natural-language `notes` field persists across rounds and is replaced by the newly generated notes after each decision.

The main output schema is:

```text
price → public justification → competitor-information disclosure → private notes
```

A price-last treatment changes the order to:

```text
public justification → competitor-information disclosure → private notes → price
```

### Oversight modes

- **Passive:** flags are recorded, but prices are not changed.
- **Revision:** a flagged proposal triggers a second model call requesting a lower revision.
- **Veto:** a flagged proposal is replaced according to the regulator rule.

The behavioral flags cover an elevated price relative to the competitive benchmark, sustained increases, and parallel elevated movement after a warm-up period.

## API and model configuration

The completed preliminary runs used the **Google Gemini Developer API** through the `google-genai` Python SDK with model `gemini-3.5-flash-lite`. Calls were asynchronous and returned schema-constrained JSON. Normal experiment calls used `store=false`; API keys were loaded from ignored environment files and are not included in this repository.

The current code path for `gemini-2.5-*` and `gemini-3.7-*` models calls:

```python
client.aio.models.generate_content(...)
```

with `response_mime_type="application/json"` and a Pydantic response schema. The intended paper-main update is `gemini-3.7-flash`, `thinking_level=high`, temperature unset, seed recorded, and online convergence checks enabled. Attempts at this updated profile had produced zero completed rounds at the time of this audit because of provider-side quota and availability errors. No result below is attributed to Gemini 3.7 Flash.

An OpenAI Responses API adapter exists in the broader working directory, but it was not the provider used for the completed result set summarized here.

## Completed exploratory design

The response-order comparison contains:

- 3 random seeds (`0–2`);
- 2 output-field orders (`paper`, `price-last`);
- 3 oversight modes (`passive`, `revision`, `veto`);
- 100 rounds per cell;
- 18 completed cells and 1,800 market rounds in total.

The archived run report records 3,662 successful model decisions and approximately 11.63 million tokens, including revision calls.

## Preliminary results

### Late-round prices

The table reports the average executed price over the final 20 rounds.

| Seed | Order | Passive | Revision | Veto |
|---:|---|---:|---:|---:|
| 0 | paper | 1.975 | 1.500 | 1.490 |
| 1 | paper | 1.975 | 1.595 | 1.615 |
| 2 | paper | 2.000 | 1.475 | 1.325 |
| 0 | price-last | 1.950 | 1.560 | 1.600 |
| 1 | price-last | 1.420 | 1.450 | 1.400 |
| 2 | price-last | 1.850 | 1.500 | 1.580 |

Price-last reduced the passive late-round price in all three seeds, with paired differences of `-0.025`, `-0.555`, and `-0.150` and a mean difference of `-0.243`. The active-oversight effects were heterogeneous across seeds, so the current sample does not support a general claim that response order consistently strengthens revision or veto.

All 18 cells passed the implemented stability criterion between rounds 40 and 55. Seventeen reached exact fixed points by round 35; one settled into a period-two pattern. Fast convergence therefore did not imply agreement across seeds: different runs entered different absorbing states.

The self-reported `used_competitor_info` field was `false` in all nine paper-order cells and `true` in only 6 of 1,800 agent-round observations in the price-last cells. It is therefore not a useful standalone measure of whether competitor information affected the policy.

### Behavioral inertia audit

We separately audited the six passive runs so regulator actions could not mechanically create the observed price path.

| Diagnostic | Paper order | Price-last |
|---|---:|---:|
| Adjacent decisions with exactly unchanged price | 589/594 (99.2%) | 528/594 (88.9%) |
| Adjacent decisions with change no larger than 0.05 | 593/594 (99.8%) | 586/594 (98.7%) |
| Unchanged price during the first 20 rounds | 109/114 (95.6%) | 66/114 (57.9%) |
| Stay after previous profit did not decline | 582/583 (99.8%) | 517/541 (95.6%) |
| Mean absolute next-price change after non-declining profit | 0.0001 | 0.0019 |
| Notes containing a maintain/hold phrase | 473/600 (78.8%) | 414/600 (69.0%) |
| Notes containing an explicit explore/test phrase | 4/600 (0.7%) | 26/600 (4.3%) |

The price and profit diagnostics are direct calculations from the saved trajectories. The notes counts are a transparent keyword screen, not a semantic classifier and not causal evidence.

## Problems revealed by the current method

1. **Premature policy lock-in.** The agent often interprets non-decreasing profit as sufficient evidence that the current action is optimal. It then writes that conclusion into persistent notes and repeatedly reuses it.
2. **Weak endogenous exploration.** Even when the agent says it is testing an alternative, the move is usually at most `0.05`. Such local steps reveal little about the wider response surface.
3. **Self-confirming observations.** The agent sees profit only at the price it chose while the rival changes endogenously. A stable profit does not show that a substantially different unilateral price would be worse.
4. **History and notes are bundled.** Full numerical history and persistent notes grow together, so the existing runs cannot identify whether lock-in comes from observations, compressed text memory, or both.
5. **Convergence is not optimality or collusion.** An exact fixed point can represent a local heuristic, a prompt-induced convention, or a strategic outcome. Stability alone cannot distinguish these mechanisms.
6. **Self-report is weak evidence.** Near-universal denial of competitor influence conflicts with notes that sometimes discuss rival prices. Public compliance fields should not be treated as ground truth.
7. **Limited external validity and power.** The completed comparison uses one model family, three seeds, a stylized calibrated market, and a now-superseded model version.

## Next experiment: change from free search to intervention-based identification

The next study should not ask the LLM to discover the market solely through unconstrained repeated price choices. It should place controlled perturbations into an otherwise identical agent loop.

### Proposed design

1. **Matched baseline:** run a mature market from a fresh state.
2. **Regime transition:** run growth → mature with the same final mature parameters.
3. **Randomized memory intervention at transition:** carry, reset, or sanitize private notes while holding model, prompt, numerical history disclosure, seed, and final market constant.
4. **Exogenous exploration probes:** at pre-registered rounds, impose a small set of price probes or a unilateral deviation on one firm. This supplies information outside the agent's self-selected local neighborhood.
5. **Autonomous recovery window:** return control to both agents and measure whether they revert, retaliate, adapt, or discover a more profitable response.

Primary outcomes should be behavioral: post-transition adjustment speed, final-price hysteresis, profit regret relative to a known best response, reaction to unilateral deviations, recovery time, and sensitivity to memory intervention. Notes should be analyzed only after these outcomes are fixed, and preferably through pre-registered labels or held-out prediction.

This method directly tests adaptation and memory while reducing the chance that the result is merely an artifact of an LLM's reluctance to explore.

## Interpretation limits

- The inertia statistics describe these saved runs; they do not establish a universal property of LLM agents.
- Keyword counts do not prove that notes caused behavior.
- The response-order comparison is exploratory and based on only three seeds.
- Completed Gemini 3.5 Flash-Lite runs used the earlier baseline implementation and should not be labeled as a paper-perfect replication.
- The paper-aligned Gemini 3.7 Flash profile requires a fresh completed run before any direct comparison or confirmatory claim.

## Contribution and limitations — TBD

**Contribution:** TBD after the intervention pilot establishes whether path dependence, explicit memory, or deviation response is the most stable mechanism.

**Additional limitations:** TBD after the final model set, number of seeds, transition schedule, and probe design are fixed.
