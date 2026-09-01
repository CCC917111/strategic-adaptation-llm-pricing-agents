# Structured Reading List

This list records what each source contributes to the current argument. The literature synthesis itself is in [Related Work](literature-review.md).

## 1. Foundations and the identification problem

| Priority | Work | Why it is needed here |
|---|---|---|
| Core | [Calvano et al. (2020), *Artificial Intelligence, Algorithmic Pricing, and Collusion*](https://doi.org/10.1257/aer.20190623) | Establishes that independent Q-learning pricing agents can reach supracompetitive prices and display punishment-like responses. |
| Core | [Calvano et al. (2023), *Algorithmic Collusion: Genuine or Spurious?*](https://doi.org/10.1016/j.ijindorg.2023.102973) | Explains why a high price does not by itself identify a collusive strategy. |
| Core | [Asker, Fershtman, and Pakes (2024), *The Impact of AI Design on Pricing*](https://doi.org/10.1111/jems.12516) | Shows that algorithm design and counterfactual feedback change pricing outcomes. |
| Core | [Banchio and Mantegazza, *Artificial Intelligence and Spontaneous Collusion*](https://arxiv.org/abs/2202.05946) | Provides statistical coupling as an alternative explanation for coordination. |
| Supporting | [Epivent and Lambin (2024), *On Algorithmic Collusion and Reward–Punishment Schemes*](https://doi.org/10.1016/j.econlet.2024.111661) | Warns against reading every post-deviation response as strategic punishment. |
| Survey | [Bichler, Durmann, and Oberlechner (2025), *Algorithmic Pricing and Algorithmic Collusion*](https://doi.org/10.1007/s12599-025-00965-z) | Maps results across online learning, games, and market design. |

## 2. LLM pricing and test-time adaptation

| Priority | Work | Why it is needed here |
|---|---|---|
| Core | [Fish, Gonczarowski, and Shorrer, *Algorithmic Collusion by Large Language Models*](https://arxiv.org/abs/2404.00806) | Establishes rapid LLM pricing outcomes, prompt sensitivity, and off-path testing. |
| Core | [Luo, Schoepflin, and Wang, *Algorithmic Collusion at Test Time*](https://arxiv.org/abs/2602.17203) | Separates pretrained policy from adaptation during a finite deployment interaction. |
| Supporting | [Fish et al., *EconEvals*](https://arxiv.org/abs/2503.18825) | Provides a broader evaluation view of LLM agents learning unknown multi-turn environments. |

## 3. Robustness and changing environments

| Priority | Work | Why it is needed here |
|---|---|---|
| Core | [Keppo et al., *On the Fragility of AI Agent Collusion*](https://arxiv.org/abs/2603.20281) | Tests heterogeneity in patience, information, number of agents, and algorithm type. |
| Core | [*Algorithmic Collusion under Observed Demand Shocks*](https://arxiv.org/abs/2502.15084) | Connects the current nonstationary-demand design to prior demand-shock work in reinforcement learning. |
| Supporting | [Agrawal et al., *Evaluating LLM Agent Collusion in Double Auctions*](https://arxiv.org/abs/2507.01413) | Tests model, communication, oversight, and environmental pressure in a different market mechanism. |
| Supporting | [Collina, Arunachaleswaran, and Jagadeesan, *Breaking Algorithmic Collusion in Human-AI Ecosystems*](https://arxiv.org/abs/2511.21935) | Studies mixed human–AI environments and the effect of defections. |

## 4. Reasoning, memory, and oversight

| Priority | Work | Why it is needed here | Status |
|---|---|---|---|
| Core | *Oversight Is Not Compliance* | Separates prices, public explanations, self-disclosure, and persistent private notes. It motivates treating text as evidence to test rather than ground truth. | Public citation metadata TBD |
| Supporting | [Anthropic, *Patterns and Problems in Emerging Multiagent Systems*](https://www.anthropic.com/research/multiagent-systems) | Places coordination and oversight failures in a wider multi-agent AI context. | Background framing |

## Recommended reading order

1. Calvano et al. (2020), followed by Calvano et al. (2023).
2. Asker et al., Banchio and Mantegazza, and Epivent and Lambin.
3. Fish et al. on LLM pricing.
4. Test-time adaptation and the robustness papers.
5. Demand shocks and *Oversight Is Not Compliance*.
6. Return to the surveys only after the study's final claim is fixed.
