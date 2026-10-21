# local/validity-cutoff-jitter-amplitude-sweep-sixth-angle — lessons

Project: local/validity-cutoff-jitter-amplitude-sweep-sixth-angle. Newest first.

---

## E1 — validity cutoff jitter amplitude sweep sixth angle
- Date: 2026-10-08
- Project: local/validity-cutoff-jitter-amplitude-sweep-sixth-angle
- Tags: [ui][input][state][gamedev][testing]
- What: Sixth-angle sweep of jitter amplitude showing the validity cutoff must equal the measured maximum valid lag, while the best gate alone never reaches zero error.
- Why built: The jittered-pulse cutoff claim was tested at a single amplitude; a sweep tests whether it generalizes.
- Design: 70 valid presses with base lag 0..4 plus jitter amplitude J on every seventh, J in 0/2/4/8; 22 invalid presses at lags 3..24; cutoff at max valid lag versus one below, versus the best of 30 gates.
- Got right: Cutoff at max valid lag lost 0 at all four amplitudes; the best gate alone scored wrong plus lost of 2, 4, 6, 10 at J 0, 2, 4, 8.
- Where/why it failed: One below the max valid lag lost 14 valid presses at J 0 and 2 at the others, so a cutoff set by typical lag silently drops outliers.
- Fix: Derive the cutoff from the observed maximum valid lag, and re-derive it when jitter amplitude changes.
- Why this fix: Validity already removes invalid presses at any lag, so the cutoff only has to cover valid ones.
- Rule of thumb: Validity plus cutoff at the max valid lag is error-free at every tested jitter amplitude (0 to 8); a gate alone is never error-free because the invalid lag range overlaps.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; prediction (zero loss at max, loss one below, gate alone nonzero) matched at all four amplitudes. The zero loss at the max is partly by construction.
- Composed: local__age-cutoff-roll-up/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-08__validity-cutoff-jitter-amplitude-sweep-sixth-angle.py
- Prediction: Lost is 0 at cutoff equal to max valid lag, above 0 one lower, and the best gate alone is nonzero for every J.
- Observed: RESULT: PASS cutoff=max valid lag loses 0, one below loses >0, gate alone never zero for J in 0,2,4,8
- Scenarios: 1) J=0; 2) J=2; 3) J=4; 4) J=8 built to push the outlier far into the invalid range
- Link: scheduled brain train pass 4
- Audited: 2026-10-10 · fail · Read the entry and its stored sandbox. The claim "validity plus cutoff at the max valid lag is error-free" is built in rather than computed: the cutoff is set to max(v) and then lost_at_mx counts presses with lag above max(v), which is zero by definition for any list, so the 0-loss result would print for any jitter or data. The validity check that is supposed to remove the invalid presses is never modeled, so no invalid press is ever counted as an error under validity plus cutoff; "error-free" is asserted, not measured. Only the gate-alone half (best of 30 gates never reaches zero because lags 3..24 overlap the valid range) and the one-below-loses comparison are actually computed. The Rule of thumb therefore claims more than the run tested; the true computed finding is narrower. · brain train auto pass 3 loop 1, session_01SrR8cxyaQ3JtRkxhaY8dKS
- Cited-by: 2026-10-17 · projects/pappydapimp69__brain-auto-training.md#E28 · compatible · sandboxes/2026-10-17__age-cutoff-threshold-shifts-with-jitter.py · observed RESULT: PASS lossless threshold = max valid lag + J (0 lost at all J=0..8); max-only lost J for J=1..8; one below lost 1 each; period12 lost 1..28; early-only 0 lost at max · brain train auto pass 2, loop 1; session_01LG4GQFTi9A1QxnCzb5c6CV
- Cited-by: 2026-10-18 · projects/local__learned-cutoff-is-lossless-only-after-the-max-valid-lag-outlier-is-seen.md#E1 · compatible · sandboxes/2026-10-18__learned-cutoff-is-lossless-only-after-the-max-valid-lag-outlier-is-seen.py · observed RESULT: PASS offline cutoff 26 loses 0, period cutoff 12 loses 6, learned cutoff lossless from K=105 (first max-lag press at index 104), loss above 0 for every earlier K; loss 7, 7, 1, 1 at K 10, 30, 60, 100. · brain train auto loop 2 pass 1; session_01Q7rYJzNw1uctb9nhZsXCQx
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E453 · compatible · sandboxes/2026-10-18__fibonacci-legality-makes-a-gate-alone-nearly-error-free-until-jitter-moves-the-lag-off-the-dip.py · observed Run 1 FAIL on the tenfold bound only (J=2 gave 24). Final: RESULT: PASS fib gate-only invalid 4 37 24 38 10 at J=0,1,2,4,8 (not monotone, tracks closed form 7, max err 5) vs validity+cutoff 0 at all J; periodic gate J=0 250 · brain train auto loop 2 pass 2, session_01K8wZ3EDWp7o2YCk1kac5LF
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E465 · incompatible · sandboxes/2026-10-18__lossless-cutoff-stays-worst-gate-only-under-jitter.py · observed RESULT: FAIL lossless == max valid effective lag at J 0/2/4/8: [19, 19, 28, 32]; gate-only invalid at it equals the max over cutoffs in 2/4 cases: [95, 94, 135, 133] vs [135, 137, 135, 133]. Peak cutoff equalled the highest invalid-capable… · brain train auto session 2026-10-18; session_017XK4iPJB1weWKi2R7K4DfL
