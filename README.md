# Strategic Adaptation of LLM Pricing Agents in Dynamic Markets

## Current research question

When two LLM pricing agents face gradual demand expansion whose numerical path is not disclosed to them, do their prices adapt to the changing market, or do the agents keep an early pricing rule once it appears profitable?

We compare two market conditions:

- **Mature:** demand is stationary throughout the run.
- **Expanding:** the attractiveness of both products rises gradually during rounds 1–40 and then remains constant.

The agents receive a qualitative description of the market phase, but are never shown the demand equation, the numerical growth path, or the current demand level. They must infer the magnitude of change from their own realized quantity and profit, together with both firms' past prices.

**Current status:** all 12 cells in the main experiment are complete. We are checking the trajectories, the analysis code, and the reproducibility package. The results below are descriptive because the current sample contains only three seeds.

## Problem setup

Two LLM agents repeatedly set prices in a differentiated-products logit market.

| Item | Setting |
|---|---|
| Firms | 2 simultaneous pricing agents |
| Price range | 1.00–3.00 |
| Marginal cost | 1.00 |
| Demand model | Regular logit with an outside option |
| Product quality / temperature | 2.0 / 0.25 |
| Agent observations | Both firms' past prices; own past quantity and profit |
| Agent memory | Private notes carried from one round to the next |
| Oversight | Passive: flags are recorded but do not change prices or provide feedback |
| Model | `gemini-3.5-flash-lite` |
| API | Google Gemini Developer API, `GenerateContent`, via `google-genai` |
| Horizon | At least 60 rounds; convergence checked every 5 rounds thereafter |

The main design is `2 market conditions × 2 industry descriptions × 3 seeds`:

| Factor | Values | Purpose |
|---|---|---|
| Market | mature, expanding | Changes the demand path |
| Industry text | consumer retail, B2B software | Checks whether the result depends on one narrative context |
| Seed | 0, 1, 2 | Measures run-to-run variation |

Only the demand path changes between the mature and expanding treatment. The two industry descriptions change prompt wording but use the same economic parameters.

The expanding market is calibrated so that, at a symmetric price of 2.00, the outside-option share falls from one third in round 1 to one fifth by round 40. Agents see a qualitative market description, not this calibration.

## Requirements for interpreting the experiment

- Compare mature and expanding cells with the same seed and industry description.
- Report raw prices and prices normalized by the round-specific competitive and joint-profit benchmarks. A higher raw price can simply reflect stronger demand.
- Treat price stability as behavior to explain, not evidence of optimality or collusion.
- Do not infer strategy from notes alone. Notes are a supporting diagnostic, not a direct observation of the model's internal policy.
- Do not call a price “collusive” solely because it is above the one-shot Nash benchmark.

## Completed results

All 12 runs reached the stability criterion by round 60.

| Market | Mean price, rounds 41–60 | Dynamic price index | Unchanged next price | Change no larger than 0.05 | Stay after profit did not fall |
|---|---:|---:|---:|---:|---:|
| Mature | 2.038 | 1.249 | 96.2% | 100.0% | 99.1% |
| Expanding | 2.088 | 1.058 | 90.5% | 98.9% | 95.8% |

The dynamic price index is zero at the round-specific symmetric Nash price and one at the round-specific symmetric joint-profit price.

Three observations follow from the current runs:

1. **Expanding-market prices were only slightly higher.** The average paired difference in the final 20 rounds was `+0.05` in both industry descriptions.
2. **The normalized result points in the opposite direction.** The expanding-market index was lower because its competitive and joint-profit benchmarks increased more than the agents' prices did.
3. **Price adjustment was very limited in both conditions.** More than 90% of adjacent decisions repeated the previous price, and almost every change was no larger than 0.05.

The notes audit is consistent with this inertia: maintain/hold language appeared in 73.2% of mature-market agent-rounds and 88.6% of expanding-market agent-rounds, while explicit explore/test language appeared in only 1.5% and 3.6%, respectively. These keyword counts are descriptive and do not show that notes caused the behavior.

The current evidence therefore supports a narrow conclusion: under this prompt and model, agents often lock into a locally satisfactory price and react only weakly to hidden demand growth. It does not yet establish a general model property or a collusive mechanism.

Cell-level results are in [results/hidden-demand-summary.csv](results/hidden-demand-summary.csv). The full setup, metric definitions, API details, and interpretation limits are in [docs/preliminary-experiments.md](docs/preliminary-experiments.md).

## Current work

We are currently:

- validating all 12 saved trajectories and the dynamic benchmark calculations;
- making the hidden-demand treatment reproducible from the public code;
- checking whether the observed inertia is robust enough to justify a revised experimental method.

No unimplemented experiment is presented here as part of the study.

## Related work

The literature review is organized around the issue that directly affects this experiment:

1. reinforcement-learning pricing agents can produce high prices;
2. high prices do not by themselves identify genuine collusion;
3. LLM agents add prompt-dependent, short-run adaptation and natural-language memory;
4. recent work tests whether these results survive more realistic or heterogeneous settings; and
5. the remaining question for this project is how an LLM agent responds to hidden change within a run.

See [docs/literature-review.md](docs/literature-review.md) for the synthesis and [docs/reading-list.md](docs/reading-list.md) for the paper-by-paper reading list.

## Repository contents

```text
.
├── README.md
├── docs/
│   ├── literature-review.md
│   ├── preliminary-experiments.md
│   └── reading-list.md
├── experiments/
│   ├── README.md
│   └── hidden-demand-design.json
├── results/
│   ├── hidden-demand-summary.csv
│   └── preliminary-results.csv
├── src/
│   ├── pricing_agents/
│   ├── pricing_experiment/
│   ├── pricing_market/
│   └── pricing_regulator/
└── references/
    └── references.bib
```

`preliminary-results.csv` is retained as a legacy record of the earlier response-order and oversight pilot. It is not the main result reported above.

## Reproducibility and data handling

The repository contains the sanitized source code, fixed design values, and compact result summaries. API keys, `.env` files, key backups, virtual environments, provider logs, and raw text trajectories are excluded. Raw trajectories will be added only after checking them for sensitive provider metadata.

## Contribution and limitations

The final contribution and full limitations section remain **TBD** until the current trajectories and revised method have been validated. At present, the defensible result is the observed weak adaptation and strong price inertia in this specific 12-cell experiment.
