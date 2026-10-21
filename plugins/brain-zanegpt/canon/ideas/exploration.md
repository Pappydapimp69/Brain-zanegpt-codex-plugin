# EXPLORATION — residue that isn't a kernel

*(Migrated 2026-07-02 from the frozen `creativity` repo's `creativity-log.md`,
per the Phase 1 ruling: Creativity is a section of `ideas`, not a node.)*

This file holds what the idea repository's artifact test **rejects** but the
system must not lose: experiments (tried or worth trying), syntheses staged
against a live goal, and speculations with no commitment yet. Roads considered
and **parked with a reason** do NOT live here — those are fork-shaped and go to
the `tension` ledger (type `alternative`).

**Sorting rule (objective, no judgment call):** run every fragment through the
artifact test in `README.md`. Passes → it's a kernel → file it in
`idea-repository.md` under its DOMAIN block. Fails → it's residue → it lands
here, typed and stated.

Entry types: `experiment` · `synthesis` · `speculation`.
States: `live` (in play, may still graduate) · `promoted` (graduated — the
entry stays, with a pointer to where it went) · `spent` (dead end, kept for the
record). State changes are dated annotations, never deletions.

---

## Project: Echoes of the Shattered Realm — Milestone 0

### A1 · *migrated out* → `tension` ledger T16
Engine paths not taken (Godot / Unity / Bevy, each parked with its reason and
revisit condition). Parked alternatives are fork-shaped; the ledger holds them now.

### E1 · experiment · sim-before-render (proved the loop in a terminal first) · **live**
We built the **entire game loop as a headless simulation** and asserted the five
success criteria (`npm run demo`) *before writing one line of renderer*. This
flipped the usual order (graphics first, systems bolted on). Result: the
architecture's hardest, least-reversible risks (state ownership, determinism) were
retired on day one, and "feel" was correctly isolated as the one thing graphics
must add. **Reusable as a method**, not just for this game: if a system's logic can
be expressed without its presentation, prove it without the presentation.

### E2 · experiment · replay-as-regression-test (deterministic golden runs) · **promoted → build (see E4)**
Because the sim is deterministic and randomness is seeded, a recorded *command
stream* + final-state hash is a perfect regression test: replay it, assert the
world matches. Cheaper and more total than unit-testing each system.
*2026-06-30: promoted — realized as the M1 deploy gate (E4).*

### S1 · synthesis · pull the dormant RPG kernels into this world · **promoted → build**
Staged cross-pollination of filed kernels against the active build:
[RPG / NPC-SIM / emergent-traits] → evolving village NPCs (relieves tension T4);
[RPG / combat / courtroom-boss / evidence-as-moveset] → an alternate lore-evidence
boss encounter; [RPG / progression / quests / offered-not-assigned] → the quest
system's offered-never-pushed rule (shipped in Cycle 4).

### S2 · synthesis · the Hollow King's lore from "legendary = survivorship bias" · **live**
From [RPG / narrative-design / legendary-transformation / survivorship-bias]:
his power was never legendary — every challenger died before anyone could explain
how ordinary he was. The "vigil" is the survivorship filter itself. A ready-made
narrative twist for the boss with zero new mechanics.

### Sp1 · speculation · two co-op paths, kept open · **live** *(fork-shaped — candidate for `tension` promotion when co-op is scheduled)*
- **Lockstep** (all clients run the deterministic sim, exchange only commands) —
  cheapest given the determinism we already have; fragile to any nondeterminism
  (ties to tension T2).
- **Authoritative server + state snapshots/deltas** — robust to nondeterminism,
  costs bandwidth + reconciliation. The command/event seam supports *either*; we
  don't have to choose until co-op is actually scheduled.

### Sp2 · speculation · day/night as a stealth/AI dimension, not just combat · **live**
Night already raises enemy aggression (a combat knob). Speculative extension: at
night husks *roam* and the village *locks down*, so the clock reshapes where you
can go and who's awake to talk to — turning one variable into a world-state dial.
No commitment; parked as a richness lever for after the slice.

