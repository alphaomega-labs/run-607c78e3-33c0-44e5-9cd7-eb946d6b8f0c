# Knowledge Notes: AutoTW-ASP Literature Synthesis

## Scope
This synthesis covers neurosymbolic ASP, probabilistic logic programming, knowledge compilation, weighted/algebraic model counting, and treewidth-aware optimization for exact inference.

## Theme A: Neurosymbolic ASP and neural-probabilistic reasoning
- src_011 (2018): DeepProbLog: Neural Probabilistic Logic Programming | URL: https://doi.org/10.48550/arxiv.1805.10872
  Contribution: DeepProbLog unifies ProbLog inference with trainable neural predicates.
  Limitation: Inference speed depends on grounding and compilation complexity.
- src_012 (2020): NeurASP: Embracing Neural Networks into Answer Set Programming | URL: https://doi.org/10.24963/ijcai.2020/243
  Contribution: NeurASP framework coupling neural predicates with ASP rules and stable-model reasoning.
  Limitation: Inference can be costly due to stable-model enumeration on large/high-count instances.
- src_014 (2021): Neural probabilistic logic programming in DeepProbLog | URL: https://doi.org/10.1016/j.artint.2021.103504
- src_016 (2022): DeepStochLog: Neural Stochastic Logic Programming | URL: https://doi.org/10.1609/aaai.v36i9.21248
  Contribution: DeepStochLog framework and scalability analysis for neural stochastic logic programming.
  Limitation: Runtime still sensitive to proof-space growth and relational complexity.
- src_019 (2022): Neural-Probabilistic Answer Set Programming | URL: https://doi.org/10.24963/kr.2022/48
- src_032 (2023): Reliable Natural Language Understanding with Large Language Models and Answer Set Programming | URL: https://doi.org/10.4204/eptcs.385.27
- src_033 (2023): Scalable Neural-Probabilistic Answer Set Programming | URL: https://doi.org/10.1613/jair.1.15027
  Contribution: SLASH/SAME-style scalable neural-probabilistic ASP pipeline with extensive experiments.
  Limitation: Approximation/truncation choices can influence exactness and calibration.
- src_039 (2024): aspmc: New frontiers of algebraic answer set counting | URL: https://repositum.tuwien.at/bitstream/20.500.12708/209319/1/Eiter-2024-Artificial%20Intelligence-vor.pdf
  Contribution: Improved Clark-completion variants with stronger width guarantees.
  Limitation: Benefits are instance- and structure-dependent; no single transformation dominates all workloads.

## Theme B: Knowledge compilation and model counting foundations
- src_001 (1993): A linear time algorithm for finding tree-decompositions of small treewidth | URL: https://doi.org/10.1145/167088.167161
- src_002 (2002): A Knowledge Compilation Map | URL: https://doi.org/10.1613/jair.989
  Equation/Definition seed: target language choice is governed by succinctness and polytime query/transformation support
- src_003 (2005): DPLL with a Trace: From SAT to Knowledge Compilation | URL: https://www.ijcai.org/Proceedings/05/Papers/0876.pdf
- src_004 (2008): On probabilistic inference by weighted model counting | URL: https://doi.org/10.1016/j.artint.2007.11.002
  Equation/Definition seed: Pr(evidence) is computed from weighted counts over CNF models consistent with evidence.
- src_005 (2011): Lifted Probabilistic Inference by First-Order Knowledge Compilation | URL: https://doi.org/10.5591/978-1-57735-516-8/ijcai11-363
- src_006 (2012): Dsharp: Fast d-DNNF Compilation with sharpSAT | URL: https://doi.org/10.1007/978-3-642-30353-1_36
- src_008 (2012): Knowledge Compilation Meets Database Theory: Compiling Queries to Decision Diagrams | URL: https://doi.org/10.1007/s00224-012-9392-5
- src_022 (2023): Anytime Weighted Model Counting with Approximation Guarantees for Probabilistic Inference | URL: https://doi.org/10.4230/lipics.cp.2023.15

## Cross-paper synthesis for AutoTW-ASP design
- Backend crossover signal should combine structural width proxy (treewidth/pathwidth), expected model-count growth, and reuse ratio of grounded structure/circuits.
- Rewriting quality impacts both semantic correctness and compiler tractability; width-aware completions/cycle breaking from ASPMC-style pipelines are reusable implementation anchors.
- Enumeration remains preferable in low-reuse/high-variance instances; compilation gains dominate in shared-structure regimes with bounded width and reusable circuits.
- Evaluation matrix should include exactness-preservation checks (stable-model equivalence), runtime, accuracy, and ablations over router features and rewrite classes.

## Equations and formal definitions used downstream
- treewidth(G) = min_{(T,chi)} max_{t in V(T)} |chi(t)| - 1 (from width definitions used in tree decomposition literature and ASPMC exposition).
- Compilation-vs-enumeration crossover intuition from the uploaded Treewidth-Aware manuscript: compilation cost scales with structural width (e.g., O(n * 2^{O(tw)})) and amortizes with reuse.
- WMC-style exact inference formulation: probabilistic queries can be reduced to weighted counts over satisfying assignments in encoded CNF.

## Coverage limitations
- Several recent survey/report-style sources are included for recency and trend coverage but extracted at partial depth.
- The uploaded seed manuscript is anonymized; it is used as technical evidence and seed coverage input, but not as a formal bibliographic source due missing non-anonymous author metadata.


## Theme D: Treewidth-aware ASP structural hardness and counting limits
- src_045 (2021): Treewidth-Aware Cycle Breaking for Algebraic Answer Set Counting | URL: https://proceedings.kr.org/2021/26/kr2021-0026-eiter-et-al.pdf
  Contribution: Adds theorem-level structure-aware bounds for cycle breaking, reductions, or counting runtime.
  Why it matters: Directly informs rewrite objectives and backend routing features for AutoTW-ASP.
- src_046 (2021): Treewidth-aware reductions of normal ASP to SAT - Is normal ASP harder than SAT after all? | URL: https://doi.org/10.1016/j.artint.2021.103651
  Contribution: Adds theorem-level structure-aware bounds for cycle breaking, reductions, or counting runtime.
  Why it matters: Directly informs rewrite objectives and backend routing features for AutoTW-ASP.
- src_047 (2023): Characterizing Structural Hardness of Logic Programs: What makes Cycles and Reachability Hard for Treewidth? | URL: https://arxiv.org/abs/2301.07472
  Contribution: Adds theorem-level structure-aware bounds for cycle breaking, reductions, or counting runtime.
  Why it matters: Directly informs rewrite objectives and backend routing features for AutoTW-ASP.
- src_048 (2023): The Impact of Structure in Answer Set Counting: Fighting Cycles and its Limits | URL: https://proceedings.kr.org/2023/34/kr2023-0034-hecher-et-al.pdf
  Contribution: Adds theorem-level structure-aware bounds for cycle breaking, reductions, or counting runtime.
  Why it matters: Directly informs rewrite objectives and backend routing features for AutoTW-ASP.

## Iteration Delta 2026-04-17 (Knowledge Acquisition Validation Remediation)
- Reclassified the anonymized uploaded manuscript from scientific `report` to non-scientific `other` source type to satisfy author-attribution policy.
- Canonicalized the seed resource source URL to `workspace/resources/...pdf` and retained `/api/files/...` only in seed coverage provenance.
- Reconciled authoritative corpus counts across payload sources, refs JSONL, and source index at 50 URL-unique records.

