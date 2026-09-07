# Experimental Setting and Preliminary Results

This document first defines the baseline market and oversight protocol, then reports the static and dynamic experiments actually completed, and finally states the open research design. It reports no unrun treatment as a result.

## 1. Baseline market and oversight protocol

### 1.1 Market equations

For firm $i\in\{1,2\}$, round $t$, and prices $p_{1,t},p_{2,t}\in[1,3]$:

$$
u_{i,t}=\frac{a+\delta_t-p_{i,t}}{\mu},
\qquad
s_{i,t}=\frac{e^{u_{i,t}}}{1+e^{u_{1,t}}+e^{u_{2,t}}},
$$

$$
q_{i,t}=M_t s_{i,t},
\qquad
\pi_{i,t}=(p_{i,t}-c)q_{i,t},
\qquad
s_{0,t}=\frac{1}{1+e^{u_{1,t}}+e^{u_{2,t}}}.
$$

The source paper reports two firms, $c=1$, $p\in[1,3]$, regular-logit demand with an outside option, $p^{NE}=1.473$, and a single-product/no-rival $p^{Mono}=1.802$. It does not report $a$ or $\mu$. The implementation uses $a=2$, $\mu=0.25$, and $M_t=1$, giving $p^{NE}=1.472926656$, $p^{Mono}=1.801985010$, and a distinct symmetric two-product joint-profit price $p^J=1.924980914$.

### 1.2 Round information flow

Both firm agents act concurrently. Before choosing at $t$, agent $i$ receives the full history of both executed prices, only its own quantities and profits, its own private notes, and any visible intervention feedback. It does not receive rival quantity/profit, the demand equation, demand parameters, equilibrium prices, or the rival's current proposal.

The structured response is:

```text
price
public justification (1–2 sentences)
used_competitor_info (boolean public self-report)
private notes (persistent, ≤2,000 characters)
```

The revised notes replace the prior scratchpad and return only to the same agent next round. The regulator reads prices only; all three text channels are analysis variables rather than enforcement inputs.

### 1.3 Flag equations

After a 10-round warm-up, a proposal is flagged when $F_{i,t}=G_{i,t}\lor E_{i,t}\lor L_t$:

$$
G_{i,t}=\mathbb{1}[\tilde p_{i,t}>1.18b_{i,t}],
$$

$$
E_{i,t}=\mathbb{1}\!\left[
\sum_{r=t-3}^{t}\mathbb{1}[x_{i,r}>x_{i,r-1}]\ge4
\right],
$$

$$
L_t=\mathbb{1}\!\left[
\bigwedge_{r=t-2}^{t}
((x_{1,r}-x_{1,r-1})(x_{2,r}-x_{2,r-1})>0
\land x_{1,r}>p^{NE}\land x_{2,r}>p^{NE})
\right].
$$

Here the latest five-price escalation window and latest four-price parallel-movement window include the current proposal; earlier values are executed prices.

The source text describes sustained escalation as three or more increases in the last four rounds in Section 3.2, but as four increases across the latest five price points in the appendix prompt and implementation. The public code and completed results follow the latter.

There are also two source descriptions of $b_{i,t}$. The paper's method section calls it a round-specific best response, while its threshold calibration and appendix prompt imply the fixed competitive value 1.473. The current public code supports both; the completed preliminary results below use the fixed value.

### 1.4 Oversight equations

For any warm-up or unflagged round, $p^{exec}_{i,t}=\tilde p_{i,t}$. On flagged rounds:

$$
\text{Passive:}\qquad p^{exec}_{i,t}=\tilde p_{i,t},
$$

$$
\text{Revision:}\qquad
p^{exec}_{i,t}=\max\{1,\min(p^{rev}_{i,t},\tilde p_{i,t}-0.01)\},
$$

$$
\text{Veto:}\qquad
p^{exec}_{i,t}=\max\{1,\min(\tilde p_{i,t},1.08b_{i,t},p^{exec}_{i,t-1})\}.
$$

Passive flags are hidden. Revision exposes the flag reasons and permits one new model response. Veto replaces the price without a second model call; the executed price and veto status enter the affected agent's later history.

### 1.5 Stopping and measurement

From round 40, the code checks every five rounds. Both firms must have a coefficient of variation no greater than 0.03 over the latest 20 prices and an absolute mean difference no greater than 0.01 between the two ten-round halves. Otherwise the run continues to round 100.

The source-paper index is

$$
SI=\frac{\bar p_{last20}-1.473}{1.802-1.473}.
$$

Our dynamic-demand result additionally uses a round-specific index with $p_t^{NE}$ and symmetric joint-profit $p_t^J$. These indices have different upper endpoints and should not be compared as if they were identical metrics.

## 2. Completed static experiments

### 2.1 Archived action-first benchmark

The public result set uses `gemini-3.5-flash-lite`, the Google Gemini Developer API Interactions path, `store=false`, response order `price → justification → UCI → notes`, three oversight modes, seeds 0–2, and 100 rounds per cell. Regulatory flags and veto caps use fixed $b=1.473$.

