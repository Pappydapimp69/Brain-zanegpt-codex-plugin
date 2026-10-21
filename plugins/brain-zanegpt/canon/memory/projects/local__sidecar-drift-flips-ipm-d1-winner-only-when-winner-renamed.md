# local/sidecar-drift-flips-ipm-d1-winner-only-when-winner-renamed — lessons

Project: local/sidecar-drift-flips-ipm-d1-winner-only-when-winner-renamed. Newest first.

---

## E1 — sidecar drift silently flips ipm d1 winner
- Date: 2026-10-17
- Project: local/sidecar-drift-flips-ipm-d1-winner-only-when-winner-renamed
- Tags: [game-ads][testing][process][sandbox]
- What: A toy 8-variant ranking on IPM times D1 where D1 comes from a hand-typed sidecar keyed by film cut name while the edit list renames one recut at a time. A silent join drops the renamed variant, so the pick changes in exactly 1 of 8 renames (the one where the renamed cut is the true winner, v1 at 2.25), a length check on the join catches 8 of 8, and renaming every cut crashes the max over an empty set.
- Why built: The collective-reference lesson says a hand-kept map between two files drifts silently, and the film cut list is such a second file next to the ranking. I wanted to see how often a drifted sidecar actually changes a ranked pick rather than only losing a row.
- Design: IPM and D1 tables for 8 variants; a cut list mapping stable id to cut name; a sidecar of D1 keyed by cut name. Scenarios: rename each variant's cut once (8 runs); a count check on the join; all cuts renamed (built to BREAK the claim that drift is always silent). No randomness.
- Got right: Drift is silent for 7 of 8 renames in the sense that the pick is unchanged, which would let the bug sit unnoticed; the one flip happens only when the dropped row was the winner, and the count check flags every rename including the 7 harmless ones.
- Where/why it failed: My prediction named the wrong winner (v2); the winner is v1 (7.5 x 0.30 = 2.25 against 2.13), so the sandbox printed FAIL although the behaviour I predicted held. All-renamed was loud (a crash) rather than silent, so drift is silent only for a partial rename.
- Fix: Key the D1 lookup on the stable variant id from the cut list and assert that the joined row count equals the variant count before ranking.
- Why this fix: The silent drop changed the winner in the one case that matters and gave no signal in the other seven, so only a count assertion or a derived key reveals drift before a recut is chosen.
- Rule of thumb: A hand-typed sidecar keyed by cut name changed the IPM times D1 winner in 1 of 8 single renames and was invisible in all 8 without a join-count check; key on a stable id and assert row counts.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the IPM and D1 values are invented toy numbers and no real ad pipeline was inspected.
- Composed: collective-reference/E1, rank-ipm-times-d1-needs-fidelity-retention-link/E1, film
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-17__sidecar-drift-silently-flips-ipm-d1-winner.py
- Prediction: One of 8 single renames flips the pick (when the winner is the renamed cut), I expected the winner to be v2; the count check catches 8 of 8; renaming all cuts crashes. Assumption: a silent drop-on-missing join is how the sidecar fails.
- Observed: RESULT: FAIL flips 1/8 (winner v1), count check catches 8/8, all-renamed crash (only the winner-id guess was wrong)
- Scenarios: 1) eight single-rename runs; 2) join-count check; 3) all cuts renamed (BREAK of the silent-drift claim)
- Link: session_01FKz3vbJ5KozVVes2fUyYJ8

