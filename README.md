# Strategic Adaptation of LLM Pricing Agents in Dynamic Markets

This project studies how LLM pricing agents behave in a repeated market and whether a pricing rule that has become stable can still adapt when demand changes. The emphasis is on test-time adaptation in a multi-agent system: what agents observe, what they remember, how they choose prices, and whether their behavior changes when the environment changes.

## Market and agent setting

Two firms repeatedly and simultaneously set prices for differentiated products. Demand follows a logit model with an outside option. A lower price attracts more demand, but reduces the margin on each sale; each agent therefore faces the usual trade-off between price and quantity while also reacting to the other firm's decisions.

| Item | Setting |
|---|---|
| Firms | 2 LLM pricing agents |
| Price range | 1.00–3.00 |
| Marginal cost | 1.00 |
| Demand | Logit demand with an outside option |
| Calibrated demand parameters | Product quality 2.0; temperature 0.25 |
| Static-market benchmarks | Symmetric Nash price 1.473; symmetric joint-profit price 1.925 |
| Main model | `gemini-3.5-flash-lite` |

Repeated-pricing studies have shown that adaptive algorithms can converge to stable prices above a one-shot competitive benchmark. Some learned policies also respond to price cuts in ways that resemble punishment. These observations matter, but they do not by themselves identify collusion: high prices can also result from exploration rules, feedback design, optimization failure, or statistical coupling between agents ([Calvano et al., 2020](https://doi.org/10.1257/aer.20190623); [Calvano et al., 2023](https://doi.org/10.1016/j.ijindorg.2023.102973); [Asker et al., 2024](https://doi.org/10.1111/jems.12516)).

LLM agents add a different information structure to this setting. In each round, an agent sees both firms' past prices, its own quantity and profit, and its own persistent private notes. It returns:

```text
proposed price → public justification → competitor-information disclosure → private notes
```

The notes are carried into the agent's next decision. Public justification and self-disclosure are stored separately from the action and private notes. This separation makes it possible to compare what an agent does, what it says publicly, and what it records for itself. *Oversight Is Not Compliance* uses this type of design to show why acceptable public language or an explicit denial of competitor influence should not automatically be treated as evidence that the underlying pricing policy is compliant.

## Research gap

Existing work establishes that algorithmic and LLM pricing agents can reach supracompetitive outcomes, and that those outcomes are sensitive to learning design, prompts, information, model choice, and oversight. Three issues remain open for the setting studied here:

1. **A stable high price does not reveal the mechanism.** It may reflect a reward–punishment strategy, but it may also reflect early lock-in with little exploration.
2. **Language is observable but not necessarily faithful.** Public explanations, self-reported competitor use, private notes, and executed prices can disagree.
3. **Most comparisons use stationary markets or separate runs.** They tell us less about whether an already stabilized LLM agent detects and responds to gradual demand change within the same interaction.

Our current question is therefore:

> When demand expands gradually, does an LLM pricing agent revise a stabilized pricing rule in response to realized market outcomes, or continue a locally satisfactory rule with only small adjustments?

## Experiments completed so far

### Static-market benchmark

We first evaluate behavior under constant demand and three oversight modes: passive monitoring, revision after a flagged proposal, and deterministic veto. The design contains 3 seeds × 3 modes × 100 rounds. The table reports mean executed price in rounds 81–100.

| Seed | Passive | Revision | Veto |
|---:|---:|---:|---:|
| 0 | 1.975 | 1.500 | 1.490 |
| 1 | 1.975 | 1.595 | 1.615 |
| 2 | 2.000 | 1.475 | 1.325 |
| **Mean** | **1.983** | **1.523** | **1.477** |

Passive runs reached prices close to 2.00 in all three seeds. More importantly for the present study, the agents barely explored: 99.2% of adjacent passive decisions repeated the previous price, 99.8% changed it by no more than 0.05, and the next price stayed unchanged after non-declining profit in 99.8% of applicable decisions. Only 0.7% of private notes used explicit explore/test language.

These runs reproduce the broad market, prompt, memory, and oversight structure used in *Oversight Is Not Compliance*, but they are not an exact replication. The archived implementation used the fixed symmetric Nash price 1.473 in regulatory calculations and continued every run to 100 rounds; the full demand parameters also had to be calibrated because they were not reported. These differences are documented in [the experiment report](docs/preliminary-experiments.md).

### Response-schema diagnostic

To test whether the result depended on the LLM scaffold, we repeated the same 9 cells with the price field placed after the justification and notes. Under passive oversight, price-last reduced the late-round mean from 1.983 to 1.740, with paired differences of −0.025, −0.555, and −0.150 across the three seeds. Revision and veto showed no consistent direction.

Seventeen of the 18 total static-market runs nevertheless reached exact price fixed points, and one entered a period-two pattern. This diagnostic suggests that the scaffold can select a different stable path, while rapid convergence and weak exploration remain common.

### Mature and expanding demand

The main extension compares a mature market with an expanding market. It keeps the same two-agent market, price range, cost, base demand, paper-order response fields, private notes, and passive oversight. Two industry descriptions—consumer retail and B2B software—are included to check whether the qualitative context changes the result.

In the mature condition, product attractiveness is constant. In the expanding condition, common product attractiveness rises gradually during rounds 1–40 and then plateaus. Agents are told whether the market is mature or expanding, but they are not shown the numerical demand equation, growth rate, current demand shift, equilibrium price, or counterfactual profit. They must infer the magnitude of change from their realized quantity and profit.

The completed design contains 2 market conditions × 2 industry descriptions × 3 seeds. All 12 runs stopped at round 60 after satisfying the convergence check.

| Market | Mean price, rounds 41–60 | Round-specific price index | Unchanged next price | Change ≤ 0.05 | Stay after profit did not fall |
|---|---:|---:|---:|---:|---:|
| Mature | 2.038 | 1.249 | 96.2% | 100.0% | 99.1% |
| Expanding | 2.088 | 1.058 | 90.5% | 98.9% | 95.8% |

Raw prices were only 0.05 higher under expansion in both industry descriptions. The round-specific index was lower under expansion because the competitive and joint-profit benchmarks increased more than the agents' prices. Even when quantities and profits changed, more than 90% of adjacent decisions repeated the previous price and almost every adjustment was no larger than 0.05.

The current evidence therefore supports a limited behavioral finding: this model often keeps a price that is producing non-declining profit and makes too little endogenous variation to learn much about nearby alternatives. It does **not** yet establish genuine collusion, prove that private notes caused the behavior, or estimate a general treatment effect from three seeds.

## API and implementation

The completed experiments call the **Google Gemini Developer API** with `gemini-3.5-flash-lite` and schema-constrained JSON. The static benchmark used the archived Interactions interface; the mature/expanding experiment uses asynchronous `GenerateContent`. Both use `store=false`. API keys, `.env` files, provider logs, and unchecked raw trajectories are excluded from the repository.

Key files:

- [Experiment designs and results](docs/preliminary-experiments.md)
- [Related work](docs/literature-review.md)
- [Structured reading list](docs/reading-list.md)
- [Reproduction commands](experiments/README.md)
- [Static-market runner](src/pricing_experiment/run_paper_baseline.py)
- [Dynamic-market runner](src/pricing_experiment/run_live.py)
- [Static-market results](results/paper-baseline-summary.csv)
- [Mature/expanding results](results/hidden-demand-summary.csv)

## Current work

The present free-choice loop produces many zero or very small price changes. The next method will introduce more informative price variation so that adaptation can be tested rather than inferred from an almost fixed trajectory. The design is still being finalized and is not reported here as a completed experiment.

## Contribution and limitations — TBD

The final contribution claim and complete limitations section remain open. Confirmed limitations currently include one model family, three seeds per comparison, a stylized two-firm market, calibrated demand parameters, and known differences between the completed static benchmark and the fully aligned oversight protocol.
