# local/sandbox-combined-mirage-brain-builder-sweep-the-axis-the-failure-varies-on — lessons

Project: local/sandbox-combined-mirage-brain-builder-sweep-the-axis-the-failure-varies-on. Newest first.

---

## E1 — sandbox combined mirage brain builder sweep the axis the failure varies on
- Date: 2026-08-29
- Project: local/sandbox-combined-mirage-brain-builder-sweep-the-axis-the-failure-varies-on
- Tags: [gamedesign][testing][algorithm][method]
- What: A deterministic sandbox (fixed evenly-spread party positions, no RNG) evaluating chain cohesion under mirage#E15's "in range of anyone" rule, sweeping first over party size and then over which member is removed, and characterising the shape of each curve.
- Why built: mirage#E15 records that chain cohesion is not proximity — legal spread is (N-1)*R so recruiting widens it for free — and that single losses are POSITIONAL: dropping the middle splits the chain. brain-builder#E5 prescribes asserting smoothness rather than monotonicity because a step function is monotonic. This tests what a party-size sweep, the intuitive instrument, actually measures here.
- Design: Members spaced exactly R apart so the chain is cohesive at every party size by construction. Cohesion is then evaluated for each single-member removal from a five-member party, and the resulting cohesion-versus-drop-index sequence is checked for monotonicity and maximum step.
- Got right: Holding party size constant across all five removal cases, which isolates position as the varying quantity and makes the size axis demonstrably uninformative rather than merely less informative.
- Where/why it failed: Cohesion holds at every party size from 2 to 6, with spread growing to exactly the (N-1)*R maximum — a size sweep sees a uniformly healthy system. Removing a member from the same five-member party gives cohesion [1, 0, 0, 0, 1]: dropping either end preserves the chain, dropping any middle member splits it. The failure varies on position, not size, so the size sweep never samples the axis at all.
- Fix: Sweep the axis the failure actually varies on — here, which member is lost — and apply brain-builder#E5's smoothness assertion to that sweep; a smoothness assertion applied to the wrong axis is as blind as a monotonicity one.
- Why this fix: brain-builder#E5's advice is usually read as "use a stronger assertion," but the sandbox shows assertion strength is secondary to axis choice: the size curve is smooth, monotonic and entirely healthy while the system has a hard step on a different axis. Identifying the varying quantity is the prior step E5 does not name, and mirage#E15 supplies it for this mechanic by stating the loss is positional.
- Rule of thumb: brain-builder#E5's smoothness assertion is only as good as the axis it is swept over — sandbox-confirmed a party-size sweep of mirage#E15's chain cohesion is uniformly healthy at every size while cohesion-by-which-member-is-lost is a hard step [1,0,0,0,1]; identify the axis the failure varies on before choosing the assertion.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b17/l35.py) and confirmed cohesion holds at party sizes 2 through 6 with spread reaching exactly (N-1)*R, while single-member removal from a five-member party yields cohesion [1, 0, 0, 0, 1] with a maximum step of 1. mirage#E15 and brain-builder#E5 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__mirage/E15, pappydapimp69__brain-builder/E5
- Link: session_014mRpopK9xnhvk35tT8ozkX

