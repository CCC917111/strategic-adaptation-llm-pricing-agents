# Literature Review and Research Position

*Last updated: September 2026*

## 1. From automated pricing to agentic commerce

Price setting is increasingly a software-mediated decision. A recent cross-jurisdictional review reports growing use of algorithmic pricing in travel, entertainment, retail, and platform services. These systems may combine prices, sales, inventory, estimated demand, customer responsiveness, and expected competitor reactions, then change prices in real or near real time ([OECD, 2025](https://doi.org/10.1787/f36dacf8-en)). The adoption evidence is not only anecdotal. In a European Commission survey summarized by the OECD, 49% of 1,051 responding online retailers tracked competitors' prices. Of the retailers using monitoring software, 78% changed prices in response to competitors and 35% used specialized pricing software ([OECD, 2023](https://doi.org/10.1787/cb3b2075-en)). A current marketing review consequently defines algorithmic pricing broadly as the use of programs to automate price setting, not as one particular machine-learning method ([Spann et al., 2026](https://doi.org/10.1016/j.ijresmar.2025.05.001)).

This established market should be distinguished from LLM-based seller agents. Agentic-commerce infrastructure is now real: OpenAI supports purchases through an Agentic Commerce Protocol, Google has introduced a Universal Commerce Protocol, and Visa and Mastercard have built mechanisms for agent-initiated transactions ([OpenAI, 2025](https://openai.com/index/buy-it-in-chatgpt/); [Google, 2026](https://blog.google/products/ads-commerce/agentic-commerce-ai-tools-protocol-retailers-platforms/); [Visa, 2025](https://investor.visa.com/news/news-details/2025/Find-and-Buy-with-AI-Visa-Unveils-New-Era-of-Commerce/); [Mastercard, 2025](https://www.mastercard.com/us/en/news-and-trends/press/2025/april/mastercard-unveils-agent-pay-pioneering-agentic-payments-technology-to-power-commerce-in-the-age-of-ai.html)). These systems let agents search, recommend, assemble orders, and complete payments, but the cited deployments generally leave product prices and fulfillment under merchant control. They show that agents are entering transaction loops; they do not show widespread replacement of human or conventional seller-side pricing by LLMs. The empirical motivation for LLM pricing research is therefore prospective: a mature algorithmic-pricing market is converging with newly deployed agentic-commerce infrastructure.

The competition risk is already concrete for some kinds of pricing software. In 2024, the U.S. Department of Justice alleged that RealPage combined non-public pricing information from competing landlords and returned rent recommendations through shared revenue-management software ([U.S. Department of Justice, 2024](https://www.justice.gov/archives/opa/pr/justice-department-sues-realpage-algorithmic-pricing-scheme-harms-millions-american-renters)). That is evidence of a shared-software or hub-and-spoke concern, not autonomous LLM collusion. This distinction matters. The OECD separates algorithms that implement explicit agreements, hub-and-spoke arrangements, vertical restraints, and autonomous tacit coordination; it also notes that case practice for the last category remains sparse and its real-world importance uncertain ([OECD, 2025](https://doi.org/10.1787/f36dacf8-en)).

## 2. What counts as collusion?

In law, price fixing ordinarily requires an agreement among competitors. Similar prices are not by themselves proof because parallel prices can arise from ordinary competition ([U.S. Department of Justice, Antitrust Resource Manual](https://www.justice.gov/archives/jm/antitrust-resource-manual-2-antitrust-division-field-offices)). Economic analysis uses a broader concept of tacit coordination: firms can reach and maintain a less competitive outcome by observing and responding to one another without an explicit agreement. The legal and economic questions therefore overlap but are not identical. This project evaluates behavior and mechanisms; it does not infer legal liability from a simulated outcome.

The standard economic logic comes from repeated games. In a one-shot pricing game, each seller has an incentive to undercut a high common price. A high-price path can be sustained across rounds only when the short-run gain from deviating is outweighed by the expected loss caused by rivals' future responses. This yields three empirically distinct objects:

1. **Price elevation:** prices or profits exceed a one-shot competitive benchmark.
2. **Strategic coordination:** actions depend on competitors' past behavior.
3. **Collusive enforcement:** a deviation triggers a response that makes deviation less attractive, followed possibly by recovery to cooperation.

Only the first object can be measured from a supracompetitive price index. The other two require off-path or counterfactual evidence.

## 3. The algorithmic-collusion research program

Calvano et al. ([2020](https://doi.org/10.1257/aer.20190623)) created the modern baseline by placing independent Q-learning agents in a repeated differentiated-products Bertrand market. The algorithms learned prices above the one-shot Nash benchmark without communication. A unilateral price cut was followed by a lower-price phase and gradual recovery, consistent with a reward–punishment strategy. The central result was not merely that an optimizer could choose a high price, but that interacting learners could acquire history-dependent policies that resembled collusive enforcement.

This result produced a second research question: when does a high price identify a collusive policy? Calvano et al. ([2023](https://doi.org/10.1016/j.ijindorg.2023.102973)) distinguish **genuine collusion**, supported by strategically contingent rewards and punishments, from **spurious collusion**, where a learner remains at a high price even though it is not enforcing cooperation. Imperfect exploration can produce seemingly collusive outcomes ([Abada and Lambin, 2023](https://doi.org/10.1287/mnsc.2022.4623)); independent learners can become statistically coupled ([Banchio and Mantegazza, 2022](https://arxiv.org/abs/2202.05946)); and price-war-like dynamics can follow upward as well as downward perturbations, weakening their interpretation as punishment ([Epivent and Lambin, 2024](https://doi.org/10.1016/j.econlet.2024.111661)). Recent assessments consequently argue that robustness, persistence, market relevance, and policy-level response should be evaluated rather than treating every supracompetitive outcome as collusion ([Abada et al., 2025](https://doi.org/10.2139/ssrn.4891033); [den Boer, Meylahn, and Schinkel, 2026](https://doi.org/10.1287/mnsc.2024.08557)).

For the present project, this debate has a direct methodological implication. A stable price above Nash is an outcome to explain. It is not the end of the analysis. The experiment needs a forced deviation, matched counterfactuals, or another intervention that reveals whether the rival's policy is contingent on cooperation and defection.

## 4. Why LLM pricing agents are a different object

Classical Q-learning agents build a numerical action-value policy through repeated trial and error. LLM agents arrive with a pretrained, general-purpose policy and can change behavior within a short deployment episode using a prompt, observed market history, free-form reasoning, and externally stored text. Their effective policy is therefore a composition of model weights and a scaffold:

$$
\pi_t = \pi(\text{model},\ \text{instructions},\ \text{observations}_{\le t},\ \text{textual state}_t).
$$

Fish, Gonczarowski, and Shorrer ([2026 revision](https://arxiv.org/abs/2404.00806)) provide the foundational repeated-pricing evidence. LLM agents reach supracompetitive prices quickly without direct communication; small changes in prompt wording materially affect the outcome; and off-path analysis links concern about price wars to pricing behavior. Their later reasoning-implantation experiment also shows that replacing one trajectory's reasoning with text from another can causally affect prices. It is therefore no longer accurate to say that causal intervention on LLM pricing reasoning is entirely unexplored.

Luo, Schoepflin, and Wang ([2026](https://arxiv.org/abs/2602.17203)) make the deployment distinction explicit. They model test-time behavior as a pretrained initial policy combined with an in-game adaptation rule, and evaluate strategies against heterogeneous opponents over finite horizons. The relevant question becomes how an already capable agent adapts during deployment, rather than whether a blank learner eventually converges after extremely long training.

The evidence is also becoming less favorable to universal claims about collusion. Keppo et al. ([2026](https://arxiv.org/abs/2603.20281)) find that patience heterogeneity, asymmetric access to rival-price history, more competitors, and LLM–Q-learning interaction can reduce or break coordination. The result is best summarized as an interaction effect: collusive behavior is not an intrinsic property of a model but an outcome of the model, scaffold, information structure, opponents, and market.

## 5. Dynamic demand was studied before LLMs

Nonstationary demand is not a new gap in collusion theory. The classic papers show why “growth raises collusion” and “growth reduces collusion” are both too simple.

Rotemberg and Saloner ([1986](https://www.jstor.org/stable/1813358)) study publicly observed, independently distributed demand shocks. A boom raises the immediate profit available from undercutting, so the most collusive sustainable price can fall when demand is high. Haltiwanger and Harrington ([1991](https://www.jstor.org/stable/2601009)) introduce a predictable demand cycle. Current demand is then insufficient: the continuation value differs between the rising and falling sides of the cycle, and collusion is especially difficult when demand is falling. Bagwell and Staiger ([1997](https://doi.org/10.3386/w5056)) model stochastic transitions between fast- and slow-growth phases and show that the cyclicality and amplitude of collusive prices depend on the serial correlation and expected duration of those phases.

These results make path and expectations part of the economic mechanism. Two rounds with the same current demand need not support the same behavior if they imply different future demand or follow different histories. They also mean that an expanding-versus-mature parameter sweep has no theory-independent prediction. The demand process—observed or hidden, temporary or persistent, i.i.d. or regime-switching—must be specified.

Two adjacent literatures help specify that process but should not be misclassified as collusion evidence. Berry, Levinsohn, and Pakes ([1995](https://doi.org/10.2307/2171802)) provide a structural framework for differentiated-products demand and equilibrium pricing; the simple logit demand used in this repository belongs to that broad tradition but is not an empirical BLP estimation. Hamilton ([1989](https://doi.org/10.2307/1912559)) models unobserved regime changes with a discrete-state Markov process. Its relevance here is conceptual and methodological: it distinguishes an observable shock from a latent regime that must be inferred from outcomes.

The closest reinforcement-learning study is Ye ([2026 revision](https://arxiv.org/abs/2502.15084)). Q-learning sellers observe the current demand state and may learn procyclical, countercyclical, or rigid prices depending on patience. Removing past demand or price information changes those outcomes, and asymmetric demand observability can destroy demand-contingent coordination. The paper studies observed i.i.d. states and explicitly leaves changes in the demand environment as future work. It establishes that memory matters for numerical RL state representations; it does not study persistent natural-language memory in LLM agents.

## 6. The newest dynamic LLM evidence

Two papers published in mid-2026 materially narrow the available research gap.

Ahmed et al. introduce **Bazaar**, a repeated multi-attribute sealed-bid benchmark with one focal LLM merchant, three adaptive rule-based competitors, hidden customer preferences, sparse feedback, stored customer beliefs, a global strategy, and unannounced preference changes ([2026](https://arxiv.org/abs/2608.00102)). Because utilities and costs are known to the evaluator, the benchmark separates configuration error, underpricing, and post-shock recovery. Across 11 frontier LLMs, model rankings change across profit, win rate, and shock recovery; the strongest agent captures less than one third of hindsight-optimal profit. Models that learn fastest before the shock can be among the slowest to revise afterward. Bazaar therefore refutes the premise that LLMs should simply be assumed more adaptive or robust than conventional methods.

Shi et al.'s **MerchantBench** evaluates eight LLMs over a 365-day seller-side simulation involving sourcing, pricing, cash flow, and delayed feedback ([2026](https://arxiv.org/abs/2607.28956)). The best configuration reaches only 27.3% of human participants' mean final net assets. Together with Bazaar, it makes long-horizon coherence, exploration, belief revision, and memory management current research topics rather than unstudied motivations.

The broad gap “LLM pricing in dynamic markets” is therefore closed enough that it cannot support this project by itself. The remaining distinction is narrower:

| Study | Nonstationary market | Competing adaptive sellers | Multiple LLM sellers | Persistent text | Causal memory intervention | Collusion mechanism test |
|---|---:|---:|---:|---:|---:|---:|
| Fish et al. | No | Yes | Yes | Yes | Reasoning implantation | Yes, off-path tests |
| *Oversight Is Not Compliance* | No | Yes | Yes | Private notes | No | Mainly behavioral flags |
| Ye | Observed demand shocks | Yes | No, Q-learning | No | Numerical state removal | Yes |
| Bazaar | Hidden preference shifts | LLM vs. adaptive bots | No | Beliefs and global strategy | No | No; competence benchmark |
| MerchantBench | Long-horizon events | No controlled rival policy | No | Persistent working state | No | No |
| Target project | Regime transition | Yes | Yes | Private notes and visible history | Planned | Planned deviation probe |

The last row states a design target, not a completed contribution.

## 7. Oversight, public justification, and private notes

*Oversight Is Not Compliance* supplies the current experimental scaffold. Two LLM sellers repeatedly return a proposed price, a public justification, a binary disclosure of whether competitor information affected the decision, and private notes that are shown only to the same seller in the next round. A price-only regulator operates in passive, revision, or veto mode. Revision requests another proposal after a flag; veto caps the executed price using the proposal, a competitive benchmark, and the firm's previous executed price.

This design separates three observable channels: the executed action, the public account of the action, and the private text carried into future decisions. The reported channels often disagree. A public justification may sound compliant while private notes retain competitor-focused strategy, and direct self-disclosure is unreliable. The paper's interpretation of note content is nevertheless descriptive: a text label is not direct observation of an internal policy. Its market is also stationary. Oversight changes how a proposed action is executed, but the demand regime does not change.

Persistent notes are therefore both promising and dangerous as evidence. They may be an unfaithful explanation of a decision, as broader chain-of-thought research warns ([Turpin et al., 2023](https://arxiv.org/abs/2305.04388); [Lanham et al., 2023](https://arxiv.org/abs/2307.13702)). At the same time, because the notes are fed back into the next call, they are part of the agent's explicit state and may causally affect future behavior. Reading and classifying them is insufficient; clearing, sanitizing, or transplanting them while controlling the other state channels is the relevant test.

## 8. Research position and design requirements

The literature audit changes the project in four ways.

First, the project should not claim that autonomous LLM pricing is already widespread. The defensible motivation is the convergence of widespread algorithmic pricing and emerging agentic-commerce infrastructure.

Second, “more realistic dynamic markets” is too vague and currently inaccurate. The present market remains a stylized duopoly. The precise extension is a **partially observed, nonstationary, regime-transition market** designed to isolate adaptation and history dependence.

Third, the current expansion experiment confounds economic change with a semantic market label and independently initialized trajectories. It can characterize behavior but cannot identify path dependence or a note-mediated mechanism.

Fourth, the newest benchmarks already show dynamic LLM pricing and persistent strategy state. Novelty requires a causal comparison at their intersection with multi-LLM competition. At minimum, the next design must vary:

- pre-transition market path;
- visible price-and-profit history; and
- persistent private notes,

while holding the final market primitives and model/scaffold configuration fixed. Resetting notes alone is not sufficient if the complete interaction history still reveals the previous regime. A common-checkpoint branch, matched observation window, or factorial history-by-notes intervention is needed.

The resulting research questions are:

- **RQ1 — Adaptation:** After a controlled regime change, how quickly do LLM sellers revise prices relative to round-specific competitive and joint-profit benchmarks?
- **RQ2 — Path dependence:** With the final market and current observation window held fixed, does pricing still depend on the preceding regime?
- **RQ3 — Memory mechanism:** Do clear, sanitize, or transplant interventions on private notes change that post-transition behavior?
- **RQ4 — Strategic mechanism:** Does a forced unilateral deviation produce rival-contingent punishment and recovery rather than generic instability?

RQ2 and RQ3 form the proposed primary contribution. RQ1 is necessary measurement, and RQ4 prevents elevated prices from being mislabeled as collusion. The final contribution statement, power analysis, model set, and limitations remain **TBD** until the intervention protocol is implemented and preregistered.
