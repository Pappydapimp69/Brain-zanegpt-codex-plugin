# local/sandbox-combined-tickorder-cancel — lessons

Project: local/sandbox-combined-tickorder-cancel. Newest first.

---

## E1 — compose intra tick op order as authoritative state
- Date: 2026-07-13
- Project: local/sandbox-combined-tickorder-cancel
- Tags: [determinism][gamedev][input]
- What: Composing an intra-tick ordering bug (sandbox-dbz-combat/E1: a cancelable flag set in the phase-advance step, which runs AFTER input is sampled, opens the cancel window one frame late) with the deterministic-loop lattice principle (sandbox-combined-game-loop/E1: authoritative discrete state lives on the integer lattice, presentation is read-only) shows that the ORDER of (read-input) vs (advance-phase/set-flag) within a tick is itself authoritative discrete state, not a presentation detail: the same window and the same input timing produce a hit or a miss depending only on that order.
- Why built: To close the untested dbz-combat↔game-loop seam and confirm the composition reproduces.
- Design: Deterministic per-tick sim — a move becomes cancelable at tick 5; the player's cancel input arrives on tick 5. Compare (a) input-then-advance vs (b) advance-then-input; report the tick the cancel actually fires.
- Got right: Reproduced. input-then-advance: cancel fires never (missed — flag not yet set when input was read). advance-then-input: cancel fires at tick 5. The effective window shifts by exactly one tick from op order alone.
- Where/why it failed: If the phase transition (flag set) is ordered after input sampling — or worse, done in the float/presentation layer — the cancel window's real duration differs from its declared duration by a tick, dropping combos that should connect, with nothing logged.
- Fix: Treat intra-tick operation order (input sample vs state advance) as part of the authoritative discrete state machine (game-loop/E1's integer lattice), fix it explicitly, and set gating flags before the input read that must observe them — never in a presentation/float pass.
- Why this fix: A window is only as correct as the tick on which its gating flag becomes visible to the reader; that visibility is decided by op order, which is authoritative, so it must be pinned, not left implicit.
- Rule of thumb: The order of (read-input) vs (advance-phase/set-flags) inside a tick is authoritative discrete state, not presentation — a gating flag set after the input sample opens its window a tick late (same window, same input, hit vs miss); pin the intra-tick order on the integer lattice and set gate flags before the read that must see them.
- Provenance (verified/assumed): Verified first-hand — deterministic tick sim this session: cancel input on the opening tick fires never under input-then-advance, fires on-tick under advance-then-input. Built and observed.
- Link: this session's sandbox (sb3_cancelorder.py); source entries sandbox-dbz-combat#E1 and sandbox-combined-game-loop#E1.
- Composed: sandbox-dbz-combat/E1, sandbox-combined-game-loop/E1

