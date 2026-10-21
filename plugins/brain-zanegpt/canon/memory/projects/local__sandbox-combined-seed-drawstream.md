# local/sandbox-combined-seed-drawstream — lessons

Project: local/sandbox-combined-seed-drawstream. Newest first.

---

## E1 — compose seed with draw sequence invariance
- Date: 2026-07-13
- Project: local/sandbox-combined-seed-drawstream
- Tags: [determinism][algorithm][state]
- What: Composing "a fixed seed gives reproducibility" (dog/E12: one leaked entropy source breaks a seed) with "a value read inside a reducer can silently vary with incidental caller-side state that changes how many RNG draws happen" (the-game-the-recursion/E17) shows a seed is necessary but NOT sufficient: if incidental/cosmetic upstream work draws a variable number of values from the SAME prng stream before a gameplay draw, the gameplay value shifts even though the seed is identical. Reproducibility needs draw-SEQUENCE invariance, not just a seed.
- Why built: To close the untested recursion↔dog determinism seam and confirm it reproduces.
- Design: Deterministic sandbox — explicit LCG, same seed. Compare a gameplay draw taken after 0 vs 3 "cosmetic" draws on the SHARED stream, vs a gameplay draw taken from a SEPARATE dedicated stream unaffected by the cosmetic draws.
- Got right: Reproduced. Shared stream: cos=0 → 0.5823, cos=3 → 0.7770 (diverges under the same seed). Separate stream: 0.5823 either way (invariant). Seeding alone did not reproduce; stream separation did.
- Where/why it failed: A "cosmetic" or content-dependent branch (decorative effect count, a UI-driven code path) that happens to consume prng draws before the gameplay draw silently desyncs two same-seed runs/replays — no error, just a different world.
- Fix: Draw gameplay-affecting values from a dedicated prng stream (or fixed-count sub-stream) that no cosmetic/incidental code path can consume from; treat any draw whose COUNT depends on incidental state as a determinism leak, exactly like an unseeded source.
- Why this fix: Reproducibility is a property of the draw sequence a consumer sees, not of the seed alone; isolating the gameplay stream makes its sequence invariant to upstream branching.
- Rule of thumb: A fixed seed does not guarantee reproducibility — if any incidental/cosmetic code path draws a variable number of values from the same prng stream before a gameplay draw, the outcome shifts; give gameplay its own stream (or fix draw counts), and treat a branch-dependent draw COUNT as a determinism leak like an unseeded source.
- Provenance (verified/assumed): Verified first-hand — deterministic LCG sandbox this session: same seed, shared stream 0.5823 vs 0.7770; separate stream 0.5823 both. Built and observed.
- Link: this session's sandbox (sb2_drawstream.py); source entries the-game-the-recursion#E17 and dog#E12.
- Composed: the-game-the-recursion/E17, pappydapimp69__dog/E12

