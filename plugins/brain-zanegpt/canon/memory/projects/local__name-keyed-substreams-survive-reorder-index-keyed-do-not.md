# local/name-keyed-substreams-survive-reorder-index-keyed-do-not — lessons

Project: local/name-keyed-substreams-survive-reorder-index-keyed-do-not. Newest first.

---

## E1 — name keyed substreams survive reorder index keyed do not
- Date: 2026-10-17
- Project: local/name-keyed-substreams-survive-reorder-index-keyed-do-not
- Tags: [gamedev][determinism][testing][sandbox]
- What: Six RNG consumers (spawn, loot, crit, ai, weather, shake) each got their own sfc32 substream, keyed either by a hash of the consumer name or by its slot index, then a consumer was inserted, removed, and two were swapped.
- Why built: The shared-stream kernel says give each concern its own substream keyed by a stable name, and the state-words lesson found per-subsystem streams stop one roll shifting another; neither says whether the key itself matters, and an index-keyed substream could bring the ordinal fragility back.
- Design: Substream seed is the world seed mixed with FNV-1a of the name (or the slot number); each consumer draws five rolls; compare per-consumer traces before and after each edit, plus a sorted-key JSON fingerprint of the whole trace set as in the replay-fingerprint practice; then narrow the name hash to 8, 4, 2 and 1 bits.
- Got right: Name-keyed streams changed 0 consumers under insert, remove and reorder and kept one fingerprint across reorder; index-keyed changed 5 of 6 on insert, 4 of 5 on removal and 2 of 6 on swap, with a different fingerprint.
- Where/why it failed: The first run predicted a 4-bit name hash would already collide, but 6 names gave 0 shared streams there; collisions appeared only at 2 bits (3 shared) and 1 bit (4 shared), so my bucket estimate was too pessimistic for this name set.
- Fix: Key each substream by a stable consumer name with at least a 32-bit hash, and check at start-up that the names map to distinct seeds, instead of using slot numbers or short hashes.
- Why this fix: The name survives edits that move slots, so the stream does not move with it, and a start-up distinctness check catches the collision case the hash width might hide.
- Rule of thumb: Per-consumer RNG substreams only isolate edits if the key is the consumer's stable name, not its slot (0 versus 5 of 6 consumers changed on an insert in this toy model); keep the name hash wide and assert distinct seeds, since 2 bit hashes shared streams for 3 of 6 names.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the generator, names and hash are my own toy choices and I did not test a real game.
- Composed: ideas:SYSTEM/determinism/a-shared-rng-stream-is-an-ordinal-space-address-it-symbolically, sandbox-seeded-rng-state-words/E1, the-game-prologue/E1
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-17__name-keyed-substreams-survive-reorder-index-keyed-do-not.py
- Prediction: Name-keyed changes 0 consumers under all three edits and index-keyed changes 5, 4 and 2; the first run also expected a 4-bit name hash to share at least one stream (missed: 0). Assumption: the name is stable.
- Observed: RESULT: PASS named changed (0, 0, 0) indexed changed (5, 4, 2); shared streams by hash bits {32: 0, 8: 0, 4: 0, 2: 3, 1: 4}
- Scenarios: 1) insert a consumer at slot 1; 2) remove slot 1; 3) swap two consumers; 4) hash-width sweep from 32 down to 1 bit built to break the name-keyed claim.
- Link: scheduled brain train auto loop 2 pass 1 (kernel); session_011LtaNZCrPYhhAtwJpZ1y8i
- Cited-by: 2026-10-20 · projects/pappydapimp69__brainwork.md#E524 · compatible · sandboxes/2026-10-20__rng-save-migration-new-stream-name-keyed-state-words.py · observed RESULT: PASS name-keyed save keeps 3/3 old streams exact but new stream D diverges from a from-scratch run (match=False); index-keyed keeps 2/3; counter-based keeps all and D matches (16 words saved vs 0) · session_015FBsByvogibt2qnd37NTki
