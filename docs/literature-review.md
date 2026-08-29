# Literature Review

## Scope and framing

This review frames pricing as a multi-agent AI problem. An agent's action changes the observations, rewards, and future policy updates of other agents, so the environment is not stationary from any individual learner's perspective. The economic model supplies controlled incentives and measurable equilibria; the research target is the behavior of interacting adaptive systems.

The review is organized by conceptual transitions rather than chronology.

## 1. From algorithmic pricing to multi-agent learning

Automated pricing is shifting from static rules toward agents that observe market outcomes and repeatedly update decisions. Once multiple adaptive agents interact, pricing is no longer well described as independent stochastic optimization. Each learner changes the effective objective and data-generating process faced by the others.

[Bichler, Durmann, and Oberlechner (2025)](https://doi.org/10.1007/s12599-025-00965-z) place the topic at the intersection of online learning, learning in games, and electronic market design. Their review emphasizes that no comprehensive theory currently predicts when interacting algorithms converge to competitive equilibria, supracompetitive outcomes, cycles, or other dynamics. [Abada et al. (2025)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4891033) similarly argue that results should be evaluated by whether they establish robust, persistent risks relevant beyond a single simulation design.

This motivates an agent-centric framing:

```text
market outcome is an emergent property of agent × environment interaction
```

## 2. Classical reinforcement learning and supracompetitive pricing

[Calvano et al. (2020)](https://doi.org/10.1257/aer.20190623) provide the foundational experimental result. Independent Q-learning agents in a repeated oligopoly model learned prices above the one-shot Nash equilibrium without explicit communication. Their off-equilibrium responses resembled a finite punishment phase followed by a gradual return to cooperation. The result also survived several changes in cost, demand, player count, and uncertainty.

The canonical empirical pattern became:

```text
repeated interaction
→ supracompetitive prices
→ deviation response
→ punishment and recovery
```

This work established the phenomenon, but it did not settle how to identify the mechanism.

## 3. Genuine versus spurious collusion

High prices are an outcome, not a mechanism. [Calvano et al. (2023)](https://doi.org/10.1016/j.ijindorg.2023.102973) distinguish **genuine collusion**, in which supracompetitive outcomes are sustained by strategic reward–punishment behavior, from **spurious collusion**, in which a learning process settles on inefficiently high prices even where collusion is impossible or not an equilibrium.

Several papers sharpen this identification problem:

- [Asker, Fershtman, and Pakes (2024)](https://doi.org/10.1111/jems.12516) show that pricing outcomes depend on the learning protocol and on what counterfactual feedback the agent receives.
- [Banchio and Mantegazza (2022/working paper)](https://arxiv.org/abs/2202.05946) identify **spontaneous coupling**, an endogenous statistical linkage between learners' estimates that can support coordinated outcomes.
- [Epivent and Lambin (2024)](https://doi.org/10.1016/j.econlet.2024.111661) show that apparent price wars can follow upward as well as downward deviations, weakening a simple punishment interpretation.
- [Arunachaleswaran et al. (2025)](https://doi.org/10.4230/LIPIcs.ITCS.2025.10) show that near-monopoly outcomes can arise in algorithm space without explicitly encoded threats, suggesting that threat-based definitions may be too narrow.

The methodological conclusion is central to this project:

> Supracompetitive pricing alone is insufficient to identify the strategic policy that generated it.

Accordingly, the project will pair price-level metrics with controlled perturbations, response curves, recovery dynamics, and memory interventions.

## 4. From trained RL policies to LLM pricing agents

LLM agents enter the market with pretrained general-purpose policies and can adapt during deployment through instructions, history, tool use, and natural-language memory. This differs from classical experiments in which a numerical policy is acquired over very long training horizons.

[Fish, Gonczarowski, and Shorrer (2024; revised 2026)](https://arxiv.org/abs/2404.00806) show that LLM-based pricing agents can rapidly reach supracompetitive prices in repeated oligopoly environments without explicit communication. Small prompt changes materially affect the outcomes, and off-path analysis implicates concern about price wars. The result makes prompt and scaffold design part of the strategic environment.

[Luo, Schoepflin, and Wang (2026)](https://arxiv.org/abs/2602.17203) move the discussion toward **test-time collusion**. Their meta-game combines a pretrained initial policy with an in-game adaptation rule and evaluates strategies under finite interaction horizons, strategic diversity, and asymmetric settings. This reframes the central question from whether an algorithm can eventually learn a collusive equilibrium to how an already capable agent adapts during deployment.

[EconEvals (Fish et al., 2025)](https://arxiv.org/abs/2503.18825) provides a broader evaluation context: LLM agents can be studied as decision-makers that must explore and learn unknown environments over multiple turns, not merely as text models answering static questions.

## 5. Robustness beyond symmetric stationary benchmarks

Early symmetric benchmarks isolate behavior cleanly, but they can make coordination easier than realistic deployment conditions do. Recent work therefore varies agent composition, information access, market structure, and interaction protocols.

[Keppo et al. (2026)](https://arxiv.org/abs/2603.20281) find that LLM-agent collusion is fragile to several realistic forms of heterogeneity. Differences in patience and data access reduce price lift; more competitors and LLM–Q-learning interaction can break coordination. Model-size heterogeneity, however, can create leader–follower dynamics rather than eliminate collusion.

[Agrawal et al. (2025)](https://arxiv.org/abs/2507.01413) extend the setting to continuous double auctions, showing sensitivity to communication, model choice, oversight, and environmental pressure. [Collina, Arunachaleswaran, and Jagadeesan (2025)](https://arxiv.org/abs/2511.21935) analyze mixed human–AI pricing ecosystems and show theoretically that even limited defection by human/no-regret actors can destabilize high-price outcomes.

These papers support a stronger synthesis than a list of parameters:

```text
collusive behavior is conditional on
model × scaffold × information × opponents × environment × history
```

However, most robustness work varies conditions across agents or independent runs. Temporal heterogeneity—how the same agent carries strategic state from one regime into another—remains a distinct target.

## 6. Reasoning, persistent memory, and oversight

LLM agents expose natural-language channels that classical pricing algorithms do not. Public explanations, self-reports, and private notes can be compared with behavior. Persistent notes are especially important because they are not only reports: when fed back into later rounds, they are part of the agent's effective state.

The core project paper, ***Oversight Is Not Compliance*** (citation metadata TBD), separates executed prices, public justifications, self-disclosures, and persistent private notes in a repeated pricing environment. Its central observation is that these channels can diverge: compliance-oriented public language need not imply a compliant pricing policy; private notes may track competitors or oversight thresholds that public explanations omit; and self-reported competitor influence can be unreliable. The paper treats persistent notes as a mechanism for maintaining strategy across rounds while acknowledging that textual strategy labels do not directly reveal an internal causal mechanism.

This creates the project's most natural extension:

```text
prior work: notes as diagnostic evidence
this project: notes as a manipulable candidate state variable
```

Rather than infer causality from note content, the project can reset, sanitize, or edit memory and measure downstream behavior. A null intervention is informative: it may indicate that the text is epiphenomenal or that strategic state is carried elsewhere in the interaction history.

The wider multi-agent context strengthens the importance of this question. Anthropic's [*Patterns and problems in emerging multiagent systems* (2026)](https://www.anthropic.com/research/multiagent-systems) reports coordination failures, conformity, collusion, epistemic failures, and conflict escalation in groups of agents. It argues that individually capable or aligned agents need not compose into well-behaved systems. Pricing offers a compact, measurable environment in which to study the same composition problem.

## 7. Open research gap

The literature establishes that:

1. adaptive pricing algorithms and LLM agents can generate supracompetitive outcomes;
2. price level alone does not distinguish genuine strategic coordination from other learning dynamics;
3. LLM-agent behavior depends on prompt, model, information, opponent, and market structure;
4. test-time adaptation is a practical evaluation target; and
5. natural-language reasoning and memory may be only weakly coupled to behavior.

What remains less understood is how an LLM pricing agent adapts when the environment itself changes over time, and whether accumulated strategic state causes path dependence after the transition.

The clean counterfactual is not simply growth versus mature markets. It is:

```text
same final market
+ same model and task
+ different prior regime or retained memory
→ compare post-transition policies
```

This distinguishes effects of current fundamentals from effects of history and memory.

## 8. Proposed introduction structure

A paper introduction can be built in five paragraphs:

1. **Autonomous pricing as multi-agent learning:** adaptive agents alter one another's environment and can create unprogrammed system-level behavior.
2. **Classical evidence and identification dispute:** RL agents reach high prices, but high prices do not by themselves establish genuine collusion.
3. **LLM and test-time shift:** pretrained agents adapt through prompts, reasoning, history, and memory during finite deployment interactions.
4. **Robustness and oversight:** behavior depends on the interaction setting, while observable reasoning may not faithfully reveal policy.
5. **Open problem and project:** study adaptation, memory, and strategic response under controlled regime transitions; final contribution statement TBD.

## 9. Contribution and limitations placeholders

### Contribution — TBD

Do not finalize this section until pilot results identify a stable phenomenon. Candidate claims are listed in the [research agenda](research-agenda.md).

### Limitations — TBD

At minimum, the final paper should discuss external validity of stylized pricing games, model/version drift, stochasticity, scaffold dependence, construct validity of collusion metrics, and the distinction between explicit textual memory and latent model state.