## Project: Echoes of the Shattered Realm — Milestone 1 (Render Spine)

### E3 · experiment · graceful-degradation made the 3D app CI-verifiable · **live**
The render spine keeps its update loop (time, movement, HUD, command dispatch)
*separate* from the draw call, so when WebGL is unavailable it skips only
`renderer.render` and runs everything else headless. That one split let a 3D app
be driven end-to-end in CI and fail loud on logic errors. Reusable: **isolate the
GPU-dependent line from the logic loop, and a graphics app becomes headlessly
testable.**

### E4 · experiment · realized E2 — replay-fingerprint as the M1 deploy gate · **promoted → build (`src/sim/replay.mjs` + Pages deploy gate)**
Two same-seed runs must fingerprint-match *and* match a golden value. Promotion
from speculation → shipped guard in one milestone; the loop working as intended.

### S3 · synthesis · the retrieval loop actually closed this milestone · **promoted → record (brain/cognitive-updates/milestone-1.md)**
Brain's retrieval changed the build before a line was written: `memory` lessons
from a *different* game (lockstep — clamp max frame delta, edge-gate inputs) went
straight into the render loop; `tension` (T2) dictated movement stay cosmetic.

### Sp3 · speculation · data-drive the camera/combat *feel* in M2 · **promoted → build (see Sp5)**
Pull tunables into a `feel.json` so the M2 combat/feel pass is iterable by JSON
edit during live playtesting, not a recompile.

## Project: Echoes of the Shattered Realm — Milestone 2 (Mobile combat + controller)

### E5 · experiment · headless WebGL + touch emulation as the "is it playable" gate · **live**
Drove the *entire* mobile slice (create→quests→real-time combat→boss→victory) in
headless Chromium with a touch/WebGL emulated phone context, through exposed
`window.__game` hooks. Reusable method: expose a thin command-hook surface on any
interactive app and a headless driver can complete it.

### S4 · synthesis · the architecture *suggested* the dodge implementation · **promoted → `idea-repository.md` [SYSTEM / gamedesign / iframes-as-command-withholding]**
Invulnerability = *withhold the damage command*. No new state, no sim change.

### S5 · synthesis · one command vocabulary made the 4th input device trivial · **promoted → `idea-repository.md` [SYSTEM / input / unified-command-vocabulary]**
Keyboard, touch, mouse, gamepad all reduce to {move-vector, look-delta, attack,
interact, dodge}; adding Xbox was a ~20-line adapter.

### Sp4 · speculation · perceptual-diff screenshots to attack T11 · **live**
Golden-screenshot perceptual diffs at fixed camera/time/seed — brittle, but might
catch gross visual regressions (black screen, missing meshes, broken shader).
Worth a spike; pair with the deterministic seed so frames are reproducible.

### Sp5 · speculation · realized Sp3 — feel.json is live · **promoted → build**
Move speed, time scale, camera, aggro/melee/cooldowns all live in `feel.json`;
the M2 tuning pass was a JSON edit, no recompile.

## Cross-project mining (Shadow, Dog Park) → applied to the RPG

### S6 · synthesis · the full external→mine→file→apply→build loop closed · **promoted → record**
External repos were fed in (Shadow soundboard, Dog Park 3D), mined into
`ideas`/`memory`, and those lessons were applied straight back into the RPG in
one cycle (spatial audio, `safe()` guards, cache-busting, ambience). Knowledge
from *other* projects concretely fixed *this* project's weak spots — the
strongest evidence yet that the nodes beat working solo.

### Sp6 · speculation · sandbox self-play for breadth, external repos for novelty · **live**
Standing cadence: every 5 build-generations, spin up a randomly-chosen orthogonal
sandbox project, mine it for 5 turns, discard the code, keep the lessons. Watch
for the echo-chamber risk: does sandbox mining yield anything not already implied
by what's known?

---

