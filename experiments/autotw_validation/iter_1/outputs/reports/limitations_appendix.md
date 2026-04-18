# Limitations Appendix

- Routing evaluation uses deterministic simulation sweeps for broad coverage and bounded real-solver checks for executable confirmation.
- The real confirmatory router comparison uses two clingo configurations as backend proxies rather than a full separate compilation stack.
- Regret envelope violation rate in the broad sweep exceeds the strict 5% target for several feature-policy settings; this weakens headline router guarantees.
- Dataset families formula_eval/order/counting/shortest_path are generated from workspace generators and should be treated as controlled stress suites.
