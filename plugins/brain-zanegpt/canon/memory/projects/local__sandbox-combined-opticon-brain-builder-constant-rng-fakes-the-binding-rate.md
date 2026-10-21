# local/sandbox-combined-opticon-brain-builder-constant-rng-fakes-the-binding-rate — lessons

Project: local/sandbox-combined-opticon-brain-builder-constant-rng-fakes-the-binding-rate. Newest first.

---

## E1 — sandbox combined opticon brain builder constant rng fakes the binding rate
- Date: 2026-08-29
- Project: local/sandbox-combined-opticon-brain-builder-constant-rng-fakes-the-binding-rate
- Tags: [testing][balance][simulation][method]
- What: A deterministic sandbox (2000 iterations, explicit LCG vs stubbed constants) measuring brain-builder#E4's clamp binding-rate instrument under a correct seeded PRNG and under three constant-RNG stubs of the kind opticon#E20 warns about.
- Why built: opticon#E20 records that making a sim deterministic with a CONSTANT rng turns every `rng() < p` into a fixed branch, silently switching off probability parameters. brain-builder#E4 prescribes instrumenting a clamp's binding RATE to tell a load-bearing cap from a harmless backstop. This tests what E4's instrument reports when E20's bug is present upstream of it.
- Design: A damage roll with a 30% crit branch that pushes damage above a 25.0 cap, run 2000 times under four RNGs — a seeded LCG and constants 0.0, 0.5 and 0.99 — recording the fraction of hits where the cap actually clamped.
- Got right: Testing three different constant values rather than one, which shows the reported rate is a readout of the stub's value relative to the branch threshold, not a single fixed artifact that might be mistaken for a coincidence.
- Where/why it failed: The seeded PRNG returns 0.298, correctly recovering the true 30% crit rate. Every constant stub returns a degenerate 0.000 or 1.000 — constant 0.0 gives 1.000 (always crits, cap always binds), constants 0.5 and 0.99 give 0.000 (never crits, cap never binds). The instrument reports a crisp, confident number in every case and has no way to signal that its input was stubbed.
- Fix: Assert that a probabilistic sim's observed branch rates match their configured probabilities before trusting any downstream instrument built on them, and never accept a binding rate of exactly 0.000 or 1.000 without first confirming the RNG is live — a rate at a hard boundary is the tell.
- Why this fix: brain-builder#E4's instrument was introduced because a round constant in an outcome metric reads as coincidence rather than as a signal. Under opticon#E20's bug the instrument produces exactly such a round constant, so its diagnostic is not merely unavailable but inverted: 0.000 reads as "the cap is a harmless backstop, safe to keep" and 1.000 as "the cap binds always, retune it", and both conclusions are artifacts of the stub.
- Rule of thumb: opticon#E20's constant-RNG bug makes brain-builder#E4's binding-rate instrument actively misleading rather than unavailable — sandbox-confirmed the rate collapses to exactly 0.000 or 1.000 under three different constant stubs against a true 0.298 under a seeded PRNG; treat a binding rate at a hard 0 or 1 boundary as a live-RNG check, not a finding.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b1/l5.py) over 2000 iterations and confirmed the seeded PRNG yields 0.298 against a configured 0.30, while constants 0.0, 0.5 and 0.99 yield 1.000, 0.000 and 0.000 respectively. opticon#E20 and brain-builder#E4 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__opticon/E20, pappydapimp69__brain-builder/E4
- Link: session_014mRpopK9xnhvk35tT8ozkX

