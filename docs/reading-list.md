# Structured Reading List

This list follows the argument of the project. “Role here” distinguishes direct evidence from background or methodology.

## 1. Real-world motivation and policy categories

| Work | What it establishes | Role here |
|---|---|---|
| [OECD (2025), *Algorithmic Pricing and Competition in G7 Jurisdictions*](https://doi.org/10.1787/f36dacf8-en) | Current adoption across sectors; separates explicit facilitation, shared-software arrangements, vertical restraints, and autonomous-learning risk | Main adoption and policy source |
| [OECD (2023), *Algorithmic Competition*](https://doi.org/10.1787/cb3b2075-en) | Survey evidence on competitor monitoring and automated price adjustment; notes sparse autonomous-collusion cases | Quantitative adoption evidence |
| [Spann et al. (2026), *Algorithmic Pricing: Implications for Marketing Strategy and Regulation*](https://doi.org/10.1016/j.ijresmar.2025.05.001) | Defines algorithmic pricing and reviews firm use across consumer, business, and platform markets | Business-practice synthesis |
| [U.S. DOJ (2025), RealPage proposed settlement](https://www.justice.gov/opa/pr/justice-department-requires-realpage-end-sharing-competitively-sensitive-information-and) | Restricts current competitor data, price-alignment features, and certain information exchanges; adds monitoring | Real enforcement example; not autonomous LLM collusion |
| [European Commission (2023), Horizontal Guidelines](https://competition-policy.ec.europa.eu/system/files/2023-07/2023_revised_horizontal_guidelines_en.pdf) | Treats collusion by code and commercially sensitive information exchange under existing competition rules | Regulatory categories and responsibility |
| [Anthropic (2025), Project Vend](https://www.anthropic.com/research/project-vend-1) | A real pilot in which an LLM managed inventory and set prices | Direct seller-side demonstration; not evidence of broad deployment |
| [OpenAI ACP](https://openai.com/index/buy-it-in-chatgpt/), [Google UCP](https://blog.google/products/ads-commerce/agentic-commerce-ai-tools-protocol-retailers-platforms/), [Visa Intelligent Commerce](https://investor.visa.com/news/news-details/2025/Find-and-Buy-with-AI-Visa-Unveils-New-Era-of-Commerce/) | Infrastructure for agent-assisted shopping, checkout, and payment | Evidence that agentic commerce is emerging; not evidence of widespread LLM seller pricing |

## 2. Collusion and mechanism identification

| Work | What it establishes | Role here |
|---|---|---|
| [Calvano et al. (2020), *Artificial Intelligence, Algorithmic Pricing, and Collusion*](https://doi.org/10.1257/aer.20190623) | Q-learning agents can sustain supracompetitive prices with punishment-like responses | Foundational repeated-pricing result |
| [Calvano et al. (2021), *Algorithmic Collusion with Imperfect Monitoring*](https://doi.org/10.1016/j.ijindorg.2021.102712) | Price-war punishments can arise when deviations and adverse demand shocks are confounded | Early move beyond perfect monitoring |
| [Calvano et al. (2023), *Algorithmic Collusion: Genuine or Spurious?*](https://doi.org/10.1016/j.ijindorg.2023.102973) | High prices need not be supported by a reward–punishment policy | Defines the main identification problem |
| [Abada and Lambin (2023), *Artificial Intelligence: Can Seemingly Collusive Outcomes Be Avoided?*](https://doi.org/10.1287/mnsc.2022.4623) | Imperfect exploration can create seemingly collusive outcomes | Directly relevant to observed inertia |
| [Asker, Fershtman, and Pakes (2024), *The Impact of Artificial Intelligence Design on Pricing*](https://doi.org/10.1111/jems.12516) | Feedback and learner design change prices | Shows that the scaffold is part of the policy |
| [Banchio and Mantegazza (2022), *Artificial Intelligence and Spontaneous Collusion*](https://arxiv.org/abs/2202.05946) | Statistical coupling supplies an alternative mechanism | Competing explanation |
| [Epivent and Lambin (2024), *On Algorithmic Collusion and Reward–Punishment Schemes*](https://doi.org/10.1016/j.econlet.2024.111661) | Price-war-like dynamics are not conclusive evidence of punishment | Motivates symmetric perturbation tests |
| [Abada et al. (2025), *Where Are We and Where Should We Be Going?*](https://doi.org/10.2139/ssrn.4891033) | Proposes evaluating simulated risks by persistence, robustness, and actual-market relevance | Standard for contribution claims |
| [den Boer, Meylahn, and Schinkel (2026), *Artificial Collusion*](https://doi.org/10.1287/mnsc.2024.08557) | Reassesses policy-level evidence behind Q-learning price elevation | Prevents loose use of “collusion” |

## 3. Demand, cycles, and regime change

| Work | Main result | Correct use in this project |
|---|---|---|
| [Rotemberg and Saloner (1986), *A Supergame-Theoretic Model of Price Wars during Booms*](https://www.jstor.org/stable/1813358) | With observed i.i.d. demand shocks, stronger deviation incentives in booms can force lower collusive prices | Theory for shock-dependent incentive constraints |
| [Haltiwanger and Harrington (1991), *The Impact of Cyclical Demand Movements on Collusive Behavior*](https://www.jstor.org/stable/2601009) | Predictable future demand changes the continuation value; collusion is hardest during falling demand | Direct reason to compare equal current demand reached through different phases |
| [Bagwell and Staiger (1997), *Collusion over the Business Cycle*](https://doi.org/10.3386/w5056) | Price cyclicality depends on persistence and expected phase duration | Shows that “growth versus maturity” has no universal sign |
| [Hamilton (1989), *A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle*](https://doi.org/10.2307/1912559) | Represents unobserved regime changes with a discrete-state Markov process | Vocabulary and possible generator for latent regimes; not collusion evidence |
| [Berry, Levinsohn, and Pakes (1995), *Automobile Prices in Market Equilibrium*](https://doi.org/10.2307/2171802) | Structural demand and supply estimation for differentiated products | Demand-model lineage; not a dynamic-collusion paper |
| [Ye (2026 rev.), *Algorithmic Collusion under Observed Demand Shocks*](https://arxiv.org/abs/2502.15084) | Q-learning learns procyclical, countercyclical, or rigid prices; numerical demand and price memory matter | Closest RL comparison and boundary on novelty |

## 4. LLM pricing and test-time adaptation

| Work | What it establishes | Role here |
|---|---|---|
| [Fish, Gonczarowski, and Shorrer (2026 rev.), *Algorithmic Collusion by Large Language Models*](https://arxiv.org/abs/2404.00806) | Rapid supracompetitive pricing, prompt sensitivity, off-path tests, and causal reasoning implantation | Main LLM-pricing foundation and boundary on memory novelty |
| [Luo, Schoepflin, and Wang (2026), *Algorithmic Collusion at Test Time*](https://arxiv.org/abs/2602.17203) | Models deployment as a pretrained policy plus finite in-game adaptation | Direct test-time framing |
| [Keppo et al. (2026), *On the Fragility of AI Agent Collusion*](https://arxiv.org/abs/2603.20281) | Patience, information access, agent count, and algorithm heterogeneity can reduce coordination | Shows that behavior is agent × scaffold × environment dependent |
| [Ahmed et al. (2026), *Can LLM Agents Price Competitively?*](https://arxiv.org/abs/2608.00102) | Dynamic auction with hidden preference shifts, adaptive bots, textual beliefs, exact regret, and shock-recovery measures | Closest dynamic LLM pricing study; closes the broad gap |
| [Shi et al. (2026), *MerchantBench*](https://arxiv.org/abs/2607.28956) | Long-horizon seller operations reveal large coherence and adaptation gaps relative to humans | Supports the long-horizon state-management problem |
| [Fish et al. (2025), *EconEvals*](https://arxiv.org/abs/2503.18825) | Evaluates multi-turn LLM agents in unknown economic environments | Evaluation methodology |

## 5. Oversight, explanations, and memory

| Work | What it establishes | Role here |
|---|---|---|
| Anto and Vazquez (2026), *Oversight Is Not Compliance* | Separates executed price, public justification, competitor-use disclosure, and persistent private notes under passive/revision/veto oversight | Experimental scaffold; local source manuscript |
| [Turpin et al. (2023), *Language Models Don't Always Say What They Think*](https://arxiv.org/abs/2305.04388) | Explanations can omit causally relevant features | Reasoning-faithfulness caution |
| [Lanham et al. (2023), *Measuring Faithfulness in Chain-of-Thought Reasoning*](https://arxiv.org/abs/2307.13702) | Explanation faithfulness varies by task and model | Measurement caution |
| [Shinn et al. (2023), *Reflexion*](https://arxiv.org/abs/2303.11366) | Stored verbal reflection can change later behavior | Explicit textual-memory precedent |
| [Park et al. (2023), *Generative Agents*](https://arxiv.org/abs/2304.03442) | Memory and reflection organize multi-step agent behavior | Persistent-state background |

## Recommended reading order

1. OECD (2025), the RealPage settlement, and the EU Horizontal Guidelines, to separate deployed pricing risks from autonomous-collusion hypotheses.
2. Calvano (2020), Calvano (2023), Abada–Lambin, and Epivent–Lambin, to establish the mechanism-identification problem.
3. Rotemberg–Saloner, Haltiwanger–Harrington, Bagwell–Staiger, and Ye, to understand why demand dynamics have ambiguous effects.
4. Fish's latest revision, Luo, Keppo, Bazaar, and MerchantBench, to locate the current LLM boundary.
5. *Oversight Is Not Compliance* together with the reasoning-faithfulness papers, to assess whether note interventions should be included without treating notes as ground truth.
