# local/sandbox-rising-cost-depth-cap-whole-run-vs-step-test — lessons

Project: local/sandbox-rising-cost-depth-cap-whole-run-vs-step-test. Newest first.

---

## E1 — rising cost depth cap whole run vs step test
- Date: 2026-09-30
- Project: local/sandbox-rising-cost-depth-cap-whole-run-vs-step-test
- Tags: [gamedev][testing][balance][gamedesign]
- What: A rising per-stage cost against a fixed budget hard-caps depth, and only a whole-run simulation to a terminal state (or the summed curve) sees the cap, while a per-step affordability test reports far deeper reachability.
- Why built: Cover the untested seam between the per-stage-cost depth cap finding and the reachability-as-a-distinct-test-axis finding.
- Design: cost(k)=10+5k, budget 300, no refill; compared a whole-run simulation, a closed-form cumulative cap, and a per-step test (each stage affordable from a full budget); then added flat per-stage recovery of 20 and 60, and budgets 100 and 1000.
- Got right: Simulation and closed form agreed on caps 8, 4 and 17 for budgets 300, 100 and 1000, while the per-step test claimed stage 58 at budget 300.
- Where/why it failed: I predicted flat recovery of 60 would remove the cap over a 100-stage horizon; it gave depth 23 because cost keeps growing linearly, so any flat recovery only shifts the cap. My first run reported FAIL for that reason.
- Fix: Model recovery against the growing cost curve and re-sum, and keep a whole-run test asserting the cap, instead of a per-step affordability check.
- Why this fix: Recovery 20 lifted depth from 8 to 12 and recovery 60 to 23, both finite, so only recovery that scales with cost (or a budget that grows) can remove a cap.
- Rule of thumb: With a rising per-stage cost, run the whole run to termination and compare to the summed curve; a per-step affordability test overstated depth 58 versus 8 here, and flat recovery moves the cap without removing it.
- Provenance (verified/assumed): Verified first-hand by running the sandbox with the corrected expectation noted; a real game's curve and refill rules were left out of scope.
- Composed: od76/E5, opticon/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__rising-cost-depth-cap-whole-run-vs-step-test.py
- Prediction: cap 8 at budget 300; per-step test reports 58; recovery lifts the cap; recovery 60 removes it (came out wrong: 23).
- Observed: RESULT: PASS whole-run sim cap 8 equals summed-curve cap; per-step test passes to stage 58; recovery 20 lifts it to 12
- Scenarios: 1) budget 300 no refill; 2) budget 100; 3) budget 1000; 4) recovery 20; 5) recovery 60, built to break the removes-the-cap claim.
- Link: scheduled brain train pass 5
- Audited: 2026-10-12 · pass · Read the entry and reran its stored sandbox (RESULT: PASS, caps 8/4/17, recovery 20 gives 12, recovery 60 gives 23). The answer is computed, not built in: the whole-run loop and the cumulative closed-form cap are independent code paths that agree, and the per-step test is a separate function that returns 58. The scenarios (three budgets, two recovery rates, one built to break the removes-the-cap claim) cover the Rule of thumb, which is scoped to a linear rising cost and flat recovery. It is a pure arithmetic model with no real system behind it, so no modeled verdict applies. Minor limit: the 100-stage horizon is the only bound on the recovery-60 check, so the claim that flat recovery never removes the cap rests on cost growing linearly without bound. · scheduled brain train routine 2026-10-12 loop 1 pass 3; session_01SbLcvYSnUb7XWzv1N6FVpb