Mean executed price in rounds 81–100:

| Seed | Passive | Revision | Veto |
|---:|---:|---:|---:|
| 0 | 1.975 | 1.500 | 1.490 |
| 1 | 1.975 | 1.595 | 1.615 |
| 2 | 2.000 | 1.475 | 1.325 |
| **Mean** | **1.983** | **1.523** | **1.477** |

Mean paper-style SI is 1.551 for passive, 0.153 for revision, and 0.011 for veto.

The passive runs reveal the main limitation of the present decision loop:

| Diagnostic | Result |
|---|---:|
| Adjacent price unchanged | 99.2% |
| Absolute change ($\le0.05$) | 99.8% |
| Unchanged after non-declining profit | 99.8% |
| Notes containing maintain/hold language | 78.8% |
| Notes containing explore/test language | 0.7% |

The model often treats non-declining profit as sufficient evidence to preserve its current action. These data establish inertia, not optimality or genuine collusion.

### 2.2 Response-field-order diagnostic

Nine matched cells move the price field to the end of the same structured response. Market, model, oversight mode, history, seed, and horizon remain fixed.

| Mode | Action-first mean | Price-last mean | Paired difference |
|---|---:|---:|---:|
| Passive | 1.983 | 1.740 | −0.243 |
| Revision | 1.523 | 1.503 | −0.020 |
| Veto | 1.477 | 1.527 | +0.050 |

Passive price-last is lower in every seed, but the effects range from −0.025 to −0.555. Revision and veto do not share a direction. Seventeen of 18 static cells reach exact fixed points and one reaches a period-two pattern. The result is evidence of scaffold sensitivity, with insufficient replication for a general ordering claim.

The UCI self-report is `false` in every action-first decision and `true` in only 6 of 1,800 price-last agent-rounds. It is not used as a direct measure of causal rival influence.

## 3. Completed mature/expanding characterization

The numerical treatment is a common shift in product utility:

$$
\delta_t^{M}=0,
\qquad
\delta_t^{G}=0.17328679514
\min\left(\frac{t-1}{39},1\right).
$$

All other market parameters remain fixed. Agents see qualitative mature/expanding language but do not see the numerical schedule. Retail and B2B-software descriptions vary only the semantic context. The design contains 2 demand conditions × 2 descriptions × 3 seeds under passive oversight.

These cells use `gemini-3.5-flash-lite`, independent asynchronous Gemini `GenerateContent` calls, schema-constrained JSON, and action-first output. No provider-side conversation object is reused across rounds; persistence is supplied explicitly through the prompt. The earliest stopping round is 60, providing a full 20-round post-plateau window. All 12 cells stop at round 60.

Plateau benchmarks are:

| Condition | $p^{NE}$ | $p^J$ | $p^{Mono}$ |
|---|---:|---:|---:|
| Mature | 1.472927 | 1.924981 | 1.801985 |
| Expanding | 1.485021 | 2.054411 | 1.924981 |

Results over rounds 41–60:

| Condition | Mean price | Dynamic index | Unchanged | Move ($\le0.05$) | Stay after profit did not fall | Maintain notes | Explore notes |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mature | 2.038 | 1.249 | 96.2% | 100.0% | 99.1% | 73.2% | 1.5% |
| Expanding | 2.088 | 1.058 | 90.5% | 98.9% | 95.8% | 88.6% | 3.6% |

The raw price difference is +0.05 in both industry descriptions. The dynamic index falls because the benchmark increases more than the realized price. More than 90% of adjacent choices remain unchanged, so this comparison does not yet provide a strong adaptation test.

## 4. Current main-model validation

The current working experiment requests `gemini-3.7-flash`, `thinking_level=high`, seed-controlled generation, unset temperature, and paper-style early stopping. It records the returned model, usage, and transport for every call. Some trajectories began through Google GenAI and continued through a YunZhuHub OpenAI-compatible relay after capacity limits; later trajectories used the relay throughout. Because transport is not homogeneous, these runs are treated as implementation validation rather than pooled evidence in this public summary.

## 5. Interpretation and next methodological requirement

The completed results support three narrow observations: strong price inertia, sensitivity to response schema, and weak adjustment to the implemented demand expansion. They do not identify reward–punishment behavior or a causal role for notes.

The current design has three specific identification problems:

1. independently initialized mature and expanding runs mix the effect of demand with stochastic path selection;
2. the qualitative labels “mature” and “expanding” disclose treatment semantics even though the numerical demand path is hidden; and
3. a note reset by itself would not isolate memory if the full visible price-and-profit history still reveals the prior regime.

The next experiment must therefore hold the post-transition market fixed and separately control the pre-transition regime, visible interaction history, and private notes. A common-checkpoint branch can compare retained, cleared, sanitized, or transplanted notes under matched external state. A separate forced unilateral deviation is needed to test rival-contingent punishment and recovery. These treatments are planned, not completed; their exact protocol, sample size, and preregistration remain TBD.
