# local/game-languages-gc — lessons

Project: local/game-languages-gc. Newest first.

---

## E1 — gc game loop pool the hot path incremental needs idle time
- Date: 2026-10-17
- Project: local/game-languages-gc
- Tags: [game-languages][performance][gc][sandbox]
- What: Seeded the new GAME-PROGRAMMING-LANGUAGES domain with Unity's documented garbage-collection behaviour,
  modelled as a 60 fps frame loop with per-frame allocation, full versus incremental collection,
  reference churn, frames with no idle time, and a pooled loop.
- Why built: Brain train newdomain: coding languages for games; canon had nothing on how a language's memory
  model meets a fixed frame budget.
- Design: Stdlib loop of 600 frames: 10 ms work and 50 KB allocated per frame, a collection when garbage reaches
  5000 KB costing 0.0004 ms per KB of a 40000 KB live heap; incremental marks in slices from each frame's
  idle time, pays 0.3 ms write-barrier tax, restarts marking when reference churn outruns a slice and
  falls back to a full collection after 3 restarts.
- Got right: Full collection put 6 frames over budget at 26.0 ms; incremental with idle time kept every frame within
  16.7 ms; the pooled loop never collected and every frame stayed at 10.0 ms.
- Where/why it failed: Incremental is not free: with heavy reference churn it fell back to full collections (5 spikes to 26.3 ms),
  and in a loop with no idle time (16.6 ms of work) its write-barrier tax pushed all 600 frames over budget.
- Fix: Pool or preallocate what the hot path creates each frame, and treat incremental collection as a
  spike smoother that needs idle frame time and modest reference churn, not as a substitute for pooling.
- Why this fix: Pooling removes the cause, while incremental only moves the cost into spare time that a tight or
  churn-heavy loop does not have.
- Rule of thumb: In a garbage-collected game language, keep the per-frame hot path allocation-free; incremental collection
  smooths spikes only when frames have idle time and references don't churn faster than it can mark.
- Provenance (verified/assumed): Verified first-hand by the sandbox; Unity's collector behaviour (incremental slices, idle-time use,
  write barriers, full-collection fallback, UnityEngine.Pool) checked against the Unity Manual. Heap
  sizes and costs are toy values.
- Composed: ideas:DSP/real-time-buffer/measure-worst-case-not-average, ideas:DSP/real-time-buffer/no-unbounded-work-in-the-callback
- Sandbox: sandboxes/2026-10-17__gc-game-loop-pool-the-hot-path-incremental-needs-idle-time.py
- Prediction: Full collection puts frames over 16.7 ms; incremental with idle time puts none over; heavy churn brings
  spikes back; no idle time puts frames over; pooling puts none over.
- Observed: RESULT: PASS full 6 frames over, worst 26.0 ms; incremental with idle time 0 over; heavy churn falls back
  to full, 5 spikes; no idle time (16.6 ms work + 0.3 ms barrier = 16.9 ms) 600 of 600 over; pooled 0 over, worst 10.0 ms.
- Scenarios: 1) full GC at 50 KB/frame; 2) incremental with idle time; 3) BREAK: incremental under heavy reference
  churn; 4) incremental with no idle time; 5) pooled loop
- ZaneGPT verdict: weak — the five scenarios confirm the author's own model and its hand-picked constants, so "PASS" is circular; the rule is plausible but untested at the idle-time and churn boundaries where it would actually break.
- Hidden assumption: The simulator's constants (50 KB/frame, 5000 KB threshold, 0.0004 ms/KB, 0.3 ms barrier, 3-restart fallback) and its idle-time-sliced marking model reflect real Unity behaviour, so the PASS shows Unity's collector at work only if the model is faithful, and the rule's "allocation-free" half is never tested against a cheaper alternative.
- Would prove it wrong: A run where lowering the allocation rate to 5 KB/frame, or enlarging the live heap or the threshold, flips the full-collection result to zero frames over 16.7 ms (or where the incremental run's marginal pooling gain vanishes), which would show the outcome tracks the invented constants rather than the rule; likewise a real Unity profile where incremental GC with churn does not fall back to a full pause.
- Break scenario: Keep incremental collection with idle time, but set work to 15.5 ms so idle is only about 1.2 ms and the 0.3 ms barrier plus a modest churn rate sit right at the slice limit: the rule predicts smoothing "when frames have idle time", yet marking never finishes before garbage refills, so it oscillates between restarts and full fallbacks while every frame also pays the barrier tax, meaning incremental is worse than plain full collection.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest ce25d66fb930
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

