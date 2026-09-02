# Related Work

The literature review follows the same progression as the experiments. It begins with the paper whose setting we implement, then explains the earlier collusion-identification debate, and finally shows why output order and dynamic demand are relevant extensions.

## 1. The study we start from: *Oversight Is Not Compliance*

*Oversight Is Not Compliance* (public citation metadata TBD) studies two LLM pricing agents under passive, revision, and veto oversight. The agents repeatedly propose prices, observe market outcomes, and carry private notes across rounds. The experiment records four separate channels: proposed and executed prices, public justifications, structured competitor-information disclosures, and private persistent notes.

The paper's main relevance is not simply that prices can be high. It shows that observable compliance language and actual pricing behavior can diverge. An agent may provide an acceptable public explanation or deny competitor influence while its pricing path and private notes tell a different story. Oversight can also alter the executed action without proving that the agent's underlying policy has changed.

Our first experiment implements this setting before changing it. This gives a concrete baseline for the later questions: whether the response schema affects pricing and whether a stabilized policy adapts when demand changes.

## 2. Why high prices are not enough to identify collusion

The interpretive problem predates LLM agents. [Calvano et al. (2020)](https://doi.org/10.1257/aer.20190623) showed that independent Q-learning pricing agents can reach prices above the one-shot Nash equilibrium without communicating. Their learned policies also displayed punishment-like responses after deviations.

Later work explains why that pattern is not conclusive. [Calvano et al. (2023)](https://doi.org/10.1016/j.ijindorg.2023.102973) distinguish genuine reward–punishment strategies from spurious high-price outcomes caused by the learning process. [Asker, Fershtman, and Pakes (2024)](https://doi.org/10.1111/jems.12516) show that the learning protocol and counterfactual feedback can materially change prices. [Banchio and Mantegazza](https://arxiv.org/abs/2202.05946) identify statistical coupling between learners as another coordination mechanism, while [Epivent and Lambin (2024)](https://doi.org/10.1016/j.econlet.2024.111661) show that punishment-looking responses can also follow upward deviations.

These papers set the interpretation rule used throughout this repository: a stable price above a competitive benchmark is an outcome to explain, not sufficient evidence of genuine collusion.

## 3. What changes when the pricing agents are LLMs

LLM agents begin with a pretrained language policy and adapt through instructions, context, history, and natural-language memory. Unlike classical Q-learning agents, they can settle on a pricing rule after only a few interactions, without learning a numerical value table over a long training period.

[Fish, Gonczarowski, and Shorrer](https://arxiv.org/abs/2404.00806) show that LLM pricing agents can reach supracompetitive prices in short repeated interactions. Their prompt variations and off-path tests also demonstrate that the scaffold is part of the experimental environment. [Algorithmic Collusion at Test Time](https://arxiv.org/abs/2602.17203) makes the deployment-time issue explicit by separating a pretrained initial policy from the adaptation rule used during a finite game.

This literature motivates our response-order extension. Moving the price field does not change economic incentives, but it changes when the action is produced relative to justification and notes. If matched runs reach different fixed points, the result shows scaffold sensitivity rather than a change in the underlying market.

## 4. Why robustness and changing environments come next

Recent work asks whether LLM pricing outcomes survive less symmetric or more realistic interaction settings. [Keppo et al.](https://arxiv.org/abs/2603.20281) find that differences in patience and information, additional competitors, and interaction with other algorithm types can weaken coordination; some model-size differences instead create leader–follower behavior. [Agrawal et al.](https://arxiv.org/abs/2507.01413) report sensitivity to model choice, communication, oversight, and environmental pressure in continuous double auctions.

Research on reinforcement-learning pricing under demand shocks, including [Algorithmic Collusion under Observed Demand Shocks](https://arxiv.org/abs/2502.15084), shows that nonstationary demand is already important in the broader algorithmic-pricing literature. The remaining LLM-specific issue is how a pretrained language agent with a prompt, full interaction history, and persistent notes infers gradual change during deployment.

Our dynamic-market experiment follows directly from the static baseline. The baseline agents converged rapidly and explored very little. Mature and expanding conditions then test whether those agents adjust when realized quantities and profits change over time.

## 5. Position of the current project

The project therefore has a narrower progression than the previous version of this review suggested:

1. reproduce the paper-based static oversight setting;
2. establish that the LLM response schema can change the stable path; and
3. test whether gradual demand expansion produces meaningful adaptation.

The current results show strong inertia in both the paper-based baseline and the dynamic extension. They do not yet identify a collusive reward–punishment mechanism or establish that persistent notes caused the behavior. The next methodological change is motivated by this repeated lack of exploration, not by a claim already established in the literature.

The paper-by-paper roles and reading priorities are listed separately in the [structured reading list](reading-list.md).
