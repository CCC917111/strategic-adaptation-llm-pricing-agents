# Related Work

This review asks one narrow question: what does prior work tell us about interpreting the prices produced by adaptive pricing agents, and what is still unknown when an LLM agent faces hidden demand change during deployment?

## 1. High prices can emerge, but the mechanism is disputed

[Calvano et al. (2020)](https://doi.org/10.1257/aer.20190623) showed that independent Q-learning pricing agents can reach prices above the one-shot Nash equilibrium without communicating. After an exogenous deviation, their learned policies often cut prices and later return to the previous level. This supplied influential evidence that repeated interaction between learning algorithms can produce behavior resembling tacit collusion.

Later work showed why the price level and a punishment-looking path are not sufficient evidence of collusion. [Calvano et al. (2023)](https://doi.org/10.1016/j.ijindorg.2023.102973) distinguish genuine reward–punishment strategies from spurious high-price outcomes created by the learning process. [Asker, Fershtman, and Pakes (2024)](https://doi.org/10.1111/jems.12516) show that the information and feedback available to a learning algorithm can materially change its pricing outcome. [Banchio and Mantegazza](https://arxiv.org/abs/2202.05946) identify statistical coupling between independently learning agents as another route to coordinated behavior. [Epivent and Lambin (2024)](https://doi.org/10.1016/j.econlet.2024.111661) further show that responses interpreted as punishment may also follow upward deviations.

The conclusion relevant to this project is straightforward: a stable price above a competitive benchmark is an observation, not a mechanism. Identifying collusion requires evidence about how an agent responds to deviations and what sustains the outcome.

## 2. LLM pricing agents make short-run adaptation part of the problem

LLM pricing agents differ from Q-learning agents because they begin with a pretrained policy and make decisions from instructions, natural-language context, interaction history, and sometimes persistent notes. They need not learn a pricing table through millions of numerical updates.

[Fish, Gonczarowski, and Shorrer](https://arxiv.org/abs/2404.00806) find that LLM pricing agents can reach supracompetitive prices within relatively short repeated interactions. Their results also show that prompt wording matters and use off-path tests to examine whether agents anticipate price wars. This shifts part of the research problem from long-run learning dynamics to deployment-time behavior: what information is in the prompt, what history is retained, and how the agent reacts within a finite run.

[Algorithmic Collusion at Test Time](https://arxiv.org/abs/2602.17203) makes this distinction explicit by studying the combination of a pretrained policy and an in-game adaptation rule. Its focus on finite horizons, strategic diversity, and asymmetric settings is directly relevant to experiments in which an LLM must infer an environment while acting in it.

For the present study, the implication is that the prompt and memory loop are part of the experimental treatment. A high or stable price may reflect strategic interaction, but it may also reflect an early heuristic that the LLM keeps reusing because observed profit has not fallen.

## 3. Robustness depends on the interaction setting

Recent research tests whether high-price LLM outcomes survive changes that make the environment less symmetric or less controlled. [Keppo et al.](https://arxiv.org/abs/2603.20281) find that differences in patience and data access, additional competitors, and interaction with a different algorithm can weaken coordination; some model-size differences instead produce leader–follower behavior. [Agrawal et al.](https://arxiv.org/abs/2507.01413) study LLM agents in continuous double auctions and report sensitivity to model choice, communication, oversight, and environmental pressure.

This work changes the appropriate empirical standard. A result from one model, prompt, market, or opponent composition should not be treated as a general property of LLM agents. The environment must be varied through controlled comparisons, and run-to-run variation must be reported.

Studies of demand shocks in reinforcement-learning pricing environments, including [Algorithmic Collusion under Observed Demand Shocks](https://arxiv.org/abs/2502.15084), show that nonstationary demand is already an important part of the broader algorithmic-pricing literature. They do not remove the LLM-specific question considered here, because an LLM's pretrained policy, language context, and persistent scratchpad create a different adaptation process.

## 4. Reasoning, memory, and oversight are evidence channels, not ground truth

LLM agents produce public explanations, structured self-reports, and private notes in addition to actions. These outputs are useful because they can be compared with later behavior, but they should not automatically be treated as faithful descriptions of the policy that generated a price.

The project's core manuscript, *Oversight Is Not Compliance* (public citation metadata TBD), separates executed prices, public justifications, competitor-information disclosures, and persistent private notes. It reports that compliant language and self-disclosure can diverge from pricing behavior. Persistent notes may help an agent carry a plan across rounds, but reading those notes does not by itself show that the text caused the subsequent action.

This distinction matters for the current results. The frequent “maintain” language in the saved notes is consistent with price inertia, but it is only supporting evidence. The primary evidence remains the executed price path and the agent's response to changing realized outcomes.

## 5. Position of the current study

Prior work establishes four points: adaptive pricing agents can produce high prices; high prices do not identify a collusive mechanism; LLM behavior is sensitive to prompts and finite interaction history; and robustness must be tested across environments and runs.

The current experiment applies those lessons to a hidden numerical path of gradual demand expansion. Mature and expanding markets use the same model, base economic parameters, observation structure, and oversight mode. The expanding treatment changes common product attractiveness over rounds 1–40. Agents receive a qualitative market-phase description but are not told the demand equation, rate, or current demand level. They must infer the magnitude of change from realized quantity and profit.

The analysis therefore asks two concrete questions:

1. Do raw prices rise when hidden demand expands?
2. Do prices keep pace with the round-specific competitive and joint-profit benchmarks, or remain anchored near an early value?

This design does not claim that any high price is collusive. Its immediate purpose is to measure adaptation under hidden nonstationarity and to determine whether the strong inertia seen in the current runs requires a different experimental method. The final contribution statement remains TBD.

## Writing principle used in this review

The sections are organized by claims and disagreements, not by a sequence of paper summaries. Each section ends with the implication for the present experiment. The paper-specific details and reading priorities are kept separately in the [structured reading list](reading-list.md).
