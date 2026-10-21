# local/sandbox-one-state-vector-pheromone-view-outcome — lessons

Project: local/sandbox-one-state-vector-pheromone-view-outcome. Newest first.

---

## E1 — one state vector pheromone view outcome
- Date: 2026-10-08
- Project: local/sandbox-one-state-vector-pheromone-view-outcome
- Tags: [simulation][architecture][testing][rendering]
- What: Built the unapplied kernel one-state-vector-drives-picture-score-and-outcome on a per-cell pheromone field (the sibling kernel's recurrence) with a recorded-trace replay. Picture and outcome from one shared vector never disagreed, but the guarantee held only when both read the same predicate and no eased presentation value fed the picture.
- Why built: The kernel claims the visuals cannot disagree with the ending when both derive from one state vector. No memory entry had built against it. The pheromone field gives a vector whose decay differs per cell, so an authored global-rate animation visibly differs from the model, and brain-builder/E7 gives the trace-replay form of the same discipline.
- Design: Python stdlib, no RNG. 12 cells, tau updated as (1-rho)*tau with exposed rho 0.30 and sheltered 0.05, 40 ticks. View = contiguous lit cells above a threshold, outcome = how far a tracker follows the trail above a threshold, both read from tau. Cases: shared predicate, replay from stored trace, authored view with a global mean rho, mismatched thresholds, repeated-deposit steady state, eased presentation value.
- Got right: With one vector and one threshold, view and outcome matched on all 41 ticks, and a view rebuilt from the stored trace matched the live one (0 mismatches). The authored global-rho view disagreed on 3 of 41 ticks. Repeated deposit converged to deposit/rho per cell (max error 4.9e-9; caps 0.667 exposed, 4.0 sheltered).
- Where/why it failed: Sharing the vector is not sufficient. Picture threshold 0.05 against outcome threshold 0.2 disagreed on 4 ticks starting at tick 5, so the picture showed a trail the tracker had already lost. Feeding an eased presentation value to the picture disagreed on 1 tick.
- Fix: Derive picture and outcome through one shared readout function (one predicate, one threshold constant) over the raw vector, and keep eased or particle values out of that readout.
- Why this fix: The disagreement arose in the readout between the vector and each consumer, so a single shared readout removes it where sharing only the numbers does not.
- Rule of thumb: One shared state vector is necessary but not enough for a picture that cannot contradict the ending; the picture and the outcome must also share the same readout predicate, and presentation smoothing must stay outside it.
- Provenance (verified/assumed): Verified first-hand with the sandbox in this session; it is a reduced 1D model, and the real pond film or rendering code was not run.
- Composed: ideas:SIMULATION/legibility/one-state-vector-drives-picture-score-and-outcome, ideas:SIMULATION/spatial-decay-fields/pheromone-style-per-cell-decay, brain-builder/E7
- Sandbox: sandboxes/2026-10-08__one-state-vector-pheromone-view-outcome.py
- Prediction: Shared vector with shared threshold gives 0 mismatches and replay equals live; the global-rho authored view and the mismatched-threshold view give more than 0; I expected the eased value to break it.
- Observed: RESULT: PASS shared tau agrees (0 mismatches) but only with one shared predicate (S3 4 ticks) and no eased presentation value (S5 1); authored parallel view drifts on 3. The first run failed only because my steady-state tolerance was 1e-9 against a 4.9e-9 convergence error, so I set it to 1e-6.
- Scenarios: 1) one vector, one threshold, plus trace replay; 2) authored global-rho view; 3) BREAK: shared vector with different view and outcome thresholds; 4) repeated-deposit steady state; 5) BREAK: eased presentation value in the picture
- Link: scheduled brain train session 2026-10-08
- Cited-by: 2026-10-09 · projects/local__sandbox-npc-memory-guardrails.md#E1 · compatible · sandboxes/2026-10-09__npc-memory-hysteresis-asymmetric-tiered-guardrails.py · observed RESULT: FAIL A_kept=0 B_kept=24 B_hostile_kept=12 C_key=0 mid_sticky_agree=0.0 days_to_20 key=62 bg=15 poke debounce1=11.5 debounce2=65.0 parity=True order_ok=True · brain train auto pass 5
