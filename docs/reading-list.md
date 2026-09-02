# Structured Reading List

The list follows the argument of the study: repeated-pricing foundations, identification of collusion, LLM-specific behavior and information channels, and finally robustness and changing markets.

## 1. Repeated pricing and algorithmic collusion

| Priority | Work | Role in this project |
|---|---|---|
| Core | [Calvano et al. (2020), *Artificial Intelligence, Algorithmic Pricing, and Collusion*](https://doi.org/10.1257/aer.20190623) | Establishes the repeated differentiated-products setting and supracompetitive Q-learning result |
| Survey | [Bichler, Durmann, and Oberlechner (2025), *Algorithmic Pricing and Algorithmic Collusion*](https://doi.org/10.1007/s12599-025-00965-z) | Maps the wider learning-in-games literature and experimental choices |

## 2. Genuine versus spurious collusion

| Priority | Work | Role in this project |
|---|---|---|
| Core | [Calvano et al. (2023), *Algorithmic Collusion: Genuine or Spurious?*](https://doi.org/10.1016/j.ijindorg.2023.102973) | Explains why high prices do not identify a collusive strategy |
| Core | [Asker, Fershtman, and Pakes (2024), *The Impact of AI Design on Pricing*](https://doi.org/10.1111/jems.12516) | Shows that algorithm design and feedback alter pricing outcomes |
| Core | [Banchio and Mantegazza, *Artificial Intelligence and Spontaneous Collusion*](https://arxiv.org/abs/2202.05946) | Provides statistical coupling as an alternative mechanism |
| Supporting | [Epivent and Lambin (2024), *On Algorithmic Collusion and Reward–Punishment Schemes*](https://doi.org/10.1016/j.econlet.2024.111661) | Warns against treating punishment-looking paths as conclusive evidence |

## 3. LLM pricing, test-time adaptation, and oversight

| Priority | Work | Role in this project | Status |
|---|---|---|---|
| Core | [Fish, Gonczarowski, and Shorrer, *Algorithmic Collusion by Large Language Models*](https://arxiv.org/abs/2404.00806) | Establishes short-horizon LLM pricing behavior, prompt sensitivity, and off-path testing | Available |
| Core | [Luo, Schoepflin, and Wang, *Algorithmic Collusion at Test Time*](https://arxiv.org/abs/2602.17203) | Separates pretrained policy from adaptation during deployment | Available |
| Core | *Oversight Is Not Compliance* | Studies prices, public justifications, self-disclosure, persistent private notes, and three oversight modes | Public citation metadata TBD |
| Supporting | [Fish et al., *EconEvals*](https://arxiv.org/abs/2503.18825) | Frames LLM agents as multi-turn decision-makers learning an unknown environment | Available |

## 4. Robustness and changing markets

| Priority | Work | Role in this project |
|---|---|---|
| Core | [*Algorithmic Collusion under Observed Demand Shocks*](https://arxiv.org/abs/2502.15084) | Connects the dynamic-demand design to nonstationary algorithmic pricing |
| Core | [Keppo et al., *On the Fragility of AI Agent Collusion*](https://arxiv.org/abs/2603.20281) | Tests information, patience, agent count, and algorithm heterogeneity |
| Supporting | [Agrawal et al., *Evaluating LLM Agent Collusion in Double Auctions*](https://arxiv.org/abs/2507.01413) | Tests robustness in a different market mechanism |
| Supporting | [Collina, Arunachaleswaran, and Jagadeesan, *Breaking Algorithmic Collusion in Human-AI Ecosystems*](https://arxiv.org/abs/2511.21935) | Extends the question to mixed human–AI settings |
| Background | [Anthropic, *Patterns and Problems in Emerging Multiagent Systems*](https://www.anthropic.com/research/multiagent-systems) | Places pricing-agent coordination in broader multi-agent safety work |

## Recommended reading order

1. Calvano et al. (2020), followed by the 2023 genuine/spurious paper.
2. Asker et al., Banchio and Mantegazza, and Epivent and Lambin for alternative explanations.
3. Fish et al. on LLM pricing and Luo et al. on test-time adaptation.
4. *Oversight Is Not Compliance* for public/private information channels and intervention design.
5. Demand shocks and robustness papers before fixing the final contribution claim.