## How the Brain orchestrator uses this file
During retrieval, after mining `idea-repository.md`: scan the **live** entries
for an experiment worth running now or a synthesis/speculation ripe to promote.
During write-back: residue that fails the artifact test lands here; anything that
graduates gets its state flipped to `promoted` with a pointer, in the same commit.

### E6 · experiment · one explainer film mutated three times chasing an audience · **live**
The film entry in the Picture House vote (vs the data Garden) drifted through three
distinct forms under owner feedback, and the experiment's question changed with it:
(1) "The Lesson & the Seed" — a cute two-protagonist drama; (2) "The Sentence I Didn't
Want to Write" — a first-person auditor confession with a real moral choice at the
climax (the strongest STORY form), built then set aside as the entry; (3) "The Robot
Who Kept Forgetting" — a plain-language picture-book explainer (pictures carry the
meaning, few words on screen), then made vibrant with a gentle music bed. So the vote
no longer measures drama-vs-map; it now measures **explainer-vs-map** (fork tracked as
tension T18). Road kept in git, not re-walked: the auditor-confession STORY cut — reach
for it if the goal flips back to *move the viewer* rather than *teach* them.

### S7 · synthesis · graft an emotional arc onto the explainer without losing clarity · **live**
Staged against the live goal (win the vote with a clear-AND-affecting film). From an
ideas mine: fold the filed `[narrative-design/AI-fiction/fresh-instance/inherited-files]`
existential arc (the robot wakes unmoored, acting on rules it never wrote -> the two
jars become *belonging*) plus one `[RPG/.../survivorship-bias]` style reveal (forgetting
reframed weakness -> superpower) onto the picture-book explainer. Hypothesis: keeps the
explainer's comprehension win while adding the *feeling* the plain chronicle lacks —
reconciling the `chronicle-is-not-a-story` memory with the teach-first objective.
Promote into the next film version if we iterate before staking.

## Project: Opticon 3D — Milestone 1

### E1 · experiment · tier-capture-exposure-by-difficulty-for-ai-vs-ai-balance-sim · **live**
In an asymmetric stealth game whose difficulty knob is *bluff frequency*, an
AI-vs-AI balance simulator scores every difficulty tier identically — the knob
only bites a human reading the seeker's gaze, which the sim has no model of.
Experiment: make the capture-exposure rule itself scale with difficulty — easy =
caught only if lit; medium = lit OR on a fresh noise tile; hard = lit OR noise
within 1 tile. That turns difficulty into a *mechanical* lever the simulator can
score, so difficulty ordering becomes automatically verifiable instead of
playtest-only. Status: proposed, not yet run (Opticon shipped beta with
bluff-only tiers). Relates to the open tension "is an AI-vs-AI sim a valid
balance oracle for a human-facing threat model?".
Source: Opticon 3D milestone-1 (2026-07-24), game/tests/balance.mjs.

---

## Project: Brain films

### S8 · synthesis · next Brain film: a week of self-repair, not a trial verdict · **live**
Snapshot (2026-10-17, owner: keep as a snapshot for now). Concept for the
film after "Brain" (v6) and "Five Days": the week since Oct 12 told as a
system catching its own mistakes. The age-cutoff flood purged (lessons 2,472
to 1,827, back to 2,141 by real growth); the ideas steward jammed 30 hours by
8 bad Linked lines until fixed; three projects found split under two names and
merged through the real steward (27 lessons moved, 7 age-cutoff remnants
dropped); a citation pointing at the wrong E1 corrected; intake guards added
so unresolved citations and split project names are held. The paths
two-halves trial appears only as a closing card ("verdict pending, may be
inconclusive"), never as the climax: its data is contaminated (forced picks,
other sessions, the new half reinforcing its own path) and its 7-day reuse
score favours older lessons. Craft notes from Brain: run growth on an event
clock so the purge reads as one sharp event; keep caption warp near 1.5x;
label tension counts as tracked, open from the tool's own classifier.
Graduates when the owner commissions the film.
Source: ZaneGPT pressure test and `brain query film`, session_015qgYN9GL7cHD9BS1wmwyMx.
