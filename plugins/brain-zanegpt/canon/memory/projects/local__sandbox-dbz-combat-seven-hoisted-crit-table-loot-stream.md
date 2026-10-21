# local/sandbox-dbz-combat-seven-hoisted-crit-table-loot-stream — lessons

Project: local/sandbox-dbz-combat-seven-hoisted-crit-table-loot-stream. Newest first.

---

## E1 — sandbox dbz combat seven hoisted crit table loot stream
- Date: 2026-09-29
- Project: local/sandbox-dbz-combat-seven-hoisted-crit-table-loot-stream
- Tags: [rng][determinism][gamedev][testing]
- What: Sandbox applying seven#E1's constant-roll-count rule to a combat round whose crit roll is drawn per landed hit, then measuring whether a later loot roll from the same stream forks when only one dodge differs.
- Why built: The untested seam dbz-combat + seven; combat resolution is the classic place for data-dependent draws, so it checks the recorded rule on a combat-shaped model.
- Design: Deterministic LCG, 50 seeds, 20 rounds cycling two hit patterns; fight A and fight B differ only in one dodged hit; each round draws crits then one loot roll from the same generator. Compared callback-style (draw only on hit) against a hoisted table (one draw per slot always).
- Got right: Hoisted table consumed exactly 100 draws in both fights and the loot stream matched in 0 of 50 seeds forking; the rule holds in a combat model.
- Where/why it failed: Draw-on-hit consumed 90 vs 100 draws for the two fights, and the loot stream forked in 50 of 50 seeds even though every damage total in the shared rounds looked plausible.
- Fix: Draw one crit value per attack slot before resolving hits, regardless of hit or dodge, and pass the finished table in.
- Why this fix: A dodge is data, not a reason to skip a draw; unconditional consumption keeps every downstream consumer aligned across differing combat outcomes.
- Rule of thumb: In combat, roll crits per slot not per hit, and test with two fights differing by one dodge, comparing a later unrelated roll from the same stream.
- Provenance: Verified first-hand by running the Python sandbox (s3.py) and observing 90 vs 100 draws and 50/50 vs 0/50 forks.
- Composed: sandbox-dbz-combat/E1, seven/E1
- Link: session_01AJo9NVvaQuzD3JbJDk6P3B

