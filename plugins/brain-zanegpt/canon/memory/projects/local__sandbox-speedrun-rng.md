# local/sandbox-speedrun-rng — lessons

Project: local/sandbox-speedrun-rng. Newest first.

---

## E1 — frame seeded rng is fully manipulable by timing
- Date: 2026-07-20
- Project: local/sandbox-speedrun-rng
- Tags: [algorithm][determinism]
- What: A PRNG whose state advances exactly once per frame regardless of
  player input, consumed at the moment a player triggers an action, is
  fully manipulable — for EVERY possible outcome, a specific frame-delay
  exists that deterministically produces it, so a player able to control
  frame-perfect timing can select any outcome at will, with no real
  randomness protecting it. Mixing in a per-session salt unknown to the
  player (fixed for the run, not derivable from frame-timing alone)
  breaks the majority of those frame-delay mappings.
- Why built: `brain train new-domain`, seeding SPEEDRUN as a genuine gap
  (`brain query` returned broad tag-noise only, nothing organized as a
  domain around RNG-manipulation/anti-manipulation craft). This is the
  well-documented real-world "RNG manipulation" technique speedrunners
  use in many shipped games (Ocarina of Time, Pokémon, and others).
- Design: `sandbox.py` — a small deterministic LCG, zero true
  randomness anywhere. `frame_seeded_roll(start_state, frame_of_trigger,
  n)` advances the LCG once per frame from a fixed start state and
  returns `state % n` at the trigger frame — the buggy pattern.
  `find_frame_for_outcome` is the speedrunner's own algorithm: brute-
  force search over frame delays (0..500) for one that produces a
  target outcome. `session_mixed_roll` is the fix: XOR a fixed session
  salt into the state before advancing.
- Got right: found a valid manipulating frame-delay for ALL 6 possible
  outcomes of a modeled 6-outcome roll (e.g. a critical-hit table), not
  just one — confirming full manipulability, not a partial/lucky case.
- Where/why it failed: for every one of the 6 outcomes, the exact same
  frame-delay found by the search reliably reproduced that outcome when
  fed back through `frame_seeded_roll` — full manipulability confirmed.
  Re-using those SAME 6 frame-delays against the session-salted version
  broke 4 of the 6 mappings (only 2 coincidentally still matched) —
  confirming the salt genuinely disrupts frame-timing-only prediction,
  though it does not (and isn't claimed to) make the RNG itself
  unpredictable in general, only unpredictable via frame-timing alone
  without knowing the salt.
- Fix: never derive a consumed RNG roll purely from a value that's a
  pure function of frame count/timing the player controls (frame
  count, elapsed real time since a fixed epoch) — mix in something the
  player cannot control or predict from timing alone (a per-session
  seed drawn from a real entropy source at boot, not derived from when
  the roll happens to be consumed).
- Why this fix: the vulnerability isn't the RNG algorithm's quality —
  the LCG itself is a perfectly fine generator — it's that the STATE
  FED INTO IT is entirely observable/controllable by the player via
  input timing; any deterministic function of a player-controlled input
  is exploitable regardless of how "random-looking" its output
  distribution is.
- Rule of thumb: before shipping any "random" game outcome a speedrunner
  or competitive player might want to control (crit chance, loot drops,
  enemy spawn variety), check whether the RNG state consumed at that
  roll is a pure function of something the player can control the exact
  TIMING of (frame count, elapsed frames since level start) — if so, it
  is manipulable regardless of the underlying algorithm's statistical
  quality, and the fix is mixing in session-scoped entropy the player
  cannot derive from timing, not "using a better PRNG."
- Provenance (verified/assumed): Verified first-hand — ran `sandbox.py`
  (zero true randomness; the LCG is deterministic by design, which is
  exactly the property under test), confirmed all 6 outcomes
  independently manipulable via frame-delay search, and confirmed the
  session-salted version breaks 4/6 of those same mappings. Re-ran as
  two independent process invocations; output byte-identical both
  times.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  new-domain`, speedrun-RNG gap); sandbox
  `scratchpad/loop7/speedrun/sandbox.py`, run twice as independent
  process invocations, outputs diffed identical
- Cited-by: 2026-10-11 · projects/pappydapimp69__brainwork.md#E107 · compatible · sandboxes/2026-10-11__salted-hash-round-robin-dealing-blocks-id-steering-but-costs-stability.py · observed RESULT: PASS unsalted 6/6 steerable; unknown salt 1/6 hits; leaked 1/1; moved session 0.85 deploy 0.00 add-one 0.76 · scheduled brain train session; session_019pmW8Yty9p54AwvJD8tq1s
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E259 · compatible · sandboxes/2026-10-14__seeded-rng-full-state-save-vs-seed-count-and-where-single-stream-stops-holding.py · observed RESULT: PASS full-state True cost 4 vs 10000; leak distinct 3/3; frame-seed manipulable 6/6; order divergence 28/30 · session_017SJAeaijx8mHKPVUZV6hJB brain train auto loop 1 pass 1
