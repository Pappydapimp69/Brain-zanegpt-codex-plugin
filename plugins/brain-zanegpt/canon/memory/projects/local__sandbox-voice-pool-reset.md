# local/sandbox-voice-pool-reset — lessons

Project: local/sandbox-voice-pool-reset. Newest first.

---

## E1 — pooled voice reacquire inherits stale envelope
- Date: 2026-07-26
- Project: local/sandbox-voice-pool-reset
- Tags: [audio][animation][state][testing][realtime][gamedev]
- What: Two recorded lessons composed: `anim/E4` — an animation FSM's
  per-clip state (frame index, time accumulator, done flag) must reset on
  every transition; sharing the animator's fields leaks the previous
  clip's frame/timing, so a new clip starts on the old clip's frame instead
  of frame 0 — and `audio-realtime/E3` — for audio resume paths, verify
  continuity and callback budget SEPARATELY; "state resumes correctly" is
  not evidence a specific repair/reuse path is correct. Tested claim: a
  pooled audio voice reused across `play()` calls is the exact same shape
  of FSM as an animation clip — "clip" is "note," "frame" is "envelope
  phase/level" — so the identical bug (reset only the fields that look
  load-bearing, not the whole per-instance state) reproduces exactly, and a
  coarse continuity check ("is the mixer still producing sound") is an
  audio-specific instance of the check E3 says is insufficient.
- Why built: To test whether anim/E4's per-clip-FSM-reset lesson and
  audio-realtime/E3's coarse-continuity-check warning both generalize to a
  pooled audio voice, which is the same FSM shape as an animation clip
  under different vocabulary.
- Design: Modeled a simple attack/decay/sustain/release voice, forced pool
  reuse (one voice, so a retrigger during release MUST recycle it — the
  realistic case for a rapid-fire sound like footsteps or UI clicks against
  a small pool), and compared resetting only `done`/`position` (the fields
  that "obviously" need it for a new note) against a full reset including
  envelope phase and level.
- Got right: Sweeping across 18 different release-fade depths at retrigger
  time, rather than testing one arbitrary instance — which is what showed
  the bug is structural (reproduces on every depth) rather than a rare
  timing coincidence.
- Where/why it failed: The buggy reset started the "new" note's first
  rendered frame at 0.630 instead of the correct attack-curve value ~0.833
  — inheriting the previous note's mid-release level as if it were the new
  note's starting point instead of silence. Swept across 18 different
  release-fade depths at retrigger time: 18/18 wrong under the partial
  reset, 0/18 wrong under the full reset. Not an edge case — every single
  retrigger during an in-progress release is affected, because the bug is
  structural (a field never reset), not timing-dependent. The coarse
  continuity check cannot see it either: a mixer-level "is total output
  nonzero" check — the audio-specific version of "does playback resume" —
  reported `true` identically in both the buggy and fixed cases (1.330 vs
  1.533, both nonzero), because two OTHER voices were carrying ambient
  sound throughout. The broken voice IS producing audio, just audibly
  wrong; a check that only asks "is anything playing" is structurally
  blind to "is THIS specific reused thing playing correctly" — exactly
  E3's warning, now demonstrated on the envelope-reset bug rather than the
  resume-repair-queue bug it was originally filed against.
- Fix: Reset the FULL per-voice state on every acquire — phase and level
  alongside position and the done flag — the same discipline anim/E4
  already prescribes for clip playback. There is no field that is
  "obviously fine because the voice was free": a voice mid-release is not
  yet free by wall-clock but can be forced into reuse by a small pool under
  load, at which point every field its FSM owns is live state that needs
  resetting, whether or not it looks load-bearing at the call site doing
  the resetting.
- Why this fix: Matches the discipline anim/E4 already prescribes for
  animation clips — reset every field the FSM owns on every
  transition/reacquire, not the subset that looks relevant to the caller —
  now confirmed to generalize to a structurally identical audio-voice FSM.
- Rule of thumb: A pooled/reused stateful object — an animation clip, an
  audio voice, a particle, a projectile — is a small FSM, and reacquiring
  it is a TRANSITION like any other: reset every field the FSM owns, not
  the subset that looks relevant to the caller triggering reuse. The
  caller usually only cares about the fields it's ABOUT to set (position, a
  new duration); it has no visibility into which OTHER fields a downstream
  `step()` depends on.
  And verify a reused/resumed voice by inspecting ITS OWN first rendered
  value against the correct curve, not by checking that the system as a
  whole is still making sound. A multi-voice (or multi-anything) system
  will mask a single broken instance behind everything else that's
  working, and "the mixer/renderer/system is not silent" is the trap:
  identical in the correct and incorrect case.
- Provenance (verified/assumed): Verified first-hand — deterministic
  sandbox (`sb-voice-pool-reset.mjs`, fixed dt=1/60, explicit
  trigger/release/retrigger schedule, no RNG). All numbers above are
  observed output.
- Composed: sandbox-anim/E4, sandbox-combined-audio-realtime/E3
- Link: projects/local__sandbox-anim.md,
  projects/local__sandbox-combined-audio-realtime.md
- Cited-by: 2026-09-05 · projects/pappydapimp69__brain.md#E31 · compatible · no sandbox · session 01WwnWBKT6iCY1qyip37moLX
- Audited: 2026-10-15 · modeled · Bridge recheck. I read E1 in full, its cited source local__sandbox-combined-audio-realtime#E3, and the later lesson that refuted E3 (pappydapimp69__brain-creative-training#E2, Polarity incompatible). That lesson refutes E3's claim that resume continuity and the drain-cap budget are orthogonal and can be verified separately: a capped drain delayed the state restore by 32 callbacks into a lasting phase slip while each check passed alone. E1 does not depend on that orthogonality. It borrows only E3's narrower warning that a coarse system-level check (here, the mixer is not silent) is not evidence that one specific reused path is right, and the refuting lesson actually reconfirms that warning (its peak meter read 1.000 on the broken render). So the bridge survives, though E1's What still paraphrases E3 as verify SEPARATELY, which is now the refuted half and should not be repeated as advice. The verdict is modeled, not pass, for two reasons. First, no stored sandbox exists: E1 names sb-voice-pool-reset.mjs as session-local and sandboxes/ holds no voice-pool file, so the 0.630 versus 0.833 first-frame value, the 18 of 18 versus 0 of 18 sweep and the 1.330 versus 1.533 mixer sums cannot be re-checked. Second, as described, the model largely assumes its answer: a partial reset that never clears level must start the next note at the old level on every release depth (the 18 of 18 is structural by construction), and the expected curve is defined as attack from silence. Real synth and game voice engines often retrigger from the current level on purpose, because snapping a 0.63 release to 0 is itself an audible click. So the Rule of thumb's reset every field the FSM owns covers a hand-written ADSR model, not real pooled voices, and its audio version should say reset to a defined start state such as a short fade from current level, then check the instance's own first frames against that curve. · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 2 pass 3
