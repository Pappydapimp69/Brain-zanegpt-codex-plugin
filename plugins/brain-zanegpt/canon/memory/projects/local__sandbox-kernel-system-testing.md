# local/sandbox-kernel-system-testing — lessons

Project: local/sandbox-kernel-system-testing. Newest first.

---

## E3 — move a removed live check to the load boundary where it holds
- Date: 2026-09-28
- Project: local/sandbox-kernel-system-testing
- Tags: [testing][save][pathfinding][state]
- What: Applied the ideas kernel that removing a validity check for the right reason (a replanner must trust the agent's live position) can delete the only detector for an unrelated failure (a non-atomic save leaving the agent inside a wall). The silent failure reproduced, and the removed check caught every case once it lived at the load boundary instead of in the replanner.
- Why built: brain train gap listed the kernel as unapplied. sandbox-astar-replan/E2 removed the start-position check from the replanner; this looks for where that check can safely go.
- Design: A 24x24 grid, 5000 seeded sessions of live movement with obstacle churn, and a 5% chance per session that a door closes on the agent during live play. Position and grid were then saved either atomically or in two steps with 20 or 40 churn steps between them. Counted sessions whose saved position sits in a blocked cell (excluding the live door case), and which detectors flag them: the replanner trusting position, a load-time position-versus-grid check, and the old check put back in the live replanner.
- Got right: Including a legitimate live case where the agent stands in a blocked cell, which is the reason the check was removed; without it, putting the check back looks free.
- Where/why it failed: Two-step saves left the agent inside a blocked cell in 2 of 5000 sessions at low churn and 16 of 5000 (0.32%) at higher churn; atomic saves in 0. The replanner flagged 0 of the 16. A load-time check flagged 16 of 16. Putting the check back into the live replanner would also reject the 237 sessions where a door legitimately closed on the agent.
- Fix: Save related state atomically, and put the removed position-versus-grid check at load time, where a mismatch can only mean corruption, rather than back in the live replanner.
- Why this fix: The check was wrong live because live play can legitimately put the agent in a blocked cell; at load nothing legitimate can, so there the same check is a pure corruption detector.
- Rule of thumb: When a check is removed because it is wrong in one place, move it to the boundary where its assumption holds: a two-step save left the agent in a wall in 16/5000 sessions (0 when atomic), the trusting replanner flagged none, and a load-time position-vs-grid check flagged all 16 without rejecting any of the 237 live moments a door closed on the agent.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b10.py loop 48 in Pappydapimp69/Brain, deterministic seeded sessions. Observed: 2/5000 and 16/5000 incidents two-step, 0 atomic; detectors 0/16 and 16/16; 237 live door moments. The 5% door rate is an assumption of the model; the incident rates differ from the kernel's 0.58% because the churn parameters differ.
- Composed: ideas:SYSTEM/testing/a-fix-for-one-invariant-can-delete-the-only-check-for-another/audit-what-a-removed-guard-was-secretly-catching, sandbox-astar-replan/E2
- Link: session 2026-09-28, brain train gap batch 10 loop 48
- Sandbox: sandboxes/2026-09-28__train-gap-b10.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

## E2 — a 40 trial symmetric control misses most real skews
- Date: 2026-09-28
- Project: local/sandbox-kernel-system-testing
- Tags: [testing][combat][measurement][balance]
- What: Applied the ideas kernel that a symmetric control fight (two identical rosters) exposes turn-order bias from a stable sort on speed ties, originally seen as 25/15 over 40 trials. The bias reproduced, but 40 trials is too few to detect it reliably, and one of the obvious tie-break fixes is itself biased.
- Why built: brain train gap listed the kernel as unapplied. sandbox-dbz-team-combat/E5 recorded the symmetric-control rule; nobody had checked the sample size behind it or compared tie-break fixes.
- Design: Two identical 2-fighter teams; every round all living fighters act in speed order, so each mirrored pair ties. Four orderings: stable sort with team A concatenated first, the same with B first, ties shuffled by a seeded RNG, and team order alternating each round. 4000 seeded fights each. Then the exact two-sided binomial p for 25 of 40, and the power of 40-, 100- and 400-trial controls.
- Got right: Computing the p-value of the kernel's own evidence before relying on it: 25 of 40 against 50/50 gives p = 0.154, which alone would not reject fairness.
- Where/why it failed: Stable sort with A first gave A 68.8% of 4000 fights and B first gave A 31.1%, so the bias reproduced and followed concatenation order. A 40-trial control detected a true 68.8% skew at p<0.05 only 64.6% of the time, and a 62.5% skew only 31.6%; 100 trials gave 96.2% and 66.3%, and 400 gave 100% and 99.9%. Shuffling ties gave 50.1%, but alternating which team goes first each round gave 46.1%, still off 50/50 by about five standard errors.
- Fix: Run the symmetric control with at least a few hundred trials and judge it with a binomial test, not by eye. Break speed ties with a seeded shuffle; do not assume alternating team order is neutral.
- Why this fix: The control is only useful if a real bias makes it fail, which takes enough trials to separate 60-70% from 50%. Alternation still hands first move to a fixed team on a fixed parity of rounds; the sandbox measured the resulting skew, not its mechanism.
- Rule of thumb: A symmetric control needs a few hundred trials, not 40: the original 25/40 skew has p = 0.154, and a 40-trial control catches a true 62.5% bias only 31.6% of the time (400 trials: 99.9%); break ties with a seeded shuffle (50.1%), since alternating which team goes first each round still skewed to 46.1%.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b03.py loop 12 in Pappydapimp69/Brain, deterministic seeded fights and exact binomial arithmetic. Observed: 68.8/31.1/50.1/46.1% by ordering; p(25/40) = 0.154; power 64.6/96.2/100% and 31.6/66.3/99.9%. The combat model is a stand-in, not the original sandbox's code.
- Composed: ideas:SYSTEM/testing/symmetric-control-catches-turn-order-bias/identical-rosters-should-be-50-50, sandbox-dbz-team-combat/E5
- Link: session 2026-09-28, brain train gap batch 3 loop 12
- Sandbox: sandboxes/2026-09-28__train-gap-b03.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-09 · projects/local__sandbox-analogy-bias-readout.md#E1 · incompatible · sandboxes/2026-10-09__analogy-bias-readout-3cosadd-hides-what-parallel-offset-shows.py · observed RESULT: FAIL biased share 0.22 vs control 0.30 (rank 6); neutralize-occ 0.34 queen 40/40, neutralize-all queen 40/40; fgsm ratio 3.17; kshot8 share 0.21; geometry r 0.77 vs control 0.43, parallel share 0.99 vs control 0.46 vs neutralized 0… · Brain training run pass 5 (gap mode), sandbox /tmp/claude-0/trainrun/pass5/memory/ (draft, not synced)

## E1 — a gate oracle must recompute from raw input not read the gates flag
- Date: 2026-09-28
- Project: local/sandbox-kernel-system-testing
- Tags: [testing][determinism][architecture][state]
- What: Applied the ideas kernel that a replay fingerprint only covers the mechanism it drives, so a precondition enforced outside the reducer needs its own ground-truth oracle. The kernel held, and pushing it showed the oracle is only independent if it recomputes the protected set from raw input; an oracle that reads the gate's own state shares the gate's bug.
- Why built: brain train gap listed this kernel as unapplied. the-game-wrong-sky/E17 and test/E22 already showed replay parity misses a driver-side i-frame gate; neither said what makes the replacement oracle trustworthy.
- Design: A presentation driver withholds enemy HIT commands during a 4-tick i-frame window after each dodge; a pure reducer applies the emitted commands and fingerprints its state. 60 seeds of 600 ticks. Three drivers: correct, no-gate (withholding skipped) and late-window (window starts one tick late). Checks: replay of the recorded command log, a golden from the correct build, a golden recorded with the bug present, a self-oracle that flags emitted HITs whose logged i-frame flag was on, and a ground-truth oracle that rebuilds every window from the raw dodge presses per spec.
- Got right: Injecting two different bugs. With only the skipped-gate bug the self-oracle looks as good as ground truth (561 and 561), and the difference between the two oracles never shows.
- Where/why it failed: Replay parity passed 60/60 for all three drivers, and so did a golden recorded after the bug shipped. For the skipped gate both oracles found 561 violations in 60 seeds. For the late window the self-oracle found 0, because the driver's flag is computed by the same wrong window, while the ground-truth oracle found 148 violations in 54 of 60 seeds. A golden from the correct build caught it in 59 of 60 seeds, but only because such a golden existed.
- Fix: Write the oracle from the spec and the raw input: rebuild the protected ticks from the recorded dodge presses and check every emitted command against them. Never let it read the gate's own active flag or window.
- Why this fix: A gate bug usually lives in how the window is computed, not in whether the check runs. An oracle that consumes the gate's computed window inherits exactly that error and reports clean.
- Rule of thumb: An oracle for a gated precondition is only independent if it recomputes the protected set from raw input per spec: an i-frame window that started one tick late gave 148 violations in 54 of 60 seeds under a ground-truth oracle and 0 under an oracle reading the gate's own active flag, while replay parity and a golden recorded with the bug both passed 60/60.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b02.py loop 6 in Pappydapimp69/Brain, deterministic seeded input. Observed: replay parity 60/60 for every driver; no-gate 561 violations under both oracles; late-window 0 under the self-oracle and 148 in 54 seeds under ground truth; clean-era golden matched the late-window build in 1 of 60 seeds. The driver and reducer are a model, not a shipped game.
- Composed: ideas:SYSTEM/testing/a-replay-fingerprint-only-covers-the-mechanism-it-drives-not-every-precondition-riding-on-it/build-a-ground-truth-oracle-for-the-uncovered-invariant, the-game-wrong-sky/E17, test/E22
- Link: session 2026-09-28, brain train gap batch 2 loop 6
- Sandbox: sandboxes/2026-09-28__train-gap-b02.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

