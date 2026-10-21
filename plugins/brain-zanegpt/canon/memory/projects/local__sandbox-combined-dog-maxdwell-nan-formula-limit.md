# local/sandbox-combined-dog-maxdwell-nan-formula-limit — lessons

Project: local/sandbox-combined-dog-maxdwell-nan-formula-limit. Newest first.

---

## E1 — sandbox combined dog maxdwell nan formula limit
- Date: 2026-09-29
- Project: local/sandbox-combined-dog-maxdwell-nan-formula-limit
- Tags: [gamedev][state][testing][determinism]
- What: A sandbox composing dog#E11's max-dwell guaranteed exit with skilltree-formula#E5's silent NaN propagation: the dwell limit is a formula output that can turn NaN or infinite.
- Why built: dog#E11 says every FSM state needs an unconditional timeout, but that guarantee is only as good as the limit value feeding it; formula outputs are exactly where NaN appears without an error.
- Design: Deterministic FSM stuck in "approach" (data guard never flips), 2000 ticks, dwell counter increments per tick. Three exit forms: stay-while dwell < limit, exit-when dwell >= limit, and exit-when dwell >= limit with a non-finite limit clamped to a default of 50. Limits tried: 30, NaN, infinity.
- Got right: With a finite limit all three forms exit exactly once, so the standard dog#E11 test ("break the guard, assert the state is left") passes.
- Where/why it failed: With a NaN limit, the exit-when dwell >= limit form never exits (state stays approach, 0 exits in 2000 ticks) because every NaN comparison is false, while the stay-while dwell < limit form exits at once; with infinity both raw forms are trapped forever. Whether the guarantee survives depends on comparison direction, which no finite-limit test reveals.
- Fix: Validate or clamp the limit to a finite default before the comparison (only the clamped form exited under NaN and infinity, 1 exit each), and add a timeout test that feeds a NaN and an infinite limit.
- Why this fix: A comparison against NaN is false in both directions, so the only robust guarantee is to make the limit itself finite rather than choose a comparison form.
- Rule of thumb: A max-dwell timeout is a liveness guarantee only if its limit is finite; clamp formula-derived limits and test the exit with NaN and infinity, not just small numbers.
- Provenance (verified/assumed): Verified first-hand by running the sandbox script; the exit counts above are the observed output for limits 30, NaN and infinity.
- Composed: dog/E11, sandbox-combined-skilltree-formula/E5
- Link: brain train pass 2, 2026-09-29

