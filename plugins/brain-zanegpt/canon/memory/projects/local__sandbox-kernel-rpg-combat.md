# local/sandbox-kernel-rpg-combat — lessons

Project: local/sandbox-kernel-rpg-combat. Newest first.

---

## E1 — a saturating damage cap bounds fights and keeps power deciding
- Date: 2026-09-28
- Project: local/sandbox-kernel-rpg-combat
- Tags: [combat][balance][gamedesign][measurement]
- What: Applied the ideas kernel that every damage curve collapses to one-shots past about 5-10x power, while capping per-hit damage at 20% of the defender's max HP holds fight length flat. Both held, and near parity the hard cap hands the fight to whoever moves first.
- Why built: brain train gap listed the kernel as unapplied. sandbox-power-scaling/E2 recorded the cap rule and brain-builder/E4 warned that a binding clamp erases stat variance; neither measured who wins inside the band where both sides are capped, or tried a cap that keeps power in play.
- Design: 1v1 fights, HP 10 x power, alternating first mover, 400 seeded fights per cell, per-hit jitter of plus or minus 10%, and base damage of 30% of the defender's HP at 1x. Six formulas: raw ratio, ratio capped at 5x, log, sqrt, min(raw, 20% of defender max HP), and a saturating cap of 20% of defender max HP x r/(1+r). Ratios 1 to 100000.
- Got right: Measuring win rate beside fight length. The kernel judged the cap on fight length alone, where it looks perfect.
- Where/why it failed: Ratio, capped-5x, log and sqrt damage fell to 1 or 2 hits by 5x to 10x and to 1 hit by 100x. The hard cap held the stronger side at exactly 5 hits from 1x to 100000x, but at 1.1x and 1.2x the stronger side won only 50%, the same as at 1x, because both sides hit the cap and the first mover decides; from 1.3x it won 99-100%. The saturating cap bounded the stronger side between 5.5 and 10.3 hits across the whole range and let the stronger side win 99% already at 1.1x.
- Fix: Scale damage as a saturating fraction of the defender's max HP (for example 20% x r/(1+r)) rather than a hard min(raw, 20%), so fight length stays bounded but a power edge still decides the fight.
- Why this fix: A hard cap binds on both sides once both deal at least the cap, so near parity it flattens both to the same hit count. A saturating curve reaches the cap only asymptotically, so any ratio above 1 still means more damage per hit.
- Rule of thumb: A hard percent-max-HP cap keeps fights at a flat 5 hits from 1x to 100000x but, while both sides reach the cap (here up to 1.2x), the stronger side wins only 50% because first move decides; a saturating cap (20% x r/(1+r)) keeps length between 5.5 and 10.3 hits and the stronger side winning 99% from 1.1x.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b04.py loop 20 in Pappydapimp69/Brain, deterministic seeded fights. Observed: uncapped curves 1 to 2 hits by 5-10x; hard cap 5.0 hits at every ratio with 50/50/50/100/99% stronger-side wins at 1/1.1/1.2/1.3/1.5x; saturating cap 10.3 to 5.5 hits and 48/99/100% at 1/1.1/1.2x. The 1.2x edge of the band depends on the 30% base damage chosen here.
- Composed: ideas:RPG/combat/percent-max-hp-damage-cap/the-only-fix-that-survives-a-100000x-ratio-sweep, sandbox-power-scaling/E2, brain-builder/E4
- Link: session 2026-09-28, brain train gap batch 4 loop 20
- Sandbox: sandboxes/2026-09-28__train-gap-b04.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

