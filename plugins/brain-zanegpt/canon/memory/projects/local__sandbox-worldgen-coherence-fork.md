# local/sandbox-worldgen-coherence-fork — lessons

Project: local/sandbox-worldgen-coherence-fork. Newest first.

---

## E1 — worldgen simulate vs template coherence fork
- Date: 2026-10-09
- Project: local/sandbox-worldgen-coherence-fork
- Tags: [procgen][worldbuilding][testing]
- What: A toy 6-civ, 40-turn world history built three ways (simulate-forward, unconstrained template pool with rationalized links, state-constrained template pool), audited by a fact-index/timeline checker, plus terrain-driven vs independent settlement placement.
- Why built: To test where the kernel's simulate-vs-template coherence fork actually shows up, and whether a timeline checker alone can tell the two architectures apart.
- Design: Seeded LCG, 40 seeds per arm. Simulator emits conquer/fall events from strength state. Template picks event kinds independently, then a rationalizer attaches a prior event as the claimed cause (thin: any prior event; thick: same-actor prior event). Checker replays the timeline and counts dead actors acting and claimed causes that are not a real conquer-then-fall chain.
- Got right: The checker split the arms cleanly. Simulate-forward had 0 state violations in 557 events. The free template had 4126 violations in 4800 events. Terrain-driven placement put 0.58 of settlements on the river band versus 0.14 for independent placement.
- Where/why it failed: Adding a state constraint (skip events by dead civs) drove state violations to 0 but left 701 of 751 claimed causes not genuine. A thick rationalizer (same-actor links) only cut that to 597. Timeline consistency is not causal coherence. Caveat: "genuine" for the simulator arm is true by construction (its cause is the state fact), so the 0 fake-cause figure is definitional; the real comparison is the template arms.
- Fix: Treat the checker as necessary, not sufficient. Pair the timeline checker with an explicit cause-validity check (does the cause's precondition hold in state?) when evaluating a template generator, and budget the rationalization corpus rather than expecting constraints to supply causality.
- Why this fix: The constrained arm shows state-consistency is cheap (0 violations) while causality remains an illusion, so a pass on the checker alone would falsely approve a thin template generator.
- Rule of thumb: In this toy, a state-consistency checker passing a template generator proves only ordering sanity; constraints removed 100% of state violations but left about 93% of claimed causes non-genuine, so validate causes separately.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the toy world is far simpler than Dwarf Fortress or Caves of Qud, so magnitudes are not claims about those systems.
- Composed: ideas:WORLDBUILDING/procgen/simulate-forward-vs-template-constrain, ideas:WORLDBUILDING/procgen/terrain-driven-placement-avoids-the-oatmeal-problem, ideas:WORLDBUILDING/canon-management/fact-index-plus-timeline-plus-checker
- Polarity: compatible
- Sandbox: sandboxes/2026-10-09__worldgen-simulate-vs-template-coherence-fork.py
- Prediction: Simulate has 0 state violations; free template has more than 0; constrained template has 0 state violations but still many non-genuine causes; terrain-driven river share more than double independent.
- Observed: RESULT: PASS sim=(0,0) free_viol=4126 constrained=(0,701) river_share 0.58 vs 0.14
- Scenarios: 1) simulate-forward; 2) free thin template; 3) constrained thin template (built to BREAK the idea that constraints give coherence); 4) constrained thick template; 5) terrain-driven vs independent placement
- Link: brain train auto pass 1
- Audited: 2026-10-13 · pass · Read the entry and its stored sandbox. The state-violation numbers are genuinely computed: the checker replays a timeline and counts dead actors acting, and the constraint arm really goes from 4126 violations to 0 by skipping dead-actor events. The headline about claimed causes is weaker. The checker exempts the simulator from the cause test (genuine is true whenever the event carries a true cause), and the rationalizer links each event to a randomly chosen prior event, so a non-genuine cause is almost guaranteed by construction (701 of 751, and 597 even with same-actor links); the 0 for simulate-forward is definitional, as the entry itself admits. Terrain placement is also by construction, since the driven arm picks the candidate nearest the river out of six. So the supported claim is the narrow one the Rule of thumb states, scoped to this toy: a consistency checker cannot see missing causality, and state constraints alone do not supply it. It does not show that a real cause-validity check or a richer rationalizer would behave the same way, or that the 93 percent figure transfers. Within its stated toy scope the verdict is pass. · scheduled brain train auto loop 2 pass 3, 2026-10-13; session_011eTW7aDHC86vQjq7f9sRQG
