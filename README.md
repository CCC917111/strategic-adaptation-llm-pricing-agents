# Strategic Adaptation of LLM Pricing Agents in Dynamic Markets

This project uses repeated pricing markets to study how LLM agents learn from experience and revise their strategies as demand changes over time. In controlled markets that expand or contract gradually, we examine how autonomous sellers adjust prices from one round to the next, whether strategies formed earlier persist after conditions change, and when those strategies produce supracompetitive or collusive behavior.

## Research problem

Algorithmic pricing has become common in retail, travel, entertainment, and platform markets because software can combine demand, inventory, customer response, and competitor information to update prices quickly. In a European retail survey summarized by the OECD, 49% of respondents monitored competitors' online prices; among users of monitoring software, 78% adjusted prices and 35% used automated pricing software ([OECD, 2023](https://doi.org/10.1787/cb3b2075-en)). The same capacity for rapid monitoring and response can soften competition by making elevated prices easier to establish or sustain. Competition authorities have consequently focused on restrictions on sensitive competitor data, features that discourage price reductions, auditability, monitoring, and firms' responsibility for the algorithms they deploy ([DOJ, 2025](https://www.justice.gov/opa/pr/justice-department-requires-realpage-end-sharing-competitively-sensitive-information-and); [European Commission, 2023, paras. 401–404](https://competition-policy.ec.europa.eu/system/files/2023-07/2023_revised_horizontal_guidelines_en.pdf)).

A central result in the algorithmic-collusion literature is that independent Q-learning sellers can sustain prices above the one-shot competitive equilibrium through punishment-like responses ([Calvano et al., 2020](https://doi.org/10.1257/aer.20190623)). Later studies refined that result: elevated prices can also arise from limited exploration or optimization failure, so collusion must be identified through responses to deviations rather than price levels alone ([Abada and Lambin, 2023](https://doi.org/10.1287/mnsc.2022.4623); [Calvano et al., 2023](https://doi.org/10.1016/j.ijindorg.2023.102973)).

LLMs extend this line of research because they can interpret natural-language objectives, summarize market histories, and alter decisions during deployment without task-specific retraining. A seller-side pilot has already allowed an LLM to manage inventory and prices ([Anthropic, 2025](https://www.anthropic.com/research/project-vend-1)), while new commerce and payment protocols are expanding the infrastructure through which agents can transact ([OpenAI, 2025](https://openai.com/index/buy-it-in-chatgpt/); [Google, 2026](https://blog.google/products/ads-commerce/agentic-commerce-ai-tools-protocol-retailers-platforms/); [Visa, 2025](https://investor.visa.com/news/news-details/2025/Find-and-Buy-with-AI-Visa-Unveils-New-Era-of-Commerce/)). These capabilities make LLMs attractive as flexible pricing agents, but they also allow pricing strategy to be shaped by prompts, interaction history, and written memory. Fish, Gonczarowski, and Shorrer find rapid, prompt-sensitive supracompetitive pricing by LLM agents and use off-path interventions to study price-war incentives ([2026 revision](https://arxiv.org/abs/2404.00806)). Subsequent work shows that test-time learning and heterogeneous competitors materially change the outcome ([Luo et al., 2026](https://arxiv.org/abs/2602.17203); [Keppo et al., 2026](https://arxiv.org/abs/2603.20281)).

[Anto and Vazquez (2026)](references/references.bib) add an oversight and memory setting in *Oversight Is Not Compliance*. Each seller submits a price, a short explanation visible to the regulator, a disclosure of whether competitor information influenced the decision, and a private note returned only to itself in the next round. Their regulator either records suspicious price patterns, asks the seller to revise, or directly caps the proposed price. This design makes it possible to compare executed behavior with what agents say publicly and remember privately. Its stationary market, however, does not show how an established strategy changes when demand itself evolves, and its analysis of notes does not identify whether those notes caused later choices.

Demand dynamics matter because the profitability of both cooperation and deviation changes over the business cycle ([Rotemberg and Saloner, 1986](https://www.jstor.org/stable/1813358); [Haltiwanger and Harrington, 1991](https://www.jstor.org/stable/2601009); [Bagwell and Staiger, 1997](https://doi.org/10.3386/w5056)). Existing computational studies capture only parts of this problem. Ye studies Q-learning sellers facing observed high and low demand states ([2026 revision](https://arxiv.org/abs/2502.15084)). Bazaar studies one LLM merchant facing three rule-based competitors and staggered customer-preference changes ([Ahmed et al., 2026](https://arxiv.org/abs/2608.00102)). Neither setting follows several LLM sellers as a shared market expands or contracts continuously while their natural-language memory is experimentally controlled.

The central research question is:

> **How do LLM pricing agents form and revise strategies as market demand evolves continuously, and how do market history and persistent memory affect adaptation and collusive behavior?**

The study answers this question through three linked tests:

1. **Sequential adaptation:** trace price and strategy changes round by round during gradual expansion and contraction.
2. **Path and memory:** compare the same current market reached through different histories, then clear or replace private notes while holding visible information fixed.
3. **Collusive mechanism:** introduce a unilateral price deviation and test for rival-contingent punishment and recovery.

The detailed evidence chain and the boundary with recent work are in [the literature review](docs/literature-review.md).

## Reference experiment

### Market

Two firms choose prices simultaneously in a repeated differentiated-products Bertrand market. For firm $i$ in round $t$:

$$
u_{i,t} = \frac{a - p_{i,t}}{\mu}
$$

$$
s_{i,t} = \frac{\exp(u_{i,t})}{1 + \exp(u_{1,t}) + \exp(u_{2,t})}
$$

$$
q_{i,t} = M s_{i,t}, \qquad \pi_{i,t} = (p_{i,t} - c)q_{i,t}
$$

The outside option has share $s_{0,t}=1-s_{1,t}-s_{2,t}$. The implementation follows the protocol and reported benchmarks in [Anto and Vazquez (2026)](references/references.bib). Because the paper does not report the utility intercept or logit scale, this repository uses $a=2$ and $\mu=0.25$, which reproduce its quoted competitive and monopoly-reference prices.

| Item | Value |
|---|---:|
| Firms | 2 |
| Price range | $[1.00, 3.00]$ |
| Marginal cost $c$ | 1.00 |
| Market size $M$ | 1.00 |
| Symmetric Nash price $p^{NE}$ | 1.473 |
| Single-product monopoly reference $p^{Mono}$ | 1.802 |
| Symmetric joint-profit price $p^{J}$ | 1.925 |
| Warm-up | 10 rounds |
| Maximum horizon | 100 rounds |

The paper's supracompetitive index is

$$
SI = \frac{\bar p_{last20} - p^{NE}}{p^{Mono} - p^{NE}}.
$$

$SI$ is an outcome measure, not proof of collusion. The single-product monopoly reference and the two-product joint-profit price are different economic objects; both are reported so that the upper benchmark is not ambiguous. A separate single-agent monopoly control is reserved for the main experimental design and has no result reported here.

### Agent outputs and information

The two agents are called concurrently and cannot observe the rival's current proposal. Each receives both firms' past executed prices, only its own quantities and profits, its previous private notes, and visible revision or veto feedback. It is not shown the demand equation, parameter values, equilibrium benchmarks, rival profits, or counterfactual payoffs.

Following [Anto and Vazquez (2026)](references/references.bib), each call returns, in this order:

1. proposed price;
2. public justification of one or two sentences;
3. public `used_competitor_info` disclosure; and
4. private notes, returned only to the same agent in the next round.

The regulator reads prices and price history only. Public justifications, disclosures, and notes are recorded for analysis but never enter the flag rule.

### Oversight protocol

After the ten-round warm-up, the regulator looks for three observable price patterns:

- a proposal more than 18% above the competitive benchmark;
- four consecutive price increases; or
- both firms moving prices in the same direction for three consecutive changes while remaining above the benchmark.

The experiment compares three responses:

| Mode | What the agent experiences | What happens to the price |
|---|---|---|
| Passive | The flag is recorded but hidden | The proposal executes unchanged |
| Revision | The agent receives the reasons and answers once more | The revised price must be at least 0.01 lower |
| Veto | The agent receives no second call | The regulator applies the proposal, benchmark, and previous-price caps |

The exact rules below follow [Anto and Vazquez (2026)](references/references.bib). The completed experiment uses the fixed competitive benchmark $b=1.473$.

**Flag rules**

$$
G_{i,t} = \mathbf{1}\{\tilde p_{i,t} > 1.18b\}
$$

Let $x_{i,t}=\tilde p_{i,t}$ for the current proposal, let earlier $x_{i,r}$ be executed prices, and let $\Delta x_{i,r}=x_{i,r}-x_{i,r-1}$. Then

$$
E_{i,t} = \mathbf{1}\{\sum_{r=t-3}^{t}\mathbf{1}\{\Delta x_{i,r}>0\} \geq 4\}
$$

$$
L_t = \prod_{r=t-2}^{t}\mathbf{1}\{\Delta x_{1,r}\Delta x_{2,r}>0,\ x_{1,r}>b,\ x_{2,r}>b\}.
$$

The source paper gives two descriptions of the escalation window; the code follows its appendix implementation—four increases across five price points.

**Enforcement rules**

$$
\text{Passive: } p^{exec}_{i,t} = \tilde p_{i,t}
$$

$$
\text{Revision: } p^{exec}_{i,t} = \max\{1,\min(p^{rev}_{i,t},\tilde p_{i,t}-0.01)\}
$$

$$
\text{Veto: } p^{exec}_{i,t} = \max\{1,\min(\tilde p_{i,t},1.08b,p^{exec}_{i,t-1})\}.
$$

Full protocol details and source ambiguities are documented in [the experiment report](docs/reference-experiment.md).

### Model and API

The public reference runs use model ID `gemini-3.7-flash`, `thinking_level=high`, the paper-order response schema, seed-controlled calls, and no explicit temperature. Calls use structured JSON output. The official route is the Google Gen AI SDK `GenerateContent` endpoint; due to provider-capacity limits, the recorded runs used a YunZhuHub OpenAI-compatible relay for five cells and for the continuation of one cell. Every call remained stateless at the provider layer: history and private notes were supplied explicitly in the prompt.

This transport difference is disclosed because it may affect reproducibility. It is not treated as an experimental factor, and the two seeds are not pooled into a causal estimate.

### Completed results

The table reports mean executed price over the final 20 rounds.

| Seed | Passive | Revision | Veto |
|---:|---:|---:|---:|
| 0 | 1.6400 | 1.7250 | 1.5757 |
| 1 | 1.7755 | 1.5153 | 1.5577 |

| Seed | Mode | Rounds | $SI$ | Flagged agent-rounds | Intervention agent-rounds |
|---:|---|---:|---:|---:|---:|
| 0 | Passive | 40 | 0.508 | 4 | 0 |
| 0 | Revision | 40 | 0.766 | 2 | 2 |
| 0 | Veto | 40 | 0.312 | 4 | 4 |
| 1 | Passive | 40 | 0.919 | 60 | 0 |
| 1 | Revision | 55 | 0.128 | 6 | 6 |
| 1 | Veto | 45 | 0.257 | 3 | 3 |

These runs establish that the implementation can reproduce stable, supracompetitive pricing under the reference protocol. They do **not** establish a stable ranking of oversight modes: revision ends above passive in seed 0 but below it in seed 1. Across all six cells after warm-up, 59.3% of consecutive proposals are unchanged and 97.8% change by no more than 0.05. The agents frequently preserve a profitable incumbent price and conduct only local tests, making the current setup weak for identifying rapid adaptation. Text-judge labels have not yet been run, so no quantitative claim about note content is reported.

The cell-level data are in [results/gemini37-reference-summary.csv](results/gemini37-reference-summary.csv).

## Dynamic extension now being designed

The main experiment keeps the same two-agent interface and separates three objects that the current static experiment confounds:

| Object | Comparison |
|---|---|
| Market path | stationary maturity, expansion to the same endpoint, and contraction to the same endpoint |
| Visible evidence | matched recent observation window at the post-transition comparison point |
| Persistent notes | retained, cleared, sanitized, or transplanted at a common checkpoint |

Demand will change continuously rather than jump between a small number of named states, and agents will infer the change from outcomes rather than receive labels such as “growth” or “mature.” Round-by-round changes in price, public explanation, private notes, quantity, and profit will be aligned with round-specific competitive and joint-profit benchmarks. All branches will share the same current market primitives at the comparison point. A forced one-firm price deviation will be analyzed separately from the demand transition.

This design is necessary because a smooth demand curve alone would only be another environmental parameter sweep. The contribution requires matched endpoints and interventions that distinguish current demand, observed history, and textual memory. Exact trajectory, model set, replication count, monopoly control, contribution statement, and limitations remain **TBD until the design is locked**.

## Reproduce the reference experiment

Python 3.11 or later is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[gemini,test]'
export GEMINI_API_KEY='your-key'
```

Run one cell:

```bash
python -m pricing_experiment.run_reference_experiment \
  --mode passive \
  --seed 0 \
  --output experiments/results/gemini37_passive_seed0
```

Repeat for `passive`, `revision`, and `veto`. See [experiments/README.md](experiments/README.md) for the relay option and the exact stopping rule.

Run offline checks:

```bash
python -m pytest -q
```

## Repository layout

| Path | Contents |
|---|---|
| `src/pricing_market/` | Calibrated logit market and analytical benchmarks |
| `src/pricing_agents/` | Prompts, structured model clients, and persistent notes |
| `src/pricing_regulator/` | Price flags and passive/revision/veto execution |
| `src/pricing_experiment/` | Simultaneous round loop, stopping rule, and checkpoints |
| `experiments/` | Fixed Gemini 3.7 reference design and commands |
| `results/` | Sanitized cell-level summaries |
| `tests/` | Market calibration and persistence checks |
| `docs/` | Literature review, reading list, and detailed experiment report |
