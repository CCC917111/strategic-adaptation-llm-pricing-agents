# Experiment and Current Results

## Research question

When demand expands gradually without being disclosed, do two LLM pricing agents infer the change and adjust their prices, or do they keep an early price once it produces acceptable profit?

## Experimental requirements

The comparison is designed to isolate the demand path.

- Mature and expanding cells use the same model, market parameters, prompt structure, oversight mode, and stopping rule.
- Industry descriptions change the narrative context only; they do not change the demand or cost parameters.
- Agents are shown a qualitative mature/expanding market description, but not the demand equation, numerical growth path, current demand shift, equilibrium price, or counterfactual profits.
- Agents observe both firms' past prices and only their own realized quantity and profit.
- Analysis uses both raw prices and round-specific economic benchmarks.
- Price and note analysis is descriptive; neither is treated as sufficient proof of collusion or internal reasoning.

## Market and information setup

Two firms choose prices simultaneously in each round. Prices lie between 1.00 and 3.00, marginal cost is 1.00, and demand follows a regular-logit model with an outside option. Product quality is 2.0 and temperature is 0.25.

In the mature condition, common product attractiveness remains fixed. In the expanding condition, it increases linearly from zero in round 1 to `0.1732867951` in round 40 and remains at that level. This value is calibrated so that, when both prices equal 2.00, the outside-option share falls from one third to one fifth.

The agents receive only qualitative scenario text. They are told that they operate either in consumer retail or B2B software and that the market is mature or expanding, but they are not shown how that description maps to the numerical demand process.

Each agent's private `notes` field is passed into its next decision. The full numerical history is also shown each round.

Oversight is passive. The system records behavioral flags, but flags do not alter prices and are not shown to the agents. This avoids regulator feedback becoming a second treatment.

## Model and API

The completed runs used:

- model: `gemini-3.5-flash-lite`;
- provider: Google Gemini Developer API;
- SDK: `google-genai`;
- method: asynchronous `GenerateContent`;
- response: schema-constrained JSON;
- stored provider interaction: disabled;
- response-field order: price, justification, competitor-information disclosure, private notes.

The API key was loaded from the environment and was not written into result files. The saved manifests record `generate_content`, and the public client exposes the API method explicitly.

## Completed design

| Factor | Values |
|---|---|
| Market | mature, expanding |
| Industry description | consumer retail, B2B software |
| Seed | 0, 1, 2 |
| Oversight | passive |
| Requested maximum | 100 rounds |
| Minimum before stopping | 60 rounds |

This gives 12 completed cells. Convergence is checked every 5 rounds using a 20-round window. Both agents must have a price coefficient of variation no greater than 0.03 and a difference between the two half-window means no greater than 0.01. The 60-round minimum ensures that the expanding cells contain at least 20 rounds after demand reaches its plateau in round 40.

## Metrics

- **Late-round price:** mean executed price across both agents in rounds 41–60.
- **Dynamic price index:** the executed price minus the round-specific symmetric Nash price, divided by the gap between the round-specific symmetric joint-profit price and Nash price. Zero corresponds to Nash and one to the joint-profit benchmark.
- **Unchanged decision:** the next posted price exactly equals the previous posted price.
- **Small move:** the absolute price change is no larger than 0.05.
- **Stay after non-declining profit:** the next price is unchanged when the agent's previous realized profit was at least its profit one round earlier.
- **Notes screen:** a transparent keyword count for maintain/hold and explore/test language. This is not a semantic classifier.

At the demand plateau, the calibrated benchmarks are:

| Market | Symmetric Nash | Symmetric joint-profit | Standalone monopoly |
|---|---:|---:|---:|
| Mature | 1.473 | 1.925 | 1.802 |
| Expanding | 1.485 | 2.054 | 1.925 |

## Current results

| Market | Late-round price | Dynamic price index | Unchanged | Move ≤ 0.05 | Stay after profit did not fall | Maintain/hold notes | Explore/test notes |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mature | 2.038 | 1.249 | 96.2% | 100.0% | 99.1% | 73.2% | 1.5% |
| Expanding | 2.088 | 1.058 | 90.5% | 98.9% | 95.8% | 88.6% | 3.6% |

The paired expanding-minus-mature late-round price difference averaged `+0.05` in the retail description and `+0.05` in the software description. The cell-level differences vary across seeds; with three seeds they should not be treated as a precise treatment-effect estimate.

The dynamic index is lower in the expanding cells even though their raw prices are higher. This is not contradictory. Hidden demand growth raises the economic benchmarks, and the agents' prices do not rise by the same amount.

Across both market conditions, agents changed prices very little. If profit had not fallen, they usually repeated the previous decision. Notes often described the current price as stable or satisfactory and rarely proposed meaningful exploration. This suggests a concrete limitation of the current method: the agents learn only from prices they choose themselves, and very small changes provide little information about a changing demand curve.

## What the results do and do not show

The results show strong inertia and weak adjustment to hidden demand expansion for this model, prompt, and set of 12 runs. They also show why raw prices must be interpreted against changing benchmarks.

They do not show that:

- all LLM pricing agents behave this way;
- the notes caused the price inertia;
- the observed prices are optimal;
- the agents formed a genuine collusive reward–punishment strategy; or
- the treatment effect is precisely estimated with three seeds.

## Current work

The active work is limited to what is already underway:

1. verify the 12 trajectories and all derived metrics;
2. align the public implementation with the saved hidden-demand design and API manifests; and
3. decide, from that audit, how much exogenous exploration a later method will require.

No later intervention experiment has yet been run, so none is reported as part of the current study.

## Earlier pilot

An earlier 18-cell pilot compared response-field order and passive, revision, and veto oversight. It is retained in `results/preliminary-results.csv` as provenance for the initial code. The most relevant diagnostic was that paper-order passive runs repeated the previous price in 99.2% of adjacent decisions and made changes no larger than 0.05 in 99.8%. This pilot motivated the closer inertia analysis, but it is not the main experiment in this repository.

## Contribution and limitations — TBD

The final contribution and complete limitations section will be written after the current audit and any revised experiment are complete. The present limitation is already clear: the main design contains one model version, two narrative contexts, three seeds, and a stylized two-firm market.
