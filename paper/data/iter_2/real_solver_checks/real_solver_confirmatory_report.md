# Real Solver Confirmatory Report

This report captures bounded real clingo executions for semantic-equivalence and routing-regret checks.

## Protocol
- Backend A: `clingo --configuration=frumpy` (enumeration-oriented baseline).
- Backend B: `clingo --configuration=trendy` (proxy for alternate exact solver policy).
- Semantic check: compare full model sets between naive and rewritten encodings.
- Regret check: compare deterministic router choice against per-instance best backend runtime.

## Caveats
- Backend B is a clingo policy proxy, not a full compilation backend.
- These checks are confirmatory and do not replace larger benchmark sweeps.

- Total real solver invocations: 270.
- Mean regret (all instances): 0.006572 s.
- Semantic pass rate (all instances): 1.0000.
