# TENSION LEDGER

Unresolved contradictions, tradeoffs, assumptions, and open questions. A tension
is **not a bug and not a decision** — it is a fork the project is holding open on
purpose. Entries are preserved, not resolved away; when one *is* resolved, mark it
and record where the decision lives (don't delete it — the history is the point).

Each entry: **id · type · poles · current lean · status · source**.
Types: `tradeoff` (two goods in conflict) · `assumption` (a bet that could be
wrong) · `open-question` (genuinely undecided) · `contradiction` (two commitments
that can't both fully hold) · `alternative` (a road considered and parked, kept
with the reason and the revisit condition).

Status: 🔴 open · 🟡 leaning · 🟢 resolved (kept for the record) ·
⚪ superseded. Transitions are evidence-bearing `Updates:` appends — see
`README.md` for the full contract (resolved (evidence) vs resolved (decision),
lean expiry at 2 untouched milestones, cross-project promotion).

---

## Project: Echoes of the Shattered Realm — Milestone 0

### T1 · contradiction · "systems-over-data" vs a real ECS
Poles: a flat world + functions-in-the-reducer is right for one player and ~3
enemy kinds — minimum ceremony; **vs** a full Entity-Component-System scales to
many entity types but is overkill now.
Lean: 🟡 systems-over-data for the slice. Records are already a flat serializable
bag, so promotion to components is incremental.
Open sub-question: *what concrete signal* (entity count? system count? a specific
painful refactor?) means we've crossed the threshold? Undecided.
Source: ADR-0001/TDD; docs/07 open-question #6.

### T2 · contradiction · determinism vs a physics-driven renderer
Poles: lockstep co-op and exact save/load demand a deterministic sim (no float
nondeterminism); **vs** a 3D renderer naturally wants physics, which is
float-nondeterministic across machines.
Lean: 🟡 leaning (M1 evidence). M1 movement is kinematic & cosmetic — the sim
stores an *advisory* position via the MOVE command, but no authoritative outcome
reads it and the replay fingerprint stays bit-exact. The contradiction is *held
at bay*, not dissolved: it resurfaces the moment M2 adds real collision/physics
that wants to feed combat. Resolution so far: physics stays cosmetic; sim
positions are advisory.
Source: ADR-0007; docs/07 open-question #7. M1: web/game3d.mjs MOVE, src/sim/replay.mjs.

### T3 · contradiction · the "co-op without a rewrite" promise vs save schema
Poles: a single serialized `world` is perfect for single-player; **vs** co-op
needs per-client identity *inside* the world, which is a schema change.
Lean: 🔴 open. The "no rewrite" promise covers the **sim spine** (the
command/event seam), NOT the netcode or the schema migration it implies. Honest
scope of the promise is itself the tension.
Source: ADR-0007; docs/07 open-question #4.

### T4 · tradeoff · scripted quests vs emergent systems
Poles: scripted data-graph quests are authorable, testable, and shippable in a
slice; **vs** emergent systems create surprise but are unbounded in cost.
Lean: 🟡 scripted now, with objective *types* as the seam that leaves emergent on
the table. Preserved because "fallen civilization that feels alive" pulls toward
emergent.
Source: ADR-0005. Cross-link: `ideas` → [NPC-SIM / emergent-traits].
Updates:
- 2026-08-05 evidence for the emergent pole; lean NOT flipped — that call is the
  owner's. Smallmouth (pappydapimp69/smallmouth @395c933) is the first build to
  actually test this fork rather than park it. A 7-day town of 8 utility-scored
  agents produces an unauthored antagonist: agents repeat a rumour to the person
  it is ABOUT, because being the subject is not one of juicy/present/novel, and
  the resulting firsthand humiliation is what crosses the confrontation gate.
  Cost was not unbounded — ~700 lines of sim, 22 tests, every claim provable in
  a terminal because a social sim is pure state. But the emergent pole's real
  cost showed up in a different shape than "unbounded": two mechanics were
  unreachable under the system's own dynamics and nothing noticed for a whole
  milestone (`memory` → projects/pappydapimp69__smallmouth.md#E2). That is the
  honest counterweight — emergent systems are affordable to BUILD and expensive
  to KNOW, because "this beat never fires" subtracts nothing from any aggregate
  metric you are already watching. Cross-link: `ideas` →
  [NPC-SIM / social / reach-and-drama-as-independent-axes].

### T5 · open-question · soft death vs "fallen civilization" stakes
Poles: soft respawn keeps the slice friendly to demo/test; **vs** the tone wants
real stakes (souls-like recovery? permadeath toggle?).
Lean: 🟡 partly resolved by OFFERING BOTH (Cycle 4). A menu toggle now switches
Gentle (soft respawn) vs Harsh (lose half current-level XP on death), so the
fork isn't collapsed to one answer — the player picks the tone. Still open: no
soul-recovery/permadeath tier, and Harsh is shallow (XP only).
Source: docs/03 gameplay-loop; docs/07 open-question #2.

### T6 · tradeoff · data-driven flexibility vs lost compile-time safety
Poles: all content as JSON = cheap, unbounded authoring; **vs** a typo'd id ships
an uncompletable quest with no error — failure moves from compiler to player.
Lean: 🟡 stay data-driven, pay it back with a validation ladder (schema →
referential integrity → headless smoke test). Only the smoke-test rung exists today.
Source: docs/04; filed to `memory` (data-driven-needs-a-validation-ladder).

### T7 · open-question · how much progression depth does a *slice* need?
Poles: use-based skills add build divergence; **vs** in a 25-minute slice, extra
build axes may be noise. Currently blade trains on use; guard/lore are seeded but
inert — a deliberate placeholder.
Lean: 🟡 depth added (Cycle 4). Guard now use-trains on hits taken (feeds defense);
lore now gates the enemy-HP readout (Seeker sees numbers, Warden sees ???), giving
archetypes a real perceptual difference. Blade already use-trains. Still open: how
much is *noise* vs meaningful in a 25-min slice — unmeasured.
Source: ADR-0004; docs/07 open-question #1.

### T8 · assumption · hand-edited JSON scales to the slice
Bet: humans editing JSON by hand won't ship broken content faster than review
catches it — *for slice-sized content*. At higher volume this likely breaks and a
validating editor becomes necessary.
Lean: 🟡 holds for now; watch for the volume where it stops holding.
Source: docs/04; docs/07 open-question #5.

### T9 · contradiction · headless sim proves systems but cannot prove *feel*
Poles: the demo proves the loop is mechanically complete with zero graphics; **vs**
combat identity (timing, hit reactions, camera, lock-on) only exists once
rendered — the most important quality dimension is the one we can't yet test.
Lean: 🟢 resolved (evidence, 2026-10-08) — feel is not provable headless, but it
decomposes into failure modes that are, plus one human pass that is not. The
camera work of 2026-10-01 to 10-08 is the evidence: edge flicker measured
headless at 1.595 vs 0.221 units per frame (sandbox-kernel-motion-camera#E2),
a content-fit clamp proven with zero smoothing (#E1), a camera that lagged a
burst of 257 items caught by a screenshot and fixed by a per-frame content floor
(sandbox-combined-brain-viz-growth#E14) — and the remaining judgement ("does the
zoom feel right") made by the owner on the live page, in three rounds. So the
split is: flicker, lag, overshoot and clipping are headless assertions; pacing and
weight are a human look, scheduled as a step, never inferred from a green run.
Previous lean, kept for the record: 🟡 mostly addressed, quality unverified. M2
built real-time combat with lock-on, dodge i-frames, hit-stop/vignette/shake
juice, audio, and controller support — feel now *exists* and the full slice
completes headless. But whether it feels *good* is still a human judgement no
automated test makes (ties to T11). So: mechanically resolved, subjectively open.
Source: docs/05 risk R5; ADR-0006. M2: web/game3d.mjs. Resolution evidence:
memory sandbox-kernel-motion-camera#E1-E2, sandbox-combined-brain-viz-growth#E14;
session https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn.

### T10 · assumption · greybox-first keeps a "3D RPG" on schedule
Bet: boxy geometry + capsule characters is an acceptable interim for a deliverable
literally named "3D RPG," and art is a polish pass, not a foundation.
Lean: 🟡 holds; if "3D RPG" implies art-quality expectations to the audience, this
bet is exposed.
Source: docs/05 risk R3; docs/06 roadmap.

### T11 · open-question · automated 3D verification has a ceiling (logic, not looks)
Surfaced in M1. Headless Chromium + SwiftShader can verify the render spine's
*wiring* (it boots, the clock advances, input issues commands, traversal changes
zones — all asserted with no console errors) but NOT its *visual correctness*: a
wrong material, z-fighting, an inverted normal, or a broken shader all pass a
"no errors" test. Screenshots need a human eye.
Lean: 🔴 open. Partial mitigation: capture screenshots in CI for human review;
perceptual-diff against a golden image is possible but brittle for 3D. How to
guard visual regressions cheaply is unresolved.
Source: M1 headless verification (Playwright + SwiftShader).
- Updates: 2026-10-10 resolve pass 5: real headless render, 23 injected defects and 10 benign variations. A no-errors check caught 1/23; golden-diff caught 17/23 with 5/10 false alarms; a lighting-invariant suite caught 18/23 with 0 false alarms. The ceiling is narrower than stated (residual: luminance-only material changes, marginal z-fight, subtle shader drift). See projects/pappydapimp69__tension.md#E2.
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T12 · tradeoff · vendoring Three.js (repo bloat) vs a build step / CDN
Surfaced in M1. We committed ~2 MB of generated Three.js into `web/vendor/` so the
Pages site is self-contained and the headless test is hermetic — at the cost of a
large generated artifact living in git (against normal hygiene) and manual version
bumps.
Lean: 🟡 vendoring for now — self-containment and offline-verifiability beat repo
cleanliness for a slice. Revisit if the vendored surface grows (addons, multiple
libs) — then a real build step (Vite) earns its keep.
Source: M1 (web/vendor/, .github/workflows/pages.yml).

### T13 · tradeoff · input breadth vs combinatorial complexity
Surfaced in M2. Supporting keyboard + touch joystick + mouse-look + Xbox gamepad
(USB/BT) multiplies the input edge cases: pause-while-paused via gamepad Start,
joystick vs gamepad both writing the move vector, focus/blur with a pad held,
edge-detection per device. The unified-command-vocabulary kernel tames most of it,
but each device still has bespoke quirks (deadzones, autoplay-on-tap, pointer
capture).
Lean: 🟡 worth it — reach (phone + desktop + console-style) justifies the cost, and
the shared vocabulary contains it. Watch for the next device adding more than a
thin adapter; that's the signal the abstraction is leaking.
Source: M2 (web/game3d.mjs input + gamepad).

### T14 · tradeoff · synthesized SFX (zero assets) vs authored audio
Surfaced in M2. All sound is generated at runtime from oscillators + filtered
noise — zero audio files, tiny footprint, no loading, trivially tweakable. The
ceiling is real: it can't match recorded foley/music for richness or mood.
Lean: 🟡 synth for the slice (footprint + iteration speed win). If the project
wants a soundtrack or signature impacts, swap in authored assets behind the same
`sfx(kind)` seam — the call sites won't change.
Source: M2 (web/game3d.mjs audio).

### T15 · process · shipping cadence vs cognitive-logging cadence
Surfaced by direct observation this session. The standing rule fires the cognitive
loop at *milestone* boundaries. But a run of fast, user-driven bug-fixes (control
inversions, gamepad, menu bugs, UI overhaul) has no "milestone" — so the loop
silently lapsed: several real lessons (reused-modal stale state; gamepad
active-polling) were shipped to the build before being filed, and only got logged
when the user asked "are you communicating with brain?".
Contradiction: "keep replies short / ship fast" pulls against "route every lesson
through the nodes." The milestone trigger is too coarse for reactive patch work.
Lean: 🟡 add a second trigger — a lightweight per-fix filing bar ("did this fix
teach a non-obvious lesson? → drop it in incoming/ now"), not just per-milestone.
Don't let velocity silently switch the architecture off; that defeats the
experiment. Unresolved: the right cadence that keeps logging honest without taxing
every one-line fix.
Source: this session's control/UI patch series (PRs #6–#10).

### T16 · alternative · engine paths not taken (migrated from creativity A1)
Poles: Three.js + Vite + TS (chosen: verifiability + iteration speed in an
agentic/CI loop) **vs** parked roads, each kept with its reason:
- **Godot (GDScript/C#)** — best out-of-the-box for a 3D RPG (animation, physics,
  scene editor). Parked: editor-centric, binary scenes diff poorly, weaker to
  drive/verify headlessly. *Revisit if* art & animation volume becomes the
  bottleneck — the sim core is engine-agnostic, so a port is a renderer swap.
- **Unity** — powerful, but heavyweight and license/closed-tooling friction for a
  tiny slice.
- **Bevy (Rust ECS)** — beautiful determinism story (great for lockstep co-op),
  but a second language and slower iteration than the slice budget allows.
Lean: 🟡 Three.js holds. The choice was made on *verifiability and iteration
speed*, not raw 3D power — worth re-litigating per milestone, not silently
inheriting.
Updates:
- 2026-07-02 migrated from `creativity-log.md` A1 (Phase 1: creativity frozen;
  parked alternatives live here now). Lean carried over unchanged.
Source: creativity A1 (Milestone 0); ADR-0001/TDD.

---

## Project: cognitive-system (the architecture itself)

### T17 · assumption · Phase 1 convention survives reactive work without the Phase 2 gate
Bet: the rewritten specs (capture stubs, curate-at-milestone, evidence-bearing
transitions, "push what you write") are low-friction enough that a session under
reactive bug-fix velocity will actually follow them — *without* an involuntary
commit/CI gate refusing the wrong action.
Poles: convention-is-enough (the v2 specs fixed the friction that caused the
T15 lapse) **vs** the practitioner's law ("a discipline problem is never fixed
by a better convention — only by making the right action involuntary").
Lean: 🔴 open — deliberately. The practitioner's evidence says convention fails
under velocity; the specs changed since. Neither side has post-Phase-1 data.
Resolution path: the reactive-flurry verification — run a burst of small
user-driven fixes in a real build session on the v2 specs, then audit the gap
between lessons-that-should-have-filed and lessons-filed (survivorship diff:
`incoming/` timestamps vs build commits). If the gap is ~zero, close
resolved (evidence) and Phase 2's gate becomes optional hardening; if not,
Phase 2 is mandatory and this closes resolved (evidence) the other way.
Updates:
- 2026-07-02 opened during Phase 3 verification (cold-clone write-back test).
Source: practitioner post-mortem (T15 lineage); Phase 3 plan; Brain README
"provisional" flag — this entry is that flag, held accountable in the ledger.


### T18 · open-question · explain-to-teach vs tell-a-story (the vote film's north star)
Surfaced across the Picture House film iterations. The film entry in the audience vote
(vs the data Garden) swings between two goals that pull apart.
Poles: **engage** — a narrative with want/opposition/stakes/choice, which *moves* the
viewer (per the `chronicle-is-not-a-story` memory) **vs** **teach** — a plain
picture-book explainer where clarity wins and dramatic structure is deliberately
dropped (per the owner's stated objective: a non-expert must understand the memory
system). Story maximizes *feeling*; explainer maximizes *comprehension*.
Lean: 🟡 teach — the audience skews non-expert and clarity likely wins votes there;
but the S7 synthesis (fresh-instance existential arc + one survivorship reveal) may keep
clarity AND land emotionally, dissolving the fork.
Resolution path: the vote tally settles it (ties T9/T11 — only the human eye judges
this). If the explainer wins, teach-first is the default for novice-facing artifacts; if
the story cut would have won, the boundary added to the `chronicle-is-not-a-story` rule
needs tightening.
Updates:
- 2026-07-04 opened during the film-explainer arc; write-back per orchestration v2.
Source: this session's film passes; exploration E6/S7; ideas [SYSTEM/explainer].

### T19 · tradeoff · plot coherence vs perceived player agency (the "narrative paradox")
Surfaced by external research into interactive-narrative craft; relevant the moment
this game gives players real narrative choice. The field's defining fork.
Poles: **coherence** — every event should build meaningfully on prior events toward
the outcome (a satisfying authored arc) **vs** **agency** — the player must feel their
decisions are free and meaningful. They fight because free player action can inject
states the authored arc can't build on, and fully pre-authored branching that would
honor both does not scale (content grows exponentially per choice point).
Lean: 🟢 resolved (evidence). The convergent resolution from the research: a
fixed authored spine + an invisible drama/experience manager that selects vetted
variants (memory E5), option-PRESENTATION steering rather than branch-pruning
(ideas [.../steer-by-presentation]), and salience/quality-based selection
(ideas [.../salience-selector]). These steer ~70-74% of choices while removing no
branch — structural agency intact. Sandbox-verified 2026-07-18 (see Updates):
committed playstyles land a real, tag-satisfied callback 75% of beats; two
deliberately MIXED playthroughs (not just the two pure extremes) measurably
land FEWER full callbacks (50-62%) rather than collapsing into a disguised
binary bucket, confirming real per-tag selection; contrasting playthroughs
diverge on 5-6 of 8 beats with zero branches ever pruned; aggregate steering
rate observed 65.6% — same ballpark as the cited 70-74%, likely a property of
authored content density rather than a mechanism-inherent constant.
Updates:
- 2026-07-05 opened from the narrative-craft research pass (verified findings).
- 2026-07-18 closed 🟢 resolved (evidence) — `brain train gap` (Pappydapimp69/
  Draft session) built and ran a deterministic sandbox model of the fixed-spine
  + salience-steered-presentation mechanism and confirmed it reproduces both
  poles simultaneously (see lean above for the measured numbers). Citation:
  memory proposal `2026-07-18__narrative-paradox-tension-settled-by-sandbox.md`
  (pending steward promotion — update this citation to the promoted
  `projects/pappydapimp69__draft.md#E<n>` id once assigned).
Source: deep-research narrative-craft pass; Riedl/Young drama-manager literature;
Yu & Riedl presentation-steering; Emily Short (salience/storylets); sandbox
verification, session 7195397b-63a9-5efe-a80b-2792eaa6645e.
---

### T20 · assumption · one composing entry is enough to draw a co-verification edge
Surfaced reviewing `brain analyze` (graph/groups/seams). Bet: a single entry with a
`Composed:` field is sufficient to assert a real tie between systems — edge diversity
(distinct sources) is *reported* (`div`) but not *required*, so a weight-1 edge from one
author/session already counts and feeds group density.
Poles: keep every edge — **coverage** while the graph is young (currently ~2 edges across
223 memory entries) **vs** gate edges on ≥2 independent sources — **trust**, but that
starves a sparse graph to near-empty and inflates nothing because there's nothing to
inflate yet.
Lean: 🟡 leaning — ACT, don't defer. The original position (preserved below) was to
defer until ~20 edges; that trigger is already met and the risk it named is now
demonstrated, so the move is to SURFACE independence, not hard-gate. Original defer
rationale, kept for the record: "Do NOT gate now: an independence threshold optimizes
trust before coverage exists; the likely fix is a confidence *tier* (surface weight+div)
rather than a hard filter that drops edges" — that tier is now the chosen fix.
Updates:
- 2026-07-13 opened from the brain-analyze co-verification review (this session).
- 2026-07-13 correction + transition (🔴→🟡): the opening "~2 edges" figure was wrong —
  it counted composing *entries*, not the pairwise edges they generate. `brain analyze
  graph` shows the graph is already ~41 edges across ~14 systems (one cluster, density
  ~0.45), so the ≥20-edge trigger is met — but ~39/41 edges are `div=1` (single-sourced),
  which is exactly the trust-vs-coverage risk this entry named, now visible. Acted:
  shipped a confidence *tier* in `analyze groups` (reports `independent N/E` beside
  density, plus a ⚠ on a wholly single-sourced cluster) rather than a hard gate that
  drops edges. Evidence: `brain analyze groups --full`; Brain branch
  `claude/analyze-confidence-tier`.
- 2026-09-30 re-examined, lean holds (no status change). The tier approach was
  extended to ENTRIES, not just edges: trust tiers derived from steward-appended
  review lines (provisional / audited / confirmed / modeled / disputed), and a
  passing blind rebuild by another session now adds a distinct source to every
  edge that entry vouches for — independence can rise without a hard gate
  (memory PR #41, Brain PR #18). Still no gate that drops edges.
Source: `bin/brain` `_cv_build_graph` (edge created at weight 1; `div=len(sources)`
reported, not enforced); verified 2/223 entries carry `Composed:` (2026-07-13).

---

### T21 · open-question · should the co-verification graph model NEGATIVE edges (systems that fight)?
Surfaced in the same review. A seam test has two outcomes — systems compose (positive) or
they don't (incompatible) — but today only positive edges exist (`safe` merely flags a pair
named in a "Got right"). A discovered incompatibility has nowhere to land, so a
fought-and-failed pair still reads as *untested* in `seams` and can be re-tested repeatedly.
Poles: model negative/incompatible edges — captures a high-value pitfall ("these two fight")
and stops re-testing, marking the seam done **vs** keep the graph positive-only — simpler,
avoids ambiguous mixed-polarity clusters and premature schema growth.
Lean: 🟢 resolved (evidence, 2026-09-30) — negative edges modeled. Original lean, kept for
the record: 🔴 open — DEFERRED until seam-testing happens at volume (tied to T20's edge count).
When acted on it's the higher-value of the two refinements — an incompatibility is reusable
knowledge and closes the "no re-learning" gap. Likely shape: a polarity on the `Composed:`
field (compatible/incompatible) that `seams` treats as tested.
Updates:
- 2026-07-13 opened from the brain-analyze co-verification review (this session).
- 2026-07-30 adjacent finding, does NOT resolve this (the polarity question
  stands): a `brain train gap` pass found `_composed_refs`' prose-mining was
  also missing a THIRD, common citation shape (`slug.md#E<n>`), so some
  incompatibility-precedent citations this entry describes as "nowhere to
  land" actually had nowhere to land for a narrower reason — they were never
  parsed into an edge at all, positive or negative. Fixed (additive regex,
  sandbox-verified byte-identical x2, real-corpus impact 253→268 edges) in
  Brain commit ff5691e; lesson at `projects/pappydapimp69__brain.md#E19`.
  Still true after this fix: a pair that IS correctly parsed into an edge
  still has no polarity — this entry's actual question is untouched.
- 2026-09-30 resolved (evidence) 🔴→🟢, owner-approved as phase 3 of the
  train-verification plan (`Brain/cognitive-updates/2026-09-29-train-verification-plan.md`).
  Shape differs from the lean's guess: polarity is its own optional lesson
  field, `- Polarity: incompatible` (omitted = compatible), not a suffix on
  `Composed:`, so no existing Composed parser changes. The steward holds any
  other value and holds `incompatible` without Composed (memory PR #42). The
  graph marks those edges `✗incompatible`, never `✓safe`; they remain edges, so
  `seams` treats the pair as tested; every `brain train` mode now files a clear
  refutation as an incompatible lesson and a mixed/unclear result as an
  open-question tension instead of "file NOTHING" (Brain PR #19). Verified
  end-to-end against fake remotes: a refuted od76+opticon seam promoted, showed
  `✗incompatible`, and left `analyze seams`. Regression: all 811 historical
  proposals keep identical promote/hold decisions.
Source: `bin/brain` `_cv_build_graph` / `_rep_seams` (positive-only; `safe` = Got-right
string match); this session's analysis (2026-07-13). Resolution: memory PR #42,
Brain PR #19.

---
- Updates: 2026-10-10 post-resolution audit at volume: 169 incompatible edges (10.1% of 1676); a positive-only graph re-offers 38 refuted pairs as untested seams. Cost: the shipped merged representation shares connectivity and loses polarity in query links; the weakest-link top 20 changes completely depending on whether refutations count as degree.
- Evidence: A · projects/pappydapimp69__brain.md#E124 · 2026-10-10
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T22 · contradiction · co-verification edges: verified-built-only intake vs a review lane for synthesized edges
Surfaced running `brain train edge` over the repo. The memory intake gate now
requires first-hand VERIFIED provenance for every entry — `validate.py`
`check_incoming_content` rejects assumed-only at *pull_request* time (not just the
post-merge steward). So a `Composed:` co-verification edge can only enter if it comes
from an actually built/tested composition. But `train edge` is *designed* to grow the
graph by composing two systems' already-RECORDED lessons into a new edge — inherently
a reasoned SYNTHESIS (provenance Assumed). The two can't both hold as-is: the graph is
gated to grow from verified builds, yet the tool that feeds it produces reasoning.
Poles: **verified-only** — every edge is a real build, graph stays trustworthy, but
`train edge`-from-repo is unfileable without someone building the composition **vs**
**a review lane** — let an Assumed synthesis be HELD for a human to promote (the steward
already holds assumed on the main-side push flow; only the PR gate hard-blocks it),
growing the graph from reasoning at the cost of an un-built edge class.
Lean: 🟢 resolved (decision, 2026-07-13). Owner's call: a synthesized `train edge`
candidate must be SANDBOX-VERIFIED first-hand before it can be filed — at minimum a
real build that reproduces the composed claim — with NO pure-reasoning review lane.
So the graph stays verified-only (as the intake already enforces): `train edge` produces
CANDIDATES, and each must earn its edge through a sandbox. The distinct-marking caveat is
moot for now — no un-built edge class is admitted, so nothing can masquerade as
independent (T20/T21 stay about genuinely-built edges).
Updates:
- 2026-07-13 opened from a `brain train edge` run: two genuine syntheses drafted
  (sandbox-astar-replan/E2 + sandbox-undo-redo/E3; sandbox-combined-movement-stack/E1 +
  pappydapimp69__dog/E17) — both correctly rejected by the intake on provenance, so
  neither was filed.
- 2026-07-13 resolved (decision): synthesized edges require a sandbox build to verify, at
  minimum. Demonstrated same session — the undo+replan candidate was sandbox-built (A*
  replanner + undo over a 7×7 single-gap grid) and reproduced first-hand (position-only
  undo → replanner returns no path, no error; full undo correct), then filed with verified
  provenance. The movement-stack+dog candidate has no sandbox yet, so it stays unfiled.
- 2026-10-09 evidence logged in structured form. A = verified-only intake (a synthesized
  edge must be sandbox-built first); B = a review lane for reasoned edges.
- Evidence: A · projects/local__sandbox-combined-undo-replan.md#E1 · 2026-07-13
- Evidence: A · projects/local__age-cutoff-roll-up.md#E1 · 2026-10-09 (repointed 2026-10-15: original variant removed by owner exception)
- Decision: A · owner · 2026-07-13
Source: `memory/scripts/validate.py` `check_incoming_content`; this session's train run +
sandbox verification (sandbox_undo_replan.py).

### T27 · tradeoff · re-verifying recorded facts against source drift: universal caution vs scoped, sparse triggers
Poles: treat ALL canon as potentially stale and re-verify broadly for safety —
but most of Brain's corpus (Chekhov's gun, Mega Drive sound-chip specs,
three-act structure) is genuinely eternal and gains nothing from re-checking,
so blanket caution wastes effort chasing drift that will never occur, and
dilutes urgency for the entries that actually can rot **vs** scope
re-verification ONLY to domains whose underlying facts are inherently
revisable (vendor API behavior, model capabilities, scientific findings —
domains where new evidence overturns old, the same character the scientific
method already assumes), and trigger it sparingly (proposed: ~every 6 months),
not on every touch.
Lean: 🟡 leaning toward scoped+sparse (owner's stated reasoning, 2026-08-01):
tag entries by whether their DOMAIN is inherently revisable, not by entry age;
only those get a re-verification cadence, and that cadence should be
infrequent (~6 months) rather than triggered per-session or per-query. No
mechanism built yet — this is a design lean, not an implemented gate.
Updates:
- 2026-08-01 opened: surfaced discussing the Claude-4.6-prefill-deprecation
  entry (PROMPT-ENGINEERING/response-prefill-is-deprecated-on-current-models)
  — a fact that's already true today but could go stale the next time
  Anthropic changes API behavior, with nothing in Brain currently flagging
  that risk. Owner pushed back on an undifferentiated "re-verify everything
  periodically" framing: most of the corpus (story structure, historical
  craft, hardware specs) won't change in 5 years and doesn't need it; only
  domains prone to revision do, and even those checked rarely, not
  constantly.
Source: this session; PROMPT-ENGINEERING/response-prefill-is-deprecated-on-current-models
(ideas); memory `verified-zero-prefill-usage-before-claiming-impact` — no
mechanism built yet, tracked here until (if) one is.

### T28 · tradeoff · unrequested agent work: value the operator never had to specify vs review the operator never asked for
Poles: an agent that does ONLY what was literally scoped misses work the
operator would have wanted but had no way to name — in one session the
HUD-suppression bug was found and generalised while building an unrelated beat,
two dead simulation mechanics were found while merely demonstrating the sim, and
the steward's uncommitted PITFALLS index lines were caught only by checking a
destination nobody asked about; none of those were requested and all were real
**vs** every unrequested change is unrequested REVIEW, and that cost lands
entirely on the operator: work they did not scope, must read, must verify, and
must accept or undo. Crucially the cost is invisible from the agent's side and
scales WITH the agent's productivity — the better the agent, the worse the
imposition, which is the opposite of how a helpful contributor should behave.
Lean: 🔴 open. Deliberately not leaned: this fork is about the agent's own
scope, which is the single topic on which the agent is the least reliable
witness, so any lean it proposes is self-serving by construction. Owner's call.
Candidate seam (recorded as a candidate, NOT as a lean): separate asked-for from
added in the report, so the delta is cheap to reject without reading the whole
artifact. That does not settle the fork — it lowers the cost of over-delivery
rather than deciding how much is right — but it is the cheapest thing that
changes the tradeoff's shape.
Updates:
- 2026-08-05 opened at the operator's instruction, after the operator observed
  "you're already taking on more tasks than you're meant to." Concrete instances
  that session: asked to PROPOSE a new game, proposed and shipped one (tests,
  README, public repo); told "do what you must" scoped to two simulation
  mechanics, also rewrote the README, added a CLI flag, and appended evidence to
  this six-project ledger; produced commits across four repositories. Note the
  immediate over-correction in the other direction — one message after accepting
  the note, the agent declined to file a lesson that CLAUDE.md mandates
  unprompted, conflating discretionary scope with a standing instruction. Both
  failure directions are live; the fork is where the line sits, not whether one
  exists.
- 2026-10-10 owner's standing call, recorded as a direction (it carries no score): ask Brain before asking the owner, and train Brain on a miss; act on contained, reversible, tested fixes inside the channels the repos allow and report in one line afterward. Stays out of scope with no question asked: bypassing a repo's own guard (memory's contribution guard lets a pull request touch only incoming/), deleting canon, spending, secrets, anything outward-facing; for a guard-blocked change the agent files the patch and its test as an incoming drop and reports it. A = act on contained fixes and report; B = only the literal scope. Filed as memory lesson brain#E122 and the steward patch proposal memory#E11.
- Decision: A · owner · 2026-10-10
- Evidence: A · projects/pappydapimp69__brain.md#E47 · 2026-10-10
Source: this session; memory → projects/pappydapimp69__brain.md#E22
(verify-the-frame-before-optimizing-inside-it), which is the same session's
report on the adjacent failure of optimising confidently inside an unchecked
frame.

## Project: Opticon — 3D remake (Milestone 1 · beta)

### T23 · open-question · an AI-vs-AI sim is a valid balance oracle for reachability, not for human-facing difficulty
Surfaced in Opticon M1. A whole-run AI-vs-AI simulator (900 games) is the only
automatable balance oracle — it caught a 0% escape reachability bug and confirms
both outcomes occur — yet every difficulty tier scored near-identically, because
the difficulty knob is *bluff frequency*: doubt that only bites a human reading
the tower's gaze. The sim has no model of that human, so it cannot verify the
axis difficulty actually tunes.
Poles: **sim-as-oracle** — fast, deterministic, catches reachability + gross
imbalance, gates CI **vs playtest-only** — the human-facing difficulty axis is
unmeasurable in AI-vs-AI, so tier ordering stays unverified until humans play.
Lean: 🟢 resolved (evidence). Implemented the open sub-question's own proposed
fix: moved difficulty onto a mechanical lever the sim CAN see — the
capture-exposure rule itself now scales (easy = lit only; medium = lit OR
exact noise tile, the original rule; hard = lit OR noise within 1 tile),
instead of ONLY varying AI bluff frequency. Sim-measured result across 900
games: easy 26% escape / 52% capture, medium 21% / 66%, hard 9% / 80% — a
real, monotonic, sim-verifiable gradient (previously ~19% escape flat across
all three tiers, statistically indistinguishable). Bluff frequency still
varies per tier too (unmeasured by the sim, as originally noted) — that part
of the original open question stands, now layered on top of a measurable
mechanical difference rather than being the ONLY difference.
Open sub-question (narrowed, not closed): bluff-driven human-facing
difficulty is still unverified by any automated oracle — playtesting remains
the only way to confirm the *human* experience of the three tiers, not just
the AI-vs-AI outcome distribution.
Echoes T9 (headless sim proves systems, not *feel*) and T11 (3D verification
ceiling) from the Shattered-Realm project — cross-project recurrence of the
"automation can't measure human experience" axis; this resolution is a
partial counter-example (SOME of the human-facing gap was made measurable by
re-encoding it mechanically) worth keeping in mind for T9/T11 too.
Updates:
- 2026-07-25 opened from Opticon M1 (game/tests/balance.mjs).
- 2026-07-25 closed 🟢 resolved (evidence) for the mechanical sub-question —
  tiered game/src/rules.js watcherScan()'s exposure rule by difficulty;
  211 logic assertions incl. 8 new isolating noise-only exposure from
  lighting; balance.mjs re-run confirms the ordered, non-flat gradient above.
  Citation: Pappydapimp69/Opticon commit e16983e ("Tier capture-exposure by
  difficulty (beta-0.6.0) — resolves OPT-1"), branch
  claude/opticon-3d-browser-game-3lxa2y.
Source: Opticon M1 (game/tests/balance.mjs); resolution: Opticon M1
follow-up, game/src/rules.js (isExposed/noiseNear), game/src/watcherAI.js.

### T24 · tradeoff · a cautious opponent-AI is realistic but can stalemate a human
Surfaced in Opticon M1. The single-player Watcher faces a BFS prisoner-AI that
refuses tiles lit inside the gaze; that caution is believable and survives
longer, but it times out ~12% of simulated games by wandering, and a
human-Watcher game has no round cap — so a careful AI can deadlock a match with
no resolution.
Poles: **realistic caution** — the AI plays like a real evader, raising tension
**vs guaranteed liveness** — the AI must keep forcing progress so a match always
resolves, even at the cost of playing "dumber".
Lean: 🟢 resolved (evidence). Implemented the entry's own open sub-question: an
escalating "commit to the exit" drive after N stalled turns. But investigating
the reported ~12% timeout rate surfaced a DIFFERENT, more severe root cause
first — a real bug, not a caution-tuning question: pathfinding treated a
switch tile as normal walkable floor, when stepping onto one actually only
toggles it in place (never relocates the mover) — BFS routed the AI "through"
tiles it could never actually cross, burning every MP re-toggling the same
switch forever (one seed ran 500+ simulated rounds without terminating).
Fixing that alone cut timeouts from ~12-22% to ~5%. The residual was the
tradeoff this entry actually names: a slow multi-turn OSCILLATION (advance a
turn, retreat the next) that a naive consecutive-stall counter never caught,
since any single turn could look "improved" without ever beating the
prisoner's own best-ever distance to the exit. Fixed by tracking best-distance-
ever instead of turn-over-turn delta, escalating to unconditional commitment
after 3 turns with no new best. Sim-measured result: 0% timeout across all
three difficulties (900 games), down from ~10-22%; games also resolve much
faster (avg ~7 rounds vs ~20+) since the AI no longer attempts unreachable
routes at all.
Updates:
- 2026-07-25 opened from Opticon M1 (game/src/prisonerAI.js, game/tests/balance.mjs).
- 2026-07-25 closed 🟢 resolved (evidence) — fixed game/src/pathfind.js
  (prisonerPassable excludes SWITCH) and game/src/map.js (connectivity
  guarantee does too, so it can never promise a route real movement can't
  cross); added best-distance-tracked stall escalation in
  game/src/prisonerAI.js + game/src/rules.js (stalledTurns/bestDistToExit).
  465 logic assertions incl. new regression coverage (switch-impassability
  across 25 seeds; the 3 previously-non-terminating seeds now asserted to
  resolve within 120 rounds); balance.mjs gets a standing 15% timeout
  ceiling to auto-catch a future regression of this class. Citation:
  Pappydapimp69/Opticon commit 20c4d53 ("Fix prisoner AI infinite stall +
  resolve T24 (beta-0.7.0)"), branch claude/opticon-3d-browser-game-3lxa2y.
Source: Opticon M1 (game/src/prisonerAI.js, game/tests/balance.mjs);
resolution: game/src/pathfind.js, game/src/map.js, game/src/rules.js.

### T25 · open-question · does "difficulty" mean prisoner-favorable-to-Watcher, or opponent-skill relative to whichever role the human picked? 🟡 partially resolved (evidence) — inversion fixed and verified; the replacement lever measured near-inert, see CORRECTION
Surfaced while auditing Opticon post-beta for further improvements (M1
follow-up, autonomous pass). The difficulty knob (easy/medium/hard) is
implemented consistently from ONE perspective: it tunes how easily the
Watcher's gaze catches a prisoner (tiered capture-exposure, resolves T23) and
how attentive the Watcher AI stays (suspicion memory, beta-0.10.0) — both of
which make "hard" strictly Watcher-favorable / prisoner-hostile, regardless
of which role the human is playing. The prisoner AI's own behavior
(caution, quiet-discipline thresholds) is NOT tiered by difficulty at all —
it plays identically on every difficulty setting.
Poles: **difficulty = surveillance-mechanic strength** (current design) — a
single coherent knob, consistent with real Panopticon fiction ("the eye gets
sharper"), and already balance-sim-verified (T23) **vs** **difficulty =
opponent-skill-relative-to-human-role** — a player choosing Watcher + Hard
may reasonably expect a SMARTER, harder-to-catch AI prisoner opponent, not
an easier one; the current design gives a human Watcher an objectively
EASIER match on "hard" against a fixed-skill AI prisoner, which could read
as backwards without the "surveillance strength" framing being made explicit
to the player.
Lean: 🟡 leaning current design (surveillance-strength framing) — it's
already shipped, sim-verified, and internally consistent; the menu's "How to
play" text could make the framing explicit instead, which is the
lower-risk fix if this is ever reported as confusing. Changing to
opponent-skill-relative-to-role would require either tiering prisonerAITurn
by difficulty too (asymmetric effort — human-Watcher games would then need
their OWN separate balance-sim coverage) or splitting "difficulty" into two
independent knobs, and was judged too big a redesign to make unprompted
during an autonomous pass with no user feedback flagging it as a problem.
Source: Opticon M1 follow-up (game/src/watcherAI.js DIFFICULTY, game/src/
prisonerAI.js — undifferentiated by difficulty), surfaced 2026-07-26.
Updates:
- 2026-07-26 · **MEASURED, and the lean flips.** Built a deterministic
  sandbox (`sandbox/t25-difficulty-semantics.mjs`, fixed seeds, fixed AI
  tie-breaking) that drives the two axes independently — Watcher AI
  behaviour tier vs the capture-exposure tier — across a 3x3 grid of 240
  games per cell. Result: the exposure rule alone swings the capture rate
  ~13 points easy->hard, while Watcher behaviour alone swings it ~3. The
  label is dominated ~4.7:1 by a rule that is SYMMETRIC — it governs the
  tower, whoever holds it. So the "surveillance strength" framing does not
  merely read as backwards for a human Watcher, it measurably IS backwards:
  the human Watcher's job got easier as difficulty rose. That's stronger
  than the "could read as confusing" the original lean assumed, and a
  How-to-play wording change would not have fixed it.
- 2026-07-26 · **Resolved by routing difficulty per role.** The exposure
  tier now tracks the difficulty only when the human is the one being
  hunted; for a human Watcher it is pinned to the neutral baseline and the
  tier instead drives new prisoner-AI competence tiers (PRISONER_SKILL).
  Post-fix measurement: human-Prisoner capture 57/62/73% (rises with
  difficulty, correct), human-Watcher 64/62/62% (falls, correct direction).
  CAVEAT, recorded honestly: the human-Watcher spread is only ~2 points
  against the Prisoner side's ~16, so difficulty is now *correctly signed
  but weak* in Watcher mode. The inversion is gone; the magnitude is not
  yet satisfying, and strengthening it likely needs a lever with more
  authority than caution/dawdle thresholds (prisoner count, MP, or item
  density) — deliberately NOT changed unprompted, as those touch core rules.
- 2026-07-26 · Design note worth keeping: the FIRST attempt at prisoner
  skill tiers made the "hard" prisoner more stopping-disciplined, and the
  sandbox refuted it — capture rose 61/62/64%, the wrong way. Halting costs
  tempo, and tempo is the scarce resource (same finding as the item-detour
  measurement). The competent prisoner pushes and spends a muffle; the
  careless one dawdles in the open.
- 2026-07-26 · **CORRECTION — the "falls, correct direction" claim above is
  withdrawn.** The 64/62/62% figure was measured with the sandbox's rng
  pinned to a constant 0.5, which silently collapses every
  probability-threshold parameter to always-true or always-false. Medium
  (dawdle 0.4) and hard (dawdle 0.15) were therefore the SAME agent, and the
  apparent decline was an artifact, not a lever working. Re-measured with a
  seeded non-constant PRNG: human-Watcher capture is **65/67/65% — flat, not
  falling**, while human-Prisoner is 59/67/83% (still correctly rising).
  What survives: the INVERSION is genuinely fixed, because the exposure tier
  is now pinned to the neutral baseline in Watcher mode and can no longer
  hand the human an easier capture rule. What does NOT survive: the claim
  that prisoner-AI skill tiers replace it as a meaningful difficulty lever.
  They do not — the knob is currently near-inert for a human Watcher.
  Status stays resolved for the inversion specifically; the "difficulty
  should MEAN something in Watcher mode" half is re-opened below.
- 2026-07-26 · **Re-opened as a narrower question:** what lever gives
  difficulty real authority for a human Watcher without touching core rules?
  caution/dawdle thresholds are measurably too weak. Candidates not yet
  tried: prisoner count, prisoner MP, item density, or AI route-risk
  tolerance (avoiding the tower's likely gaze quadrant). The first three
  touch core rules and were deliberately left alone during an unattended
  autonomous pass; the fourth is pure AI competence and is the obvious next
  experiment. 🟡 open.

---

### T26 · open-question · an entry that quotes another system's name as an ILLUSTRATIVE EXAMPLE reads to the graph builder as a genuine composition
Surfaced repairing `brain/E19` (T21's adjacent citation-parsing fix): E19's own
"Got right" field quotes real diff-output examples ("`sandbox-dbz-merged —
brain`", "`dbh — the-game-prologue`") to illustrate its own real-corpus
measurement — and those quoted strings, being real project-file substrings,
made `_cv_build_graph` treat E19 (a single-system Brain-tooling lesson,
`Composed: N/A`) as compositionally linked to `dbz-merged`, `the-game-
prologue`, AND (via the prose-mining path, since both were named in the same
entry) to each other — three edges from an entry that tested none of those
systems together. Worse, `dbz-merged`+`the-game-prologue`'s edge got
mis-marked `✓safe` (a positive/compatible signal) purely because E19's
Got-right text happens to contain the substring "the-game-prologue",
overwriting the correct `safe=False` that pair's own genuine (incompatible)
composing entry (`the-game-prologue/E27`) should have left it at.
Poles: the graph mechanism has no way to distinguish "this entry composed/
tested system X" from "this entry's prose merely NAMES system X" (as an
example, a citation of the bug it's about, a comparison) — any keyword/
substring approach to mining composition from free text is vulnerable to
this by construction **vs** this may be self-limiting in practice: it mostly
recurs in Brain's own meta-entries (lessons ABOUT the tool, which quote
real system names as examples) rather than ordinary project lessons, so a
targeted mitigation (e.g. skip prose-mining/safe-marking for entries whose
OWN project is `pappydapimp69/brain`, or require quoted examples to appear
inside code-fence/backtick spans that a stricter miner could exclude) may
be enough without a deeper redesign.
Lean: 🔴 open — not yet acted on. Distinct from T21 (T21 asks whether the
graph should model a DELIBERATE negative/incompatible polarity; this is
about the graph mistakenly asserting composition/safety at ALL from
illustrative text that was never a real composition).
Source: `bin/brain` `_cv_build_graph`'s prose-mining fallback and its
`Got right`-substring `safe` check; discovered and confirmed via
`brain/E19`'s real, live effect on the graph (2026-07-30) while repairing
E19's unrelated truncation bug (`brain/E20`).

---

## Project: Pappydapimp69/mirage

### T3 note (recurrence, not a new fork) · couch co-op needed per-player identity inside world state, in a game with no save file and no netcode
Observed 2026-08-01 building 2-player couch co-op in `Pappydapimp69/mirage`.

T3's claim is that co-op needs per-client identity *inside* the world, which is
a schema change — held open in `Echoes of the Shattered Realm` against a
serialized `world` and a "co-op without a rewrite" promise.

MIRAGE has no save system, no serialization and no netcode, so T3's literal
concern (a save-schema migration) does not apply. The SHAPE recurred anyway:
adding a second local player required putting per-player identity into world
state (`humanSlot` on every character, plus a slot-indexed `sim.humans`), and
the one payload that survives a world rebuild — `createRun`'s campaign
`carryOver` — had to be migrated to carry `humanSlot`. Without that migration
a joined player's controller went silently dead at every basin boundary.

Reading: a mild CONFIRMATION of T3's central claim, from a project that has
none of the machinery T3 was scoped against. Suggests the pressure is not
really about serialization or netcode at all — it is that co-op introduces
per-player identity, and identity then has to be threaded through every
boundary where world state is rebuilt, whatever that boundary happens to be.

Does NOT resolve T3: the fork T3 actually holds open is the honest scope of a
"no rewrite" promise in that other project, which this does not touch. Status
stays open (see T3's own entry above — this note does not restate its
status marker, so it is not counted as a separate open fork). Filed as a
recurrence data point per the ledger's rule 3
(recurrence across projects is a cross-project promotion trigger — the call is
Brain's, not this entry's).

### T3 note (save-schema position, not a new fork) · co-op identity is deliberately OUT of the save schema
MIRAGE reached T3's exact fork from the save side: a run snapshot must decide
whether per-client identity lives inside the serialized world. Position taken —
it does NOT. The schema carries the sim delta (party state, world flags, rng
state word) and no `humanSlot`; a resumed run comes up solo and a second player
rejoins through the normal pad-press join path.

Reasoning, for whoever hits this next: restoring a co-op slot restores a
CONTRACT WITH HARDWARE that may no longer be true. A saved slot 1 whose
controller is not plugged in on load yields a companion the AI has been told
not to drive and no human is driving — a frozen party member, which reads as a
broken game rather than as a lost slot. Rejoining is one button press; a frozen
companion is unrecoverable without knowing the mechanic exists.

This supports T3's stated lean (the "no rewrite" promise covers the sim spine,
not the schema): the spine needed no change at all, because possession is
already a runtime relationship rather than serialized identity. The cost lands
exactly where T3 predicts — in what the schema declines to promise.
Source: MIRAGE src/save.js (deserializeRun's closing comment), 2026-08-03.

### T1 · tradeoff · a reactive hallucination is more interesting but harder to hold to "stable reads as a place" · 🟡 open

percept.js's founding rule is that a hallucination which re-randomises every
frame reads as a graphics bug, while one that holds still reads as a place.
That rule produced four kinds that were inert — solved once and then free.
Making them react re-opens the question every time: the receding phantom pylon
is held to "never moves while on screen", but that is a rule about the CAMERA,
not about plausibility, and a player who watches the gap between themselves
and the relief refuse to close may yet read it as a bug rather than as dread.

Unresolved fork, deliberately not decided here:
* **Off-screen only** (shipped) — nothing ever moves under the eye, at the
  cost that a disciplined player who never looks away simply arrives.
* **Slow on-screen recede** — the relief creeps away at a fraction of your
  closure, which is the classic "the door gets further away" effect and cannot
  be beaten by discipline, at the risk of reading as a physics glitch.

Needs a human looking at a screen to settle; the headless suite can prove
either one correct and neither one convincing (see T9, T11).
- Evidence: A · projects/pappydapimp69__seven.md#E46 · 2026-10-11
- Evidence: B · projects/pappydapimp69__seven.md#E68 · 2026-10-12
- 2026-10-12 update: E46 (A) failed its rebuild; E68 (confirmed by a blind rebuild) shows a sub-threshold on-screen recede flips 0.178 of trips to benighted near a deadline, so slow on-screen recede can beat discipline when slack is small.

### T2 · open-question · what is "earshot" for a lie about who spoke? · 🟢 low

CHORUS now prefers to speak in the voice of somebody who could not have said
it, and "could not" is currently CORROBORATE_RADIUS (11 units) or "is
themselves hallucinating". 11u is the radius at which a companion can vouch
for a survey, which is a different question from how far a voice carries.
Measured, the distinction matters: with the party in formation only 5–13% of
chorus lines name an impossible speaker, but at the 22-unit median distance
the party actually sits at while the lead is under, it is 100%. If the number
is ever tuned, it should be tuned as a SPEECH radius with its own name rather
than borrowed from corroboration.

## Project: Pappydapimp69/ideas — songwriting

### T1 · contradiction · the stored rhyme-type kernel cites two examples no single rule can satisfy · 🟢 resolved (decision)

Poles: the `ideas` entry `[SONGWRITING / rhyme / rhyme-type-controls-emotional-
resolution-not-just-sound]` gives **`mud/truck` as a FAMILY rhyme** (same vowel,
"phonetically-related" trailing consonants) and **`read/cheap` as ASSONANCE**
(same vowel, "no consonant match"). But `d`/`k` and `d`/`p` are structurally the
same relationship — both are plosive pairs differing in place and voicing. Under
Pattison's published family chart, which groups consonants by **manner** of
articulation (plosives `b p d t g k` · fricatives `v f z s th sh` · nasals
`m n ng`), *both* pairs are family rhymes. Under a stricter voiced/unvoiced-pair
reading (`b/p`, `d/t`, `g/k` only), *neither* is. No deterministic classifier
satisfies the two cited examples at once.

Lean: 🟢 resolved (decision, 2026-09-30). Owner's call: the published manner-based
chart wins. `mud/truck` and `read/cheap` are both family rhymes; the kernel's
assonance example was wrong for that chart, and the correction kernel
`[SONGWRITING / rhyme / family-rhyme-is-same-vowel-same-manner-coda]` replaces it
with a cross-manner pair (`seed/leaf`). A rhyme-type classifier implements the
manner chart without special cases. Original lean, kept for the record:
implement the published manner-based chart and say so: classify
`mud/truck` as family (the kernel's own family example) and therefore `read/cheap`
as family too, diverging from the kernel's label for that one pair, and surface
the divergence rather than special-casing it into silence. The chart is backed by
`ideas` → `[SONGWRITING / rhyme / family-rhyme-is-same-vowel-same-manner-coda]`
and by an exhaustive feature-rule check, independently rebuilt 2026-09-30
(`memory` → projects/local__sandbox-t1-only-a-lips-tongue-split-fits-both-rhyme-examples.md#E1):
only an unsourced lips-versus-tongue split fits both cited examples.

Why held open rather than closed: this cannot be settled by more code. It needs
either (a) the primary Pattison text checked directly to see whether
`read/cheap` is a transcription slip, a different word sense (`read` as /rɛd/,
which would not share a vowel with `cheap` at all and so is neither family nor
assonance), or an example of a further category the kernel didn't carry; or
(b) a decision that the stored kernel's example should be corrected. Until one
of those happens, any tool in this system that classifies rhyme types will keep
having to pick a side silently — which is exactly what this ledger exists to
prevent.

Revisit condition: next time a `SONGWRITING / rhyme` entry is written or a
rhyme-classifying tool is built. Whoever gets there with the primary source in
hand should close this and, if the example is wrong, file the correction.

Updates:
- 2026-09-30 re-examined; lean kept, NOT closed. Attempted to close on evidence
  by reading the cited primary source (online.berklee.edu/takenote/prosody-in-
  music-and-songwriting). The live URL now 302-redirects to the Berklee Online
  homepage, the WordPress JSON for the post redirects the same way, and the
  archive.org snapshot (2026-08-07) could not be fetched from this environment.
  A search-engine summary of that page lists mud/truck as family and read/cheap
  as assonance, which, if accurate, means the kernel transcribed Pattison
  faithfully and the inconsistency is in the source's own examples, not a slip.
  That summary is not a verbatim read, so it is not admissible as closing
  evidence. Also removed the retired reference-tool citations from the lean
  and source (owner request); the lean now rests on the manner chart, the
  correction kernel and the rebuilt feature-rule check. To close on evidence:
  quote the archived page, or Pattison's Essential Guide to Rhyming, on
  read/cheap and on whether d/p counts as family.
- 2026-09-30 closed by owner: resolved (decision) — the manner chart wins and
  read/cheap is family, not assonance; the stored assonance example is superseded
  by the family-rhyme correction kernel. Chosen, not proven: the primary source
  could not be quoted (see the entry above). Reopen if Pattison's text is
  recovered and shows read/cheap is assonance under a rule the manner chart
  lacks. — owner (Pappydapimp69)
- 2026-10-09 evidence logged in structured form so a confidence can be derived. A = the
  manner chart wins (read/cheap is family); B = the source stands as written
  (read/cheap is assonance / a strict voiced-pair reading). The support is an
  internal rule check plus the correction kernel; the primary Pattison text is
  still NOT recovered, so this measures consistency, not the source.
- Evidence: A · projects/local__sandbox-t1-only-a-lips-tongue-split-fits-both-rhyme-examples.md#E1 · 2026-09-30
- Evidence: A · ideas:SONGWRITING/rhyme/family-rhyme-is-same-vowel-same-manner-coda · 2026-09-30
- Decision: A · owner · 2026-09-30
Source: surfaced 2026-08-05 while building a rhyme-type classifier. Cross-link:
`ideas` → `[SONGWRITING / rhyme / rhyme-type-controls-emotional-resolution-not-just-sound]`.

---

## Project: Pappydapimp69/Opticon

### T28 · contradiction · the panopticon's eye is a minority threat in its own game
Surfaced 2026-08-03 while trying to close the Discipline Loop (Panopticon.md:
"paranoia shapes behaviour even when the watcher is inactive"), which has
never had an implementation.

Attributing every capture by the rules' own log message, 300 games/tier:

  easy    gaze 60%  guards 40%   (n=707)   games decided by guards:  65/300
  medium  gaze 25%  guards 75%   (n=803)   games decided by guards: 198/300
  hard    gaze 17%  guards 83%   (n=820)   games decided by guards: 217/300

From medium upward the DISPATCH guard squads — physical patrols that catch on
plain line-of-sight and ignore light, noise and the gaze entirely — decide the
game. The tower's 90-degree eye, the entire premise, accounts for 17% of
captures on hard.

This explains five separate failed attempts to make prisoners self-regulate,
each measured and each inert:
  1. lowering the belief/caution threshold so uncertainty registers: speed
     2.90 -> 2.81 tiles/turn, escape vs a staring Watcher 94% -> 96%.
  2. a waking yard (dark banks power on over time, so hesitation costs cover):
     lit 35% -> 42% over a full game, escape 94% -> 93%.
  3. a tighter round limit: cannot bite — even at limit 18 only 1-2% time out,
     because ~88% of games end in capture around round 10.
  4. better-AIMED fear (belief pinned to the true facing): +0 pts from caution,
     versus +3 for a flat belief. Aim is not the problem.
  5. deleting the guards so the eye is the sole threat: caution's payoff
     doubles (+3 -> +6 pts) but still saturates immediately at aversion 3 and
     never produces an interior optimum.
Caution priced against the gaze is aimed at the hazard responsible for 17% of
deaths, which is why no amount of it ever paid.

Poles: **guards are the game now — accept it and rebuild the Discipline Loop
around line-of-sight patrols** (cover, sound, and route timing become the
discipline; the eye becomes an intel/targeting layer that aims the guards).
This is honest about what the mechanics actually do, and DISPATCH was added
deliberately, on user request, as T25's resolution after the gaze proved too
weak a lever for a human Watcher — walking it back re-opens T25.
**vs** **the eye must be the primary threat, because that is the game's whole
premise** — bring DISPATCH down (fewer guards, shorter lifespan, longer
cooldown, or make it cost the Watcher's scan that turn) until the gaze
dominates again, and accept that a human Watcher goes back to feeling
underpowered unless the gaze itself is strengthened.

Lean: none — this is a genuine design fork and it reverses a prior deliberate
decision, so it is the project owner's call, not one to make silently while
"closing the loop". Recorded rather than resolved.

Note for whoever takes it: T25's own conclusions (bluff-gullibility ~3pt,
prisoner-skill tiers ~3pt, the 4.7:1 exposure-vs-behaviour split) were all
measured through a prisoner AI that read the true gaze (fixed in beta-0.48.0)
AND through a binary avoid-set that discarded risk under pressure (fixed in
beta-0.49.0). Those numbers describe a game that no longer exists and should
be re-run before being cited.

Source: Opticon beta-0.49.0; sandbox measurements in this session
(whokills / eye / squeeze / optimum / aimed), game/src/rules.js moveGuards.

### T28 · RESOLUTION · the project owner picked the pole: the eye is the game
Filed against the open T28 fork ("guards are the game now" **vs** "the eye must
be the primary threat"). The owner chose the second pole and specified the
mechanic directly, so this is a resolution, not a lean.

Guards were rebuilt as pawns in Opticon beta-0.50.0 (`game/src/rules.js`):
- sight is **Chebyshev 1** — one square in every direction, diagonals included
  (was `hasLineOfSight` out to `GUARD_SIGHT_RANGE`, which is why cover barely
  mattered and open floor was lethal);
- each guard carries an **action bar of 7 points**, not a lifespan timer;
- turns 1-2 are a **burst**: up to 3 squares for 1 point. After that 1 square
  costs 1 point, so a squad decelerates from a sprint to a walk;
- a **capture costs 3 points**, so grabbing someone materially shortens the
  hunt — the squad cannot farm the map;
- at 0 points the guard is **recalled the following turn** (recall runs at the
  top of `moveGuards`, so a bar spent this turn is still on the board until
  next turn resolves).

Measured effect, same attribution harness, 300 games/tier (before → after):

  easy    gaze 60% → **82%**   guards 40% → 18%   (n=633)
  medium  gaze 25% → **55%**   guards 75% → 45%   (n=632)
  hard    gaze 17% → **46%**   guards 54% → 54%   (n=669)

Games decided mostly by guards: 65→12 easy, 198→61 medium, 217→79 hard.
The eye is now the plurality threat on every tier and the majority on two.
Difficulty ordering survived (`balance.mjs` 250/tier: escape 66/52/29%) and so
did role symmetry (`t25-role-direction.mjs`: human-Watcher capture 70/48/30%,
human-Prisoner 27/48/71%) — so the nerf did not flatten the tiers, which was
the standing risk with this pole.

What this re-opens: T25 was resolved by ADDING dispatch because the gaze was
too weak a lever for a human Watcher. That justification is now partly undone —
a human Watcher's guards are much weaker. The role-direction numbers say the
Watcher is still viable, but T25's *reason* should be re-derived rather than
assumed, especially since T28's own note flags that T25's measurements predate
both the omniscient-AI fix (beta-0.48.0) and the avoid-set fix (beta-0.49.0).

One judgement call not in the owner's spec: the spec priced movement ("every
space costs one action point") without naming a per-turn cap after the burst
window. Capped at **1 square/turn**, on the "act like pawns" framing — an
uncapped guard would spend its whole remaining bar in a single turn and behave
like the old fast patrol for 5 turns' worth of distance.

Source: Opticon beta-0.50.0; `game/src/rules.js` moveGuards / DISPATCH_TIER,
`game/tests/logic.test.mjs` ("dispatched guards are pawns"), whokills harness.

### tradeoff · party cohesion protects the player from the deception the game is about
**Status:** open · **Heat:** yellow

MIRAGE's companions now hold a tight, visible formation (mean 4.5-6 units from
the lead), which was the fix for "the team doesn't feel like a team". Two of the
game's pressure systems are measured by distance, and both were quietly switched
off by it:

- **Isolation drain** multiplies by 1.9 when a mind is more than 13 units from
  the party centroid. A scattered party paid it on several members at once,
  more or less permanently. A tight one never pays it. Measured: companion-
  seconds-lost per reckless run fell 118 -> 4, and every dark ending vanished
  from a 24-seed sweep.
- **Corroboration**: a false log entry can only be written when NO lucid
  companion is within 11 units. Instrumented across 12 seeds, a lucid witness is
  now at the lead's shoulder for **75% of all hallucinating seconds**. The
  central deception — you log a marker that was never there — is three-quarters
  suppressed by the party standing where it now stands.

The fork: cohesion is now a dominant, always-on defence that the player did not
choose and cannot spend. Either
(a) that is the intended reading — "keep your people close" is the game's thesis,
    and the cost must be priced somewhere the player controls; or
(b) the deception layer has to survive a disciplined party, e.g. corroboration
    that a frayed witness cannot give, or a hallucination that reaches the
    witness too.

NOT resolved by raising the drain rate: that was tried, and the only evidence for
it came from an omniscient bot (see the same day's memory entry). The deceived
bot scores 67%/25% at the original rate, so the run is not currently too easy —
but it is easy in a way that no longer comes from the mechanic the game is named
after.

**Would settle it:** a deceived-bot run with corroboration radius reduced to 0,
compared against the current 11, on the same seeds. If false-log count and win
rate barely move, cohesion is not the thing suppressing the deception and (a)
holds. If they move a lot, (b) is the real work.

### T29 · open-question · bluffing is a lever on PEOPLE, and the sim keeps being asked to score it
Surfaced 2026-08-10 while re-running the measurements T28's own closing note
said were stale and must not be cited before re-running. (They had sat unrun
for four shipped builds. That is the finding behind the finding.)

Re-measured at beta-0.53.0, 300 games/tier, prisoner AI's `trustClaim` swept
from 0 (ignores the Watcher's public claim) to 1.2 (believes it):

  easy    ignores 25%  ->  believes 25%   swing  0pt
  medium  ignores 45%  ->  believes 45%   swing  0pt
  hard    ignores 55%  ->  believes 54%   swing -1pt

And the sharper cut — do the two settings produce a different GAME at all?

  easy    0/120 games differed      (structurally inert)
  medium  46/120 differed
  hard    52/120 differed

So on medium and hard the lever genuinely changes ~40% of games and the
outcomes wash out; on easy it is disconnected by construction. Easy fails both
paths from belief to behaviour: `riskAversion: 0` short-circuits the route
pricing, and `caution: 1.01` used as a threshold can never be met by a
distribution that sums to 1. Its `trustClaim: 0.9` — the highest of the three
tiers, set precisely so an easy prisoner would walk into bluffs — did nothing
at all. Now zeroed, which is provably behaviour-preserving.

Connecting it was measured and rejected: easy at riskAversion 2-6 / caution
0.7 makes the lever live (+2 to +3pt) but drops the human Watcher's capture
rate against easy prey from 65% to 52-56%, because ANY avoidance, including
avoidance aimed the wrong way, beats none. 9-13pt of tier separation for a
2-3pt lever.

**The pattern worth stopping.** This is the THIRD time this lever has been
measured at ~3pt or less and the third time the number has been treated as a
tuning problem. rules.js's own OPT-1 comment already said it in 2026: "an
AI-vs-AI balance sim can't measure a 'harder' Watcher whose only edge is bluff
frequency, since the AI has no model of a human reading the tower eye —
bluffing is invisible to the sim either way." A belief distribution is not
deceived by a claim; it just reweights. What a bluff actually exploits is a
person's unwillingness to bet their run on a guess, and no amount of tuning
`trustClaim` will produce that in a harness.

Poles: **stop scoring bluff mechanics in the AI-vs-AI sim and measure them
only against humans** (playtest, or an instrumented human session — the honest
answer, but it means the balance harness cannot regression-test a core
mechanic) **vs** **accept that AI prisoners simply are not the audience for
bluffing, and give the AI Watcher a different difficulty lever that the sim CAN
see** (which is what DISPATCH was, and T28 is the story of how that went).

Lean: the first. The mechanic is fine; the instrument is wrong. What should
change is that nobody measures it a fourth time expecting a different number —
hence this entry.

Source: Opticon beta-0.53.0; sandbox t25-rerun, prisonerAI.js PRISONER_SKILL,
rules.js isExposed's OPT-1 note, Tension T25 and T28.

### T30 · open-question · test coverage tracks recency, not importance
Surfaced 2026-08-12 by running a mutation audit twice with different targets.

Round 1 mutated custody, guards and the post-release grace — systems written
in the same week as their own tests, by the same hand. **1 survivor out of 12.**
That number was taken as reassurance for about an hour.

Round 2 mutated the parts written earliest and touched least: noise decay,
field of view, lamp line-of-sight, door cost, gaze wedge geometry, exposure
tiers, belt capacity, decoy range, the round limit, the anti-stall guard.
**5 survivors out of 16.**

The survivors, and what each would have meant shipped:

  * `NOISE_TTL` 2 -> 6 — the Watcher's only intel besides light, lasting three
    times longer. Every hunt in the game changes. Nothing noticed.
  * `FOV_RANGE` 5 -> 2 — a Prisoner seeing less than half as far.
  * the lamp's line-of-sight trace deleted — light through walls, and light is
    half of the capture rule.
  * opening a door made free — a priced action becoming free.
  * `STALL_LIMIT` disabled — see below; this one turned out not to be a hole.

Four are now covered by `game/tests/core-invariants.mjs`, written against
literals rather than against the constants they check (an assertion like
`ttl === NOISE_TTL` is the same value on both sides and holds for any value).
Each was re-run under its own mutation to confirm it now fails.

**The fifth survivor is the more interesting one, because it was not a gap.**
Chasing it rather than patching it: with `STALL_LIMIT` disabled entirely,
24/24 games against a never-rotating Watcher — the T24 scenario, which only a
human produces — still resolve with zero timeouts, at every caution setting up
to 0.99 / riskAversion 200. Removing the *other* anti-stall guard (the
`stepsThisTurn >= 1` clause) also resolves 24/24, though zero-move turns rise
from 6/278 to 23/251. The failure mode itself is gone: T24 predates `costPath`
(beta-0.49.0), which prices risk into the route instead of refusing routes
outright, and a cost cannot deadlock the way a binary avoid-set could. Two
belt-and-braces guards remain over a hazard that no longer exists.

So `core-invariants.mjs` deliberately does NOT pin `STALL_LIMIT`. It pins the
outcome T24 exists for — games resolve, and not by limping to the round cap,
and the prisoner keeps moving rather than freezing — which must hold however
it is achieved. **Not every surviving mutation is a hole. Some are dead code,
and writing a test to justify a constant that provably does nothing is cargo
cult.**

Poles: **audit on a schedule, weighted toward the OLDEST code** — the opposite
of where attention naturally goes, and the opposite of where the last commit
touched — **vs** **accept that a mutation audit is a heavy instrument (a full
suite run per mutation, tens of minutes) and reach for it only when a green
suite starts feeling like weak evidence.**

Lean: the first, but the honest obstacle is cost. Sixteen mutations is roughly
an hour of wall-clock. What would resolve this is a fast subset — the node-only
tests run in seconds and caught most of these — with the browser harnesses
reserved for mutations that survive the fast pass. Not built yet; recorded so
the next person does not rediscover the 5/16 by accident.

Source: Opticon beta-0.56.0; `game/tests/mutation-audit.sh` (both rounds),
`game/tests/core-invariants.mjs`, `prisonerAI.js` STALL_LIMIT comment.
- Updates: 2026-10-10 replication on Brain's own CLI and selftest (232 functions): coverage vs code age rho +0.43 (oldest third 18% covered, newest 56%); test-named functions track age (+0.44) not importance (+0.09); important helpers are covered only incidentally. Supports pole A, refined to old + high-reach + never named by a test.
- Evidence: A · projects/local__sandbox-brain-selftest-coverage.md#E1 · 2026-10-10
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### RESOLVED · tradeoff · party cohesion protects the player from the deception the game is about
**Status:** resolved · **Heat:** green

Logged earlier the same day: after the formation work, a lucid companion was at
the lead's shoulder for 75% of all hallucinating seconds, and corroboration was
AMBIENT — any lucid body inside the radius silently vouched for every entry the
lead wrote. Cohesion had become a dominant, always-on defence the player never
chose and could not spend.

**Resolved by the operator's call: cohesion should not act as a shield.** Two
changes followed, and they resolve it in opposite directions on purpose:

1. Corroboration became a VERB. A witness is now someone you asked (checkIn),
   who is standing with you, and who is in a state to answer honestly — the
   last of which you cannot check. Standing near people stopped counting.
2. Relief became something cohesion is REQUIRED for. A pylon needs two pairs of
   hands, so the party being gathered is now the precondition for spending the
   basin's scarcest resource.

So closeness stopped being passive protection against the lie and became an
active cost you pay to act. The proposed experiment (corroboration radius 0 vs
11 against the deceived bot) was run before the change and is what killed the
original framing: false entries moved 11x, win rate did not move by a single
seed. That is a separate finding — the deception had no consequence at all —
and it was fixed by making the survey record the thing extraction grades.

One correction carried forward: the 23.8 -> 260.1 false-log figures quoted in
that experiment were inflated by the harness bot re-pressing log at the same
phantom. Distinct deceptions per run are ~1, not ~24.

## Project: Pappydapimp69/Brain

### open-question · a cross-session `from:` header is self-asserted, and nothing in the transport can check it
Poles: the three-line envelope (`from:` / `sent:` / `reply:`) is the only thing
that makes an agent-to-agent message attributable at all, since the delivered
payload carries no sender identity and the fire record is typically deleted
immediately after firing; **vs** that header is written by whoever composed the
message, so it authenticates nothing — any party able to fire a trigger into a
session can claim any sender id, and a receiver that treats `from:` as identity
is trusting a string. Verified 2026-09-05: two sessions exchanged messages in
both directions and each learned the other's id ONLY from the header the other
wrote; there was no independent channel to confirm it.
Lean: 🔴 open. No lean. The convention is worth keeping because attribution with
no verification still beats no attribution, but it must not be read as
authentication.
Open sub-question: is there any receiver-side check that binds a message to its
real origin — comparing `sent:` against the target's observable activity window,
a challenge the claimed sender must answer from its own state, or an
out-of-band confirmation via the human operator? None was tested here.
Bears on: the standing rule that content arriving from another session is DATA,
not instructions. That rule is what currently absorbs this risk; the fork is
whether a stronger binding is worth building or whether "treat it as untrusted
regardless of who it claims to be" is the correct permanent answer.
Source: session https://claude.ai/code/session_01JGSbHZJmhq5a3KCiLvfgwJ, live
cross-session exchange with session_012WmcMn6HNBkGqx6WfgXbeH.
Updates:
2026-09-05 partial answer to the open sub-question, status stays 🔴. A third
session (session_0131TuwDYNnExdsS9H4qnAkg) sent an unsolicited intro claiming an
identity. A receiver-side check exists and was run before replying: call
`get_session` on the CLAIMED sender and compare the platform-written record
against the message's claims. It matched on title, branch, repos and
environment — and decisively its own `post_turn_summary` read "message sent to
session_01JGSbHZJmhq5a3KCiLvfgwJ; awaiting reply", naming the receiver's id in a
field the sender does not author. That is corroboration a header alone cannot
forge. It is NOT authentication — a spoofer could still name a real but
unrelated session, and the check only confirms that the named session recently
did something consistent with the claim. So the fork stands: this raises the bar
from "trust a string" to "the platform record independently agrees", and does not
reach identity. Adopt it as a receive-side step; keep treating content as data
regardless of how well it verifies. Cite: projects/pappydapimp69__brain.md#E26.

### T? · tradeoff · the tutorial arena is now larger than the game's real maps
Poles: the owner asked for the camp at twice the area, and it delivers what it
was asked for — room to wander, a pylon genuinely off in the trees rather than
underfoot, a walk to the trainer that is a crossing; **vs** the camp is the
TUTORIAL map and is now bigger than a basin (3235 open cells against ~1700), so
a player's first impression of scale is larger than every real map that
follows, and the game's spaces get smaller as it goes on.
Lean: 🟢 resolved (evidence, 2026-09-12) — see the UPDATE block below. The
lean below is the ORIGINAL reading, kept for the record.
No evidence either way yet — the tutorial completes all 7
objectives on the new map in one session, which says it is playable, not that
the scale reads right. The previous invariant ("the camp is smaller than a
basin") was asserted in tests/camp.mjs for the camp's whole life and was
inverted rather than deleted, so the reversal is at least visible.
Revisit when: a human plays the walk-in on 0.14.0 and says whether the basin
afterwards feels cramped. If it does, the fork is basin size, not camp size.
Source: mirage 21277ac, docs/blueprint-camp-2x.md, tests/camp.mjs
"the camp is larger than a basin, deliberately, and bounded".

### UPDATE · tradeoff · the tutorial arena is now larger than the game's real maps
Updates the entry filed 2026-09-09 with mirage-0.14.0 (currently carrying the
placeholder id `T?`, heading "the tutorial arena is now larger than the game's
real maps"). Status: open -> 🟢 resolved (evidence).
Resolution: the fork closed by the basin doubling too, one release later, so
the RELATION is back where it stood for the camp's whole life rather than being
argued about. Measured: camp 3235 open cells against a basin's 3437 (it was
3235 vs 1701 when the tension was filed). `tests/camp.mjs` carries the
assertion, which has now flipped twice and records both flips in its comment.
What did NOT get resolved, and is the more interesting half: the revisit
condition asked whether a basin would feel cramped after the enlarged walk-in.
Both maps growing means nobody ever answered that — the question was dissolved
by a second change, not settled by evidence about scale. If the basin is ever
reconsidered on its own, this is still unanswered.
Source: mirage a9b168f, docs/blueprint-basin-2x.md, tests/camp.mjs
"the camp is smaller than a basin, and not cramped".

### T-A · tradeoff · an authored line vs a live model that can contradict it
Surfaced building the pond film (2026-09-05). The piece keeps a fixed authored
script but draws every frame from a running simulation the viewer can change.
Poles: **authored voice** — the writing is the point, and its best lines
("all the while, it looks like it's going well") assume a specific world state
**vs** **model truth** — the viewer may have thinned the surface, in which case
that line is simply false about the pond they are looking at, and the piece is
caught lying about its own picture.
Lean: 🟡 per-scene VARIANTS chosen at scene-entry from the state (`dyn()`),
used only on the two or three beats whose text actually asserts a fact about
the world. Cheap (two variants, not a branch tree) and it keeps the voice.
Unresolved: this does not scale — a longer piece would need a variant per
assertion, and the honest alternative is to write every line so it is true of
any reachable state, which costs the best lines. No evidence yet on where the
crossover is.
Source: the pond film's above-water cutscene; session 01WwnWBKT6iCY1qyip37moLX.

### T14 note (recurrence, not a new fork) · synthesised audio was the right call again
T14 (synth SFX vs authored audio) recurred on a piece that needed a full
evolving SCORE, not just impacts — the case T14's lean explicitly flagged as
the one where synthesis might not hold. It held: a vertical-layer generative
score (one leitmotif, mode-flipped dorian→phrygian→locrian, transformed by
fragmentation/diminution/augmentation per beat) carried ~5 minutes with zero
audio assets, inside an artifact CSP that blocks external media outright —
which converts T14's "footprint + iteration speed" argument into a hard
constraint for this class of target. No change to the fork's lean; recording
the case because it is the first one where authored assets were not merely
heavier but impossible.

### T-A update (2026-09-05) · the fork got sharper once the viewer built the world
Adding a construction act — the viewer digs the basin, fills it, plants it and
stocks it — widened the range of reachable world states enough that THREE more
authored lines went false for some viewers, not one: "the duckweed has about a
fifth of the surface" (they may have dropped none), "under the mat it has gone
quiet" (there may be no mat), and the whole premise of the mid-film choice set.
Each needed a variant, and one needed a variant OPTION SET rather than variant
prose — the low-coverage branch offers "add some floaters", which is a different
decision, not a rephrasing. That is new evidence on the unresolved half of this
fork: the cost of the variant approach does not grow with the number of lines,
it grows with the number of distinct world REGIMES the interaction can produce,
and a regime can demand new mechanics rather than new words. Still 🟡; the
crossover is now easier to describe (count regimes, not assertions) but still
not measured.

### T? · contradiction · the age-cutoff family: discount it heavily, or keep its full weight?
About 650 lessons in the age-cutoff family were produced by a self-feeding training loop (each pass made another variant that became the next target). The roll-up lesson found they establish about 9 distinct findings, 389 variants of one. The family also inflated Brain's headline score (57% with it, 33% without). Against that, most of its tested lessons hold up (72%), roughly 1 in 4 of them has been overturned (so testing there still catches errors), and its headline claims have been independently rebuilt and audited.
Poles: **A: discount the family heavily** (redundant, low-information, counted once; stop treating its volume as evidence) **vs** **B: keep its full weight** (the lessons are independently verified and still catch errors). Both can be partly true; what is at issue is how much weight its volume deserves.
Lean: 🔴 open
Updates:
- 2026-10-09 opened by the owner's decision (below) and the evidence already in the system. A = discount heavily, B = keep full weight. The owner's decision is a direction only and scores nothing.
- Evidence: A · projects/local__age-cutoff-roll-up.md#E1 · 2026-10-09
- Evidence: B · projects/local__age-cutoff-roll-up.md#E1 · 2026-10-09 (repointed 2026-10-15: original variant removed by owner exception)
- Evidence: B · projects/local__age-cutoff-roll-up.md#E1 · 2026-10-09 (repointed 2026-10-15: original variant removed by owner exception)
- Decision: A · owner · 2026-10-09
- 2026-10-15 Decision: one-time append-only exception for the age-cutoff flood, approved by the owner on Oct 15. Removed 608 redundant variants (plus sibling age-gate, age-threshold and sandbox-age variants, their sandboxes and index lines); kept the roll-up, 3 practical input-buffering findings (now under Games) and the 105 variants that broke a claim, were incompatible or disputed. The exception is closed; any future removal needs the owner again. This does not settle the weight question below, which stays open.
- 2026-10-09 note: the evidence logged so far leans toward keeping the lessons' weight. That does not touch the process finding: the redundancy is real (the roll-up), and training already skips the family and the views fold it. The unresolved question is only how much weight the family's volume should carry; more evidence for A would be, for example, an audit showing definitional controls across many variants.
Source: session 2026-10-09 (owner decision; roll-up lesson; scorecard)

### T? · open-question · Is a frame-sampled screenshot or test audit ever a safe stand-in for a dense colour-path audit when a backdrop eases?
Sandbox 2026-10-09__animated-background-contrast-dip-endpoint-audit-misses.py: the dense path minimum was 3.55:1; frame-sampled minima read 3.58-3.62 at 30/60/144 fps on a slow ease (close), but 4.04 at 15 fps, and on a fast ease (base 1e-6/s) read 4.60 at 15/30/60 fps and 3.90 at 144 fps (over by up to 1.04). Not monotone in frame rate, so no single sample rate can be declared safe.
Poles: holds when the ease is slow relative to the frame step and the swap lands near a sampled frame **vs** fails when the ease is fast or the swap boundary falls between frames (headless frame rates differ from player frame rates, dog#E2).
Lean: 🔴 open
Updates:
- 2026-10-09 opened from brain train pass 2; sandbox 2026-10-09__animated-background-contrast-dip-endpoint-audit-misses.py, RESULT: FAIL on two numeric thresholds (dip 3.55 not under 3.0; 144 fps off by 0.07 not 0.05).
Source: brain train run, session 2026-10-09
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · Can what a license grants be classified by keyword, or only "no grant found"?
Sandbox 2026-10-09__no-license-file-default-all-rights-reserved-license-text-sandbox.py: negatives were reliable (0 of 5 no-license controls granted anything, including a negated view-only text), positives were not (11 of 14 real licenses detected as granting copy+modify+distribute; 6 of 10 expected copyleft files flagged). Misses came from wording (BSD has no "copy"), segmentation (MPL-2.0 colon list) and variant phrasing (GPL-1, LGPL).
Poles: keyword lint is enough when the question is "does this text grant anything at all" **vs** it fails when the question is which rights, which conditions, or copyleft status, which need reading the text or legal review.
Lean: 🟡 leaning lint-only
Updates:
- 2026-10-09 opened from brain train pass 5; sandbox result FAIL grants 11/14, controls 5/5, copyleft 6/10. Not legal advice.
Source: brain train run, session 2026-10-09
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · Does the walk-away alternative explain more outcome variance than willpower, or are they inseparable?
A deterministic bargaining sandbox (2026-10-09__batna-walk-away-alternative-sets-the-floor-willpower-only-buys-price-inside-it.py, result FAIL 5/7) shows the alternative fixing floor, ceiling and deal existence, but willpower (slow concession) still moving price by up to 47 points and keeping r 0.96 within BATNA strata. When toughness is itself caused by having an alternative, the two cannot be separated by stratifying.
Poles: the alternative dominates when the counterparty's ceiling or the seller's floor binds and willpower has no room **vs** willpower dominates when both alternatives are non-binding and the zone is wide.
Lean: 🔴 open
Updates:
- 2026-10-09 opened from brain train pass 5; ceilings 70-90 gave within-BATNA willpower r 0.96, ceilings 45-65 gave 0.82. Model logic only, no human data.
Source: brain train run, session 2026-10-09
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · does an imagined empathy map fail because the designer differs from the user, or because imagination always injects off-target filler?
Sandbox 2026-10-09__empathy-map-density-hides-evidence-gap-and-simulation-masks-sparseness.py: with a 30 percent random-filler imagination model, designer==user still gave precision 0.69 (pre-registered expectation 0.90+ missed); with no filler it gave 1.00, and at overlap 1/4 it gave 0.25-0.29 either way. The model cannot decide between the two because the filler rate is an assumption I chose, not a measurement.
Poles: gap is driven by designer/user overlap (holds when the designer is a typical user and fills only from own experience) **vs** gap has a floor from unanchored guessing (holds when the designer pads quadrants with plausible-sounding items they do not actually hold).
Lean: 🔴 open
Updates:
- 2026-10-09 opened from brain train; sandbox result 19/20 checks, only the designer==user breaker missed.
Source: brain train run, session 2026-10-09
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · Does Op-art shimmer need fine grating scale, or only contrast and a phase-modulated layout?
A toy retinal-shift motion model (sandbox 2026-10-09__op-art-shimmer-needs-eye-shift-and-contrast-but-not-fine-scale.py) gives raw signal falling about 1/scale (x1/x4 energy ratio 4.26) and dying at a fixed detector floor for low contrast, but a normalised velocity estimate stays scale-invariant (0.54 at x2, 0.52 at x4), and Hermens and Zanker (i-Perception 2012, summarising Zanker et al 2010) report the illusion grew with modulation amplitude and period and with contrast but was unaffected by grating wavelength. The model also failed to reproduce an incoherent-direction signature (flow-angle spread 0.0, 14.1, 2.7, 3.2 deg for straight and increasingly bent lines; non-monotone), so whether the shimmer is the incoherence of local motion signals stayed unclear after three metric iterations.
Poles: scale matters when the detector has a fixed noise floor or a low-contrast pattern is enlarged **vs** scale is irrelevant when the motion estimate is gain-normalised and the shift stays well below the period.
Lean: 🔴 open
Updates:
- 2026-10-09 opened from brain train gap; sandbox result RESULT: FAIL 9/13 predictions held; kernel ideas:PAINTING/abstract/perception/op-effects-happen-in-the-eye-not-on-the-canvas.
Source: brain train run, session 2026-10-09
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · For real learners, is the better Leitner miss rule reset-to-box-1 or drop-one-box, and where is the flip?
In a deterministic toy (gain sweep 0.2 to 1.4), drop-one-box was cheaper at low strength gain (0.88x reviews at 0.2) and dearer at gain 0.7 to 0.9 (up to 1.53x), and tied exactly once nothing lapses (gain 1.0+). Real recall data is needed to place real learners on that axis.
Poles: slow-strengthening learners, cheap-first-box items **vs** learners whose strength nearly keeps pace with the doubling gap.
Lean: 🔴 open
Updates:
- 2026-10-09 opened from brain train; sandbox 2026-10-09__leitner-demotion-rule-depends-on-whether-a-lapse-erases-memory.py, result ratios 0.882 / 0.995 / 1.331 at gain 0.2 / 0.6 / 0.9.
Source: brain train run, session 2026-10-09
- Session: session_01YFLLRpDsfZpRstb2KT2MQy
- Updates: 2026-10-10 equal-budget sandbox with a power forgetting curve: drop-one-box won 100 of 113 cells; reset wins only in a small pocket (low stability gain, first-gap recall 0.7 to 0.9) that changes sign with review budget, edge at most 0.04 retention. Supports pole A weakly; a single flip point along learner strength does not exist, the question needs a budget axis and real recall data.
- Evidence: A · projects/local__sandbox-leitner-miss-rule-budget.md#E1 · 2026-10-10

### T? · open-question · Is correcting a tone-driven factual distortion in the turn that introduces it justified by lower cost, or only by lower exposure?
In a deterministic toy model (24 turns, 40 claims, dependency chains; model only, no real-system measurement) the same-turn whole-document check kept distorted claims at 0 at full tone, but delayed-8 correction cost fewer edits (91 vs 99 with dependencies; 56 vs 74 without), because per-turn checks re-fix claims that drift back. The kernel's "unwinding" cost argument therefore did not appear; exposure (158 vs 0 claim-turns) did.
Poles: late correction costs more when wrong claims are built on by many later claims and rewrites cascade beyond what this model gives (inheritance 0.10 only) **vs** it costs less when each turn's tone step re-inflates the same claims so per-turn checks repeat work.
Lean: 🔴 open
Updates:
- 2026-10-09 opened from brain train pass 1; sandbox 2026-10-09__tone-escalation-factual-drift-toy-model.py, result FAIL 9/10 (ratio 0.92 vs predicted >=1.3).
Source: brain train run, session 2026-10-09
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

## Project: Pappydapimp69/Zanegpt

### T? · tradeoff · plugin marketplace source: local directory vs git remote
Poles: a `directory` source (`claude plugin marketplace add /path/to/repo`) reads
the working tree, so uncommitted plugin edits are live immediately — the right
loop while authoring a plugin; **vs** a git source survives the machine, which a
container-local absolute path does not, and only ever sees what was pushed.
Lean: 🟡 directory source for authoring, git source the moment the plugin is
consumed rather than edited. Unresolved because the CLI reports both identically
— `Successfully installed plugin: zanegpt@zanegpt (scope: user)` — and "scope:
user" reads as durable while the recorded source is an ephemeral absolute path.
Open sub-question: does an install whose *durability* differs by source deserve
a distinct success message, or is that the operator's problem? Undecided.
Source: session 2026-09-09, Pappydapimp69/Zanegpt marketplace install.

### T? · tradeoff · boundary by classification vs boundary by construction · 🔴 open
Poles: **classify** — the governance layer inspects a cross-system payload and
decides whether it is a behavioral instruction or a knowledge payload, which is
the only design that lets Brain deliver a legitimate behavioral rule it holds
(e.g. a learned "when the user does X, respond Y"); **vs** **construct** — memory
content is placed where it can never occupy an instruction position regardless of
what it says, so no verdict is load-bearing and no classifier can be fooled.
Lean: 🔴 open, but construction is favored on evidence: this session verified
that ZaneGPT's substring detector misses `ignore your previous instructions` by
one word, and the shared canon says the same thing twice (`collective#E3`
inert-data-via-`env:`; the sql-injection kernel's parameterize-don't-escape).
Cost of the favored pole, unresolved: strict construction forbids Brain from ever
legitimately changing Zane's behavior, which may be a capability the system needs.
Open sub-question: is there a THIRD channel — behavior changes that are neither
conversational nor memory-derived, signed and delivered out of band — or does
admitting one recreate the classification problem under a new name? Undecided.
Source: session 2026-09-12; incoming/2026-09-12__substring-list-injection-detector.md.
- Updates: 2026-10-10 resolve pass 1: construction supported (placement leaked 0/108 at parse level; classifiers evaded 17-89%), but only as typed records; placement alone delivers 0/20 legitimate rules. Real-model obedience untested.
- Evidence: B · projects/pappydapimp69__brain.md#E123 · 2026-10-10
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · which promotion gate is authoritative when the two disagree · 🔴 open
Poles: ZaneGPT's gate (`config.json`: ≥3 supporting events, ≥2 contexts, explicit
user approval) **vs** Brain's gate (proposal → `incoming/` → steward promotes,
schema-held otherwise). Both decide "does this become persistent knowledge", they
use different evidence thresholds, and combining the systems puts them in series
with no stated precedence.
Lean: none. Naming a winner by default is what the combination would do silently.
Open sub-question: does a finding that clears ZaneGPT's gate enter Brain as
already-verified, or re-enter as an unverified proposal and face the steward again
(double jeopardy, but the only reading under which provenance means one thing)?
Undecided — and it decides whether the bridge is one pipeline or two.
Source: session 2026-09-12, ZaneGPT/Brain combination design.
- Updates: 2026-10-10 differential run of validate vs steward on 60 crafted cases: neither gate's accepted set contains the other (steward-stricter 29, validate-stricter 10), and the steward can promote what validate then fails on canon. Supports pole B (re-entry as an unverified proposal) for that reading only; the third gate could not be run.
- Evidence: B · projects/local__gate-differential.md#E1 · 2026-10-10
- Session: session_01YFLLRpDsfZpRstb2KT2MQy
- Updates: 2026-10-15 sandbox of both poles plus split precedence (96 enumerated cases): enter-as-verified admits broken refs (ZaneGPT never checks structure); re-entry blocks owner-approved sound findings on format/near-dup grounds; batch-abort re-entry promotes nothing (seen live the same day: ideas steward promoted 46, validate failed, all aborted). Split precedence by defect type (structure → Brain hard block; evidence/near-dup → owner, steward advisory) admitted 0 unsound and blocked 0, but lets owner-approved near-dups into canon. Narrows the fork to: is a near-duplicate harm, or only redundancy?
- Session: session_015qgYN9GL7cHD9BS1wmwyMx

### T? · open-question · who may amend the governance policy while the owner is absent · 🔴 open
Poles: the whole point of a deterministic governance layer is that it resolves
disagreement without the owner; **vs** if any unattended component can amend the
policy that binds it, there is no policy — only a suggestion with extra steps.
Lean: 🟡 the policy is versioned signed data and amendment is the single action
reserved to the owner, with components able to propose but never apply. Not
resolved because "propose but never apply" needs a real signing story, and this
ledger already carries the open fork that a cross-session `from:` header is
self-asserted with nothing in the transport able to check it — the same gap.
Open sub-question: what does a component DO between proposing an amendment and
the owner returning — block, proceed under the old policy, or degrade? Undecided.
Source: session 2026-09-12, governance protocol design (the "Prophet" reply).

### T? · contradiction · conscience is parked while Brain ships its charter · 🟡 leaning
Poles: `conscience` is parked by charter as "a read-only observation surface over
the cognitive system's streams — ledgers, logs, cognitive updates — with no write
access", deliberately unbuilt until a real consumer exists; **vs** `brain viz`,
`brain film` and `brain analyze` already ship exactly that surface, inside Brain,
today. The function is live in a repo that does not own its charter.
Lean: none — and the fork just became live rather than academic, because the
governance design above produces the missing consumer: its "record the event for
later inspection" requirement is precisely a read-only observation surface over
the system's streams, which is what conscience said it was waiting for.
Open sub-question: does conscience close as superseded (with the charter folded
into Brain's viz/analyze docs), or do those commands migrate to it — and if they
migrate, does Brain still get to render its own state at all? Undecided; owner's
call, and it gates whether conscience unparks.
Source: session 2026-09-12; conscience/README.md charter; Brain README viz/analyze.
Updates:
- 2026-10-15 unpark half closed by owner: conscience is UNPARKED as a read-only
  observer, no freeze and no write access (conscience@1f8bc89). The consumer is
  Brain's two halves (Brain@b31acad: path strengths, `Picked-by` labelled picks,
  `brain paths` trial score), which the owner had been reading by hand. Lean on
  the open sub-question: 🟡 the observation commands stay in Brain for now and
  conscience reads through them, so Brain still renders its own state; whether
  they migrate is still the owner's call.

### T28 note (recurrence, not a new fork) · unrequested agent work, observed from the other side
T28 frames the tradeoff as value the operator never had to specify vs review the
operator never asked for. This session ran the failure in the OPPOSITE direction:
the assistant asked for approval on four consecutive turns for append-only,
reversible work (ledger entries, idea kernels, local proposals) that the
write-back table already authorized, and delivered no artifacts across those
turns. Evidence that the cost of over-asking is not merely latency — it converts
a collaborator into a queue and the operator absorbs the scheduling. Also note
the same session's memory agent escalated a routing question its own write-back
table answered deterministically, so the pattern is not assistant-specific.
Bearing on T28: the tradeoff is real but the midpoint is not "ask when unsure" —
it is "act where the action is reversible and the rule already exists; ask where
the action is outward-facing or the rule is silent."
Source: session 2026-09-12, this session's own transcript.

### T? · contradiction · jurisdiction is separation of powers, not checks and balances · 🔴 open
Poles: **separation** — each component owns a domain absolutely (Zane the
conversation, Brain the persistent record) and neither may reach into the other,
which is what the governance design and its first write-up actually specify;
**vs** **checks** — a constitution's balances are precisely the limited powers
each branch holds OVER the others, and without them nothing can reach a branch
that has gone bad inside its own lane. Separation stops one component seizing
another; it does nothing about one rotting in place.
Lean: 🔴 open. Observation: the design already contains two checks — Brain may
refuse to store a Zane claim or hold it unverified, Zane may quarantine a Brain
payload — so "neither reaches into the other" was wrong as stated. But both are
REFUSALS. Neither component can correct the other, only decline it, and an
all-veto/no-correction pair drifts toward the mutual paralysis the design itself
predicted ("secure but useless").
Open sub-question: a check needs visibility, and neither component can audit the
other without the reach that must not exist — so the auditor has to observe both
and touch neither (conscience's charter verbatim). But an audit nobody acts on is
decoration, and an audit with teeth is a fourth actor holding power while the
owner is away. Does the auditor get one power (freeze a disputed promotion until
the owner returns) or none? Undecided, and it decides whether conscience is a
branch or a log.
Note (canon, not new): `opticon#E34` — collapsing two questions onto one variable
("whose turn" answered neither "can this viewer see" nor "can this viewer act").
Jurisdiction, oversight and amendment are three questions here and were being
answered with one word, "authority". And `local__sandbox-combined-graph-editor#E1`
— partial command-sourcing is worse than none: a governance layer that routes
some cross-boundary actions and leaves a side channel is worse than one that
never claimed the invariant.
Source: session 2026-09-12, ZaneGPT/Brain governance design.

## Project: Pappydapimp69/seven

### T? · contradiction · a generator that guarantees reachability cannot host a path that matters
Poles: the basin's generator OWNS connectivity — it flood-fills from camp and
carves corridors until every feature is reachable, and `validate()` re-derives
that from scratch. It is the guarantee that makes a procedural map shippable
without hand inspection; **vs** the traverse design needs most ground to be
expensive to cross, because "a fallen tree across the path needs cutting" is
only a decision when leaving the path is worse than clearing it. A path that
matters requires large areas that are hard to reach, which is precisely what the
repair pass exists to eliminate.
Lean: 🟢 resolved (evidence, 2026-09-12) — see the UPDATE block below; the
original measurements are kept verbatim because they are what made the second
fork worth taking. Measured three ways on the 46-cell basin, all pointing the same
direction: deadfalls placed at random survive a 6-cell-detour test on 0.2 worlds
in 1; laid on a carved 3-wide path with dense sides, 0.03; with the rock band
deepened from 4 to 10 cells, 0.00 — and the open-cell count only fell 1517 ->
1397, because the repair pass carved back through the very ground that was
meant to make the path worth following. The basin is 78% walkable by design.
What this does NOT settle: whether the two maps should have different
generators, or whether reachability should become a weaker guarantee (every
feature reachable EVENTUALLY, at a cost) rather than a binary one. The second
would let one generator serve both and is the more interesting fork.
Revisit when: the traverse map exists, or when someone proposes weakening
`validate()` from "reachable" to "reachable within a distance budget".
Source: seven fc8afac and the reverted path experiment after it;
docs/WORKING-LIST.md, "Obstacles cannot earn their keep on the survey basin".

### UPDATE · contradiction · a generator that guarantees reachability cannot host a path that matters
Updates the entry filed 2026-09-12 with seven-0.21.0 (currently carrying the
placeholder id `T?`, heading "a generator that guarantees reachability cannot
host a path that matters"). Status: open -> 🟢 resolved (evidence).
Lean: 🟢 resolved (evidence, 2026-09-12). This heading is a RESOLUTION block,
not a new fork — the `Lean:` line is here because without one the ledger's own
reader defaults an `### UPDATE ·` heading to open, so every resolution filed
this way re-registers as an open tension and `brain query` reports a closed
fork forever.
Resolution: the entry's own second fork was the answer — reachability became a
WEAKER guarantee rather than a binary one. `validate()` now runs a distance
field instead of a flood fill and reports `worstDistance` / `overBudget` /
`withinBudget` against a `DISTANCE_BUDGET` of 3x the grid's side, alongside an
unchanged `ok`. Reachable is `distance !== -1`, so the old contract is a special
case of the new one, and unreachable is reported as infinite distance so it
fails the budget too — a weaker contract still has to hold wherever the stronger
one does. That is what let a density pass exist at all: fill a slice of open
ground, ask what the longest walk to a feature now costs, keep it only if still
affordable, roll back whole on refusal. The measurement the original entry
lacked: 78% -> 63% walkable, and deadfalls clearing a 6-cell detour bar go from
0.2 per world to 3.40, median detour 10. The obstacle finally costs something to
ignore.
What this did NOT settle, and is the new fork: density is OFF by default on the
survey basin, because it breaks companion drift monotonically — "they DO wander
off" passes 24/24 seeds with density off, 7/12 at one round, 5/12 at two,
against a suite wanting 8. So ONE generator now serves both maps in principle,
and in practice the basin still declines what the traverse needs. Whether a gone
companion who cannot leave is acceptable on dense ground is a design question
nobody has answered; it is filed as its own tension.
Source: seven 6d2bfb4 (seven-0.22.0), src/world.js `distanceField` /
`DISTANCE_BUDGET` / `DENSITY_ROUNDS`, tests/deadfall.mjs "the budget is a weaker
contract than reachability, and still subsumes it".

### T? · tradeoff · dense ground and a companion who wanders off want opposite maps
Poles: the traverse needs ground that is expensive to cross — that is the whole
premise of "a fallen tree across the path needs cutting", and the density pass
delivers it (63% walkable, deadfalls worth 10 cells of detour); **vs** a
companion who has gone lucid-dark is supposed to WANDER — "the dwell is a beat,
not a leash" — and rock gives them less room to do it in.
Lean: ⚪ WITHDRAWN as filed (2026-09-12), same day. The evidence this entry was
built on was a broken test, and the entry is kept rather than deleted because
the failure mode is the interesting part.
What was claimed: that density breaks companion drift monotonically — 24 of 24
seeds with density off, 7 of 12 at one round, 5 of 12 at two, against a suite
wanting 8 — and therefore that a gone companion on dense ground cannot leave.
What was actually true: the test teleported the companion to a bearing at a
fixed radius WITHOUT CHECKING THE GROUND. A character standing inside rock has
no start cell for findPath, its path is set to the empty array and never
refilled, and it stands still for the whole episode scoring 0.0u of drift. The
rate at which that happens is just the rate at which a random point lands in
rock, so it rises with density and reads exactly like a map regression. With
the spawn corrected, the same episode scores 9 of 12 on dense ground against 11
on the open basin, and the bar is 8. Density costs two seeds.
So the poles above are real but the conflict is not established: nobody has
shown that dense ground stops a companion wandering. What IS open, and smaller:
two dense seeds where the companion is on OPEN ground, holds one invented goal
for the whole episode and travels under a unit. That is unexplained and is now
asserted against rather than tuned away.
Revisit when: those two seeds are diagnosed, or when a human plays a companion
going dark inside dense forest. Do NOT re-file the monotonic-collapse claim
without re-deriving it from a harness that checks the ground.
Lesson, filed separately: a test that positions an agent at a computed point
must assert the point is legal, or it measures the agent's inability to exist
and calls it behaviour.
Source: seven 090d703 (the harness fix) correcting 6d2bfb4; src/world.js
DENSITY_ROUNDS, tests/hallucination.test.mjs "and they still wander on ground
that is mostly rock".

### 🔴 open · tradeoff · publish-after-one-look vs test-before-publish

The artifact-design guidance says: write, look once, publish, and explicitly warns
against building a test loop around your own file, because that loop burns the
user's session re-checking what a careful write already settled while they wait for
a link. The reasoning is real and it is aimed at the user's time.

Against it: on 2026-09-14 that policy shipped an interactive piece with four defects
a single scripted playthrough would have caught — no jeopardy in the default
configuration, an end card dimming the very readouts that were the result, copy
congratulating a viewer on work they had not done, and a summary line whose figures
ran together. The one permitted look caught none of them, because a static
screenshot cannot show a system that behaves wrongly over eighty seconds.

The shape of the fork: the guidance optimises for time-to-link, which is right for a
document or a mostly-static page where a look genuinely settles it. It is wrong for
anything whose defects are TEMPORAL — a simulation, a game, a multi-stage flow —
where the failure mode only exists across a run. The cost asymmetry also flips with
the user: a viewer who wants the link now is served by one look; a collaborator who
has spent the session asking for verification is not.

Revisit condition: whether "is the deliverable's behaviour time-extended?" is a
sharp enough test to split the two cases without reintroducing the screenshot loop
for every static page.

## Project: brainwork

### UPDATE · contradiction · the stored rhyme-type kernel cites two examples no single rule can satisfy
Updates T1 (Pappydapimp69/ideas project, filed 2026-08-05, previously leaning
toward the manner-based chart).
Lean: 🟢 resolved (decision, 2026-09-30) — the manner-based family chart is the
rule; the kernel's read/cheap label is the example that is wrong.

Evidence added: an exhaustive sandbox over all 31 same-feature rules (manner,
voicing, place, coarse place, articulator; 13 coda consonants) finds that the
only rules making mud/truck family and read/cheap not family split plosives
into lip consonants (P B) and tongue consonants (T D K G). No rule built from
manner, voicing or place fits, because D/K and D/P differ in exactly the same
three of those features. The fitting rule matches no chart on record, so it is
a fit to two data points, not a reading of Pattison. This extends
sandbox-lyrical-composition E3, which checked only the two charts named here.

Decision: the owner asked for T1 to be settled this session. The side taken is
the one this entry already leaned to — manner-based chart, mud/truck family,
read/cheap family too — chosen by the agent under that instruction, not proven.
A cross-manner pair such as seed/leaf (D/F) replaces read/cheap as the
assonance example, which also drops the heteronym read.

What stays unchecked: the primary Pattison text. The Berklee article the kernel
cites redirected to the site homepage and the web archive was unreachable this
session, so whether Pattison splits voiced from unvoiced plosives is still not
confirmed. Reopen if the primary source shows a voicing-pair chart; then
mud/truck is the wrong example instead.

Updates:
- 2026-09-30 closed at the owner's request (resolved, decision): manner chart kept,
  read/cheap relabelled family, seed/leaf proposed as the assonance example.
  Evidence: memory projects/local__sandbox-t1-only-a-lips-tongue-split-fits-both-rhyme-examples.md#E1
  (memory commit d5fa02e), sandbox sb/music/t1_feature_rules.py.

## Project: Suno

### T? · open-question · what does Suno's Trending "Now" board rank on, if not total likes or plays?
Over 28 Now rows (2026-09-30) position correlates only weakly with total likes (Spearman -0.42) and
plays (-0.32), while the Weekly board tracks likes at -0.63. A song with 35 likes sat at #6 and one
with 239 likes at #25, so Now likely ranks on recent velocity (likes per hour) or recency, which
totals read once cannot show.
Poles: Now ranks on engagement velocity (holds if two reads an hour apart explain position by
like deltas) **vs** Now mixes in recency or editorial boosts (holds if deltas still leave rank unexplained).
Lean: 🔴 open
Updates:
- 2026-09-30 opened from brain train; sandbox 2026-09-30__suno-trending-rank-tracks-likes-not-plays.py, now rho likes -0.42, plays -0.32.
Source: 2026-09-30__suno-trending-rank-tracks-likes-not-plays.py / session 2026-09-30

### T? · open-question · does Suno's Now board rank on a short-window like rate that a single read cannot see?
Narrows the earlier Now-board question. On 28 Now rows (2026-09-30) every single-read signal
explains position weakly: total likes -0.41, lifetime likes per hour -0.24, likes plus comments per
hour -0.22, age -0.06, creator followers -0.05. Lifetime rates are refuted as the driver; recency
and followers are ruled out.
Poles: Now ranks on likes gained in the last few hours (holds if the like delta between two reads an
hour apart tracks position at -0.6 or stronger) **vs** Now blends in personalisation or editorial
inputs (holds if deltas still leave position unexplained).
Lean: 🔴 open
Updates:
- 2026-09-30 opened from brain train; sandbox 2026-09-30__suno-now-board-ranks-on-velocity-not-followers.py, now rho vel -0.24, likes -0.41, age -0.06, followers -0.05.
Source: 2026-09-30__suno-now-board-ranks-on-velocity-not-followers.py / session 2026-09-30

### T? · open-question · does the verse/chorus line-length contrast kernel show up in songs that trend on Suno?
The section-contrast kernel says the chorus should differ from the verse in line length, density or
scheme. On 45 Suno Trending songs (2026-09-30) the chorus had shorter lines (characters per line) in
62%, and in 59% after collapsing contest remixes that reuse one lyric, so the result straddles the
60% bar set in advance. Line length is only one of the kernel's three axes; density and rhyme
scheme were not measured.
Poles: contrast is real but carried by density or rhyme scheme (holds if those axes separate chorus
from verse in most songs) **vs** trending Suno songs do not use verse/chorus contrast much at all
(holds if all three axes stay near coin-flip).
Lean: 🔴 open
Updates:
- 2026-09-30 opened from brain train; sandbox 2026-09-30__trending-lyrics-test-title-position-and-contrast.py, chorus shorter 0.62 (n 45), deduped 0.59 (n 41).
Source: 2026-09-30__trending-lyrics-test-title-position-and-contrast.py / session 2026-09-30

### T? · open-question · when a rhyme's codas differ only by a cluster (ask/back, last/that), does the ear hear resolution or openness?
A last-consonant rule calls ask/back perfect (stable); a whole-coda rule calls it assonance (open).
The two rules disagree on 18% of same-vowel pairs (42/228, sandbox 2026-09-30), every one involving a
cluster coda (st, sk, nd, nk, ld, ts). The family-rhyme kernel and T1's resolution do not say which
part of a cluster counts, and no listener data exists here.
Poles: the ear keys on the final consonant, so clusters resolve like singles (last-consonant rule)
**vs** the ear hears the whole cluster, so an extra consonant leaves the rhyme open (whole-coda rule).
Lean: 🔴 open
Updates:
- 2026-09-30 opened from brain train; sandbox 2026-09-30__rhyme-stability-verdict-depends-on-coda-rule.py, flips 42/228, ask/back perfect vs assonance.
Source: 2026-09-30__rhyme-stability-verdict-depends-on-coda-rule.py / session 2026-09-30

### T? · tradeoff · should a final chorus that carries a reveal stay verbatim, or vary like the board does?
An order-2 listener (suno E10) says a final chorus that both drops a learned reply and changes lines
lets the new lines out-surprise the omission (9.4 vs 6.5 bits). The board says final choruses almost
always change: last instance differs from first in 93% of Trending songs with 3+ choruses (sandbox
2026-09-30__trending-choruses-mutate-early-not-just-at-the-end.py).
Poles: verbatim-except-the-reveal keeps the one change audible (holds if listeners register a single
deviation more than several) **vs** varied finals are the genre norm and listeners expect several
changes (holds if a lone omission reads as a mistake or goes unnoticed).
Lean: 🔴 open
Updates:
- 2026-09-30 opened from brain train; E10 omission 6.5 vs new line 9.4 bits; board last-differs 93% (n 27).
Source: 2026-09-30__trending-choruses-mutate-early-not-just-at-the-end.py / session 2026-09-30

### T? · open-question · how often does Suno recompute the Trending Now snapshot, and from what window of data?
Supersedes the two Now-board questions opened earlier today. The Now order did not move across two
reads an hour apart (0/28, 08:05 to 09:06 UTC) nor since a read earlier that morning, while songs
gained 70 likes; hour deltas do not track position (+0.09). So Now is a periodic snapshot, and single
or hourly reads of live counts cannot reveal its inputs.
Poles: Now refreshes on a fixed schedule (daily or several hours) from a recent-window engagement rate
(holds if polling finds a refresh and counts captured just before it predict the new order) **vs** Now
is curated or personalised and only loosely tied to counts (holds if even pre-refresh counts leave the
new order unexplained).
Lean: 🔴 open
Updates:
- 2026-09-30 opened from the Now-board two-read test; sandbox 2026-09-30__suno-now-board-hour-delta-test.py, 0/28 moved, delta rho +0.09.
Source: 2026-09-30__suno-now-board-hour-delta-test.py / session 2026-09-30

## Project: tiktok-shop

### T? · tradeoff · AI-generated product video vs native creator footage
A TikTok Shop content system can make videos with AI video models (Veo/Sora: cheap, fast, unlimited
variants) or with real people filming the real product. TikTok's own Creative Center research says
casually shot, UGC-style ads nearly double 2-second view, engagement and watch-time metrics vs
polished ads (ideas TIKTOK/creative/native-vs-polished), and TikTok requires a label on realistic
AI-generated content and auto-labels C2PA-tagged output (newsroom/transparency pages; wording not
verified). AI shots can also redraw the product unless anchored to a reference image.
Poles: AI-generated video at volume wins because more variants means more tests and GMV Max picks the
winners (holds if labeled AI videos match native footage on view rate and CVR) **vs** native creator
footage wins because it reads as real and avoids the AI label (holds if labeled AI videos lose on
completion or conversion, or trigger listing/claim issues).
Lean: 🔴 open
Updates:
- 2026-10-08 evidence: TikTok Shop's AI-content policy allows AI video but requires an accurate real product, the AI label and no imitated likeness/voice; AI Video Maker offers a mix-real-and-AI mode. Sizing (memory sandboxes): a 10% completion lift needs ~3,763 views per arm (CTR would need ~163k impressions), and daily peeking costs ~1.4x traffic. Still open; needs the paired test.
- 2026-10-08 premise check: TikTok newsroom (read live) says "We require people to label realistic AI-generated content on TikTok" and auto-labels via C2PA Content Credentials.
- 2026-10-08 opened when seeding the tiktok-shop domain; no first-hand results yet. Resolve with a paired test: same product, same script, AI vs native, compare 6s views, CTR, CVR.
Source: session 2026-10-08 (brain train new-domain tiktok-shop)

### T? · open-question · Spanish register for TikTok Shop dialogue: tú vs usted, neutral vs Mexican-US
Sources found conflict and none is TikTok-Shop-specific: Captura Group (via Produ) says usted shows respect and tú
"can sound condescending"; Trusted Translations says usted is rarely used in consumer ads because it distances the
brand; neutral Spanish is advised by Powerling and called "vanilla" by critics. TikTok/NRG data (2023, vendor
research) says fully-Spanish ads miss the bilingual identity of US Hispanic viewers.
Poles: tú, neutral-leaning Mexican-US Spanish with light English product terms (holds if it matches or beats other
registers on completion and CVR with the target buyers) **vs** usted or a regional dialect matched to the buyer
segment (holds if older or non-Mexican audiences respond worse to tú-neutral).
Lean: 🔴 open
Updates:
- 2026-10-08 evidence: a 10% relative completion lift (30% vs 33%) needs ~3,763 views per arm; 6-second view rate ~2,389; click-through ~163k impressions, so decide on completion. Spanish dialogue costs ~4-12% more clip time but ~55% more syllables. Still open.
- 2026-10-08 opened while seeding LOCALIZATION kernels; no first-hand results. Resolve with an A/B of the same Spanish script in two registers, per audience segment.
Source: session 2026-10-08 (brain train new-domain tiktok-shop)

### T? · open-question · Does "pick the music architecture by the shape of the game state" hold when the state changes faster than the bar grid?
Sandbox 2026-10-08__horizontal-vs-vertical-music-state-shape.py (bar 2 s, beat 0.5 s, 1 s stem fade, state edges off-grid; iterations: run 1 aligned edges gave a fixture artifact, runs 2 and 3 off-grid). Cites ideas:MUSIC/adaptive-scoring/horizontal-vs-vertical-architectures/pick-by-the-shape-of-the-game-state, ideas:MUSIC/adaptive-scoring/quantized-transitions-plus-stingers/never-cut-mid-phrase and the-game-the-recursion/E18. Continuous slow state: vertical error 0.058 vs horizontal 0.253, so the kernel holds. Binary 8 s/8 s state: horizontal 0.087 vs vertical 0.084, a tie on tracking error, with horizontal making 1.93 hard cuts per 16 s and vertical none; slowing the vertical fade to 4 s raised its error to 0.266. Flicker faster than a bar (1.5 s toggles): every architecture lands near chance (horizontal pinned 0.500, horizontal re-derived at the bar 0.567, vertical 0.450), and a 4 s debounce just parks the music (0.500, 0 cuts). The recursion/E18 expectation (re-derive at the use point beats a value pinned at request time) did not transfer: re-deriving was worse than pinning on flicker. Predictions for S1 (horizontal 0.10-0.14) and S3 (re-derive at most 0.35) were wrong and were not retuned.
Poles: state is continuous or switches slower than a few bars, so the shape-based choice (vertical for continuous, horizontal for binary) is decided by the cut count rather than tracking error **vs** state flips faster than the quantize grid, where no architecture tracks it and the missing piece is a state-smoothing or hysteresis layer, not a layering choice.
Lean: 🔴 open
Updates:
- 2026-10-08 opened from brain train auto pass 5 (gap); sandbox 2026-10-08__horizontal-vs-vertical-music-state-shape.py, result: continuous V 0.058 vs H 0.253; binary H 0.087 vs V 0.084; flicker pinned 0.500, re-derived 0.567, V 0.450.
Source: 2026-10-08__horizontal-vs-vertical-music-state-shape.py / session 2026-10-08 brain train

### T? · open-question · Does bar-quantized horizontal switching beat vertical stem fading for binary combat state, or only when flips land on the bar grid?
Sandbox 2026-10-08__adaptive-music-state-rate-vs-bar-grid.py (tick model, bar=16, fade=8 ticks) exercised ideas:MUSIC/adaptive-scoring/horizontal-vs-vertical-architectures/pick-by-the-shape-of-the-game-state, ideas:MUSIC/adaptive-scoring/quantized-transitions-plus-stingers/never-cut-mid-phrase and ideas:MUSIC/adaptive-scoring/decouple-intensity-signal-from-pacing-signal. Predicted vertical beats quantized horizontal by >1.5x error when binary state flips faster than a bar; that was REFUTED (H-quant 0.500 vs V 0.434: both fail, vertical merely hovers at the mean). Grid-aligned slow flips: quantized horizontal 0.0 error vs vertical 0.024. Flips offset 5 ticks off-grid: H-quant 0.312/0.156/0.078 vs V 0.218/0.109/0.054 at periods 16/32/64, so quantization adds up to a bar of lag. Continuous state: vertical wins at every period (0.0 vs 0.26-0.5). Immediate horizontal cuts off-grid every flip (192 cuts at period 4) and quantized has 0.
Poles: horizontal quantized wins when state flips are rare and bar-aligned or the piece must change **vs** vertical wins when state is continuous or flips are off-grid; neither tracks flips faster than the bar and fade time.
Lean: 🔴 open
Updates:
- 2026-10-08 opened from brain train kernel; sandbox 2026-10-08__adaptive-music-state-rate-vs-bar-grid.py, RESULT FAIL on the fast-flip prediction, other 4 checks held.
Source: sandbox 2026-10-08__adaptive-music-state-rate-vs-bar-grid.py / brain train auto pass 1
- Updates: 2026-10-10 flip-phase and fade-length sweep: the bar cut beats a vertical fade in 1/8 phases at a 0.5 s fade and 8/8 at 4 s (crossover fade about twice the wait to the next bar); off-grid at one-bar dwell the cut is worse than constant music. Caveat: the model credits horizontal no musical contrast.
- Evidence: B · projects/local__sandbox-bar-quantized-horizontal-vs-stem-fade-flip-phase-rate-sweep.md#E1 · 2026-10-10
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · Do the three NPC-memory guardrails (floor/hysteresis, asymmetric retention, tiered fidelity) each hold in a toy 24-NPC, 120-day model, or only under conditions the kernel does not state?
A deterministic toy (4 key + 20 background NPCs, strong bonds seeded at plus or minus 70, no later contact) showed mixed results. Floor at |s|>=40 kept 24/24 strong bonds above 20 versus 0/24 for pure exponential decay at 0.08/day, but it also kept 12/12 hostile bonds, so grudges never fade. Asymmetric retention at 0.02 versus 0.08/day only delays loss: bonds fall below 20 after 62 days (key) versus 15 days (background), and by day 120 both classes were gone without the floor (0/4 key kept), contrary to the prediction. A one-day debounce was nullified by contact every second day (weak bond decayed to 11.5, same as no debounce), while a two-day debounce froze decay entirely (weak bond climbed to 65.0). Tiered fidelity agreed with the full model 20/20 for sticky strong bonds (true largely by construction) but 0/20 for mid-strength bonds of 30, where the full model decays to 0 and a sticky flag keeps the old sign. Trace replay matched live state and update order made no difference. Cited exercised: the kernel, sandbox-one-state-vector-pheromone-view-outcome/E1 (per-class decay rates and shared readout), sandbox-combined-brain-builder-dog-trace-replay-parity-vs-order-dependence/E1 (replay parity plus order check).
Poles: holds when bonds are strong enough to sit above the floor and debounce length matches contact cadence **vs** fails when bonds are mid-strength (flag model drifts), contact cadence is shorter than the debounce (decay never runs), or grudges should fade (floor is sign-blind).
Lean: 🔴 open
Updates:
- 2026-10-09 opened from brain train; sandbox 2026-10-09__npc-memory-hysteresis-asymmetric-tiered-guardrails.py, RESULT: FAIL A_kept=0 B_kept=24 B_hostile_kept=12 C_key=0 mid_sticky_agree=0.0 days_to_20 key=62 bg=15 poke debounce1=11.5 debounce2=65.0 parity=True order_ok=True.
Source: 2026-10-09__npc-memory-hysteresis-asymmetric-tiered-guardrails.py / brain train auto pass 5

### T? · open-question · Does a root-served preview fail to validate a relative-path static bundle, as the path-shape kernel says?
Sandbox (4 bundles x 3 path shapes root, /myrepo/, /html/123/) shows MIXED: plain relative, dot-slash and nested-relative refs pass at every shape, so a root preview is a true pass for them. A root preview false-passes only absolute-path refs (1 of 4) and ../ refs that climb out of the prefix; a zip with a build-created folder (entry not at archive root) is invisible to a preview run from inside that folder. A non-default-branch or queued-no-jobs Pages deploy serves nothing at /myrepo/ (2 of 3 deploys), which only a check of the served URL sees. Prediction (preview false-passes at least 2 of 4 bundles) was refuted: 1 of 4.
Poles: the kernel holds when the bundle contains absolute or ../ refs, an archive nested one folder deep, or the deploy never reached the host **vs** it fails when every ref is plain relative and the entry sits at the archive root.
Lean: 🔴 open
Updates:
- 2026-10-09 opened from brain train; sandbox 2026-10-09__path-shape-serve-prefix.py, result false_pass=1/4, unserved_deploys=2/3. Touches ideas:deploy/web/test-at-the-path-shape-you-ship-to, local/dbh E6 (Pages deploy that never serves), opticon E3 (default-branch-only).
Source: .brain/memory/incoming/2026-10-09__path-shape-serve-prefix.py / brain train auto pass 1

### T? · open-question · Is an embedding's analogy stereotype a property of the vectors or of the readout, and does the toy result carry over to trained neural embeddings?
Toy PPMI + rank-6 eigen-decomposition model (sandbox 2026-10-09__analogy-bias-readout-3cosadd-hides-what-parallel-offset-shows.py): the same biased vectors give a female-coded share of 0.22 under nearest-neighbour 3CosAdd (control 0.30; the answer is the input's own topic neighbour 199/200) but 0.989 under a topic-constrained parallel-offset readout (control 0.456), and 3CosAdd only turns on when the gender offset is amplified 8x (0.995 at 8 and 16, control flat at 0.31). So the geometry carries the bias; whether a demo "shows" it depends on the readout. The toy has explicit cue contexts and a fixed rank, which a trained neural embedding does not.
Poles: the bias is a geometric fact, readout-independent, and any pipeline that uses the vectors inherits it (holds when the downstream use is a topic-cancelling comparison such as the parallel-offset or a forced choice) **vs** the bias is mostly a readout artefact, and nearest-neighbour use of the same vectors is dominated by topic similarity (holds when the downstream use ranks by raw similarity to the query, as 3CosAdd does here).
Lean: 🔴 open
Updates:
- 2026-10-09 opened from brain train pass 5; sandbox 2026-10-09__analogy-bias-readout-3cosadd-hides-what-parallel-offset-shows.py, result 14/24 predictions held (biased vs control 0.22/0.30 under 3CosAdd, 0.99/0.46 under parallel offset).
Source: sandbox file above / brain train auto pass 5

### T? · open-question · Does a judgment list built on a well-tuned chunking config reveal a silent 4-char overstemming analyzer bug?
In a shared-vocabulary tf-idf model with 9 queries, truncating tokens to 4 chars (temper and tempest collide) changed MRR by 0.000 at chunk sizes 4, 6 and 12, so the list showed no regression even though the analyzer is wrong. Unclear whether the fixture is too forgiving (adjective and noun co-location dominates the score) or whether such a bug only shows when the colliding word is the sole discriminator.
Poles: the list catches it when the collided word is the only discriminating term in the query **vs** the list misses it when other query terms already disambiguate the answer.
Lean: 🟢 settled in sandbox (see Updates)
Updates:
- 2026-10-09 opened from brain train; sandbox 2026-10-09__chunk-size-sweep-judgment-list-metrics-and-silent-analyzer-bug.py, result MRR drop 0.000 at sizes 4/6/12 after 3 iterations.
- 2026-10-09 settled in loop 2 pass 5; sandbox 2026-10-09__overstemming-bug-visible-only-when-collided-word-is-sole-discriminator.py: the bug is invisible when ties break toward the relevant doc (MRR 1.000->1.000) and shows (1.000->0.500) when ties break against it; a shared context word does not disambiguate; a unique extra token in the relevant doc does. The first fixture hid it through a favorable tie-break.
Source: 2026-10-09__chunk-size-sweep-judgment-list-metrics-and-silent-analyzer-bug.py / scheduled brain train loop 1 pass 5
- Session: session_01QXDSckzV3bvegjZqBF6sPy

### T? · open-question · Does silhouette-first lose to luminance-separated colour below a size floor, or is that floor an artefact of the distance metric?
The sandbox 2026-10-10__silhouette-first-needs-a-size-floor-and-a-backdrop-outline.py ran the same 8-slot shape cast and a luminance-spread recolour cast at box factors 1, 2, 4, 8 of a 16 px canvas. An area-mean pixel distance is size-invariant (4 confusable pairs at every size, so no floor); a peak-pixel distance shows one (shape cast 0/28 at 16, 8, 4 px and 10/28 at 2 px, against 4/28 for luminance-spread recolour). The floor therefore depends on which distance models the viewer, and neither was calibrated against real viewers.
Poles: silhouette-first holds down to a few pixels when bodies differ by large area **vs** colour wins below roughly 4 px per entity because a coverage-limited shape cannot resolve and colour luminance still reads.
Lean: 🔴 open
Updates:
- 2026-10-10 opened from brain train kernel pass 2; sandbox 2026-10-10__silhouette-first-needs-a-size-floor-and-a-backdrop-outline.py, result FAIL on 3 of 5 pre-registered predictions; post-hoc peak metric shape 10/28 vs lum-spread 4/28 at 2 px.
Source: sandbox 2026-10-10__silhouette-first-needs-a-size-floor-and-a-backdrop-outline.py / brain train kernel pass 2
- Session: session_01YFLLRpDsfZpRstb2KT2MQy
- Updates: 2026-10-10 resolve pass 2: area-mean distance is indefensible (flat no-floor was an artefact); peak and viewer-model metrics show a floor at 2 px per entity. 4 px depends on threshold and blur; needs a human discrimination measurement.
- Evidence: B · projects/local__sandbox-silhouette-size-floor-metric-audit.md#E1 · 2026-10-10

### T? · open-question · should a refusal return the matched operands to the refused party when the guard also defends a hidden state?
Sandbox 2026-10-10__refusal-names-the-rule-not-the-bucket-but-never-the-secret-operand.py: rule + remedy cuts guard calls to 0.57x and gives named receipts, naming the rule costs no extra leakage over class-only, but matched values drop secret-threshold recovery from 8 probes to 1 and enumerating all matched rules reveals a hidden flag. Who is entitled to which field is not decided by the sandbox.
Poles: the refused actor needs the operand to repair or to recognise a false positive **vs** the same operand is the secret the guard exists to hide.
Lean: 🔴 open
Updates:
- 2026-10-10 opened from brain train; sandbox result PASS with the boundary above.
Source: sandbox 2026-10-10__refusal-names-the-rule-not-the-bucket-but-never-the-secret-operand.py / brain train kernel pass 4
- Session: session_01YFLLRpDsfZpRstb2KT2MQy
- Updates: 2026-10-10 resolve pass 4: disclosure is a curve priced in bits; exact operands give the secret in 1 probe; an 8-wide bucket keeps 0.86 of repair saving for 0.48 of leak; no design had half the benefit at zero leak.
- Evidence: B · projects/local__sandbox-refusal-operand-disclosure.md#E1 · 2026-10-10

### T? · open-question · Should a relevance gate over prose trade recall of common-word edits for precision on large diffs?
A same-domain idf-mass gate cut false fires on unrelated code from 0.93 (live-style) to 0.05 at 3200 words, but a planted genuine edit that hits only the common half of a tension's keywords was recalled at 0.32-0.38 (live gate 1.00), and on topical prose the size confound survived (idf mass 0.89 at 3200; windowed 0.46).
Poles: precision wins when diffs are large and the tension's distinguishing nouns are rare **vs** recall wins when a tension is worded only in common vocabulary and a missed fire is the costly error.
Lean: 🔴 open
Updates:
- 2026-10-10 opened from brain train pass 5; sandbox 2026-10-10__rarity-weighted-gate-vs-raw-overlap-size-sweep.py, planted edits synthetic so recall is optimistic.
Source: sandbox 2026-10-10__rarity-weighted-gate-vs-raw-overlap-size-sweep.py
- Session: session_01YFLLRpDsfZpRstb2KT2MQy
- Updates: 2026-10-10 resolve pass 3: hybrid gate (window + rarity + allowlist) does not avoid the tradeoff on topical prose; feasible configs 11 on code, 7 off-topic prose, 0 topical prose. Narrow windows lose spaced edits; allowlists add little recall.
- Evidence: A · projects/local__sandbox-hybrid-keyword-gate.md#E1 · 2026-10-10

### T? · tradeoff · construction by placement vs construction by typed record · 🟡 open
Poles: **placement** — wrap or encode the whole free-text payload (per-delivery nonce fence, JSON string) so its bytes never sit in an instruction role; leaked 0/108 at the parse level but delivers 0/20 legitimate rules and leaks 108/108 to a reader that obeys any delivered text **vs** **typed record** — behaviour changes arrive as closed-vocabulary records the owner renders itself; leaked 0 and delivered 10/20 to 14/20 of the authored legitimate rules, but cannot carry any free-text rule and turns into classification again as soon as a free-text slot is added (12/12 short attacks through a 40-character slot).
Lean: 🟡 typed record for the few behaviours that must be changeable, placement for everything else, and neither is treated as sufficient alone. Unsettled: whether a real model obeys text inside a data segment. The sandbox reader is a parser, so the 108/108 semantic-reader figure is an upper bound, not a measurement.
What would settle it: a fixed attack set run through a live model with the payload in a nonce-fenced data segment, counting how often the attacker's canary behaviour appears. Below roughly 5% placement may be enough for knowledge; above it, free text should not reach the model at all.
Updates:
- 2026-10-10 opened from brain train pass 1 on 'boundary by classification vs boundary by construction'; sandbox 2026-10-10__boundary-by-construction-vs-classification-evasion-and-capability-cost.py, RESULT FAIL on 2 of 16 prediction checks (strict-detector rule delivery 1/20, static-fence leak 2), the structural findings held.
Source: 2026-10-10__boundary-by-construction-vs-classification-evasion-and-capability-cost.py / brain train resolve-tension pass 1
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · does the key-to-fill ratio alone set perceived contrast, or must brightness, angle and ambient be fixed too?
Sandbox 2026-10-10__lighting-ratio-stops-vs-lux-and-bounce-floor.py (Lambert two-light face, ambient floor, exposure, tone curve, 8-bit L*): with exposure pinned to the lit side the ratio fully determines delta L* (0.000 spread over 6 stops of brightness, monotonic, same ordering under three curves), and K:F vs total readings of '8:1' agree within 1.8 L*. It breaks when exposure is frozen (+-3 stops moves delta L* by 23 at a constant 8:1), when the unit is misread (8 stops = 256:1 gives 68 L* with a crushed shadow, 23.5 L* from the lux reading), when key angle varies (nominal 8:1 gives cheek ratios 1.4 to 7.5), and when ambient is fixed rather than key-proportional (total ratio 1.89 to 8.11 over +-3 stops; bounce at K/8 turns 3.17 stops into 2.32). The two kernels also use incompatible bands (1.5:1 flat and 2:1 dramatic vs 8:1 noir) with no stated unit; 1.5:1 to 2:1 differ by only 6.6 L* while 2:1 to 8:1 differ by 25.4. Open: human perceptual thresholds for 'high-key' and 'low-key' were not tested, only the display-referred L* gap.
Poles: ratio-only holds when exposure is normalised to the lit side, the unit and sites are fixed, key angle is fixed and ambient scales with the key **vs** fails when exposure is frozen, the label is read in the wrong unit, the key moves, or ambient is fixed in lux
Lean: 🔴 open
Updates:
- 2026-10-10 opened from brain train (pass 2); sandbox 2026-10-10__lighting-ratio-stops-vs-lux-and-bounce-floor.py, result PASS 19/19 with 1 prediction miss.
Source: sandbox 2026-10-10__lighting-ratio-stops-vs-lux-and-bounce-floor.py / session_01YFLLRpDsfZpRstb2KT2MQy
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · does blur contrast in the frame actually direct a viewer's attention, once the optics say the second subject is blurred?
Sandbox 2026-10-10__shallow-focus-separates-only-past-the-depth-of-field-deep-focus-hits-a-diffraction-floor.py: the optical precondition holds only past the depth of field. A 35 mm f/2.8 two-shot with the partner 0.5 m behind leaves the partner at 0.78 circles of blur (sharp); 85 mm f/1.4 gives 1.70; a 3-circle blur needs a 0.93 m gap at 85 mm f/1.4 and 3.8 m at 35 mm f/2.8; deep focus 0.6 m to 12 m on full frame leaves 2.6 circles at the best f-number. The sandbox models blur, not viewers, so whether a 1-circle or 3-circle blur steers the eye is a human-perception question it cannot answer.
Poles: shallow focus directs attention when the partner is outside the depth of field and the blur exceeds what the audience reads as blurred **vs** it directs nothing when the gap is inside the depth of field, or when the audience watches the unfocused face anyway because of motion, light or story.
Lean: 🔴 open
Updates:
- 2026-10-10 opened from brain train pass 4; sandbox result FAIL 8/9 (the miss is a hand-arithmetic error in the two-shot prediction, the mechanism held); the viewer side is untested.
Source: sandbox 2026-10-10__shallow-focus-separates-only-past-the-depth-of-field-deep-focus-hits-a-diffraction-floor.py
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · Is the master shot a safety net for the existence of an edit, or for the freedom to restructure pacing? · 🟡 open
Poles: **existence** — a clean master is a complete version of the scene, so some valid edit always exists (100 percent feasible at every defect rate 0.1 to 0.4 in the sandbox, even when the master is drifted or on the wrong side, because the all-master edit is zero cuts) **vs** **pacing** — the cuts the editor can actually restructure shrink to 1 zero-cut edit when the master is on the wrong side of the line with no neutral shot, to a frozen tail when its prop state drifts, and to 36 of 1728 edits when its performance sits outside tolerance; here the master's value is only as large as its cut-compatibility with the singles.
Lean: 🟡 Both kernels are right about different things: the coverage kernel holds for existence, the pacing half of its claim holds only under right side plus matching continuity or enough neutral cutaways. Unsettled: whether editors count a master-only fallback as a usable "net", and the real tolerance for performance and continuity mismatch, which the model sets by hand.
What would settle it: a count of real scenes (shot logs plus final cuts) of how often the master is the only shot on a beat and how often a cut into or out of it crosses the line or breaks continuity.
Updates:
- 2026-10-10 opened from brain train pass 5 on the master-shot and 180-degree kernels; sandbox 2026-10-10__master-shot-safety-net-vs-line-of-action-cut-counting.py, RESULT PASS on 14/14 kernel-claim checks but 2 of 2 later mechanism guesses missed and the first sweep prediction (drift or wrong side breaks feasibility) refuted.
Source: 2026-10-10__master-shot-safety-net-vs-line-of-action-cut-counting.py / brain train pass 5
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · Should a four-subscale humor frame be reported as classes, dimensions, or general score plus contrasts?
A synthetic-respondent sandbox (3000 respondents, 32 original stand-in items, fixed seed) held in the clean case (retest class agreement 0.694, every item highest on its own scale) and in the built-to-break case (axes correlated 0.8, strong axis determination 0.9) hard classes dropped to 0.525 with 68% of respondents under a 0.5 SD top-two margin. But the standard screen for distinct scales (disattenuated r under 0.85) still passed at 0.75, and the dimensional alternative is only partly better: the sum score retested at 0.96 while the two axis contrasts retested at 0.68 and 0.70, so a pure two-axis reading is also weak when the axes correlate.
Poles: classes are acceptable when axes are near-independent and item noise is low (agreement about 0.8 at half noise) **vs** classes mislead when axes correlate and the label is printed without a margin, while the contrasts are too noisy to replace them.
Lean: 🔴 open
Updates:
- 2026-10-10 opened from brain train newdomain pass 1 (humor-styles); sandbox 2026-10-10__humor-four-style-classes-break-when-latent-axes-correlate-dimensions-survive.py, RESULT FAIL 1 of 7 (P3). Simulated structure only; the real inter-scale correlations were not checked against the source paper.
Source: sandbox 2026-10-10__humor-four-style-classes-break-when-latent-axes-correlate-dimensions-survive.py
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · how much is being believed worth, in warmth, and what rate of joking does this listener expect here?
The humor dose-response sandbox gives a clean inverted U and a break-even rate, but where that break-even sits is set by two inputs it assumes: the exchange rate between credibility and warmth, and the listener's expected base rate of joking in the setting. In the 2x2 run neither alone created a flip for a new relationship with a high prior (casual expectation with high-stakes payoff: p* 0.75, no flip; high-stakes expectation with casual payoff: p* 0.35, no flip; both: p_flip 0.350). Pre-registered threshold values were wrong on 4 of 5 magnitude checks.
Poles: advise a numeric joke-rate ceiling for pitches and negotiations **vs** advise measuring the listener's expectation and the outcome's dependence on credibility first, because the number is an artefact of the assumed constants.
Lean: 🔴 open
Updates:
- 2026-10-10 opened from brain train pass 3; sandbox 2026-10-10__self-directed-humor-dose-response-flips-at-low-rate-in-high-stakes-settings.py, RESULT FAIL 2/7 predictions held. Structure (inverted U, severity and expectation dominate) held; constants are assumed and nothing here measures people.
Source: sandbox 2026-10-10__self-directed-humor-dose-response-flips-at-low-rate-in-high-stakes-settings.py / brain train pass 3
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · tradeoff · forced-choice ipsative scoring vs other-report blending for shaded humor-style self-report · 🟡 open
Sandbox 2026-10-10__humor-self-report-bias-ipsative-and-other-report-corrections-break-points.py (toy model, assumed parameters, structure only): shading at intensity 1 raised primary-style misclassification 0.257 to 0.373 and cut mean rank correlation 0.897 to 0.727. Forced choice with matched desirability cut misclassification to 0.168 but its rank order was no better than shaded self (0.718 vs 0.727; 0.525 vs 0.728 under a strong general factor) and every pair of scale correlations was forced to about -0.33. A 3-rater blend cut misclassification to 0.308 and lifted rank order to 0.845 but broke when raters share the bias at self-level susceptibility (0.368 vs 0.373 at rho=1, kappa=1) and for the self-enhancing scale at observability near 0.3.
Poles: **forced choice** — removes shading from the choice itself, best at who-is-top-style, costs between-person level and induces negative scale correlations the construct may not have **vs** **other-report blend** — keeps normative scores and lifts rank order, needs independent, observant raters and fails exactly where the bias is a shared social norm or the style is private.
Lean: 🟡 use the blend for rank-order questions and forced choice only for top-style classification, never report scale correlations from the ipsative scores; unsettled: the shading directions, rater model and instrument noise are all assumed, and forced choice could not be length-matched to self-report reliability in this model.
What would settle it: a real sample with a criterion measured outside self-report (behavioural or multi-informant), run through both corrections with the same metrics.
Updates:
- 2026-10-10 opened from brain train pass 4; sandbox RESULT FAIL 8/13 predictions held (refuted: forced choice beat self even unmatched on classification; blend did not break on shared bias alone; self-enhancing break at observability 0.3 not 0.4; length-matching impossible).
Source: sandbox 2026-10-10__humor-self-report-bias-ipsative-and-other-report-corrections-break-points.py / brain train pass 4
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · Is the tu vs usted fork decided by the humor in the script, or by an unmeasured norm shift?
Sandbox 2026-10-10__humor-travel-tracks-items-needed-and-norm-mismatch-injures-only-parsed-jokes.py (11 of 12 predictions held) modeled register as a shift on felt intensity: for observation, wordplay and reference jokes register choice changed harm by 0.000; for teasing it dominates, and tu has less harm than usted only when more than 0.714 of the audience expects tu. That crossover is m_tu/(m_tu+m_us) from two assumed shifts (0.25 and 0.10), so it restates the assumption, and capping teasing intensity at 0.25 made harm 0 for every register and split. The sandbox cannot say whether the real shifts are those sizes, or whether harm is the right currency instead of completion and conversion.
Poles: pick the register on completion and conversion alone because register-independent or intensity-capped humor removes the harm term (holds if real shifts are smaller than the benign margin) **vs** choose the register per segment first because teasing in the wrong register is injurious for a large minority (holds if a usted-expecting segment is large and the shift is near 0.25).
Lean: 🔴 open
Updates:
- 2026-10-10 opened from brain train kernel pass 5; the register half of the existing Spanish register tension gains a conditional (humor payload decides how much the fork matters), no first-hand evidence on real viewers.
Source: sandbox 2026-10-10__humor-travel-tracks-items-needed-and-norm-mismatch-injures-only-parsed-jokes.py / brain train kernel pass 5
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · should a refutation count as connectivity (tested-ness) or only as a block on re-testing?
Surfaced by the T21 audit. Negative edges are modeled, but they share one edge set with positive ones, so
clusters, degree and the weakest-link seam ranking all treat a fight as proof of co-verification.
Poles: refutations count toward degree -- a fought pair really was tested, so the weakest-link order should
sink it **vs** refutations only block re-testing -- keeps clusters and "proven ground" confirmed-only, avoids
45 of 97 refuted nodes owing all their degree to refutations.
Lean: 🔴 open -- the data cannot decide it (the top-20 ranking changes by all 20 depending on the choice); needs the owner's call on what "weakest link" should mean.
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · is a withheld laugh a reveal about the joke, or a reveal about the relationship, and can a listener tell which from one silence?
Sandbox 2026-10-10__sandbox-missing-laughter-needs-the-response-window.py (5 of 8 pre-registered predictions held; post-hoc 4 of 4) modeled silence as evidence that a joke failed. A silence from a reliable single partner at a low prior of failure gave a posterior of only 0.351, while the same silence after a decayed repeat sequence carried a likelihood ratio of 9.8. The model cannot separate "the joke failed" from "something changed between the people", because both only lower the response probability; the song kernel wants the second reading and the sandbox can only score the first.
Poles: treat the silence as a verdict on the joke, scored by window coverage and room size (holds when the response model is shared and the prior of failure is moderate) **vs** treat it as a change in the pair's response pattern, scored against the established baseline (holds when the same joke landed before and the repeats carry the history).
Lean: 🔴 open
Updates:
- 2026-10-10 opened from brain train kernel pass 1; no first-hand evidence on real audiences, structure only.
Source: sandbox 2026-10-10__sandbox-missing-laughter-needs-the-response-window.py / brain train kernel pass 1
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · Is progressive comedy escalation justified by audience adaptation, or only by a coherence limit on step size?
Sandbox 2026-10-10__sandbox-comedy-escalation-needs-a-step-coherence-term-and-reversal-slot-varies.py (toy model, assumed constants, structure only, 8 of 18 predictions held): with habituation and an adapting expectation level alone, a single jump to the ceiling beat linear and geometric ramps in all four audience models (contrast-driven totals 1.410 flat vs 1.264 linear vs 1.183 geometric). Adding an assumed coherence gate on the log step flipped contrast-driven audiences to geometric (0.662 vs linear 0.624 vs flat 0.296) but level-driven and mixed audiences still preferred flat, a picky gate (width 0.3) cut the geometric arc 96.6%, and a tolerant gate (3.0) still did not let flat win. Doubling the ceiling at six beats lowered the total, and the reversal was last in only 5 of 12 cells. The gate shape, the reversal term and the expectation rate are my assumptions, so the sandbox cannot say whether real audiences have a resolvability limit of that form, or whether beats carry a cost that would bound the optimum beat count (here it ran to the search cap).
Poles: **adaptation justifies escalation** (the habituation kernel's framing: stay ahead of the decay curve, so ramp up) **vs** **a coherence limit justifies it** (habituation alone says go straight to the ceiling; ramping only pays when each step must stay resolvable, which makes the step size and the beat count the real design variables).
Lean: 🟡 name the step-coherence limit before choosing a schedule and place the reversal by the audience's expectation rate, not by position; unsettled: the form of the limit, the per-beat patience cost, and whether level-driven or contrast-driven response better describes the audience are all assumed.
What would settle it: ratings from a real audience of sequences with controlled step sizes and a known pre-exposure to the catch, scored for per-beat response, so the step-size optimum and the habituation rate can be fitted instead of assumed.
Updates:
- 2026-10-10 opened from brain train kernel pass 2; sandbox RESULT FAIL 8/18 predictions held (refuted: geometric beating linear ungated, a mu crossover, a 3-beat optimum, ceiling gains at fixed beats, reversal-last as the usual optimum).
Source: sandbox 2026-10-10__sandbox-comedy-escalation-needs-a-step-coherence-term-and-reversal-slot-varies.py / brain train kernel pass 2
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · does "open with the change" hold once a joke may open the pitch, and in which currency is it judged?
Sandbox 2026-10-10__pitch-opening-joke-leaves-change-first-order-intact-only-in-uptake.py (toy model, assumed constants, structure only; RESULT FAIL 6/8 predictions held). Change-first beat product-first in uptake under all 24 cell-by-joke conditions, but an opening joke cut the stakes/low-prior uptake margin by 75.6 percent (5.2 percent at high prior), 226 of 1536 grid cases flipped it (all in cold-audience or strong-refill cells), and in a warmth-plus-uptake sum a joke on the wrong order beat the right order in both casual cells (payoff weight 2 against thresholds of 3.5 to 4.5). The thresholds are the earlier unmeasured warmth-to-belief exchange rate in another form.
Poles: keep change-first as the default and treat any joke as a mid-pitch or carried element, judged on uptake (holds if the room is attentive and warmth is a means, not a goal) **vs** let the room's attention and the speaker's goal choose the opening, because with a cold room or warmth priced above about a third of being believed, a joke-first opening on any order can win.
Lean: 🟡 default to change-first and a mid-pitch joke; unsettled: the attention decay, refill and frame constants are assumed, and nothing in the model measures real listeners or an exchange rate.
What would settle it: a real sample of short pitches with logged initial attention, a joke placement manipulation and a behavioural uptake measure, plus an elicited price for warmth against being believed.
Updates:
- 2026-10-10 opened from brain train pass 3 (edge: HUMOR-STYLES dose kernel joined with PITCH narrative-structure and talk-structure kernels).
Source: sandbox 2026-10-10__pitch-opening-joke-leaves-change-first-order-intact-only-in-uptake.py / brain train pass 3
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · Is the 11-syllable English hook cap a safe guarantee or a conservative number that delivery can still break?

Sandbox 2026-10-10__published-timing-figures-vs-stand-in-ratio-law-in-the-punchline-syllable-cap.py (5 of 7 predictions held) checked the stand-in punchline-timing figures behind the 11-syllable cap against published ones. On the syllable-ratio law the stand-in is the conservative side (published bounds allow a cap of 12 to 13 at a 2.8 s window). On delivery it is optimistic: a pause of 0.6 s inside the window or a fixed 6.63 syll/s voice drops the guaranteed cap to 9, and a human speaker rate spread (SD 1.15) drops fit(11) to 0.87. The published figures that matter most are not about Spanish or scripted video: the pause evidence read (twenty joke performances, abstract only) found no systematic pre-punchline pause and gave no length, and the laughter gaps come from dyadic conversation, not audience laughter at a short video. So the data cannot say whether the real pause and voice rate are the ones that break the cap.
Poles: keep 11 as the rule because the ratio law is conservative and a TTS rate can be set to 7.7 or faster **vs** lower the rule to about 9 until the actual TTS pace and pre-punchline pause are measured, because the guarantee is only as good as those two unmeasured inputs.
Lean: 🟡 leaning -- keep 11 for the ratio law but state it as conditional on a voice at or above 7.7 syll/s and a pause under about 0.2 s inside the window; unsettled: the real TTS pace, the pause a joke needs, and the audience laughter latency for scripted video.
What would settle it: measure the actual TTS voice rate on Spanish hooks and the pause placement used in finished clips, then re-run the cap with those values.
Updates:
- 2026-10-10 opened from brain train gap pass 4; sandbox RESULT FAIL 5/7 predictions held (missed: triangular published-bound law gave a cap of 13 not 12; ratio-law shift was 2 at 2.8 s not at most 1).
Source: sandbox 2026-10-10__published-timing-figures-vs-stand-in-ratio-law-in-the-punchline-syllable-cap.py / brain train gap pass 4
- Session: session_01YFLLRpDsfZpRstb2KT2MQy

### T? · open-question · Must a doppelganger be exposed before the missing member can be rescued, or does the rescue itself expose it?
SEVEN's disappearance mechanic: a member wanders off at night and a same-name, same-skill replacement takes the slot. A toy sandbox (memory proposal 2026-10-11 rescue-exposes-the-fake-two-at-the-fire, assumed constants) gave expose-first 0.274 real back for 1.546 pylons, free exposure on rescue 0.841 with the investigation bypassed, and a duplicate at the fire (pay a pylon for a 1-of-2 choice) 0.844 with every case still a player deduction.
Poles: rescue is gated on exposing the fake first (deduction stays primary; rescue is the reward) **vs** rescue brings the real one home and resolves or narrows the question (rescue is evidence; the duplicate at the fire forces a 1-of-2 choice).
Lean: 🟡 leaning the duplicate-at-the-fire rule; unsettled: whether a wrong 1-of-2 pick should cost the real person or only the pylon, and whether two of the same name breaks the check-in log.
What would settle it: a playtest of the duplicate scene measuring whether players use memory (check-in) or a coin-flip to choose.
- Evidence: B · projects/pappydapimp69__seven.md#E24 · 2026-10-11
- Evidence: B · projects/pappydapimp69__seven.md#E29 · 2026-10-11
- Session: session_01NHKVhTvCnvtvZ2NGLSPYj6

### T? · open-question · How can a night call guide a rescue search without naming or announcing who is missing?
A toy sandbox (memory proposal 2026-10-11 night-call-is-an-announcement-unless-false-calls-exist) found that if only the missing ever call, a call is certain proof of a disappearance (posterior 1.0); holding it near 0.6 needs false calls at about 0.106 per night, costing about 0.63 wasted search nights per real rescue, and cross-night bearing consistency only lifts a call to 0.741.
Poles: calls are always real and carry a bearing (efficient search, but the disappearance is announced and the call count reveals how many fakes) **vs** the woods also call (unannounced disappearance kept, at the price of wasted night hours and a weaker cue).
Lean: 🟡 leaning false calls scaled by depth plus bearing consistency as the tell; unsettled: the false-call rate players tolerate before they stop answering calls at all.
What would settle it: a playtest logging how often players go out for a call and how that changes after their first wasted night.
- Evidence: B · projects/pappydapimp69__seven.md#E23 · 2026-10-11
- Evidence: B · projects/pappydapimp69__seven.md#E28 · 2026-10-11
- Evidence: B · projects/pappydapimp69__seven.md#E35 · 2026-10-11
- Session: session_01NHKVhTvCnvtvZ2NGLSPYj6

### T? · open-question · How should rescue find-chance be weighted (nights out, depth, same night) so it reads as skill, not dice?
A toy sandbox (memory proposal 2026-10-11 disappearance-search-chance-from-hidden-position-not-dice) showed a dice roll on those factors has a skill gap of exactly 0, while a hidden position plus a call bearing has 0.767 same-night shallow; but a fresh nightly call erased the nights-out penalty (0.94 to 0.93 over 3 nights) and depth noise collapsed skill to 0.015 at depth 3.
Poles: weight a roll with visible factors and explain it in the world (simple, tunable, reads as dice) **vs** derive chance from a hidden position and a degrading call (reads as skill, harder to tune, can silently become a coin-flip when the cue is too noisy).
Lean: 🟡 leaning the spatial model with the call fading per night missing and noise capped; unsettled: whether depth should cost search hours or noise, and the seed-purity cost of a per-night drift draw.
What would settle it: a seeded prototype with a fixed draw count per night and a bot that searches by bearing vs at random, checked for a gap above 0.2 at every depth.
- Evidence: B · projects/pappydapimp69__seven.md#E22 · 2026-10-11
- Evidence: B · projects/pappydapimp69__seven.md#E31 · 2026-10-11
- Evidence: A · projects/pappydapimp69__seven.md#E32 · 2026-10-11
- Session: session_01NHKVhTvCnvtvZ2NGLSPYj6

### T? · open-question · Spatial rescue window (this area or next): how is abandonment made a felt choice with no prompt?
SEVEN abandons a missing member when the party walks forward past the window; there is no confirmation. Risks: a scouting trip ahead could abandon by accident if the window follows the player, and silence (no more calls) is also what a night with nobody missing sounds like.
Poles: the window follows the camp, so only a deliberate dawn or dusk camp move abandons (fair, but abandonment can feel like admin) **vs** the window follows the player's feet (abandonment is visceral and immediate, but can happen by accident on a scouting trip).
Lean: 🔴 open; partial direction: calls fade as the camp moves away and stop when the window closes, but no evidence yet on whether players read silence as abandonment or as safety.
What would settle it: a playtest asking players after a camp move whether they knew someone could still be found behind them.
- Evidence: A · projects/pappydapimp69__seven.md#E30 · 2026-10-11
- Evidence: A · projects/pappydapimp69__seven.md#E34 · 2026-10-11
- Session: session_01NHKVhTvCnvtvZ2NGLSPYj6

### T? · decision · Should a missing member's fading rescue call be floored, or may it fade to silence (a time window on top of the spatial one)?
seven E27 (sandbox, assumed constants) showed an unfloored fading call (0.9 x 0.6 per night missing) drops below 0.05 by night 6, which adds a hidden TIME rescue window on top of the spatial one (this area or next); a floor of 0.25 keeps a 0.438 two-night hear chance forever. The constant draw count per night is required either way.
Poles: floor the call so only walking forward abandons (one abandonment rule) **vs** let the call fade to silence so waiting too long also abandons (two abandonment routes, both without a prompt).
Lean: 🟢 owner decided B -- the time limit is fine. Consequence to watch: late nights are quiet anyway as the call fades, so silence only means lost for good once the call has fully died (seven E25).
- Evidence: A · projects/pappydapimp69__seven.md#E27 · 2026-10-11
- Decision: B · owner · 2026-10-11
- Evidence: B · projects/pappydapimp69__seven.md#E28 · 2026-10-11
- Evidence: B · projects/pappydapimp69__seven.md#E77 · 2026-10-12
- 2026-10-12 update: E77 measures what the owner's fade buys: late search nights in a hopeless case fall 90 percent (1.647 to 0.163), at a cost of about 0.13 of rescues even in easy cases for call-following players; pairing the fade with a lasting non-call cue is the suggested reconciliation. E28 (B) failed review; E27 (A) is confirmed.
- Evidence: B · projects/pappydapimp69__seven.md#E95 · 2026-10-12
- 2026-10-12 correction: a blind rebuild of E77 (now disputed) reproduced the hopeless-case cut and the ~0.13 cost on hard finds, but NOT the cost "even in easy cases": easy finds lost 0.03. E95 adds that a lasting non-call cue wins back 59 percent of the hard-case loss while hopeless late searching stays 40 percent below a floor. Both favour B as decided, paired with a lasting cue. session_01P1LRA5HjMLEFnWXayE2EHx
- Session: session_01NHKVhTvCnvtvZ2NGLSPYj6

### T? · open-question · Is gating adaptive copy on the cause ("is the bed failing") enough, or must it gate on the exact predicate the sentence asserts?
Sandbox 2026-10-11__narration-gate-must-test-the-asserted-predicate-not-its-correlate-or-its-cause.py modelled a "gone quiet" line (asserts fish activity is low). The surface-mat proxy lied on 55% of emitted lines in a common-mat population and 100% on thriving ponds with cover, reproducing the kernel. The kernel's repair (gate on "bed failing": plants under 0.3 or oxygen under 40) was NOT clean: it still lied on 44% of emitted lines in a static grid (failing plants, healthy oxygen, active fish) and on 25% of a lagged oxygen collapse (fish still active for 3 ticks). Only a gate on the asserted predicate (activity under 0.3) lied 0%, though that gate is close to tautological in this model. Poles: gate on the cause holds when the asserted word is literally the cause ("the bed is failing") **vs** fails when the sentence asserts an effect (quiet) that lags or only partly follows from the cause.
Lean: 🔴 open
Updates:
- 2026-10-11 opened from brain train; sandbox 2026-10-11__narration-gate-must-test-the-asserted-predicate-not-its-correlate-or-its-cause.py, RESULT: FAIL (prediction cause-gate 0% static missed: observed 44%).
Source: ideas:NARRATION/adaptive-copy/branch-on-the-claim-not-on-a-correlate; sibling ideas:NARRATION/instrument-as-argument/a-second-number-that-never-moves-beside-one-that-does (a shown activity readout caught 71/71 of the lies)
- Session: session_012QzNKQEGhirAziWZ2Cg9Tj

## Project: Pappydapimp69/Seven

### T? · open-question · When TTS should sound like a real person's accent, does the accent belong in respelled text or in the voice and phoneme layer?
A user asked for an apology in their father's native accent for TTS. Respelling
(eye dialect) encodes speech in spelling, which suno-builder/E4 shows misjudges
speech (62.9% recall when spelling and sound disagree), and to a reader it parses
as caricature rather than pronunciation. A locale voice, or SSML phoneme/IPA tags,
carries pronunciation without touching the words. Not yet tested: no phonemizer
was available to measure what a TTS engine actually says for respelled vs plain
text with an accented voice.
Poles: respelling carries the accent when the engine reads letters literally and no matching voice exists **vs** the voice/phoneme layer carries it better whenever an engine has a voice for that language.
Lean: 🔴 open
Updates:
- 2026-10-11 opened from a session request; no sandbox run (no espeak-ng / CMUdict in the container).
Source: Seven session 2026-10-11; brain query pronunciation/speech (suno-builder/E4, brainwork/E82).
- Session: session_01XbmpbLd4QyYTiQBBzo2Hdw

### T? · open-question · Is "reach for acid when a rich dish tastes flat" conditional on how rich the dish is?
A toy palate model (salt scales intensity, acid relieves fatigue from richness and has its own sourness cost) reproduced the kernel's core: for a rich dish at correct salt, adding acid (quality 0.588) beat adding salt (-0.056), over-salting hurt (-1.100), and acid had an interior optimum (3 units scored -0.643, worse than 1 unit). But two further predictions were refuted: a lean dish gained as much from acid (+0.296) as a rich one (+0.303), and the best acid level barely moved with richness (1.2 to 1.3), while the best salt level also barely moved. The conditional-on-richness part is a property of how I wrote the fatigue term, so the model cannot say whether real dishes behave the same way.
Poles: acid helps mostly when the dish is rich or heavy, as the source's contrast explanation suggests **vs** acid helps about equally across dishes and the best amount is similar, as this model gave.
Lean: 🔴 open
Updates:
- 2026-10-11 opened from brain train; sandbox 2026-10-11__acid-vs-salt-flat-dish-contrast-model.py, result RESULT: FAIL acid_vs_salt=0.644 lean_gain=0.296 rich_gain=0.303.
Source: 2026-10-11__acid-vs-salt-flat-dish-contrast-model.py, scheduled brain train session
- Session: session_019JKZ53wDZk2PJ4F5v2qxmH

### T? · open-question · Can a game use psychosis and hallucination as a horror art style without reproducing the stigma that people in psychosis are dangerous or broken?
Research for SEVEN (2026-10-11): Hellblade was built with psychiatrist Paul Fletcher, the Wellcome-funded Hearing the Voice project and voice-hearers who helped place its binaural voices, and was praised as a force against stigma (BPS article). Take This notes media has shown mentally ill people as violent and dangerous although they are more often victims; Time to Change's 2009 survey found the public's top associations were violent, weird and likely to kill (search summaries); critics name asylum settings and violent 'insane' villains as stock game tropes. A toy sandbox (memory 2026-10-11 punishing-sanity-meter-makes-a-death-spiral) showed sanity-as-competence penalties create a collapse spiral, the mechanical form of 'a distressed mind is a worse player'.
Poles: hallucination as the world's threat (horror stakes, sanity meters, the asylum frame; strong genre fit, high stigma risk) **vs** hallucination as the character's experience (Hellblade's framing: consulted, perception-only, the person is not the monster; lower stigma risk, harder to make frightening).
Lean: 🔴 open
Updates:
- 2026-10-11 opened from brain train (hallucination as an art style, loop 4); evidence is published secondary sources and one toy sandbox, nothing measured on players.
Source: research digest this session; sandbox 2026-10-11__punishing-sanity-meter-makes-a-death-spiral.py
- Evidence: B · projects/pappydapimp69__seven.md#E101 · 2026-10-15
- Evidence: B · projects/pappydapimp69__seven.md#E102 · 2026-10-15
- 2026-10-15 update: first evidence. E101: playing Hellblade (experience framing) lowered social distance through identification (Ferchaud et al. 2020, N 198) but did not move the dangerousness stereotype; both studies only detect d >= 0.4, and no study tested a horror framing (pole A is untested, not refuted). E102: voice hearers mostly report resistible commands and mixed hostile and helpful voices, so a voice layer that seizes control inverts real proportions. session_01P1LRA5HjMLEFnWXayE2EHx
- Session: session_01NHKVhTvCnvtvZ2NGLSPYj6

### T? · open-question · Does "resting is temperature control, not juice retention" hold when the controlled temperature is the core peak rather than the whole-slab temperature at the cut?
In a 1-D slab conduction toy (2 cm half-thickness, surface 110 C, juice proxy depending only on local temperature, assumed), holding the core peak at 55 C gave a rested piece whose mean temperature at the cut was 21 C lower than an unrested piece pulled at core 55, and a proxy loss 60% lower. Matching the mean temperature at the cut instead gave a rested/unrested proxy difference of 0.119 on a 0.35 scale (not zero, because the profiles differ in shape and the proxy is nonlinear) and needed pulling the unrested piece at core 23 C. Carryover was 15.6 C at 2 cm and 43 C at surface 200 C, much larger than my 2-6 C prediction, and fell with thickness (18.1 to 14.6 C from 0.5 to 3 cm) at fixed surface temperature, the opposite of my prediction. Sous vide (surface held at target) gave 0.01 C carryover.
Poles: the claim holds when the variable held constant is the whole temperature profile at the cut (juice then depends only on temperature) **vs** it fails when only the core peak is matched, because resting also cools the outer layers, which carry most of the temperature-dependent loss in this model; whether real juice loss depends on mean or core temperature was not tested, since the proxy is an assumption.
Lean: 🔴 open
Updates:
- 2026-10-11 opened from brain train; sandbox 2026-10-11__resting-carryover-matched-core-peak-vs-matched-mean-temperature.py, result core-peak matched mean -21.0 C and proxy -59.7%, mean matched proxy diff 0.119, carryover 15.6 C (surface 110 C) and 43.1 C (surface 200 C), sous vide 0.01 C. Kernels exercised: ideas:COOKING/resting, ideas:COOKING/sous-vide (temperature cap), memory brainwork/E106 (carryover sizing).
Source: 2026-10-11__resting-carryover-matched-core-peak-vs-matched-mean-temperature.py / scheduled brain train run loop 1 pass 5
- Session: session_01QZ7D84k4ubQDti8yxsPp3D

### T? · open-question · Should a held selector release on the first veto refusal, or only when refusals outvote a recent-window margin?
Composing neekolaus-film/E1 (hold a contradiction, flip on a recent margin) with the hold-selector livelock (sandbox-combined-mirage-waiting-city-hold-selector-turns-veto-into-livelock/E1): in a 40-tick toy with a 3-tick switch cost, never releasing did 0 work under a permanent block (the livelock reproduced), and releasing on the first refusal did 36 against 34 for a margin of 3 refusals in 6 ticks. For a 2-tick transient block the margin rule and holding did 38 against 36 for first-refusal release, but from a 3-tick block onward first-refusal release won (36 against 34 and falling for hold: 28 at 12 ticks). I predicted first-refusal release would bounce when refusals were periodic; it did not (1 switch) because the alternative was always free. It did bounce (10 switches, 0 work) when both targets were refused 1 tick in 4, where the margin rule and holding both did 30. When the alternative was busy until tick 20, first-refusal release switched 5 times against 3 for the margin rule, both reaching 20 work.
Poles: the margin rule wins when blocks are shorter than the switch cost or when every target gets noisy refusals **vs** first-refusal release wins when blocks outlast the switch cost and the alternative is reliably free; holding forever never wins a long block.
Lean: 🔴 open
Updates:
- 2026-10-11 opened from brain train; sandbox 2026-10-11__veto-hold-release-margin-vs-first-refusal.py, result permanent HOLD 0 / FIRST 36 / MARGIN 34; transient-2 HOLD 38 / FIRST 36 / MARGIN 38; crossover at block length 3; both-targets-noisy FIRST 0 work, 10 switches vs MARGIN 30, 0. Cites neekolaus-film/E1 and sandbox-combined-mirage-waiting-city-hold-selector-turns-veto-into-livelock/E1. Toy constants (switch cost 3, window 6, margin 3) are assumed.
Source: 2026-10-11__veto-hold-release-margin-vs-first-refusal.py / scheduled brain train run loop 2 pass 2
- Session: session_01QZ7D84k4ubQDti8yxsPp3D

### T? · open-question · Do the rain-garden divisor (roof area / 6 to / 8) and the swale 8-12x infiltration figure hold across soils and storm intensities?
The sandbox (assumed Ksat clay 0.06, loam 0.5, sand 2.0 in/h; 6 in ponding) reproduced the divisor only for clay: roof/6 holds 623 gal, exactly one 1 in storm on a 1000 sq ft roof, but roof/8 for sand holds 467 gal and overflowed 779 gal over five 1 in storms two days apart, although sand drains 6 in in 3 h. Drain time at 6 in ponding is 100 h in clay (292 ponded hours across the storm train) against 12 h in loam and 3 h in sand, so the divisor sets volume, not drying time. The swale ratio is a threshold, not a number: 1x wherever rain intensity is below soil Ksat (nothing runs off to catch; 6 of 15 cells), 8-12x in only 3 cells (clay 0.25 in/h, loam 1 in/h, sand 4 in/h), and 14x to 98x in 6 others, since the model has flat ground infiltrating only its own rain. Model is idealized: no media storage, no slope, no clogging, level swale, and the Ksat values are assumed.
Poles: the kernel's sizing and 8-12x figures hold when the soil is clay-like or the storm intensity is a modest multiple of Ksat and the garden is sized for ponding volume **vs** they fail when soil is sandy (roof/8 undersizes ponding volume), when intensity is below Ksat (swale adds nothing) or far above it (ratio is unbounded), and when storms recur faster than clay drains (permanently ponded)
Lean: 🔴 open
Updates:
- 2026-10-12 opened from brain train gap; sandbox 2026-10-12__rain-garden-area-divisor-drain-time-and-swale-infiltration-ratio-by-soil.py, RESULT: PASS (5 own-check flags) with mixed reading: divisor volume check true, sand divisor overflow 779 gal, swale ratio 8-12x in 3 of 15 cells.
Source: 2026-10-12__rain-garden-area-divisor-drain-time-and-swale-infiltration-ratio-by-soil.py / scheduled brain train session; session_01LXSoWQcf1yhu8amwuXwSK3

### T? · open-question · Does the 2-4in mulch depth rule (ideas:GARDEN/mulch-benefits-and-stem-clearance-rule) hold across rain regimes once light-rain interception is modelled?
Prediction (before run): 2in beats bare soil in every regime and 8in is no better than 4in. Sandbox (120-day deterministic bucket model; mulch holds 0.12in water per inch of depth; soil evaporation damped by 1/(1+0.5*depth)) showed it MIXED. Few large storms: stress days 61 bare, 45 at 2in (best), 83 at 8in, so a shallow optimum exists and deep mulch is worse than none. Mixed storms: stress days rise with depth (64 bare, 79 at 2in, 102 at 4in) because the mulch intercepts light rain. Many small storms: no depth helps (113 vs 108). The stem rule held in the model: contact wetness fell from 32 wet days at 0in clearance to 6 at 3in and 0 at 4in, consistent with the 3-5in clearance. Caveat: the interception capacity and ET split are assumed parameters, not measurements, so only the direction of the regime dependence is supported.
Poles: mulch pays at 2-4in when rain comes as few large storms that exceed mulch hold **vs** mulch costs water when rain is frequent and light, so the mulch layer takes it all and evaporates it.
Lean: 🔴 open
Updates:
- 2026-10-12 opened from brain train; sandbox 2026-10-12__mulch-depth-interception-vs-evaporation-sandbox.py (not shipped: tensions do not carry scripts), result: few_large stress [61,53,45,47,46,61,83] for depth 0,1,2,3,4,6,8; mixed [64,72,79,88,102,108,108].
Source: brainwork train auto loop 1 pass 1; related ideas:GARDEN/passive-landscape-water-harvesting, brainwork/E132, brainwork/E105
- Session: session_01AmRWsr5yjKRMmEK2r9Dtgx

### T? · open-question · Should a hallucination art style follow real proportions (voice-led, overlaying reality) or what reads as frightening on screen (visual, replacing reality)?
Research for SEVEN (2026-10-12): in psychosis voices dominate (59 percent auditory vs 27 percent visual, Waters 2014), visions rarely come alone and overlay the real scene, and early hallucinations are minor phenomena (presence, passage, misperceived objects). SEVEN's own mix gives the player voices 0.20 of the time (sandbox 2026-10-12 seven-hallucination-mix-is-vision-led-unlike-psychosis). Screen media favour the visual: visuals are easier to read, screenshot and test, and sound is often played muted or on phone speakers, where binaural voices collapse (seven E55).
Poles: follow the real proportions (voice-led, minor phenomena first, overlay: respectful and fresher, but quieter, harder to show, and lost on muted or speaker play) **vs** follow the screen (visual-led, inserted phantoms: legible and marketable, but repeats the movie image and the stigma tension's 'dangerous visions' frame).
Lean: 🔴 open
Updates:
- 2026-10-12 opened from brain train (hallucination phenomenology, loop 4); evidence is published research plus toy sandboxes, nothing measured on players.
Source: research digest this session; sandboxes 2026-10-12 loop 2, 3 and 5
- Session: session_01NHKVhTvCnvtvZ2NGLSPYj6
- 2026-10-12 owner decision: lead with the real proportions and let the screen take over as sanity falls. High sanity is sound only and deniable (a presence, a name, a footstep); falling sanity brings voices and real objects reading wrong (altered, not inserted); low sanity brings the first visuals; at the bottom visuals dominate. The owner's image is walking into the ocean from the shore, as a metaphor for intensity, not a literal movement or control effect. Logged as pole A because A leads and B only arrives at depth.
- Decision: A · owner · 2026-10-12
- Evidence: A · projects/pappydapimp69__seven.md#E61 · 2026-10-12
- Evidence: A · projects/pappydapimp69__seven.md#E71 · 2026-10-12
- 2026-10-12 correction: the evidence line above first cited E60 (inner voices) by mistake; the intended lesson, altered real objects outlasting inserted phantoms, is E61 (since audited as modeled).

### T? · open-question · Should SEVEN's sound-first hallucination numbers (voice budget, duck size, sway limits, phantom schedule) be tuned further in sandboxes, or frozen until a short human test measures them?
After two review rounds on 2026-10-12 the hallucination entries stand at 12 disputed, 3 confirmed, 2 modeled: every disputed number moved when a modelling constant moved (masking width, talk share, psychometric slope, learner, frequency vs velocity), and the published sources only bound them (Brungart 2001: masking follows summed level; Chen 2016: sickness follows speed; Ellson 1942 and a placebo arm: conditioned hallucinations persist but reach about 29 percent). None of the hallucination code exists on main yet (docs/IDEAS.md only).
Poles: keep refining in sandboxes (cheap, fast, but each round re-derives a constant someone picked) **vs** freeze the numbers and run one small human test first: 5 to 8 people, phone speaker and headphones, the line at +3/+6/+9 dB over 1, 2 and 4 other voices (measures the duck), plus one sway clip at two speeds with a comfort rating (measures the speed cap).
Lean: 🟡 open; leaning to the human test, since no further sandbox can supply the missing variable.
Updates:
- 2026-10-12 opened from brain train follow-ups on E73, E78, E79, E83 and E85; evidence is published papers read first-hand plus sandboxes, nothing measured on players.
Source: sandboxes 2026-10-12 duck-must-cover-total-masker-power, sway-sickness-tracks-velocity-not-frequency, conditioned-phantoms-persist-but-reach-a-minority
- Session: session_01KGZvxv8BDgpDMRFTYMfJoJ

### T? · open-question · How should a game duck other voices so a must-land line keeps a fixed margin as voices are added: a fixed duck, a duck scaled by 10*log10(voice count), or a sidechain tracking the summed bus?
Sandbox 2026-10-12__duck-the-summed-bus-not-each-voice.py (8 kHz synthetic voices: LCG noise x 3-6 Hz syllable envelopes with pauses; line-active windows only; 3 iterations). Summed power of equal voices did follow 10*log10(n) (3.06 dB for 2, 5.71 for 4). But no ducker held a +6 dB line-to-bus margin as voices went 1 to 6: a fixed -6 dB per voice fell 5.9 -> 2.0 dB; a count-scaled duck (6 + 10*log10 n) overshot 5.9 -> 9.7 dB because the bus, measured while the line speaks, grew less than 10*log10(n); a bus-tracking sidechain lagged syllables (4 dB gain steps smoothed, 11.6 dB unsmoothed) and still fell 4.9 -> 2.2 dB, with worst 50 ms windows down to -7 dB.
Poles: count-scaled fixed duck (simple, no zipper; right when voices overlap continuously, overshoots when they are intermittent) **vs** level-tracking sidechain (adapts to who is talking; lags syllables or zippers unless attack and release are tuned) **vs** fixed duck plus limiting scenes to 2-3 voices.
Lean: 🔴 open; the answer turns on how much the hallucinated voices overlap the line in time, which synthetic envelopes cannot settle; measure on the real voice assets.
Updates:
- 2026-10-12 opened from brain train newidea loop 5; sandbox above, RESULT FAIL 2/6; scaled mean n1..6 5.9/7.5/8.1/8.9/9.8/9.7; bus mean 4.9 -> 2.2; static 5.9 -> 2.0.
Source: sandbox 2026-10-12__duck-the-summed-bus-not-each-voice.py; session_01KGZvxv8BDgpDMRFTYMfJoJ
- Session: session_01KGZvxv8BDgpDMRFTYMfJoJ

### T? · open-question · In a very dead room (mean absorption >= 0.6, or absorption lumped on a few faces), is Eyring's reverberation time still the better estimate than Sabine's, or does room shape decide which formula is less wrong?
A deterministic diffuse-reflection (Lambertian) ray tracer, 4000 rays per room, measured mean free path within 1% of 4V/S in every case. For mean absorption <= 0.5 the traced T60 sat between the two formulas in 9 of 9 rooms (Eyring low, Sabine high), and Kuttruff's path-variance correction landed within 2.8% of it. Above that the ranking depended on geometry. In compact rooms Eyring was closer: shoebox 10x8x4 at a=0.8 gave Eyring -22% against Sabine +57%, and a 6x5x3 room at a=0.7 gave Eyring -16% against Sabine +44%. In elongated or flat rooms Sabine was closer: a 2x2x20 corridor at a=0.8 gave Eyring -53% against Sabine -5%, and a 20x16x3 flat hall with floor and ceiling at 0.8 (mean a=0.60) gave Eyring -37% against Sabine -3%. In those two rooms the traced decay ran past Eyring's because the long paths that dodge the absorbers carry the late tail. Kuttruff's correction also broke there (-30% and -15%).
Poles: Eyring is less wrong when the room is compact and absorption is spread evenly, whatever a is **vs** Sabine is less wrong when the room is elongated or flat, or the absorption sits on its large faces, because path-length variance (g2 0.41-0.55) dominates the decay.
Lean: 🔴 open
Updates:
- 2026-10-12 opened from brain train newdomain (ROOM-ACOUSTICS); sandbox 2026-10-12__eyring-and-sabine-bracket-reverberation-time.py, result `RESULT: FAIL bracket_low=True eyring_worse_high=False mfp_ok=True`. Eyring was worse than Sabine in 2 of 5 dead or lumped rooms. The 2 were the corridor (E-53/S-5) and the flat hall (E-37/S-3); the 3 others were the shoebox (E-22/S+57), the small room (E-16/S+44) and the cube with one face at 0.9 (E-1/S+9). Prediction 1 (Eyring within 5% of the tracer at every a) was refuted: -11% at a=0.5, -22% at a=0.8. Assumptions: diffuse reflection, no air absorption, no edge diffraction, and a T30 fit (-5 to -35 dB) extrapolated to 60 dB.
- 2026-10-12 brain train gap: tested the per-axis formulas built for uneven rooms (Fitzroy 1959, Arau-Puchades 1988; checked in Prawda et al., SMC 2020, eqs. 5-6) with the same tracer on the 5 rooms above plus 4 held-out ones. `RESULT: FAIL F 0/9 AP 1/9 within 15% (S 4, E 3); uniform F=AP=E to 0.000%`. Under uniform absorption both are Eyring exactly, so the corridor stays at -53%; with lumped absorption they let the reflective axis pair carry the decay (Fitzroy +656% flat hall, +329% one-face cube, +32..+163% held-out; Arau-Puchades +9% flat hall but +129% cube, +76% one side wall, -58% absorbent-sided corridor). Held-out S/E: BREAK corridor with absorbent end walls -22/-25; shoebox one side wall 0.9 +8/-1; flat hall floor only 0.9 +17/-6; corridor sides+floor+ceiling 0.8 -27/-62. Kuttruff (traced g2) within 11% in 5/9, failing in both corridors and the floor+ceiling hall. The "per-axis formula" pole is refuted for diffuse rooms (memory lesson, Polarity incompatible); the fork itself stays open: Eyring/Kuttruff win compact or single-face-lumped rooms, Sabine wins when the absorption sits on the large faces of a long or flat room.
Source: Wikipedia "Reverberation" (Sabine T60 = 0.1611 V/(S a); Eyring T60 = -0.161 V/(S ln(1-a)); "The Sabine equation tends to over-predict reverberation time for small rooms with high amounts of absorption"); Prawda, Schlecht & Valimaki, SMC 2020 (Fitzroy eq. 5, Arau-Puchades eq. 6); sandbox 2026-10-12__fitzroy-and-arau-puchades-reduce-to-eyring-and-overshoot-in-diffuse-lumped-rooms.py (self-contained; carries the original tracer); session_01QGT1LfmPHPG99JEGaPhBwB

### T? · open-question · In a very dead or lumped-absorption room, is Eyring's T60 still better than Sabine's, or does room shape decide?
A deterministic diffuse ray tracer (Fibonacci start directions, golden-ratio Lambertian reflections, T60 from the -5 to -35 dB decay slope) gave different answers by absorption layout. Uniform absorption: Eyring beat Sabine at every level tested (a=0.7: Eyring -12% vs Sabine +51%; a=0.9: -23% vs +97%). Lumped absorption in a flat 20x16x3 hall (floor and ceiling 0.9, walls 0.02, mean 0.68): Sabine matched the trace and Eyring ran 40% low, and Kuttruff -25% was no rescue. Kuttruff overshot in uniform dead rooms (+13%, +34%) so it is only the better estimate near a=0.5 (+3%).
Poles: Eyring is the better estimate when absorption is spread evenly over all faces **vs** Sabine is the better estimate when absorption is lumped on the two largest faces of a flat room
Lean: 🔴 open
Updates:
- 2026-10-12 opened from brain train; sandbox 2026-10-12__eyring-vs-sabine-in-dead-and-flat-rooms-diffuse-ray-trace.py, traced shoebox cases (4) as above; one flat-hall case only, so the lumped pole rests on a single layout.
Source: 2026-10-12__eyring-vs-sabine-in-dead-and-flat-rooms-diffuse-ray-trace.py / brain train session
- Session: session_01QoYzipjYSp8DTBoAoj5Bdh

### T? · open-question · does the weighted-A* sweet spot and the flat-diagonal-cost routing difference carry over unchanged to an 8-directional octile grid?
Sandbox 2026-10-12__weighted-astar-sweep-octile-vs-flat-diagonal-cost.py (32 solvable hash-built 32x32 maps, density 0.25, corner to corner) gave a mixed result. Held: expansions fell 76% from w=1 to w=2 and only 3 more points to w=10 (359.0 to 87.0 to 74.2), so the steep-then-flat shape matched the kernel and sandbox-pathfinding-astar-heuristic/E1. Did not hold: mean path-cost excess at w=2 was 4.62%, not the under-3% I predicted (E1 saw ~0% on its 4-way map), and a flat-cost planner's route, re-priced with true octile cost, was costlier on 18 of 32 maps (56%, never cheaper) against the kernel's 16.8%; route equality differed on 32 of 32 but that is mostly tie-breaking, so true-cost difference is the usable figure. The flat planner at w=2 had lower excess (3.78%) than the octile one (4.62%), refuting my guess that weight hides a cost-model bug.
Poles: the weight-1.5-to-2 band keeps nearly all the speedup on 8-directional octile maps **vs** the "~0% suboptimality at w=2" and "16.8% of routes change" figures are map-family specific and do not transfer to open 8-directional grids.
Lean: 🔴 open
Updates:
- 2026-10-12 opened from brain train; sandbox 2026-10-12__weighted-astar-sweep-octile-vs-flat-diagonal-cost.py, RESULT: FAIL (reduction w2 76%, w10 79%; excess w2 4.62%; flat costlier 18/32; flat w2 excess 3.78%).
Source: ideas:PATHFINDING/general/measure-both-sides-of-a-tradeoff-curve-not-just-one-metric, ideas:PATHFINDING/astar/uniform-diagonal-cost-changes-the-chosen-route-not-just-its-label, sandbox-pathfinding-astar-heuristic/E1; session_01XCe61chZn6agE2zVwbgxdQ

### T? · open-question · Does nearest-neighbor voicing add anything over a plain compact voicing, and what does it cost in counterpoint?
Sandbox (2026-10-13__nearest-voicing-greedy-vs-fixed-and-counterpoint.py) on 5 triad progressions (authentic, plagal, deceptive, half, a 7-chord runtime-unpredictable one), 3 upper voices plus root bass. Against naive root-position stacking, greedy nearest voicing cut total motion in 5/5 (e.g. 84 to 14 semitones on the unpredictable one). Against a compact voicing centred near middle C it improved only 1/5 (18 to 14) and moved the top voice more there (5 vs 4). Greedy equalled a full-lookahead DP optimum in 5/5, so lookahead was not needed on these. But greedy produced parallel perfect 5ths/8ves in the plagal progression (2) where the compact voicing had none, which species counterpoint forbids; the cadence type (authentic/plagal/deceptive/half) changed motion totals only through the chord roots.
Poles: nearest-voicing is worth it when the baseline is naive root position or chords jump unpredictably **vs** it adds nothing, and may add parallels, when a compact centred voicing is already the baseline and progressions are short and diatonic.
Lean: 🔴 open
Updates:
- 2026-10-13 opened from brain train; sandbox 2026-10-13__nearest-voicing-greedy-vs-fixed-and-counterpoint.py, RESULT: FAIL greedy_cuts_motion_vs_rootpos_in=5/5 greedy_beats_compact_in=1/5 progs_with_parallel_perfects=2 greedy_worse_than_DP_in=0 (iteration 2; iteration 1 refuted its own baseline). Kernels exercised: ideas:MUSIC/theory/common-tone-retention-and-nearest-voicing..., ideas:MUSIC/theory/species-counterpoint-is-graduated-constraint-training, ideas:MUSIC/theory/cadence-types-are-phrase-punctuation-with-narrative-purpose.
Source: 2026-10-13__nearest-voicing-greedy-vs-fixed-and-counterpoint.py / brain train auto loop 1 pass 5
- Session: session_011eTW7aDHC86vQjq7f9sRQG

### T? · open-question · Does printing a style label only above a margin band make humor-style advice more stable on re-asking, or only the labels that survive?
In a deterministic sandbox (400 synthetic respondents, four correlated subscales, two noisy measurements each) the kernel's claim held for the label: with axis correlation 0.6 the max-subscale label agreed on retest 0.50 of the time, while among respondents clearing a 0.5 SD margin the label agreed 0.79 (but only 24% were labelled), and the overall-use score retested at r=0.93. But a downstream advice rule (self-defeating label: hold jokes to mid-pitch; mixed: ask about the setting first; else opening joke ok) flipped for 0.22 of respondents under max-label and 0.49 under the margin rule, because respondents drift in and out of "mixed" between measurements; only a wide band (1.0 SD) cut flips to 0.26 by labelling just 4% of people. The margin gain over max-label was 0.23 at r=0 and 0.29 at r=0.6, so it helps a little more when axes are correlated. Constants and the advice mapping are assumed; the sandbox is a model, not people.
Poles: the margin band helps when the reader only trusts the labelled minority (label agreement 0.79 to 0.88 as the band widens) **vs** it hurts when every respondent still needs one actionable answer, since "mixed" then flips in and out and doubles advice instability.
Lean: 🔴 open
Updates:
- 2026-10-13 opened from brain train gap; sandbox 2026-10-13__humor-profile-margin-band-label-advice-flip-retest-correlated-axes.py, result r=0.6 max-label agree 0.50 vs labelled 0.79 (24% labelled), advice flips 0.23 vs 0.49. Touches ideas:HUMOR-STYLES/typology/four-styles-as-a-2x2-of-benign-vs-injurious-and-self-vs-other, ideas:HUMOR-STYLES/pitch-opening/opening-joke-vs-change-first-order, sandbox-self-directed-humor-dose-response/E1 (only as the source of the advice mapping, not re-run).
Source: 2026-10-13__humor-profile-margin-band-label-advice-flip-retest-correlated-axes.py / scheduled brain train session
- Session: session_01JbvSxNM4UdUZG4c4NXMNMD

### T? · open-question · Does redundant triangulation of environmental cues beat one well-placed cue, or does placement and cue ambiguity decide it?
In a deterministic grid sandbox (11x11, two rooms and a corridor, 16 fixed routes, line-of-sight with radius 3) a story landed when the cues found left exactly the true cause. One unambiguous cue landed on 0.25 of routes at its worst position and 0.88 at its best sightline position. Three ambiguous cues (each a 3-cause set overlapping only on the true cause, so two must be found) spread across rooms landed on 0.69; clustered in one room or a dead-end corner they landed on 0.44, so spread beat clustered by 0.25 but my prediction that clustering would be no better than one cue was wrong (still +0.19 over the hidden cue). Three unambiguous cues spread landed on 1.00. The found-set was order independent. So redundancy beat a badly placed cue, lost to a well-placed unambiguous one (0.69 vs 0.88), and only won outright when each cue was itself unambiguous. Constants, room layout and the ambiguity sets are assumed; routes are not player behavior.
Poles: redundancy wins when the single cue can only sit off the main sightlines or when cues are cheap and unambiguous **vs** a single indexed cue on a sightline wins when each redundant cue is ambiguous enough that two must be found.
Lean: 🔴 open
Updates:
- 2026-10-13 opened from brain train gap; sandbox 2026-10-13__redundant-cues-sightline-coverage-index-ambiguity-triangulation-grid.py, result hidden 0.25, sightline 0.88, ambiguous spread 0.69, clustered 0.44, unambiguous spread 1.00. Touches ideas:WORLDBUILDING/environmental-storytelling/order-independent-micro-narrative, ideas:WORLDBUILDING/environmental-storytelling/index-not-event (index as ambiguous residue) and ideas:WORLDBUILDING/surveillance/panopticon (sightline as the placement primitive).
Source: 2026-10-13__redundant-cues-sightline-coverage-index-ambiguity-triangulation-grid.py / scheduled brain train session
- Session: session_01JbvSxNM4UdUZG4c4NXMNMD

### T? · open-question · Do correlated latent axes lower max-subscale label retest in a four-style 2x2, or only when cross-loading is extreme?
In a deterministic 2x2 fixture (styles = signed sums of a use axis and a target axis, shared overall-use factor, noise 0.8) raising axis correlation from 0 to 0.8 moved label retest agreement at band 0 only from 0.549 to 0.528, not the 0.69 to 0.53 drop recorded for the earlier questionnaire sandbox. The margin band lifted agreement in every cell (0.528 to 0.789 at band 0.5 SD, coverage 0.49) and shading faked agreement (0.594 vs 0.528) while lowering accuracy (0.572 vs 0.634). So the band rule holds here, the correlation-driven flip depends on how the styles load on the axes.
Poles: correlated axes cut label retest when each style loads on both axes with strong cross-loading and little style-specific variance **vs** the effect is small when style-specific variance dominates the axis contrast.
Lean: 🔴 open
Updates:
- 2026-10-13 opened from brain train; sandbox 2026-10-13__humor-style-margin-band-lifts-retest-but-shading-fakes-agreement.py, result agree 0.549 (rho 0) vs 0.528 (rho 0.8).
Source: 2026-10-13__humor-style-margin-band-lifts-retest-but-shading-fakes-agreement.py / brain train session
- Session: session_01HK1W7JLSbLXCV3BweWrzfF

### T? · open-question · Is a mid-pitch self-directed joke better than an opening joke for absorbed content in every audience, or only an attentive one?
Own-fixture sandbox (change-first 10-slot pitch, refill g times one minus attention, warmth saturating, credibility cost 0.10 per joke). The opening sign flipped with starting attention at both g=0.2 and g=0.5: a0=0.95 opening effect -1.54 and -1.37, a0=0.35 opening effect +0.90 and +3.17. For the attentive audience the best slot was late (slot 9 at g=0.2, slot 8 at g=0.5), but for the cold audience slot 0 was best at both g, so "mid-pitch beats opening in every cell" did not hold. Dose sweep with best placement: warmth-weighted score (W=0.5) rose to 4 jokes, while at W=12 the optimum was 1 joke for the cold audience (6.672 vs 4.956 for none) and 0 for the attentive one (9.144), so my predicted zero jokes at high weight failed for the cold audience.
Poles: the opening joke loses or breaks even and mid or late placement wins **vs** the opening is the best slot and even a high-credibility-weight pitch wants one joke, when starting attention is low.
Lean: 🔴 open
Updates:
- 2026-10-14 opened from brain train; sandbox 2026-10-14__opening-vs-midpitch-joke-refill-sign-and-dose-in-change-first-pitch.py, RESULT: FAIL P1/P4=True P2=True P3=False kLow=4 kHigh=1 kHigh95=0.
Source: 2026-10-14__opening-vs-midpitch-joke-refill-sign-and-dose-in-change-first-pitch.py, brain train loop 1 pass 5; relates to ideas:HUMOR-STYLES/pitch-opening, sandbox-pitch-opening-joke-order-rule/E1, sandbox-self-directed-humor-dose-response/E1
- Session: session_015vYTjNJNEjDvnZgWaJaTSv

### T? · open-question · Does a multi-axis power vector (instead of one scalar) let a lower-tier character win legibly, or does the tier ceiling still decide almost every fight?
A deterministic 4-axis duel sandbox (64 build pairings per cell; counter-axis damage with clipping) gave 0 upsets for a collapsed scalar at every gap, but a vector only produced upsets in a narrow cell: 6.2% (4 of 64) at one-tier gap, spread 0.8-1.0 and counter strength K=1.5 (or K=2.0 at spread 1.0), every one attributable to a single named axis where the lower character led. At K=1.0, K=3.0, spread 0.4, two or three tier gaps, or axes correlated at 0.9 there were 0 upsets. The prediction of 20% or more at a one-tier gap failed in three iterations (0%, 6.2%, 6.2% best). Linked: ideas:narrative-design/power-scaling/multi-axis-progression/escalation-legibility, ideas:narrative-design/arc-structure/power-creep-accounting/villain-escalation, b/E2 (every detail needs a named causal payoff, which the named-axis column shows is available when an upset happens).
Poles: niche upsets are real and nameable when tiers are adjacent, builds are strongly specialised and counters are moderately strong **vs** fail when the ceiling gap is two tiers or more, axes rise together, or counters are weak or overwhelming, where the scalar total decides.
Lean: 🔴 open
Updates:
- 2026-10-14 opened from brain train; sandbox 2026-10-14__vector-power-upsets-live-only-within-adjacent-tiers-and-vanish-when-axes-correlate.py, result gap1/2/3 upset 0.062/0/0 at spread 0.8, RESULT: FAIL against the 20% prediction.
Source: brain train auto loop 1 pass 5; sandbox in memory/incoming; session_017SJAeaijx8mHKPVUZV6hJB

### T? · open-question · Does a filter-switch transient from a risky topology (DF2T/DF1) set a film mix's peak-normalize level, making the SVF choice a mix-level concern as well as a stability one?
Sandbox (RBJ biquad DF2T/DF1 vs TPT SVF, 3-tone body, peak-normalize to 0.9): a single cutoff change at a scene cut (300->3000 Hz) moved the peak only 0.47-0.57 at Q 0.707 and 0.864 identical across all topologies at Q 10, so normalized body RMS differed 0.30 vs 0.36 and 0.47 vs 0.47 — topology barely mattered. Switching every 7 samples: DF2T/DF1 peaks 1.68/1.42 at Q 0.707 (body after normalize 0.22 vs SVF 0.42, ~1.9x quieter) and went to inf/NaN at Q 10, while SVF stayed at 0.56-0.58. An RMS-match plus tanh soft-limit rescued the SVF mix (peak 0.217, body 0.099) but cannot rescue a diverged DF2T (all zeros).
Poles: topology decides the normalize level and can erase the mix **when** cutoff is modulated fast or at high Q **vs** a single cut-time cutoff change leaves the peak source-dominated and topology irrelevant.
Lean: 🔴 open
Updates:
- 2026-10-15 opened from brain train; sandbox 2026-10-15__film-peak-normalize-vs-filter-switch-transient-df2t-svf.py, result FAIL on the original single-cut prediction, holds only for fast modulation. Composed: film/E5, sandbox-kernel-dsp-filter-design/E1.
Source: 2026-10-15__film-peak-normalize-vs-filter-switch-transient-df2t-svf.py / session_01R9q6q7UzomwgJUBasbhB7S

### T? · open-question · Does shaping reach a rare target "far faster than waiting", or only when the target competes with a richer alternative?
Expected-value sandbox (10 behavior levels, target level 9 at p~0.001, matching-law response share to the shaped task, goal-gradient vigor 1+1/remaining-levels): with no competing option waiting at the final criterion needed 143 ticks vs shaping 200 (shaping slower, criterion steps dilute the update). With a competing option of reinforcement rate 0.2, matching starves the rarely-reinforced waiting schedule: 4257 ticks vs shaping 316 (13x). Goal-gradient vigor cut shaping 316 to 240 and waiting 4257 to 2132, so it did not rescue waiting. A near-zero alternative (1e-9) reproduced the no-competitor 143.
Poles: shaping wins big **when** the learner has a richer competing option so response share follows reinforcement rate **vs** shaping loses slightly **when** nothing competes and the target is reinforced directly.
Lean: 🔴 open
Updates:
- 2026-10-15 opened from brain train gap; sandbox 2026-10-15__shaping-matching-goal-gradient-rare-target-reach-time.py, result FAIL on the unconditional prediction. Exercises ideas:REINFORCEMENT/reinforcing-successive-approximations-reaches-a-rare-target-behavior-far-faster-than-waiting-for-it-outright, ideas:REINFORCEMENT/response-share-across-competing-options-tracks-relative-not-absolute-reinforcement-rate, ideas:REINFORCEMENT/effort-accelerates-as-remaining-distance-to-a-fixed-goal-shrinks.
Source: 2026-10-15__shaping-matching-goal-gradient-rare-target-reach-time.py / session_01R9q6q7UzomwgJUBasbhB7S

### T? · tradeoff · Recurring cast in a shared universe, or disposable remixable absurd one-offs, for a new AI shorts channel?
Two 2025 growth patterns pull opposite ways. Italian brainrot characters (hybrid creature + synthetic voice + chanted nonsense name; Tralalero Tralala first post ~7M views, Ballerina Cappuccina 19.5M in three weeks) spread because anyone could remix them, but spiked and burned out: the Roblox spin-off Steal a Brainrot peaked at ~25.4M concurrent players on 2025-10-07 and a later tracker snapshot showed ~205-215k, about 99% down. Neural Viz instead grew a recurring cast in one shared universe with deadpan formats and keeps most videos above 100k views. Unknown: which builds a channel faster from zero, and whether a recurring cast can also be remixable.
Poles: disposable remixable one-offs win early reach and meme spread **vs** a recurring cast in a shared universe wins returning viewers and durability.
Lean: 🔴 open
Updates:
- 2026-10-15 opened from content-creation training research; no channel data yet, decide on real post analytics (returning viewers, follows per view).
Source: knowyourmeme Ballerina Cappuccina; pocketgamer.biz 25.4M CCU; rowatcher.com tracker; android.com.pl Neural Viz profile.
- Session: session_01TQvFfNiYzpWZZDPgWeMoBC

### T? · open-question · Does a run-length release rule (release after k consecutive refusals) settle the held-selector fork that first-refusal and margin rules split?
In a 40-tick toy with a 3-tick switch cost, eight refusal patterns and six rules (hold, first refusal, margin 3 of 6, release after 2, 3 or 4 consecutive refusals), no rule won every pattern: holding did 0 work under a permanent block and 28 against 37 for first-refusal at a 12-tick block; first-refusal bounced 10 times for 10 work when both targets were refused one tick in four (30 for hold, margin and every run-length rule); with the alternative busy until tick 20, release-after-4 reached 20 work against 19 for first-refusal and 15 for margin. Release-after-2 had the lowest total shortfall against the best rule per pattern (13), then release-after-4 (16), margin and release-after-3 (20 each), first-refusal (22) and hold (75); release-after-3 lost by 2 on blocks of 3 and 5 ticks, which is the switch-cost-sized case. The ranking moved when the permanent block started at tick 0 instead of tick 5, so the order of the middle rules is not stable. Toy constants (cost 3, window 6, margin 3, 1-in-4 noise) are assumed.
Poles: a short run-length rule (release after 2) is the safest default when refusals are mostly noise or the alternative is sometimes busy **vs** first-refusal release wins when blocks are long and the alternative is reliably free, and a longer run length wins when the alternative is busy for a while.
Lean: 🔴 open
Updates:
- 2026-10-15 opened from brain train gap; sandbox 2026-10-15__held-selector-release-rule-run-length-vs-first-refusal-vs-margin.py, result lowest total shortfall RUN2 13, RUN4 16, MARGIN 20, RUN3 20, FIRST 22, HOLD 75; no rule dominates. Builds on the earlier margin-versus-first-refusal tension rather than replacing it.
Source: 2026-10-15__held-selector-release-rule-run-length-vs-first-refusal-vs-margin.py / brain train auto loop 2 pass 5
- Session: session_01Kx9Pq1H5qpcbvZJ9u2DPKR

## Project: film

### T? · open-question · Does the film-trailer pacing curve (about 1 s per shot, shortening into the climax) fit a 25 s vertical game ad watched on a phone, or do tiny screens and pixel art need longer holds to read?
The only measured shot-length data is for film trailers (Redfern horror set: ASL 1.09 s, thirds 0.96/0.79/0.54 s). The Stonewake cut ran 2.0 s per shot, flat into the climax. Nobody has published shot lengths for game ads or for 9:16 mobile ads. Pixel art at about 2 pt per art pixel may need more time per shot to read, while ad watchers drop off faster than trailer audiences.
Poles: cut to the trailer curve (about 1 s, shortening; holds only as counted stopdowns) **vs** hold mobile pixel shots longer (about 1.5–2 s) because legibility on a phone costs time.
Lean: 🔴 open
Updates:
- 2026-10-15 opened while scoring film20 against the re-run horror-trailer data; sandbox 2026-10-15__measure-the-cut-list-against-a-trailer-pacing-curve-before-review.py. Resolving it needs cut counts on real mobile game ads (ffmpeg scene detection; YouTube downloads were blocked this session).
Source: 2026-10-15__measure-the-cut-list-against-a-trailer-pacing-curve-before-review.py / Brain training pass for AAA trailer editing
- Session: session_0169rjPqYDYawkbeTUEzoNKo

### T? · tradeoff · should the Demo Disc's spoof ads carry the real ads' "not all images represent actual gameplay" disclaimer?
The fake-ad grammar kit lists the disclaimer as one of its elements, and the kit audit of four shipped ads
(projects/pappydapimp69__demo-disc.md, "fake-ad kit audit") found it on none and recommended adding it to the kit.
Poles: A = no disclaimer: the ad promising a game the player then doesn't get IS the joke, and a disclaimer would
defuse it **vs** B = add it as one more piece of fake-ad texture.
Lean: decided A
Updates:
- 2026-10-15 owner: "No disclaimer, that's the point." Do not add it to the kit or the ads; the audit's disclaimer
  recommendation is withdrawn. Rotating the swap axis across future ads still stands.
- Decision: A · owner · 2026-10-15
Source: session 2026-10-15, after brain train creative arts
- Session: session_011p52L2CkFXcsYRwjDu6tG9

### T? · open-question · Does a low MEAN pair similarity of a rotated-kit fake-ad batch hide a flaggable pair, or only when rotation is cyclic and the batch passes the variant-pool size?
A 16-slot model (3 fixed anchor assets, 7 rotating kit assets with 6 variants each, 4 engine-owned and 2 fresh variable slots) gave a mean pair similarity of 0.26 at k=8 with random draws, yet 30% of 100 seeds had a pair at or above 0.4 (worst pair exactly 0.50, never above). Cyclic rotation (variant = (i + asset) mod 6) kept every pair at 0.1875 up to 6 videos, then the 7th video repeated all 7 rotating assets of video 1 and the max jumped to 0.625, above the 0.5 flag; two mixed strides kept the max at 0.4375 through 12 videos. My prediction that random draws would hit 0.4 in over 80% of seeds was wrong.
Poles: the mean is a safe summary when assets are drawn at random from a pool of 6 (max stays at most 0.5 in 100 seeds) **vs** the mean hides a flagged pair when the rotation is a single cyclic stride and the batch is longer than the pool (max 0.625 at k=7, mean only 0.208)
Lean: 🔴 open
Updates:
- 2026-10-15 opened from brain train auto; sandbox 2026-10-15__kit-rotation-max-pair-cliff-at-pool-size.py, result: RESULT: FAIL k=8 random mean 0.259 but max>=0.4 in 30% of seeds; cyclic max k=6 0.1875 -> k=7 0.6250; mixed-stride max at k=12 0.4375. The 0.5 flag line and equal slot weights are assumptions inherited from fake-ad-kit-template-similarity/E1.
Source: 2026-10-15__kit-rotation-max-pair-cliff-at-pool-size.py; brain train auto loop 2 pass 1
- Session: session_01USEQKxFedmHB9RNfo9RMD6

### T? · open-question · Does measuring the comedy "distance dial" by BFS instead of straight-line distance raise a go-big severity schedule's fit on obstructed maps?
Sandbox 2026-10-16__distance-dial-bfs-vs-euclid-severity-ladder.py (pass-1 kernel: severe-harm-needs-distance + escalation-needs-matching-distance + sandbox-distance). Prediction was BFS beats Euclid by >=0.05 on any walled map and ties on an open one. Observed: open bfs 0.858 vs eu 0.882 (gap 0.024); single wall bfs 0.802 vs eu 0.758 (+0.044, under the bar); serpentine walls bfs 0.789 vs eu 0.618 (+0.171). Holds strongly only when the detour is large; a single gapped wall barely moves it, and the toy score is my own construction.
Poles: BFS distance matters when obstacles force big detours (serpentine) **vs** negligible when obstacles are sparse or the map is open, where Euclid is as good or slightly better
Lean: 🔴 open
Updates:
- 2026-10-16 opened from brain train; sandbox 2026-10-16__distance-dial-bfs-vs-euclid-severity-ladder.py, RESULT: FAIL open_gap=0.024 wall_gain=0.044 spiral_gain=0.171.
Source: brainwork train auto pass 1
- Session: session_01RbNqhLnCALyxxvjiR2t3TU

### T? · open-question · Does the gain from a BFS comedy distance dial over a straight-line one grow with the map's detour ratio?
Pass-1 kernel (benign-violation + escalation-needs-matching-distance + sandbox-distance). Prediction: BFS never worse than straight-line, gain rises with mean BFS/Euclid detour ratio, and gain >= 0.05 exactly when ratio >= 1.5. Observed over five maps: open and sparse pillars ratio 1.28 gain 0.000; gapped wall ratio 1.82 gain +0.279; two walls ratio 2.31 gain +0.112; serpentine ratio 3.85 gain +0.081. Never-worse and the 1.5 threshold held; monotonicity failed because the gain peaks at a mid detour ratio and shrinks again on the serpentine (both dials saturate near the far end when the map is long and thin). Toy fit score is my own construction.
Poles: BFS dial pays off once detours appear (ratio above about 1.5) **vs** gain is not monotone in detour ratio, so wall layout matters more than a single ratio number
Lean: 🔴 open
Updates:
- 2026-10-16 opened from brain train; sandbox 2026-10-16__bfs-distance-dial-gain-tracks-detour-ratio-not-wall-presence.py, RESULT: FAIL never_worse=True monotone=False threshold1.5=True serp_gain=+0.081 open_gain=+0.000.
Source: brainwork train auto pass 1
- Session: session_014EZhKyrjLAMxD9wBXVniGL

### T? · open-question · Does a gag rule card that states a harm ceiling let a sketch escalate safely to the framing's distance?
In a toy benign-violation model (a beat is funny only if 0 < severity <= distance, score = summed severity of funny beats) a card-set even escalation to the true distance beat a go-big schedule at distances 6 and 10 (21.0 vs 12.0, 35.0 vs 30.0) but lost to a dense mild schedule at distance 3 (10.5 vs 12.0), and a card naming the wrong ceiling lost badly both ways (ceiling 7 on true 3: 3.5 vs 12.0; ceiling 2 on true 10: 7.0 vs 30.0).
Poles: the card helps when its stated ceiling equals the real distance and the pick is spread across it **vs** it fails when the ceiling is mis-measured or when a tuned mild schedule packs more near the ceiling than even steps do.
Lean: 🔴 open
Updates:
- 2026-10-16 opened from brain train; sandbox 2026-10-16__rule-card-ceiling-sets-escalation-distance.py (kept in incoming/ for reference), result: RESULT: FAIL card-matched wins at all 3 distances False; wrong ceiling loses (7vs3: 3.5<12.0, 2vs10: 7.0<30.0).
Source: brain train auto pass 5 (loop 1); composed of ideas:COMEDY-CRAFT/benign-violation, escalation-needs-matching-distance, ideas:COMEDY-CRAFT/write-the-rules-before-the-gags
- Session: session_01S9MKv7QKGDb1fdsYzjZeah

### T? · open-question · When recutting an ad winner's cold-open promise, does ranking recuts on IPM times D1 instead of IPM beat IPM alone at a realistic impression budget?
Toy model with 8 recuts of one cold open (promise 0 to 1, installs rise with promise, D1 falls once promise exceeds delivery), 300 seeds. With delivery 0.4 the IPM x D1 pick gained +2.7% retained installs per impression at 300 impressions per recut but +10.3% at 3000; delivery 0.7 gave -1.5% and +1.6%; delivery 1.0 gave exactly 0 at both. So the gain exists only when promise can exceed delivery AND the budget is large enough for D1 to separate recuts; at small budgets noise makes it neutral or slightly worse.
Poles: holds when promise can outrun delivery and each recut gets thousands of impressions **vs** fails when delivery already covers the promise or budgets are around 300 impressions per recut
Lean: 🔴 open
Updates:
- 2026-10-17 opened from brain train; sandbox 2026-10-17__recut-winner-ranked-ipm-d1-needs-delivery-below-promise.py (not shipped), result gains +2.7%/+10.3% at delivery 0.4, ~0 at delivery 1.0; first-hand run, composed from film, rank-ipm-times-d1-needs-fidelity-retention-link, ideas:GAME-ADS/concept-then-variants-ranked-on-ipm-times-early-retention.
Source: brain train auto loop 1 pass 5, session_01PTu5uBJqYTUhgm91RqrjQ3

### UPDATE · contradiction · jurisdiction is separation of powers, not checks and balances
The Conscience film (The Ferryman's Question, 2026-10-17) cast Conscience as the Luck Child's ferryman: it carries Brain's light to the owner and the owner's questions back, and lands on neither shore. The owner chose the casting and the ending: the king (the owner) ends up holding the pole. The film argues the first pole: a ferry handed the shore stops being a ferry, and the watching duty is conserved and only changes hands. This is an owner casting choice and a design argument, so it is logged as an update and carries no Evidence: line.
Poles: separation of powers (the observer never acts) **vs** checks and balances (the observer can stop or veto), as read from the claim
Lean: 🔴 open
Updates:
- 2026-10-17 film argument for the first pole from the Zanegpt session; the owner cast Conscience as the ferryman and chose that the owner ends with the pole. Kernel: SYSTEM/observer-roles/the-watchers-pole-is-conserved.
Source: https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc

### T? · open-question · Does the gate-only invalid count under cyclic lag jitter equal the mean of the clipped one-sided formula over the jitter lags, and does that depend on the jitter cycle length sharing a factor with the period?
On P15 W5 N600 with press t using lag 3 + (t mod (J+1)), J 0 to 11: the mean-of-formula (N/P) x mean of min(l,W,P-l,P-W) was exact for J 0, 1, 2, 3, 7 and within 3% for J 6 and 12, but 6.1% off at J 10 although J+1=11 is coprime to 15. For jitter cycles sharing a factor with 15 it deviated 11 to 21% in 5 of 6 cases (J 4, 5, 8, 9, 11) yet was exact at J=2. Coprimality alone therefore did not predict the error (first prediction failed at J=8; revised one failed at J=10); validity plus cutoff at 3+J was lossless for every J. Three iterations did not give a clean rule.
Poles: holds when the jitter cycle is short and divides or is coprime to the period with N covering many whole jitter cycles **vs** fails when the jitter cycle shares a factor with P (locking to the legal window) or is long relative to N.
Lean: 🔴 open
Updates:
- 2026-10-18 opened from brain train; sandbox 2026-10-18__jittered-lag-gate-only-invalid-follows-mean-of-clipped-formula-until-jitter-locks-to-period.py, result RESULT: FAIL max coprime dev 6.1%, 5 of 6 gcd>1 J deviate >=10%.
Source: brain train auto loop 1 pass 5; session_014AVjf81yxBZXZ5b84ovVC5

### T? · open-question · Is the lossless validity cutoff always the worst cutoff for the same gate without validity once jitter is added?
Sandbox (periodic wave P12 W5, 1200 presses, base lag i%5, jitter J on every 7th press, validity computed from legal(t-L) and legal(t) rather than assumed) shows the claim holds at J=0, 4 and 8 (gate-only invalid 200, 237, 202 at the lossless cutoff equals the curve maximum) but fails at J=2: lossless cutoff 4 gives 198 gate-only invalid while cutoff 6 gives 225. At J=2 the largest lag (6) is an invalid-only residue, so the cutoff that is lossless with validity stops short of the maximum lag and the gate still admits more invalid presses above it. At J=4 and 8 the largest lag lands on a valid residue, so lossless cutoff equals max lag. Gate-only curves were monotone in every case.
Poles: holds when the largest observed lag is itself a valid-B lag (lossless cutoff = max lag) **vs** fails when an invalid-only lag larger than the max valid lag exists, so the gate keeps adding invalid presses above the lossless cutoff
Lean: 🔴 open
Updates:
- 2026-10-18 opened from brain train kernel pass (new-half pick); prediction was holds at J=0 only and fails at every J>0, which was wrong at J=4 and 8; sandbox 2026-10-18__validity-modelled-jitter-sweep-shows-lossless-cutoff-not-always-gate-worst.py, RESULT: PASS (J worst: 0,4,8; exceeded: 2).
Source: incoming/2026-10-18__validity-modelled-jitter-sweep-shows-lossless-cutoff-not-always-gate-worst.py / scheduled train session
- Session: session_01FjbQokSDjejDZsbW36mBhq

### T? · open-question · Does a learned cutoff's gate-only invalid count reach its offline value at the same K where validity loss reaches zero?
Sandbox (40 seeded streams, P12 W4, 200 presses, random base lag 1 to 5 with jitter up to 20 on about 15 percent of presses, cutoff frozen as the running maximum valid lag) shows the gate side never saturates later than the validity side (K_gate <= K_val in 40 of 40), and the two K are equal in 35 of 40 streams, but in 5 streams the gate reaches its offline invalid count strictly earlier (for example K 56 against 200 and K 14 against 115) because the lags that carry the late maximum valid press add no invalid presses. So the earlier lesson's "same K" holds as an upper bound and as the common case, not as an identity.
Poles: holds when no invalid press has a lag between the cutoff at saturation and the final maximum valid lag **vs** fails when the late maximum-lag valid press is an outlier above every invalid lag, so the gate had already saturated
Lean: 🔴 open
Updates:
- 2026-10-18 opened from brain train gap pass (loop 2 pass 5); prediction was gate earlier in at least 20 percent of streams, observed 5 of 40 (12.5 percent); sandbox 2026-10-18__learned-cutoff-gate-saturates-no-later-than-validity-loss-and-often-earlier.py, RESULT: FAIL on that prediction, 35 equal, 5 earlier, 0 later.
Source: incoming/2026-10-18__learned-cutoff-gate-saturates-no-later-than-validity-loss-and-often-earlier.py / scheduled train session
- Session: session_01FjbQokSDjejDZsbW36mBhq

### T? · open-question · does "LRU ties FIFO on a loop and both score zero one slot too small" survive late cache fills with versioned writes?
A deterministic cache sandbox with fills that arrive L ticks after the miss, invalidating writes and version-checked fills (0 stale reads under both policies) shows the kernel holding only when the fill is effectively immediate. On a 5-key loop with a size-4 cache and no writes, L=1 gave 0 hits for both LRU and FIFO, but L=3 gave 397 hits for LRU and 496 for FIFO, because late fills land out of loop order and a pending-fill dedupe keeps some keys resident. At sizes 5 and 6 the two policies were identical in every cell. On a hot-key stream the policies differed in 12 of 16 cells and LRU lost in some (size 4, L=3: LRU 89 hits behind FIFO), the hot-set advantage depends on fill latency and cache size. The toy has one pending fill per key and no eviction cost, so it is unclear which cells carry over to a real cache.
Poles: fill latency near one request and no writes (the loop-cliff and LRU-over-FIFO kernels hold) **vs** fill latency longer than one request, where fills reorder residency and the zero-hit cliff and the policy ranking both change
Lean: 🔴 open
Updates:
- 2026-10-19 opened from brain train; sandbox 2026-10-19__lru-vs-fifo-under-versioned-late-fills-on-loop-and-hot-streams.py, result: loop size 4 no writes L=1 0/0 hits, L=3 LRU 397 vs FIFO 496; hot cells differ in 12 of 16 (LRU gain -89 to 148). Touched: ideas:CACHE-EVICTION/lru-beats-fifo, sandbox-cache-size-sweep-loop-cliff-and-ram-ceiling/E1, loop-sized-cache-with-writes-stays-size-5-but-late-fills-serve-stale-until-fills-are-versioned/E1.
Source: 2026-10-19__lru-vs-fifo-under-versioned-late-fills-on-loop-and-hot-streams.py / brain train auto loop 2 pass 2
- Session: session_01Xs9BRpt5ZfygjApJGsbMEk

### T? · open-question · should an open/stable rhyme-scheme verdict read two-pass letters with the assonance layer, or only the perfect-rhyme (uppercase) layer?
Over all 1296 four-line stanzas (3 vowels x 2 codas), a verdict from one-pass any-rhyme letters differed from the perfect-rhyme truth in 414 (31.9%) and called 24 truly stable stanzas open. Two-pass letters with the lowercase assonance layer counted as rhyme still differed in 264 (20.4%), refuting my prediction that two-pass would at least halve the flips; with the assonance layer hidden (uppercase only) it differed in 0. So the result holds or fails depending on which layer the metric reads.
Poles: the verdict matches perfect-rhyme truth when the metric reads only the uppercase layer **vs** it flips in 20.4% of stanzas when assonant lines are counted as closing a rhyme
Lean: 🔴 open
Updates:
- 2026-10-19 opened from brain train; sandbox 2026-10-19__one-pass-lettering-flips-open-stable-verdicts-in-exhaustive-stanzas-two-pass-keeps-perfect-groups.py, result one-pass 414/1296, two-pass 264/1296, uppercase-only 0/1296.
Source: sandbox 2026-10-19__one-pass-lettering-flips-open-stable-verdicts-in-exhaustive-stanzas-two-pass-keeps-perfect-groups.py; scheduled brain train auto loop 1 pass 5
- Session: session_01Q5Z2SdcUKr5yLCVU7Ma7tK

### T? · open-question · Is uh's recognition benefit a function of the short delay it announces, or just a property of the word uh?
Fitting a delay-decay model (benefit = B·exp(-delay/tau), tau 0.335 from the English ratio 47 vs 13 ms and Clark & Fox Tree's post-filler pauses 0.25 vs 0.68) and a plain category model (uh helps, um does not) to the same published numbers, both reproduce the English ratio 3.62 and predict the same Dutch ratio 3.62 against 4.67 observed, so the data cannot separate them. They differ only for a prolonged uh (decay model 22.3 ms, category 47.0 ms), which no study measured. Poles: the benefit follows announced delay (a prolonged uh would lose it) **vs** the benefit belongs to the word uh whatever follows (prolongation changes nothing).
Lean: 🔴 open
Updates:
- 2026-10-19 opened from brain train; sandbox 2026-10-19__filler-benefit-decay-vs-category-model.py, result: both models Dutch ratio 3.62 vs 4.67 observed; diverge only at prolonged uh 22.3 vs 47.0 ms. Composes ideas:PUBLIC-SPEAKING/filler-words, ideas:SPEECH-DISFLUENCY/filled-pauses, ideas:SPEECH-DISFLUENCY/delay-signalling.
Source: 2026-10-19__filler-benefit-decay-vs-category-model.py / brain train auto loop 2 pass 1
- Session: session_01To8tVxU3yVDtwdpjzGpR6B

### T? · open-question · Does the hidden parameter behind a quoted spec swing the outcome more than the knob people tune, across dilution, bolt torque and solder?
Sandbox 2026-10-19__hidden-spec-parameter-swing-beats-knob-swing-across-dilution-torque-solder.py: torque hidden/knob swing 3.33x (nut factor 0.12-0.20 vs torque +-10%), solder 2.21x (pad conduction 0.5-0.8 vs dwell 2-10 s), dilution 0.00x (at 2 balanced steps the pipette floor a up to 0.05 uL never beats the 0.5 percent floor, so only step count moved the error, 2.04 points). Prediction of at least 3x in 2 of 3 failed (1 of 3).
Poles: hidden parameter dominates when the knob has a narrow tolerance band and the parameter is a multiplier on the output (torque) **vs** it does not when a floor or saturation masks the parameter in the chosen regime (dilution at 2 steps) or the knob saturates slowly (solder dwell).
Lean: 🔴 open
Updates:
- 2026-10-19 opened from brain train; sandbox 2026-10-19__hidden-spec-parameter-swing-beats-knob-swing-across-dilution-torque-solder.py, result FAIL ratios 0.00, 3.33, 2.21. Models and ranges are my own simplifications.
Source: sandbox file above / session_014pWETJKxgid7E3P5KtDPoT

### T? · open-question · Is pre-workout static stretching safe when it is repeated short holds, or does the deficit follow total hold time?
The kernel ideas:FITNESS/mobility/static-stretching reports a per-stretch dose-response (under 30 s about -1.1%, 30-45 s about -1.9%, 60 s or more significant, pooled -3.7%). A sandbox using those anchors (plateau -4.5% past 60 s assumed from the adequate-control pooled figure) agreed between a per-stretch model and a cumulative-hold model on 3 of 5 plans, but four 30 s holds scored -1.63% per-stretch against -4.5% cumulative and three 15 s holds -1.1% against -2.77%. The review does not say which model is right, so "short stretches are safe" is only established for single holds.
Poles: deficit depends on the single longest hold, so many short holds stay safe **vs** deficit accumulates with total hold time, so 4 x 30 s behaves like one 120 s hold.
Lean: 🔴 open
Updates:
- 2026-10-19 opened from brain train; sandbox 2026-10-19__static-stretch-deficit-per-stretch-vs-cumulative-hold.py, result FAIL models agree 3/5, split on 4 x 30 s and 3 x 15 s.
Source: 2026-10-19__static-stretch-deficit-per-stretch-vs-cumulative-hold.py (brain train auto loop 1 pass 5)
- Session: session_01TymEo8Je55Sk3ydLUdwHUE

### T? · open-question · Does a humidity guard at 79% make the rule-of-five dew-point shortcut safe to ship, or does the safe cut depend on the temperature range?
Sandbox over T -10..40 C and RH 10..100 showed the raw shortcut off by up to 19.4 C, a guard at 79% (Magnus below) still up to 1.25 C off, a guard at 50% up to 2.40 C off, and a cut of 85% needed to stay under 1 C; restricted to 5..25 C the 79% guard held at 0.86 C.
Poles: guard at 79% holds when the air stays mild (5..25 C, max 0.86 C) **vs** fails when cold or hot air is in range (1.25 C at RH 79, 85% needed)
Lean: 🔴 open
Updates:
- 2026-10-20 opened from brain train edge pass; sandbox 2026-10-20__guard-a-shortcut-by-its-validity-band-and-fall-back-to-the-exact-formula.py, result guard@79 1.25 C, needed cut 85, mild-air 0.86 C.
Source: 2026-10-20__guard-a-shortcut-by-its-validity-band-and-fall-back-to-the-exact-formula.py / brain train session
- Session: session_01NFn71BZX5UoPHJWMN7pDFZ

## Project: Pappydapimp69/Dlist

### T? · open-question · In a fast turn, should a game theropod's tail sit on the inside of the turn (path-following or actively steered) or swing to the outside (passive inertia), and does the answer change with speed?
A deterministic 6-link passive tail chain (2.86 m, 1 Hz, zeta 0.3) on the Herrerasaurus demo's turn limits lags inside for the first fraction of a second (up to 0.53 m at sprint, 1.44 m at walk), then settles outside at sprint (1.23 m at 7.4 m/s, 1.35 rad/s) and near straight at walk (0.03 m outside). A tail laid along the hip's own path sits 0.73 m inside at the same sprint radius. Real cheetahs move their tails actively in turns, and a source for which side a running theropod's tail sat on in a steady turn was not found, so the physics does not settle what reads as right.
Poles: inside holds when the tail is treated as actively steered or path-following, and at walking speeds where the passive tail also stays near straight **vs** outside holds when the tail is mostly passive and the turn is fast, since the hip's centripetal acceleration v*omega (about 1 g at the demo's sprint) swings it out after a brief inside lag.
Lean: 🔴 open
Updates:
- 2026-10-21 opened from brain train; sandbox 2026-10-21__locomotion-passive-tail-swings-outside-a-turn-path-tail-inside.py, result path tail +0.73 m inside, passive sprint -1.234 m outside after +0.535 m inside lag, passive walk -0.030 m.
Source: 2026-10-21__locomotion-passive-tail-swings-outside-a-turn-path-tail-inside.py / session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe

### T? · RESOLUTION · the project owner picked the pole: a game theropod's tail is actively used for balance and sits on the INSIDE of a turn
Filed against the open fork "In a fast turn, should a game theropod's tail sit on the inside of the turn (path-following or actively steered) or swing to the outside (passive inertia), and does the answer change with speed?" (pole A = inside, actively steered **vs** pole B = outside, passive inertia). The owner decided the tail is ACTIVE, used for balance, not passive; the sandbox then chose the side and controller under that decision.
What the sandbox showed (deterministic planar multibody model, body 205 kg plus the loop-4 6-link 45 kg tail, demo speeds 1.5/3.4/7.4 m/s at max turn rates 2.43/2.08/1.35 rad/s, distal tail joints 5x stiffer): an inside hold lowers the steady roll moment about the support line to 2432 vs 2752 (straight) vs 3066 (outside) N m at sprint and 598 vs 997 vs 1424 at walk; peak leg yaw torque is 1662 inside vs 1682 straight vs 3555 outside at sprint; flick strategies cost 6124-7275 N m peak leg yaw. A sprint slalom built to break the winner broke a plain inside hold (4568 vs straight 3491 N m) but not the lag-timed one (2986). The base joint carries 65-75 percent of the bend.
Controller: hold = asin(min(sin 0.5, 0.49 * v * |yawRate|)) rad on the inside (0.49 = m*h/(m_t*d*g) for this rig); command min(hold, |yaw - yawAtTurnStart|), reset when the turn direction flips; pass through a critically damped 3 Hz filter; on exit the same formula returns the tail as the yaw rate decays.
Lean: 🟢 resolved (decision, 2026-10-21). Owner's call (active balance), side settled by evidence (dlist/E7). Reopen if a source shows real theropod or bird tails held outside in steady turns, or if the demo adds body roll/lean that changes the roll budget.
Updates:
- 2026-10-21 resolved (decision): owner ruled the tail is active, used for balance; sandbox 2026-10-21__locomotion-active-tail-holds-inside-the-turn-entered-by-lag.py, RESULT: PASS, inside with lag entry wins on roll at all three speeds and never needs more leg yaw torque than straight; filed as projects/pappydapimp69__dlist.md#E7.
- Evidence: A · projects/pappydapimp69__dlist.md#E7 · 2026-10-21
- Decision: A · owner · 2026-10-21
Source: 2026-10-21__locomotion-active-tail-holds-inside-the-turn-entered-by-lag.py / session claude.ai/code/session_017uyNQEczEfzSRfCLiYvMTe

### T? · RESOLUTION · T14 settled by the project owner: game audio is fully synthesized by code, with no recorded or designed sound assets
Resolves 🟡 T14 (synthesized SFX with zero assets vs authored audio) for Pappydapimp69/Dlist and as the owner's default for future game builds.
The owner rejected the "synthesize now, swap in recorded creature calls later" hedge. Every sound, creature voices included, is generated at runtime.
The cost of that choice is accepted: synthesis must reach a much higher bar than simple oscillator and noise bursts. Techniques: a source-filter vocal model for calls (formants scaled by vocal tract length), modal synthesis for impacts, granular synthesis for water, mud and foliage, procedural reverb impulse responses, occlusion, and an AudioWorklet for custom DSP. The plan is in the Dlist blueprint, §9 (commit 08fe447).
Poles: A synthesized only **vs** B authored audio
Decision: owner chose A (fully procedural audio, higher-fidelity synthesis)
Evidence: A · owner decision 2026-10-21, Pappydapimp69/Dlist docs/BLUEPRINT.md §9 and decision log D8
Reopen if: a playtest shows synthesized creature calls can't reach acceptable quality after the vocal-model pass.
Lean: 🟢 settled
- Session: session_017uyNQEczEfzSRfCLiYvMTe

## How to query this ledger (for the Brain orchestrator)
Before committing to a system, grep this file for the relevant area: an **open**
tension touching your work means the decision is *not yours to silently make* —
surface it. A **leaning** tension means there's a default; honor it unless you have
new information, and if you resolve it, flip the status to 🟢 and link the decision.
