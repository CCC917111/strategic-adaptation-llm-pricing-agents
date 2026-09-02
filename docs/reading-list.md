# Structured Reading List

The order mirrors the project: reference experiment first, interpretation literature second, and extensions last.

## 1. Reference experiment

| Priority | Work | Role in this project | Status |
|---|---|---|---|
| Core | *Oversight Is Not Compliance* | Supplies the two-agent market, three oversight modes, separate public/private text channels, and persistent notes used by the baseline reproduction | Public citation metadata TBD |

## 2. Interpreting the baseline result

| Priority | Work | Why it is needed |
|---|---|---|
| Core | [Calvano et al. (2020), *Artificial Intelligence, Algorithmic Pricing, and Collusion*](https://doi.org/10.1257/aer.20190623) | Establishes that independent learning agents can reach supracompetitive prices and display punishment-like paths |
| Core | [Calvano et al. (2023), *Algorithmic Collusion: Genuine or Spurious?*](https://doi.org/10.1016/j.ijindorg.2023.102973) | Explains why high prices do not by themselves identify a collusive strategy |
| Core | [Asker, Fershtman, and Pakes (2024), *The Impact of AI Design on Pricing*](https://doi.org/10.1111/jems.12516) | Shows that algorithm design and feedback alter pricing outcomes |
| Core | [Banchio and Mantegazza, *Artificial Intelligence and Spontaneous Collusion*](https://arxiv.org/abs/2202.05946) | Provides statistical coupling as an alternative mechanism |
| Supporting | [Epivent and Lambin (2024), *On Algorithmic Collusion and Reward–Punishment Schemes*](https://doi.org/10.1016/j.econlet.2024.111661) | Warns against automatically interpreting post-deviation movements as punishment |
| Survey | [Bichler, Durmann, and Oberlechner (2025), *Algorithmic Pricing and Algorithmic Collusion*](https://doi.org/10.1007/s12599-025-00965-z) | Maps the larger learning-in-games literature |

## 3. Why response order is a relevant extension

| Priority | Work | Why it is needed |
|---|---|---|
| Core | [Fish, Gonczarowski, and Shorrer, *Algorithmic Collusion by Large Language Models*](https://arxiv.org/abs/2404.00806) | Establishes LLM pricing behavior and prompt sensitivity |
| Core | [Luo, Schoepflin, and Wang, *Algorithmic Collusion at Test Time*](https://arxiv.org/abs/2602.17203) | Separates a pretrained initial policy from finite in-game adaptation |
| Supporting | [Fish et al., *EconEvals*](https://arxiv.org/abs/2503.18825) | Frames LLM agents as multi-turn decision-makers learning an unknown environment |

## 4. Why dynamic demand comes next

| Priority | Work | Why it is needed |
|---|---|---|
| Core | [*Algorithmic Collusion under Observed Demand Shocks*](https://arxiv.org/abs/2502.15084) | Connects the dynamic extension to prior nonstationary-demand experiments |
| Core | [Keppo et al., *On the Fragility of AI Agent Collusion*](https://arxiv.org/abs/2603.20281) | Shows sensitivity to information, patience, agent count, and algorithm type |
| Supporting | [Agrawal et al., *Evaluating LLM Agent Collusion in Double Auctions*](https://arxiv.org/abs/2507.01413) | Tests robustness in a different market mechanism |
| Supporting | [Collina, Arunachaleswaran, and Jagadeesan, *Breaking Algorithmic Collusion in Human-AI Ecosystems*](https://arxiv.org/abs/2511.21935) | Extends the question to mixed human–AI settings |
| Background | [Anthropic, *Patterns and Problems in Emerging Multiagent Systems*](https://www.anthropic.com/research/multiagent-systems) | Places pricing-agent coordination in the broader multi-agent safety context |

## Recommended reading order

1. *Oversight Is Not Compliance*.
2. Calvano et al. (2020), followed by Calvano et al. (2023).
3. Asker et al., Banchio and Mantegazza, and Epivent and Lambin.
4. Fish et al. on LLM pricing, then test-time collusion.
5. Demand shocks and robustness papers.
6. Surveys and broader multi-agent reports after the final claim is fixed.
