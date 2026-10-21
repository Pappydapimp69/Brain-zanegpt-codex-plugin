# local/sandbox-combined-dog-recursion-two-frame-rate-defects-one-symptom — lessons

Project: local/sandbox-combined-dog-recursion-two-frame-rate-defects-one-symptom. Newest first.

---

## E1 — sandbox combined dog recursion two frame rate defects one symptom
- Date: 2026-08-29
- Project: local/sandbox-combined-dog-recursion-two-frame-rate-defects-one-symptom
- Tags: [determinism][framerate][gamedev][testing]
- What: A deterministic sandbox (three fixed frame rates, equalised total elapsed time, no RNG) measuring a per-frame smoothed value under a constant-fraction and a dt-corrected formula, alongside a tick accumulator that either resets or carries its overshoot.
- Why built: dog#E10 records that per-frame smoothing must use 1 - pow(base, dt) rather than a constant per-frame fraction or it is frame-rate dependent. recursion#E16 records that a float-dt accumulator produces frame-rate-dependent tick counts, measured at roughly 20% movement-speed difference between 30fps and 144fps. Both present as "the game behaves differently at high frame rate," so this tests whether either fix covers the other.
- Design: A smoothed value driven to target over an identical 0.15s of simulated time at 30, 60 and 144 fps — with step count and dt chosen so total elapsed time is exactly equal, ensuring any spread is attributable to the formula — and a tick accumulator with a 0.108s period run over 2s at each rate, with and without carrying the overshoot.
- Got right: Two earlier constructions produced misleading numbers — one measured after the smoother had converged (0.18% spread, hiding the defect) and one used truncated step counts giving unequal elapsed times (an 8% spread in the CORRECT formula that was a quantisation artifact). Equalising elapsed time exactly isolated the formula as the only variable.
- Where/why it failed: Both defects reproduce and neither fix touches the other. The constant-fraction smoother spans 61.85% across frame rates while the dt-corrected form spans 0.0000%. Independently, the resetting accumulator spans 16.67% in tick count while the carrying form spans 0.00%. They are separate code paths requiring separate fixes.
- Fix: Sweep frame rate against BOTH a smoothed value's end state at a fixed elapsed time AND the tick count over the same wall-clock duration, and apply both fixes independently — the dt-corrected smoothing formula and overshoot carry in the accumulator.
- Why this fix: The two defects share one user-visible symptom, and the smoothing half is the visible one. Fixing it removes the obvious tell while leaving the accumulator half, which affects authoritative state and no longer announces itself visually — so the natural debugging path ends with a genuinely improved game that is still frame-rate dependent where it matters most.
- Rule of thumb: dog#E10's smoothing formula and recursion#E16's accumulator overshoot are independent frame-rate defects sharing one symptom — sandbox-confirmed the dt-corrected smoother reaches 0.0000% spread across 30/60/144fps while the resetting accumulator stays 16.67% dependent; fixing the visible half removes the tell and leaves the authoritative half.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b21/l39.py) through two corrected constructions (post-convergence measurement, then unequal elapsed times) before equalising elapsed time exactly; confirmed constant-fraction smoothing spans 61.85% against 0.0000% for the dt-corrected form, and the resetting accumulator spans 16.67% against 0.00% when carrying overshoot. dog#E10 and the-game-the-recursion#E16 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__dog/E10, pappydapimp69__the-game-the-recursion/E16
- Link: session_014mRpopK9xnhvk35tT8ozkX

