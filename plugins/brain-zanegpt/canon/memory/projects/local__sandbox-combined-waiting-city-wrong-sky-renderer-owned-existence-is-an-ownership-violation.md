# local/sandbox-combined-waiting-city-wrong-sky-renderer-owned-existence-is-an-ownership-violation — lessons

Project: local/sandbox-combined-waiting-city-wrong-sky-renderer-owned-existence-is-an-ownership-violation. Newest first.

---

## E1 — sandbox combined waiting city wrong sky renderer owned existence is an ownership violation
- Date: 2026-08-29
- Project: local/sandbox-combined-waiting-city-wrong-sky-renderer-owned-existence-is-an-ownership-violation
- Tags: [gamedev][state][architecture][rendering]
- What: A deterministic sandbox (five fixed ticks, no RNG) spawning an entity two ways — with a sim-side existence delay and with a renderer-only fade-in over an already-live entity — recording per tick whether the entity exists, can be hit by the player, and is visible.
- Why built: waiting-city#E4 records that a "shouldn't spawn instantly" complaint about something with gameplay stakes needs a sim-side existence delay, with the entity genuinely absent from state until a scheduled tick, rather than a renderer-only fade-in on a mechanically live entity. wrong-sky#E13 records the general ownership rule: store the minimal authoritative flag in sim state and derive appearance in the read-only renderer, never letting the renderer own progress. This tests whether E4 is a separate judgement call or an instance of E13.
- Design: A world stepping five ticks with a spawn scheduled at tick 3, run once with the sim withholding the entity until then and once with the entity present from tick 1 while the renderer fades it in from the scheduled tick. Hittability is read from sim state and visibility from the render alpha.
- Got right: A first construction's fade curve began before the scheduled spawn, making the entity visible throughout and hiding the very window under test; correcting the curve to start at the spawn tick exposed the invisible-but-hittable interval.
- Where/why it failed: The renderer-only approach leaves the raider hittable while invisible on ticks 1 through 3 — a three-tick window in which the player can be struck by something not yet drawn. The sim-side delay has no such window: the entity is absent from state and from the screen together.
- Fix: Decide spawn-delay implementation by wrong-sky#E13's ownership rule directly rather than by a case-by-case gameplay-stakes judgement — if a value the renderer holds can change an outcome, it is sim state, and a renderer-owned fade over a live entity is the renderer owning existence.
- Why this fix: waiting-city#E4 is framed as a judgement about whether a particular complaint has gameplay stakes, which requires correctly assessing each case. wrong-sky#E13 already supplies a mechanical test that decides it: the renderer derives, it never owns. Recognising E4 as an instance of E13 removes the judgement step and generalises to any future cosmetic-looking delay.
- Rule of thumb: waiting-city#E4's sim-side-delay requirement is an instance of wrong-sky#E13's renderer-derives-never-owns rule, not a separate judgement — sandbox-confirmed a renderer-only fade leaves the entity hittable while invisible for three ticks; if a renderer-held value can change an outcome it is sim state, which decides the case without assessing gameplay stakes.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b18/l36.py), including a first construction whose fade began before the scheduled spawn and hid the window; confirmed the renderer-only path is hittable-but-invisible on ticks 1, 2 and 3 while the sim-side delay has no such interval. the-game-the-waiting-city#E4 and the-game-wrong-sky#E13 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__the-game-the-waiting-city/E4, pappydapimp69__the-game-wrong-sky/E13
- Link: session_014mRpopK9xnhvk35tT8ozkX

