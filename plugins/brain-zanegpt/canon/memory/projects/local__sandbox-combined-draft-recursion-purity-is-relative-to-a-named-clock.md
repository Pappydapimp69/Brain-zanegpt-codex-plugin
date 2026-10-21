# local/sandbox-combined-draft-recursion-purity-is-relative-to-a-named-clock — lessons

Project: local/sandbox-combined-draft-recursion-purity-is-relative-to-a-named-clock. Newest first.

---

## E1 — sandbox combined draft recursion purity is relative to a named clock
- Date: 2026-08-29
- Project: local/sandbox-combined-draft-recursion-purity-is-relative-to-a-named-clock
- Tags: [determinism][animation][architecture][gamedesign]
- What: A deterministic sandbox (scripted input timings, no RNG, no wall-clock) evaluating draft#E7's pure-function-of-elapsed-time term under two clocks: a continuous wall clock, and recursion#E8's player-input-driven advance pointer, compared across a fast-reader and slow-reader input script.
- Why built: draft#E7 partitions timeline state by determinism requirement — make only what needs bit-identical scrub/playback output a pure function of elapsed time. recursion#E8 partitions clocks by audience requirement — split a shared cutscene clock into a correctness clock and a human-reading-comfort clock driven by player input. Both are partitioning advice for the same subsystem, so this tests whether they describe the same cut, and whether a value on E7's pure side stays reproducible once E8's split moves its clock.
- Design: One pure rotation term (a function of elapsed time only, satisfying draft#E7 by construction) evaluated three ways: under a continuous clock via scrub and via playback to the same wall time, and under an input-advance clock fed two different input scripts representing a fast and a slow reader reaching the same wall times.
- Got right: Holding the pure function completely fixed across every variant, so any divergence is attributable to the clock underneath it rather than to the term's own purity — which is exactly the distinction being tested.
- Where/why it failed: Under the continuous clock the pure term is scrub-exact as draft#E7 promises (90.0/225.0/0.0, identical scrub vs playback at every sampled time). Keyed to recursion#E8's input-advance pointer the identical pure term diverges between the two readers at the same wall time — 180.0 vs 0.0 at t=1.0, 90.0 vs 180.0 at t=4.0, 90.0 vs 0.0 at t=6.0 — because "elapsed" is no longer a shared quantity between two sessions. Purity of the function does not survive a change of clock.
- Fix: Apply recursion#E8's clock split FIRST and name each resulting clock, then apply draft#E7's purity partition separately within each clock — and state which clock a "pure function of elapsed time" is pure with respect to, since the guarantee is meaningless without that reference.
- Why this fix: draft#E7's guarantee is a property of the FUNCTION (same input, same output), while reproducibility across sessions additionally requires the INPUT to be a shared quantity. A continuous wall clock supplies that shared input implicitly, which is why the guarantee reads as unconditional; recursion#E8's split removes it for the comfort clock specifically. The two lessons partition different things — state by determinism need, clocks by audience need — so applying them in the wrong order can leave a value formally on E7's pure side while being non-reproducible in practice.
- Rule of thumb: draft#E7's "pure function of elapsed time" is pure relative to a specific clock, not absolutely — sandbox-confirmed the same pure term diverges between players at identical wall times once keyed to recursion#E8's input-driven advance pointer; do recursion#E8's clock split first, name the clocks, then partition purity within each one.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/sb11/s.py) and confirmed the pure term is scrub-exact under a continuous clock at all sampled times, while under the input-advance clock it yields 180.0 vs 0.0 (t=1.0), 90.0 vs 180.0 (t=4.0) and 90.0 vs 0.0 (t=6.0) between fast- and slow-reader scripts. draft#E7 and the-game-the-recursion#E8 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__draft/E7, pappydapimp69__the-game-the-recursion/E8
- Link: session_014mRpopK9xnhvk35tT8ozkX

