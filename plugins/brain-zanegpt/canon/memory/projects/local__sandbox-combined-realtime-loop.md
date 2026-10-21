# local/sandbox-combined-realtime-loop — lessons

Project: local/sandbox-combined-realtime-loop. Newest first.

---

## E1 — realtime loop fingerprint across frame rates
- Date: 2026-07-13
- Project: local/sandbox-combined-realtime-loop
- Tags: [determinism][gamedev][state]
- What: A real-time loop stacking three timing-sensitive systems — a fixed-timestep accumulator (combined-game-loop), an input cadence (the-game-the-recursion), and a cancelable combat move (dbz-combat) — is frame-rate-independent only when EVERY discrete gate is driven off the integer tick lattice. Verified from a fresh integration angle: the whole loop's discrete-event fingerprint (tick total, cadence steps, cancel events) is byte-identical across two frame schedules.
- Why built: To raise independence on the single-source timing edges (cadence↔game-loop, tickorder↔game-loop) by re-verifying them together, and to record that a per-timer check doesn't cover the integrated loop.
- Design: Deterministic fixed-timestep loop; each tick advance the combat phase (set cancelable) then sample the cadence (correct op order); record (ticks, steps, cancels, cancel-tick fingerprint); run at 6ms and 33ms frame schedules over the same held duration and compare.
- Got right: The full event fingerprint was identical across frame rates — 6ms: ticks=125 steps=20 cancels=19; 33ms: identical. The integrated loop is frame-independent, corroborating the pairwise cadence and op-order edges from a combined angle.
- Where/why it failed: N/A here — the integration held. The meta-lesson: any ONE discrete gate left on float dt (cadence, cancel window, cooldown) would desync the whole fingerprint, and a per-timer unit test wouldn't reveal that the composed loop diverges.
- Fix: Verify a real-time loop's ENTIRE discrete-event fingerprint (every gate: cadence, cancel windows, cooldowns) across multiple frame schedules, not each timer alone; any divergence localizes the gate still on wall-time.
- Why this fix: Frame-independence is a property of the whole loop's authoritative event stream; only fingerprinting the composed run at multiple frame rates proves no gate leaked wall-time in.
- Rule of thumb: A real-time loop stacking a cadence + combat + fixed-timestep is frame-independent only if EVERY discrete gate is on the tick lattice — verify the whole loop's discrete-event fingerprint across multiple frame schedules, not each timer in isolation.
- Provenance (verified/assumed): Verified first-hand — deterministic integration sandbox this session (6ms and 33ms schedules produced identical ticks=125/steps=20/cancels=19 and identical cancel fingerprint). Built and observed.
- Link: this session's sandbox (sbT.py); source entries sandbox-combined-game-loop#E2, the-game-the-recursion#E16, sandbox-dbz-combat#E1.
- Composed: sandbox-combined-game-loop/E2, the-game-the-recursion/E16, sandbox-dbz-combat/E1

