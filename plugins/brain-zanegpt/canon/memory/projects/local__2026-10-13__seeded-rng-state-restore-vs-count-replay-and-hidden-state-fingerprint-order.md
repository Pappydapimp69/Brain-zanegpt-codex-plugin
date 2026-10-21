# local/2026-10-13__seeded-rng-state-restore-vs-count-replay-and-hidden-state-fingerprint-order — lessons

Project: local/2026-10-13__seeded-rng-state-restore-vs-count-replay-and-hidden-state-fingerprint-order. Newest first.

---

## E1 — seeded rng state restore vs count replay and hidden state fingerprint order
- Date: 2026-10-13
- Project: local/2026-10-13__seeded-rng-state-restore-vs-count-replay-and-hidden-state-fingerprint-order
- Tags: [gamedev][state][testing][determinism][sandbox]
- What: A mulberry32-style seeded generator saved and restored two ways (32-bit state versus replaying count draws), a state hash over insertion-ordered versus sorted-key JSON, and a generator with a cached spare gaussian that carries state outside the 32-bit word.
- Why built: Re-verify the seeded-rng kernel and its applied lessons: the prologue entry says a literal {seed,count} save replays count rolls on every load and that state hashes need canonical key order, and the test entry says to store {seed,count} in the saved world.
- Design: Count replay at 1000, 20000 and 200000 draws against a direct state restore, comparing the next five draws; two logically equal state objects built with different key order hashed with and without sorted keys; a gaussian generator that returns a cached spare on every second call, restored from state alone after 1 to 4 draws.
- Got right: Replay cost was exactly 1000, 20000 and 200000 steps against 1 for state restore, and the next five draws were identical in all three cases; the naive hash differed for equal states (9e31c7e4 vs 22aad5e5) while the sorted-key hash matched (c1dfb25b).
- Where/why it failed: The state-only restore is correct only while the 32-bit word is the whole generator state. With a cached spare gaussian it diverged on the next gaussian after 1 and 3 draws and matched after 2 and 4, so a restore that looks right at even draw counts hides the bug.
- Fix: Save every field the generator reads, including a cached spare or any buffered value, or restore by count replay when the generator has hidden state; test a restore after both an even and an odd number of draws.
- Why this fix: A single fixed-draw test passes half the time because the spare is empty at even counts, so only the parity pair exposes the missing field.
- Rule of thumb: Restore a seeded stream from its full state, not a bare count, when the generator is a one-word PRNG, but save any cached value too and check the restore at both odd and even draw counts; hash state with sorted keys, never raw insertion order.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; Python dict ordering stands in for the JavaScript behavior described in the prologue entry, which was not run in a JavaScript engine here.
- Composed: ideas:SYSTEM/seeded-rng, ideas:SYSTEM/replay-fingerprint, the-game-prologue/E1, test/E2
- Sandbox: sandboxes/2026-10-13__seeded-rng-state-restore-vs-count-replay-and-hidden-state-fingerprint-order.py
- Prediction: State restore costs 1 step against count steps for replay with identical next draws; the naive insertion-order hash differs for equal states while the sorted-key hash matches; a spare-gaussian generator restored from state alone diverges at odd draw counts and matches at even ones.
- Observed: RESULT: PASS state restore 1 step vs replay n steps with equal draws (n=1000,20000,200000); naive hash differs True canonical True; spare-gaussian state-only restore matches only at even draw counts {1: False, 2: True, 3: False, 4: True}.
- Scenarios: 1) restore at n=1000; 2) n=20000; 3) n=200000; 4) key-order hash pair; 5) spare-gaussian restore at k=1..4, built to BREAK the state-only restore claim.
- Link: brain train auto session 2026-10-13 loop 2; session_01WtWcTgcKWwuvhJ9RsCQX9c
- Cited-by: 2026-10-15 · projects/local__two-save-bugs-mask-each-other.md#E1 · compatible · sandboxes/2026-10-15__two-save-bugs-mask-each-other-so-fixing-one-doubles-divergence.py · observed RESULT: FAIL 4/5; diverged A 0, B 400, C 800, D 400 of 800; tick cross-check flags B 0, C 800, D 800 · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 2 pass 2 (edge), 2026-10-15
