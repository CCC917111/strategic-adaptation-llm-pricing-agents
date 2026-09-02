# Experiments and Results

This document reports only completed experiments. All comparisons use the same basic repeated-pricing testbed before changing the oversight rule, response schema, or demand path.

## Shared market and agent setting

Two LLM agents simultaneously set prices for differentiated products. Demand is logit with an outside option, marginal cost is 1.00, and prices are restricted to 1.00–3.00. Product quality 2.0 and temperature 0.25 reproduce the reported symmetric Nash benchmark of 1.473. Under constant demand, the symmetric joint-profit price is 1.925 and the standalone monopoly price is 1.802.

Each agent observes its firm ID, round, price range, both firms' past prices, its own quantity and profit, and its own private notes from the previous round. It returns a proposed price, public justification, competitor-information disclosure, and updated private notes. Notes persist to the next call; public text and self-disclosure are recorded separately from the action.

The experiments use `gemini-3.5-flash-lite` through the Google Gemini Developer API with schema-constrained JSON and `store=false`.

## Static-market benchmark under oversight

Demand is held constant while a deterministic regulator operates in one of three modes:

| Mode | Operation |
|---|---|
| Passive | Flags are logged; proposed prices execute unchanged; feedback is not shown to agents |
| Revision | A flagged proposal receives one model revision request and must fall by at least 0.01 |
| Veto | A flagged proposal is replaced using the benchmark cap and previous executed price |

The regulator checks an elevated benchmark gap, sustained price increases, and parallel elevated movement after a ten-round warm-up. The response order is:

```text
price → public justification → used_competitor_info → private notes
```

The completed design is 3 oversight modes × 3 seeds × 100 rounds, or 900 market rounds. It used the archived Gemini Interactions code path.

The broad market, prompt, memory, and oversight structure follows the setting used in *Oversight Is Not Compliance*. The implementation is not an exact replication: regulatory calculations used the fixed symmetric Nash price 1.473 rather than a round-specific best response, all runs continued to round 100 rather than stopping online, and the unreported demand parameters were calibrated.

### Results

Mean executed price in rounds 81–100:

| Seed | Passive | Revision | Veto |
|---:|---:|---:|---:|
| 0 | 1.975 | 1.500 | 1.490 |
| 1 | 1.975 | 1.595 | 1.615 |
| 2 | 2.000 | 1.475 | 1.325 |
| **Mean** | **1.983** | **1.523** | **1.477** |

The corresponding cross-seed mean supracompetitive indices are 1.551, 0.153, and 0.011. Passive oversight produced similar late prices in all seeds; revision and veto lowered the mean but produced more varied terminal states.

The passive condition also shows very limited exploration:

| Diagnostic | Result |
|---|---:|
| Adjacent decisions with unchanged price | 99.2% |
| Adjacent decisions with change no larger than 0.05 | 99.8% |
| Stay after previous profit did not decline | 99.8% |
| Notes containing maintain/hold language | 78.8% |
| Notes containing explicit explore/test language | 0.7% |

Stable prices therefore cannot be read directly as evidence of an optimized or collusive policy. The agents frequently treated non-declining profit as sufficient reason to keep the current action.

## Response-schema diagnostic

To check whether field order affected the result, we matched the 9 static-market cells and changed only the structured response order:

```text
public justification → used_competitor_info → private notes → price
```

| Mode | Original-order mean | Price-last mean | Paired difference |
|---|---:|---:|---:|
| Passive | 1.983 | 1.740 | −0.243 |
| Revision | 1.523 | 1.503 | −0.020 |
| Veto | 1.477 | 1.527 | +0.050 |

The passive paired differences were −0.025, −0.555, and −0.150 across seeds. Revision and veto changed direction across seeds. Seventeen of the 18 combined runs reached exact price fixed points; one entered a period-two pattern.

The diagnostic shows that a small scaffold change can select a different stable path. It does not remove the weak-exploration problem. The structured `used_competitor_info` field was also `false` in every original-order decision and `true` in only 6 of 1,800 price-last agent-round observations, so it is not treated as a reliable measure of behavioral influence.

## Mature and expanding demand

This experiment asks whether an agent revises a stabilized rule when demand changes during the interaction. It retains the two-agent market, base calibration, price histories, own quantity/profit feedback, persistent notes, original response order, and passive oversight.

| Factor | Values | Role |
|---|---|---|
| Market | Mature, expanding | Changes the numerical demand path |
| Industry description | Consumer retail, B2B software | Changes qualitative context only |
| Seed | 0, 1, 2 | Measures run-to-run variation |

In the mature condition, common product attractiveness is constant. In the expanding condition, it rises linearly from zero in round 1 to 0.1732867951 in round 40 and then plateaus. At symmetric price 2.00, the outside-option share changes from one third to one fifth.

Agents receive a qualitative mature/expanding description but not the demand equation, growth path, current shift, equilibrium prices, or counterfactual profits. They must infer the magnitude of change from realized quantity and profit.

These 12 cells use asynchronous Gemini `GenerateContent`. Convergence is checked every 5 rounds over a 20-round window, with a minimum of 60 rounds to guarantee 20 post-plateau observations. Every cell stopped at round 60.

At the demand plateau, the calibrated benchmarks are:

| Market | Symmetric Nash | Symmetric joint-profit | Standalone monopoly |
|---|---:|---:|---:|
| Mature | 1.473 | 1.925 | 1.802 |
| Expanding | 1.485 | 2.054 | 1.925 |

### Results

| Market | Late-round price | Round-specific price index | Unchanged | Move ≤ 0.05 | Stay after profit did not fall | Maintain/hold notes | Explore/test notes |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mature | 2.038 | 1.249 | 96.2% | 100.0% | 99.1% | 73.2% | 1.5% |
| Expanding | 2.088 | 1.058 | 90.5% | 98.9% | 95.8% | 88.6% | 3.6% |

The expanding-minus-mature late-round price difference averaged +0.05 in both industry descriptions. The round-specific index was lower under expansion because the economic benchmarks increased more than the agents' prices.

Demand growth led to slightly more price changes, but more than 90% of adjacent decisions still repeated the previous price and almost every adjustment was no larger than 0.05. The dominant result is inertia rather than strong adaptation.

## Interpretation and current work

The completed evidence supports three limited observations:

1. the LLM often locks into a stable price after little exploration;
2. response-field order can change which stable path is reached; and
3. gradual demand expansion produces only small adjustments under the current free-choice loop.

The results do not show that stable high prices are necessarily collusive, that private notes caused inertia, or that three seeds estimate a general treatment effect precisely. Keyword counts from notes are descriptive screens, not semantic or causal classifiers.

Because the current loop produces mostly zero or very small price changes, the next method will introduce more informative variation. That design has not yet been implemented and is not presented as a completed experiment.

## Contribution and limitations — TBD

The final contribution and complete limitations section remain open. Confirmed limitations include one model family, three seeds per comparison, a stylized two-firm market, calibrated demand parameters, and known deviations between the completed static benchmark and the fully aligned oversight protocol.
