# Structured Reading List

This list is organized by what each paper contributes to the research argument. “Core” means essential to the first full draft; it does not imply agreement with the paper's interpretation.

## A. Project anchor: reasoning, memory, and oversight

| Priority | Work | Role in this project | Status |
|---|---|---|---|
| Core | *Oversight Is Not Compliance* | Separates executed behavior, public explanations, self-disclosure, and persistent private notes; motivates causal memory intervention | Citation metadata/link TBD |
| Supporting | [Patterns and problems in emerging multiagent systems (Anthropic, 2026)](https://www.anthropic.com/research/multiagent-systems) | Broader CS/AI motivation: individually capable agents can produce conformity, collusion, epistemic failure, and conflict at system level | Read for framing |

## B. Foundations: classical algorithmic collusion

| Priority | Work | Main use |
|---|---|---|
| Core | [Calvano et al. (2020), *Artificial Intelligence, Algorithmic Pricing, and Collusion*](https://doi.org/10.1257/aer.20190623) | Foundational Q-learning result; punishment and gradual recovery; robustness baseline |
| Core | [Bichler, Durmann, and Oberlechner (2025), *Algorithmic Pricing and Algorithmic Collusion*](https://doi.org/10.1007/s12599-025-00965-z) | Frames pricing as online learning in games and maps open CS/market-design questions |
| Core | [Abada et al. (2025), *Algorithmic Collusion: Where Are We and Where Should We Be Going?*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4891033) | Critical review and criteria for deciding which simulation findings matter in actual markets |

## C. Identification: genuine, spurious, and alternative mechanisms

| Priority | Work | Main use |
|---|---|---|
| Core | [Calvano et al. (2023), *Algorithmic Collusion: Genuine or Spurious?*](https://doi.org/10.1016/j.ijindorg.2023.102973) | Establishes that high prices can arise without genuine collusive strategy |
| Core | [Epivent and Lambin (2024), *On Algorithmic Collusion and Reward–Punishment Schemes*](https://doi.org/10.1016/j.econlet.2024.111661) | Challenges simple punishment interpretation using upward and downward deviations |
| Core | [Asker, Fershtman, and Pakes (2024), *The Impact of AI Design on Pricing*](https://doi.org/10.1111/jems.12516) | Shows learning-protocol design changes pricing outcomes |
| Core | [Banchio and Mantegazza, *Artificial Intelligence and Spontaneous Collusion*](https://arxiv.org/abs/2202.05946) | Provides spontaneous coupling as an alternative coordination mechanism |
| Supporting | [Arunachaleswaran et al. (2025), *Algorithmic Collusion Without Threats*](https://doi.org/10.4230/LIPIcs.ITCS.2025.10) | Shows why explicit threats may not be necessary for high-price equilibria in algorithm space |

## D. LLM pricing agents and test-time adaptation

| Priority | Work | Main use |
|---|---|---|
| Core | [Fish, Gonczarowski, and Shorrer (2024; rev. 2026), *Algorithmic Collusion by Large Language Models*](https://arxiv.org/abs/2404.00806) | Foundational LLM pricing result; prompt sensitivity and off-path behavioral analysis |
| Core | [Luo, Schoepflin, and Wang (AAMAS 2026), *Algorithmic Collusion at Test Time*](https://arxiv.org/abs/2602.17203) | Reframes risk around pretrained policy plus finite in-game adaptation |
| Supporting | [Fish et al. (2025), *EconEvals*](https://arxiv.org/abs/2503.18825) | Evaluation methods for LLM agents learning and strategizing in unknown multi-turn environments |

## E. Robustness and realistic multi-agent structure

| Priority | Work | Main use |
|---|---|---|
| Core | [Keppo et al. (2026), *On the Fragility of AI Agent Collusion*](https://arxiv.org/abs/2603.20281) | Heterogeneity in patience, data, agent count, and algorithm type; leader–follower exception |
| Supporting | [Agrawal et al. (2025), *Evaluating LLM Agent Collusion in Double Auctions*](https://arxiv.org/abs/2507.01413) | Moves beyond repeated posted pricing; tests communication, model, oversight, and pressure |
| Supporting | [Collina, Arunachaleswaran, and Jagadeesan (2025), *Breaking Algorithmic Collusion in Human-AI Ecosystems*](https://arxiv.org/abs/2511.21935) | Mixed human–AI settings and fragility to defections/no-regret behavior |

## Recommended reading order

1. Calvano et al. (2020)
2. Calvano et al. (2023) and Epivent & Lambin (2024)
3. Asker et al. and Banchio & Mantegazza
4. Fish et al. (LLM collusion)
5. Luo et al. (test time)
6. Keppo et al. (fragility)
7. *Oversight Is Not Compliance*
8. Anthropic multi-agent report and supporting realistic-setting papers
9. Return to Abada et al. and Bichler et al. to audit the final research claim

## Reading-note template

For each paper, record:

- **Agent:** algorithm/model, training state, prompt/scaffold.
- **Environment:** game, information, stationarity, number and type of agents.
- **Memory:** state representation, context, notes, update mechanism.
- **Outcome:** price/profit/welfare and strategic-response measures.
- **Identification:** what evidence supports “collusion” rather than high prices?
- **Intervention:** what is manipulated, and what causal claim is justified?
- **Robustness:** seeds, hyperparameters, models, asymmetry, and horizon.
- **Transfer to this project:** design choice to adopt, avoid, or test.
