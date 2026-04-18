# Guard Audit Report

## Claim Scope
- Claim: guarded rewrites preserve semantics while improving runtime.

## Key Outcomes
- Auto-guarded semantic equivalence rate: 1.0000
- Auto-guarded semantic drift count: 0
- Auto-guarded speedup vs manual carry: 8.92%
- Real clingo confirmatory semantic pass rate: 1.0000

## Counterexample and Cache Findings
- Worst false-hit strategy: raw_text_hash with 271 false hits.
- Guard-signature strategy kept false hits at zero but did not reach planned injected-counterexample detection target.

## Closure Status
- Semantic-preservation portion is supported by both synthetic sweep metrics and bounded real-solver checks.
- Runtime-gain target is partially met (below the planned 10% threshold).
