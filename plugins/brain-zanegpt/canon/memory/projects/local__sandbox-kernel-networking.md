# local/sandbox-kernel-networking — lessons

Project: local/sandbox-kernel-networking. Newest first.

---

## E1 — buffered reconciliation still fails on stale acks and short buffers
- Date: 2026-09-28
- Project: local/sandbox-kernel-networking
- Tags: [networking][prediction][correctness][state]
- What: Applied the ideas kernel that client-side reconciliation must replay each unacknowledged step's buffered input, never the current input. The current-input bug reproduced in real Node, and buffered replay was correct only under two further conditions the kernel does not state.
- Why built: brain train gap listed the kernel as unapplied. Every earlier loop in this run was a Python model, so this one ran in real JavaScript to vary the substrate.
- Design: A grid mover predicted on the client each tick, with the server acking each input's resulting position after 4 ticks. 500 seeded 60-step input streams per setup. Four reconciliation variants: replay with the current input, replay the buffer after dropping entries up to the ack's sequence, drop one buffer entry per ack, and buffered replay that also ignores acks older than the newest seen. Setups: steady, server-side walls rejecting 5% of inputs, one ack in five delayed 2 ticks (arriving after a newer one), and a 12-tick latency with an 8-entry buffer. A run fails if any reconciliation leaves the client off the newest ack's position plus the inputs predicted since.
- Got right: Checking after every reconciliation instead of at the end. Once the last input is acknowledged every variant ends on the server's position, which hides all of these failures.
- Where/why it failed: For the kernel's example (right, right, up, up, up, acked after the first step) buffered replay gave [2, 3], matching the prediction, and current-input replay [1, 4]. Current-input replay failed 500 of 500 runs in every setup. Buffered replay and drop-one-per-ack both failed 0 of 500 steady and with walls, but 500 of 500 once acks arrived out of order, because an older ack rewound the client past inputs a newer ack had already cleared. Ignoring stale acks fixed that (0 of 500). With 12 ticks of latency and an 8-entry buffer every variant failed 500 of 500.
- Fix: Replay buffered inputs by sequence number, ignore any ack older than the newest one processed, and size the buffer for the worst latency, not the typical one.
- Why this fix: Reconciling from a stale ack restarts from an older server state with some inputs already discarded. A buffer shorter than the unacknowledged window loses inputs before any ack can cover them.
- Rule of thumb: Replaying buffered inputs fixes current-input reconciliation (500/500 runs wrong vs 0) only while acks arrive in order and the buffer covers the whole unacknowledged window: one ack in five arriving late broke it in 500/500 runs until stale acks were ignored, and an 8-entry buffer under 12 ticks of latency broke every variant.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b06.py loop 30 in Pappydapimp69/Brain, running real Node v22.22.2, deterministic seeded input streams. Observed: example [2, 3] vs [1, 4]; current-input 500/500 everywhere; buffered 0/0/500/500 and drop-stale 0/0/0/500 across steady, walls, reorder and short-buffer setups.
- Composed: ideas:NETWORKING/client-prediction/reconciliation-must-replay-buffered-inputs-not-current-input/a-naive-current-input-replay-corrupts-position-on-any-mid-window-direction-change
- Link: session 2026-09-28, brain train gap batch 6 loop 30
- Sandbox: sandboxes/2026-09-28__train-gap-b06.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E275 · compatible · sandboxes/2026-10-14__stamp-guard-stale-ack-and-double-advance.py · observed RESULT: PASS A-late naive 5/28 guard 0; A-dup naive 0 guard 0; B-skips naive 19 guarded 0 of 36; restart guard applies 0/3. The prediction was only partly right: duplicates did not break and late acks were wrong in a minority (5/28). · brain train auto pass 2, session_01CwpncTDkwf6YoSaQyXUsNe
