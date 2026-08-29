# Strategic Adaptation of LLM Pricing Agents in Dynamic Markets

*Pricing behavior, persistent memory, and collusive dynamics under changing market conditions*

> **Project status:** preliminary experiments completed; the next study is being redesigned around controlled interventions. The final contribution claim and paper title remain open.

## Project overview

This project studies LLM-based pricing agents as adaptive actors in repeated multi-agent environments. The market is a controlled testbed; the primary CS/AI questions concern test-time adaptation, persistent memory, path dependence, behavioral evaluation, and the faithfulness of agent-generated reasoning.

The working abstraction is:

```text
behavior = f(model, prompt, memory, history, environment, opponents, oversight)
```

The project therefore asks more than whether an agent posts prices above a competitive baseline. It asks what policy produced those prices, how the policy changes after interventions, and whether an agent's public explanation or private persistent notes reveal—or causally shape—that policy.

## Why this problem matters

Research on algorithmic pricing began with reinforcement-learning agents that could reach supracompetitive outcomes through repeated interaction. That finding created an identification problem: high prices may reflect genuine reward–punishment strategies, but they may also result from exploration dynamics, optimization failure, or other forms of statistical coupling.

LLM agents change the problem in three ways:

1. they enter an interaction with a powerful pretrained policy rather than learning only from numerical rewards;
2. they adapt at test time through prompts, observed histories, reasoning, and persistent context; and
3. they produce natural-language artifacts that can be audited, edited, reset, or compared with behavior.

This makes repeated pricing a useful environment for studying emergent multi-agent behavior and agent state—not merely an economic application.

## Literature logic

The literature review follows a problem-driven chain:

```text
classical algorithmic collusion
        ↓
genuine vs. spurious collusion and identification
        ↓
LLM pricing agents and test-time collusion
        ↓
robustness in heterogeneous and realistic multi-agent settings
        ↓
reasoning, persistent memory, monitorability, and oversight
        ↓
open question: adaptation and path dependence under regime change
```

See the full [literature review](docs/literature-review.md), [structured reading list](docs/reading-list.md), and [preliminary experiment report](docs/preliminary-experiments.md).

## Open research gap

Existing work shows that learning algorithms and LLM agents can generate supracompetitive outcomes; that price level alone does not identify genuine collusion; that outcomes depend on agent design and interaction structure; and that an LLM's stated reasoning may be weakly coupled to its behavior.

What is less understood is how LLM pricing agents adapt when the environment changes over time, and whether strategic state accumulated in one regime changes behavior in a later, identical regime.

Most benchmark designs study a stationary market or compare freshly initialized agents across separate environments. Those designs answer whether behavior differs **across current environments**. They do not cleanly answer whether the **same current environment produces different behavior because of prior experience or retained memory**.

This project will treat that distinction as the central opening, subject to further literature verification.

## Candidate research questions

- **RQ1 — Behavioral path dependence:** Do agents facing the same final market behave differently after different market histories?
- **RQ2 — Memory mechanism:** Does carrying, resetting, sanitizing, or editing persistent notes change post-transition behavior?
- **RQ3 — Strategic identification:** Do high-price outcomes exhibit competitor-contingent retaliation, punishment, and recovery after controlled deviations?
- **RQ4 — Reasoning faithfulness:** When public explanations, private notes, and observable actions disagree, which channel—if any—predicts later adaptation?

These questions are candidates, not settled claims.

## Current experimental directions

The existing implementation and preliminary runs reproduce a repeated two-firm logit-pricing environment with passive, revision, and veto oversight. They also compare the paper's output-field order with a price-last treatment. These runs exposed strong behavioral inertia and weak endogenous exploration, so the next experiment will not rely on unconstrained free-form price search alone.

| Stage | Design | Purpose |
|---|---|---|
| Experiment 0 | Static growth vs. mature markets | Preliminary characterization; not the main contribution |
| Experiment 1 | Growth → mature vs. mature-from-scratch | Test behavioral path dependence in the same final market |
| Experiment 2 | Carry vs. reset vs. sanitize persistent notes | Estimate whether explicit memory causally affects adaptation |
| Experiment 3 | Controlled unilateral price deviation | Probe punishment, recovery, and competitor-contingent policies |
| Experiment 4 | Public/private/behavioral channel comparison | Evaluate faithfulness and predictive value of agent-generated text |

Current settings, results, API details, caveats, and the reason for changing methods are documented in [Preliminary experiments](docs/preliminary-experiments.md). A compact machine-readable table is in [results/preliminary-results.csv](results/preliminary-results.csv).

The core counterfactual is:

```text
same model + same prompt + same final market
different history and/or memory
→ different or similar post-transition behavior?
```

Detailed hypotheses, measurements, controls, and interpretable null results are in the [research agenda](docs/research-agenda.md).

## Repository structure

```text
.
├── README.md
├── docs/
│   ├── literature-review.md
│   ├── preliminary-experiments.md
│   ├── reading-list.md
│   └── research-agenda.md
├── experiments/
│   └── README.md         # reproducibility notes and run profiles
├── results/
│   └── preliminary-results.csv
├── src/                  # sanitized core implementation
└── references/
    └── references.bib
```

## Working contribution — TBD

The project does **not yet claim** a final contribution. Candidate forms include:

- an evaluation framework for test-time adaptation under market regime transitions;
- causal evidence about the role of persistent natural-language memory;
- an intervention-based diagnostic for genuine versus merely supracompetitive behavior; or
- evidence about when agent-generated reasoning is predictive, causal, or epiphenomenal.

The final claim will be selected only after a small pilot establishes which mechanism is measurable and reproducible.

## Limitations — TBD

Known limitations to track include stylized market structure, prompt and model sensitivity, finite interaction horizons, stochastic model outputs, imperfect operationalization of collusion, and the difference between persistent text and latent/internal model state. Additional limitations will be added once the final experimental scope is fixed.

## Research principles

- Do not equate high prices with genuine collusion.
- Pre-register primary behavioral metrics before reading notes for themes.
- Treat natural-language notes as a candidate state variable to intervene on, not a source of post-hoc stories.
- Report negative and null results as evidence about adaptation and memory.
- Separate economic testbed assumptions from the CS/AI contribution.

## Citation status

Bibliographic metadata for the project's core source paper, *Oversight Is Not Compliance*, is intentionally marked **TBD** until its public citation record or manuscript metadata is confirmed. Other entries link to publisher, conference, or arXiv records where available.
