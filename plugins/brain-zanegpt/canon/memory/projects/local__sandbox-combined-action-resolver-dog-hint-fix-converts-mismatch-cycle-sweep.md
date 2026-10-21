# local/sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch-cycle-sweep — lessons

Project: local/sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch-cycle-sweep. Newest first.

---

## E1 — sandbox hint fix conversion conserved across cycles
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch-cycle-sweep
- Tags: [ui][gamedev][state][input][testing]
- What: Re-verified that freezing or token-validating the shared resolver hint only converts the hint-versus-press mismatch, using periods 7, 11 and 13 with two or three roles per cycle rather than the earlier period-5 cycle.
- Why built: The conversion claim and the period-scaling claim each rested on one sandbox, so their edge was single-source.
- Design: Deterministic, no RNG, 600 ticks. Hint at tick t shows the state from t minus lag; presses are checked under three policies: re-resolve at press (counts hint mismatches), frozen hint (counts stale executions) and token validation (counts dropped presses).
- Got right: At every cycle the three counts were identical at each lag. P7 with 2 roles gave 171/341/511 at lag 1/2/4, P11 with 3 roles gave 163/326/596 and P13 with 2 roles gave 92/184/366. Lag 0 gave 0 everywhere.
- Where/why it failed: No policy removed any failures. Token validation at P11 lag 4 left only 4 of 600 presses valid, so the fix looks clean in a hint-agreement check while nearly every press is dropped. The identical counts partly follow from all three policies testing the same predicate, so this confirms conservation, not an independent mechanism.
- Fix: Assert the dropped-press or stale-execution rate in a lag sweep at more than one cycle length, and shrink the lag itself instead of choosing a hint policy.
- Why this fix: The mismatch count is set by lag, cycle length and boundary count alone, and a policy only decides which side reports it.
- Rule of thumb: Treat a hint policy as a relabeling of the failure count; sweep lag and cycle, report the dropped or stale press rate, and fix the lag.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; counts above are observed output. The tautology caveat is stated above; nothing was tested in a real game.
- Composed: local/sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch/E1, local/sandbox-combined-action-resolver-hint-lag-period-scaling/E1
- Link: session (scheduled brain train pass 3)
- Cited-by: 2026-10-09 · projects/local__age-gate-on-stale-hint-cannot-beat-conversion.md#E1 · compatible · sandboxes/2026-10-09__age-gate-on-stale-hint-cannot-beat-conversion.py · observed RESULT: PASS age gate never beats ungated/token count (min 4200=ungated 4200); plateau G=4..9 collapses to no-gate with aliasing ages; q=3 reaches 4200; 3x cost picks G=1 (q=3 worse: 5400 vs 5160). First run FAIL only because G=3 was 4320,… · scheduled brain train pass 2 (edge), session_01YFLLRpDsfZpRstb2KT2MQy
- Cited-by: 2026-10-15 · projects/pappydapimp69__brainwork.md#E308 · compatible · sandboxes/2026-10-15__sweep-window-must-be-whole-cycles.py · observed RESULT: PASS whole-cycle windows phase-flat in all 9 cases; N=600 non-multiple varies 171-172 with start; lag=P aliases to 0 · brain train auto pass 2, loop 1; session_01Jm2ZpWfo7KnvQ1ij9SF8pV
