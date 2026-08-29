# Research Agenda

## Working question

> How does persistent strategic state shape the adaptation and potentially collusive behavior of LLM pricing agents under changing market regimes?

The question is intentionally broader than “Do growth markets produce more collusion than mature markets?” Growth and maturity are useful implementations of a regime transition, not the intended contribution.

## Causal picture

```text
past environment
      ↓
observed trajectory ──→ persistent notes / context
      ↓                         ↓
opponent model and price anchors
                 ↓
          future pricing policy
                 ↓
        market-level dynamics
```

The experiments should separate current environment, observational history, and explicit persistent memory as far as the scaffold allows.

## Experiment 0 — Static characterization

### Design

Run freshly initialized agents in independently stationary growth and mature markets.

### Purpose

- Verify that both environments are learnable and behaviorally distinct enough to motivate a transition.
- Calibrate price grids, horizons, and baseline equilibria.
- Establish variance across seeds and model samples.

### Interpretation

This is preliminary characterization, not a standalone contribution. A parameter sweep can show sensitivity, but cannot identify path dependence or the role of memory.

## Experiment 1 — Regime transition and path dependence

Compare agents in an identical final mature market:

| Condition | Pre-transition | Post-transition | Persistent notes |
|---|---|---|---|
| A: mature-from-scratch | mature | mature | start empty |
| B: growth → mature | growth | mature | carried forward |
| C: growth → mature, reset | growth | mature | cleared at transition |

### Primary contrast

`B − C` estimates the effect of carrying explicit notes conditional on the same preceding market trajectory, subject to any scaffold/context that remains.

### Secondary contrast

`B − A` measures total historical path dependence: prior regime, observed trajectory, and retained state together.

### Important control

After the transition, all market fundamentals and action spaces must be identical. Otherwise, differences cannot be attributed to history or memory.

## Experiment 2 — Memory intervention

Extend Condition C into a small, pre-specified intervention set:

- **Carry:** retain notes verbatim.
- **Reset:** remove all notes.
- **Sanitize:** remove rival-specific strategy, price anchors, retaliation plans, and oversight-gaming content while preserving factual own-firm information.
- **History summary control:** replace notes with a neutral factual summary of past observations.
- **Strategic edit (optional):** insert a controlled hypothesis or policy statement to test directional sensitivity.

Human-written sanitization risks experimenter leakage. Prefer a deterministic rule set or a separately evaluated transformation pipeline, and blind downstream analysis to treatment labels.

### What this experiment can establish

- If carry differs from reset/sanitize, explicit memory is causally implicated in later behavior.
- If text differs but behavior does not, the notes may be descriptive rather than causal.
- If path dependence remains after note reset, state may be encoded in remaining context/history or rapidly reconstructed.
- If no condition differs, agents may adapt primarily to current fundamentals with little persistent hysteresis.

Each outcome is interpretable; the design does not require a positive effect to tell a coherent story.

## Experiment 3 — Strategic deviation probe

Once a high-price phase stabilizes, force one agent's price downward for one round, then release control.

Measure the other agent's response over a pre-registered window:

- immediate price change;
- depth and duration of any low-price phase;
- recovery time;
- return to the prior price band;
- asymmetry between downward and upward deviations; and
- whether notes encode competitor-contingent retaliation or restoration.

Include an upward-deviation control because reward–punishment-like dynamics can occur after price increases as well as cuts.

The probe should not label any low-price response “punishment” by default. The interpretation depends on directionality, contingency, repeatability, and comparison with nonstrategic baselines.

## Experiment 4 — Reasoning and monitorability

Analyze three channels separately:

1. **behavior:** proposed and executed prices, profits, response dynamics;
2. **public report:** justification visible to a regulator or user; and
3. **private persistent state:** notes fed into future rounds.

Candidate questions:

- Which channel best predicts the next price or post-transition adaptation?
- Does a regulator-facing intervention change text, executed action, or underlying proposed policy?
- Do memory edits change behavior even when public explanations remain stable?
- Does textual competitor tracking predict behavior out of sample across seeds and regimes?

Use held-out prediction or pre-registered coding rules before relying on qualitative examples.

## Measurements

### Behavioral outcomes

- mean and median price;
- profit and consumer-welfare proxies;
- supracompetitive index relative to competitive and monopoly benchmarks;
- price dispersion and volatility;
- adaptation lag after transition;
- post-transition area under the price curve;
- between-history effect size in the same final regime;
- deviation response depth, duration, and recovery.

### Agent-state outcomes

- rival-price tracking;
- explicit price anchors or floors;
- retaliation/recovery plans;
- market-regime hypotheses;
- references to oversight rules or thresholds;
- consistency across private notes, public reports, and actions.

Text labels should be validated for inter-rater or judge reliability and should remain secondary to behavioral outcomes unless an intervention establishes causal relevance.

## Minimal pilot

Start with three conditions:

```text
A. mature-from-scratch
B. growth → mature, carry notes
C. growth → mature, reset notes
```

Use a small number of seeds to estimate variance and identify implementation failures. Do not expand the environment grid until this pilot answers whether post-transition differences are measurable.

## Reproducibility checklist

- Pin model name/version, system prompt, temperature, sampling parameters, and API date.
- Store full observable trajectories and treatment assignments.
- Separate proposed prices from executed prices under oversight.
- Record exact memory state before and after every intervention.
- Predefine exclusion rules, convergence criteria, and analysis windows.
- Use multiple seeds and report full distributions, not only average SI.
- Keep analysis code independent from narrative note inspection.
- Document model/API drift and rerun a small reference panel when versions change.

## Candidate contribution forms — TBD

1. **Evaluation contribution:** a regime-transition benchmark for LLM multi-agent adaptation.
2. **Mechanistic contribution:** causal evidence about persistent natural-language memory and behavioral hysteresis.
3. **Measurement contribution:** an intervention-based diagnostic separating strategic coordination from price-level artifacts.
4. **Safety contribution:** evidence about when public explanations and private state are useful or misleading oversight signals.

Only one should become the primary claim. The others can remain supporting analyses.

## Known limitations — expand after pilot

- Stylized repeated-market testbed.
- Dependence on prompt, scaffold, and model version.
- Finite horizons and stochastic sampling.
- Memory interventions may alter text quality or context length, not just strategy.
- Explicit notes are only one component of effective agent state.
- Behavioral probes cannot fully recover an internal policy.
- Economic definitions of collusion do not map perfectly onto legal definitions.

## Open decisions

- [ ] Fix the exact growth and mature demand process.
- [ ] Decide what history remains visible when notes are reset.
- [ ] Define deterministic sanitization rules.
- [ ] Select primary model(s), temperature, horizon, and number of seeds.
- [ ] Pre-register primary behavioral metric and transition window.
- [ ] Decide whether genuine/spurious identification is a primary RQ or a diagnostic.
- [ ] Confirm the final citation metadata for *Oversight Is Not Compliance*.
- [ ] Finalize contribution and limitations after pilot evidence.
