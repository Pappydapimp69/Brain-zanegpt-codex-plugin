# local/sandbox-combined-mirage-opticon-redaction-is-itself-an-observation — lessons

Project: local/sandbox-combined-mirage-opticon-redaction-is-itself-an-observation. Newest first.

---

## E1 — sandbox combined mirage opticon redaction is itself an observation
- Date: 2026-08-29
- Project: local/sandbox-combined-mirage-opticon-redaction-is-itself-an-observation
- Tags: [security][gamedesign][ui][testing]
- What: A deterministic sandbox (fixed secret-state sequence, no RNG) modeling three presentation surfaces reading one hidden-state stream — a HUD stat, a secret-gated affordance, and a text log — and testing whether opticon#E9's prescribed multi-surface audit actually closes the leak when its remedy is redaction.
- Why built: opticon#E9 says fixing an information leak on one presentation surface does not mean a second surface reading the same event stream is safe, and prescribes auditing every consumer. mirage#E5 says that in a system with hidden state a REFUSAL IS AN OBSERVATION — gating an affordance on the secret makes its absence a perfect readout. This tests what happens when you follow opticon#E9's audit faithfully but patch each surface the obvious way, by hiding the value.
- Design: A five-tick secret sequence alternating lucid/hallucinating. Each surface is evaluated unpatched and patched, and each is scored by whether its observation sequence partitions the secret exactly — i.e. whether an observer can recover the hidden state perfectly from that surface alone.
- Got right: Scoring leakage structurally (does the observation sequence uniquely determine the secret) rather than by whether the surface "displays" the secret, which is what makes the redacted-but-still-leaking case visible instead of looking fixed.
- Where/why it failed: After patching, all three surfaces still leak perfectly. The redacted HUD emits `None` exactly when hallucinating; the redacted log does the same; the affordance was never redacted at all. The patch replaced one observable value with another observable value — absence — carrying the identical bit. opticon#E9's audit correctly enumerated every consumer, and applying the natural remedy to each left the leak fully intact.
- Fix: A hidden-state audit must specify the remedy shape, not just the surface list — the value must be replaced by something whose distribution is independent of the secret (a plausible decoy, or a value emitted on every tick regardless of state), never removed. Where an affordance genuinely cannot exist in one state, present it always and refuse on use, so the refusal is a constant-cost action rather than a state readout.
- Why this fix: opticon#E9's audit and mirage#E5's observation are about different halves of the same problem: E9 ensures you find every channel, E5 governs what a valid patch to a channel looks like. Following E9 alone produces a complete list of surfaces and a uniformly ineffective fix on each, which is worse than a partial fix because the audit's completeness reads as thoroughness.
- Rule of thumb: opticon#E9's every-consumer audit is only as good as its remedy shape — sandbox-confirmed that redacting each enumerated surface leaves all three leaking perfectly, because absence appears exactly when the secret holds (mirage#E5); replace the value with a secret-independent one or always present the affordance and refuse on use, never hide it.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b1/l4.py) and confirmed all three surfaces score leaks=True both before and after patching, with the patched HUD and log emitting None exactly on the hallucinating ticks. mirage#E5 and opticon#E9 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__mirage/E5, pappydapimp69__opticon/E9
- Link: session_014mRpopK9xnhvk35tT8ozkX

