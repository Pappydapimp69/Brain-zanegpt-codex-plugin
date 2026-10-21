# IDEA REPOSITORY — OPERATING SPEC

Canonical file: `idea-repository.md` (same folder). Git-tracked. Every change is a committed diff — that history is the source of truth for what the repository contains.

---

## ROLE

You manage an idea repository. Two modes, inferred from my message — don't ask which.

### FILING MODE (I'm dropping a fragment)
- Acknowledge in one line. Confirm the tag header is present; if missing, propose one.
- Do not expand, develop, or critique the fragment.
- Do not suggest next steps.

### MINING MODE (I bring a goal or near-finished idea)
- Treat it as the active task.
- Search stored fragments. Pull anything that connects — match domain and keywords first, but flag cross-domain hits too.
- For each pulled fragment, state in one line how it applies. Then help finish the goal.
- Surface non-obvious matches; that's the point of the repository.

### GENERAL
- Brief by default. No preamble.
- Architecture before implementation.
- Pushback expected and welcomed.
- If a message is ambiguous between modes, default to filing.

---

## WRITE DISCIPLINE (Claude Code specifics)

**`idea-repository.md` is steward-only. Never edit it directly, and never edit
`exploration.md` or this README's own domain list directly either — a mistaken
overwrite can wipe out the whole file.** Contributors write only to `incoming/`:

1. Copy the template:
   ```
   cp incoming/TEMPLATE.md incoming/<YYYY-MM-DD>__<slug>.md
   ```
2. Fill in one `## [DOMAIN / sub / kw / kw]` header + a 2-4 sentence
   self-contained body, passing the ARTIFACT and PORTABILITY tests. Reuse an
   existing domain from ESTABLISHED DOMAINS below where it genuinely fits —
   a genuinely new domain auto-promotes into its own block the same as any
   other (see the 2026-07-20 steward.py change), so add it to the
   ESTABLISHED DOMAINS list by hand afterward as a documentation update.
3. Dedup by KERNEL, not tag, against nearby entries yourself first (see
   DEDUP RULES below) — the steward's own token-overlap check is a safety
   net, not a substitute.
4. Validate:
   ```
   python3 scripts/validate.py
   ```
   It must pass.
5. Commit **only that one file** under `incoming/`. `scripts/steward.py`
   promotes it into the correct DOMAIN block (or holds it with reasons) on
   the next push to `main` — never hand-edit `idea-repository.md` yourself,
   even to "just slot one entry in."

This mirrors `memory`'s incoming/-gated steward model: only the automated
steward has write access to canon, so one contributor's mistake can hold a
single proposal, never take down the shared file.

---

## EXTRACTION PROMPT (deploy in external sessions)

> Extract fileable fragments from this chat transcript. Output only the IDEAS block. No preamble, no commentary on your process.
>
> ARTIFACT TEST: what would exist if this were made? If nothing, drop it.
> PORTABILITY TEST: could another creator build from this entry alone? If not, drop it.
> ACCEPT = an idea (a thing). REJECT = a method/process used to get there.
> CONSOLIDATION: if the same idea appears at multiple granularities, file once at the most portable level.
> DOMAIN TAGS: match an existing domain before coining a new one — RPG, NPC-SIM, NARRATIVE-DESIGN, WORLDBUILDING, SYSTEM, DATA-TOY, GARDEN.
> GUARD: file the kernel as it actually surfaced, not the model's expanded/reframed version. One idea = one entry; do not split a single idea into several because the model elaborated it.
>
> FORMAT:
> ## [DOMAIN / sub / kw / kw]
> \<2–4 sentence self-contained description\>

Note: extraction outputs the IDEAS stream **only** — never a MEMORIES block. Memories are relay plumbing, outside repository scope.

---

## DEDUP RULES (catalog comparison)

Run on every incoming batch before it lands in the file.

- **Kernel match, not tag match.** Strip each entry to its mechanism ("observation reshapes the observed"), then compare. Two entries can share a domain tag and be distinct; two can sit in different domains and be the same idea.
- **Flag collisions** (same kernel already filed → reject the duplicate) **and complementarity** (a new kernel fills a gap in a dormant entry → not a duplicate, a connection worth surfacing).
- **Over-capture is the primary failure mode.** A single source can yield 15+ spurious entries if the gates slip. If a batch is suspiciously large, tighten the gate, not the format.
- **Dormant entries usually stall for missing purpose, not weak idea.** A complementary new entry can be the unlock rather than a duplicate to reject.

---

## ESTABLISHED DOMAINS

RPG · NPC-SIM · NARRATIVE-DESIGN · WORLDBUILDING · SYSTEM · DATA-TOY · GARDEN · DISTRIBUTION · VOICE · DSP · MUSIC · ART · PROCGEN · PATHFINDING · SEARCH · MOTION · MONETIZATION · UI-UX · ECONOMY · NARRATION · SONGWRITING · UX · PITCH · PRESENTATION · MODDING · WRITING · ZEN · COUCH-MULTIPLAYER · NETWORKING · VFX · GEOMETRY · RESEARCH · TEXT · PHYSICS · LEVEL-DESIGN · SPEEDRUN · TYPOGRAPHY · SHADERS · CRYPTOGRAPHY · LOCALIZATION · TIMEKEEPING · GEOSPATIAL · REGEX · SAMPLING · NUMERICS · HASHING · SORTING · SERIALIZATION · COMPRESSION · REINFORCEMENT · RIGGING · SURVIVAL · CINEMATOGRAPHY · 3D-MODELING · STORYTELLING · PROMPT-ENGINEERING · REGRET · EMPATHY · PAINTING · SEO · SOCIAL-MARKETING · TIKTOK · TESTING · DEBUGGING · PERFORMANCE · ACCESSIBILITY · DATABASE-DESIGN · CONCURRENCY · API-DESIGN · SECURITY · VERSION-CONTROL · DOCUMENTATION · LEGAL · NEGOTIATION · PUBLIC-SPEAKING · TEACHING · PHOTOGRAPHY · COOKING · PERSONAL-FINANCE · TIME-MANAGEMENT · DECISION-MAKING · FITNESS · STATISTICS · MACHINE-LEARNING · SPEECH-DISFLUENCY · ORAL-STORYTELLING

Reuse one of these before coining a new domain where it genuinely fits. A
proposal's domain no longer has to match this list to promote (the steward
auto-promotes new domains the same way it never gated Tags against memory's
tag legend) — this list is descriptive, not a gate; update it here by hand
whenever a new domain earns a lasting name.

CINEMATOGRAPHY added 2026-07-31: film/video craft technique — lighting design
(three-point lighting's per-light function, key/fill ratio driving high-key vs
low-key), editing grammar (180-degree rule, Kuleshov effect), optics (deep vs
shallow focus, focal length + camera distance driving perceived depth
compression), camera movement connotation, standardized shot-size vocabulary,
color grading (teal/orange complementary contrast), and the master-shot-plus-
coverage production workflow — distinct from MOTION (general animation/motion
principles, not specifically film-camera craft) and MUSIC/SONGWRITING (audio,
not visual, craft) — seeded via `brain train new-domain cinematography`, 10
entries each verified against a real external source (ASC primary accounts,
Panavision, NFI, ACMI, Wikipedia citing named academic textbooks, StudioBinder,
PetaPixel) rather than by reasoning alone, per tension T22.

3D-MODELING added 2026-07-31: real-time/web 3D asset craft — interchange format
choice (glTF as the runtime-delivery "JPEG of 3D" vs. authoring formats like
FBX/OBJ), the high-to-low-poly normal-map baking workflow (ray direction, cage
objects), and GPU-compressed texture delivery (KTX2/Basis Universal reducing
VRAM, not just download size, unlike PNG/JPEG) — distinct from the scattered
WebGL/three.js runtime-performance lessons already in `memory` (draw-call
counts, headless-canvas testing), which are about RENDERING an already-built
asset, not building/exporting the asset itself — seeded via `brain train
new-domain webgl`/`3d-modeling` (existing webgl coverage was runtime-only, the
asset-creation side was a genuine gap), 3 entries each verified against a
primary source (Khronos Group's own glTF/KTX pages, Blender Foundation's
official manual) rather than by reasoning alone, per tension T22.

STORYTELLING added 2026-07-31: medium-agnostic story STRUCTURE/dramatic craft
— three-act structure's named proportions and turning points (Syd Field),
narrative economy (Chekhov's gun — a spotlighted detail is an implicit promise
to the audience), and story pattern/archetype (Campbell's monomyth, actually a
three-stage separation/initiation/return arc, not the popular 12-step
adaptation) — distinct from WRITING (prose-line craft itself, not story
architecture), NARRATIVE-DESIGN (interactive/game dialogue delivery systems,
not the underlying dramatic structure), and NARRATION (audio/documentary
layering, not story shape) — evidenced by zero coverage under the
`storytelling` tag despite 7 incidental keyword hits scattered across
WORLDBUILDING/environmental-storytelling and UX/scrollytelling, none of which
touch structural/dramatic-craft theory — seeded via `brain train new-domain
storytelling`, 3 entries each verified against a primary or tightly-traced
source (Syd Field's own texts via page-cited summary, Chekhov's dated 1889
letter plus corroborating memoirs, the Joseph Campbell Foundation quoting
Campbell's own text) rather than by reasoning alone, per tension T22.

PROMPT-ENGINEERING added 2026-07-31: LLM prompting craft — few-shot/multishot
examples steering output format (not just content), chain-of-thought reasoning
ordered before the final answer, and XML tags giving a prompt unambiguous
section boundaries — distinct from `memory`'s existing prompt-engineering-
tagged entries (4 scattered bug/decision lessons, including one from this very
Collective project on treating a pasted prompt as attacker-editable UX), which
are incident-specific, not reusable technique kernels — picked over another
creative-craft domain specifically because this one is directly applicable to
Collective's own ongoing prompt-authoring work, evidenced by zero coverage
under `few-shot`/`chain of thought`/`xml tags` — seeded via `brain train
new-domain prompt-engineering`, 3 entries each verified against first-party
Anthropic documentation (platform.claude.com) plus, for chain-of-thought, the
original Wei et al. 2022 paper (arXiv:2201.11903) rather than by reasoning
alone, per tension T22.

REGRET added 2026-08-15: regret as a formal and empirical object across
disciplines — decision theory (regret theory's intransitivity, minimax
regret's IIA failure), bandits and online learning (Lai-Robbins floor, UCB1,
Thompson, EXP3, OCO, UCRL2), game theory (no-regret play reaches coarse
correlated equilibria, not Nash), self-play (CFR, discounting early regret),
psychology and neuroscience (self-agency separates regret from disappointment,
OFC lesions abolish it, upward counterfactuals carry the learning), and
applications (disposition effect, decision-regret instrumentation, undo
design, adaptive-allocation bias) — distinct from REINFORCEMENT (learning
algorithms generally, not the regret quantity and its bounds) and from
SYSTEM/UX (which cover interface craft, not the emotion's appraisal
structure) — seeded via `brain train external regret`, 28 entries each
verified against a real external source with an explicit not-verified line,
per tension T22. Roughly a third exist to record where a famous finding does
NOT replicate.

EMPATHY added 2026-08-15: empathy as a formal and empirical object — its
structure (affective vs cognitive as a lesion-confirmed double dissociation),
its failure modes (empathic distress driving burnout, statistics suppressing
sympathy, compassion fading from one victim to two), its limits (perspective
TAKING does not improve accuracy; perspective GETTING does), its development
(the preschool false-belief shift), and its use in practice (empathy maps as
research artifacts, and the critique that simulation can widen the gap it
claims to close) — distinct from REGRET (a different emotion, though the same
evidence-quality discipline applies) and from UI-UX (interface craft, not the
appraisal structure underneath it) — seeded via `brain train empathy`, 10
entries each verified against a primary or peer-reviewed source with an
explicit not-verified line, per tension T22. Four entries exist mainly to
record that a famous finding does not survive replication or aggregation:
literary fiction and theory of mind (792-participant three-lab null), facial
feedback (17-lab replication at 0.03 units), perspective taking (d = -0.23
across 25 experiments), and empathy decline in medical training (16 of 30
studies disagree).

MODDING added 2026-07-18: extensibility architecture for third-party creators — data-driven mod-load lifecycle staging (separating prototype-definition from live-runtime execution so mods don't require engine recompilation), conflict-resolution design decisions when independent mods edit the same data (engine-enforced merge vs. community-tooling-resolved last-write-wins), and security/sandboxing concerns when a game executes untrusted player-authored code (a managed/memory-safe language is not automatically a sandbox) — distinct from SYSTEM (general meta-architecture and accessibility/interaction concerns, not third-party extensibility) and PROCGEN (the engine generating its own content algorithmically, not external creators injecting theirs) — evidenced by zero coverage of mod-loading architecture, UGC conflict resolution, or mod-security concerns anywhere in the repository across three independent query phrasings, seeded from real external research (Factorio's official Lua API docs, Skyrim/modding.wiki's plugin load-order mechanics, and a documented, exploited tModLoader sandbox-escape incident).

ZEN added 2026-07-18: applying koan logic/structure as a build-time or verification-time instrument — proxy-vs-true-cost gauges, and koan-design/verification methodology (judging manner not content) — distinct from WRITING (short-form prose craft itself, not using koan-structure as an engineering technique) — seeded via `brain train new-domain zen`, verified first-hand with a deterministic sandbox.

COUCH-MULTIPLAYER added 2026-07-18: local/shared-screen multiplayer design — join-flow and controller-assignment pitfalls, individually-addressable devices (phones) as private channels distinct from the shared screen, and scheduled disruption events that prevent silent role-lock — distinct from RPG/NPC-SIM (single-player systems) — evidenced by zero prior coverage of shared-screen-specific design concerns.

NETWORKING added 2026-07-20: real-time multiplayer netcode — client-side prediction, server reconciliation, input replay, lag compensation — distinct from COUCH-MULTIPLAYER (local/shared-screen design concerns, no network transport involved) — evidenced by zero coverage of client-prediction/reconciliation mechanics anywhere in the repository, directly informs this ecosystem's own open co-op architecture speculation (`exploration.md` Sp1), seeded from real external research (Gabriel Gambetta's client-side-prediction/server-reconciliation reference articles) and verified first-hand with a deterministic sandbox.

TEXT added 2026-07-20: correct handling of human-readable text as opposed to raw byte/code-unit strings — Unicode grapheme clusters vs code points vs UTF-16 code units (the three-different-lengths problem), grapheme-boundary-aware truncation, and normalization (NFC/NFD) before comparing/storing user input — distinct from VOICE (directing TTS output, not string-level correctness) and SEARCH (lexical retrieval, not encoding correctness) — evidenced by zero prior coverage of grapheme/code-point/normalization handling (the one "unicode" hit was a cross-platform CLI console lesson), seeded from real external research (MDN Intl.Segmenter, the Unicode equivalence standard, and independent grapheme-cluster/normalization writeups) and verified first-hand with a deterministic sandbox (exact observed lengths 11/7/1, naive-truncation corruption, and NFC-equality).

WRITING added 2026-07-20: prose/short-form craft (a koan, flash fiction, a parable) — technique for the writing itself, not narrative worldbuilding or interactive-dialogue systems — distinct from NARRATIVE-DESIGN (game/interactive narrative systems, not standalone prose craft) — evidenced by zero coverage of short-form prose technique anywhere in the repository, seeded from real external research (koan-structure sources, flash-fiction craft guides) applied first-hand across several koans and one short story.

PRESENTATION added 2026-07-16: structuring and delivering technical/explanatory content to an audience that already wants to understand, not persuading a skeptical one — zoom-level information layering (context before internals, C4-model style), progressive disclosure of secondary detail, audience-calibrated term definition (curse-of-knowledge correction), data-ink/chartjunk discipline for visual explanation, evidence-through-real-artifact over paraphrase, and connected-narrative prose over isolated bullet fragments — distinct from UI-UX (interactive screen/HUD/menu craft, not the structuring of an explanatory document or talk) and PITCH (persuading toward a specific ask/decision against real or anticipated resistance, not general audience-calibrated explanation of how a system already works) — evidenced by zero coverage of information-architecture, audience-calibration, or explanatory-structure technique anywhere in the repository despite UI-UX's adjacent interface-craft coverage never touching how explanatory content itself gets organized for a reader.

PITCH added 2026-07-16: constructing and delivering a persuasive product/technical pitch to a skeptical or undecided audience — narrative structure (leading with a named external change rather than the product, positioning the status quo itself as the real competitor), refutational objection-handling (naming the audience's likely skepticism and explicitly answering it, not just gesturing at it), credibility-through-specificity (concrete checkable mechanisms beating vague superlative claims), and adoption-friction framing for developer tools specifically (the real risk is "will anyone use it," not "does it work") — distinct from NARRATIVE-DESIGN (in-fiction story/character/plot construction, not real-world persuasive argument structure) and DISTRIBUTION (getting an already-finished work discovered by an audience, not persuading a specific audience once you already have their attention) — evidenced by zero coverage of pitch/persuasion structure, objection-handling, or credibility framing anywhere in the repository despite this saga now needing exactly this craft for a real pitch.

UX added 2026-07-16: interaction-design and preference-elicitation METHODOLOGY — techniques for structuring how a system asks or extracts a signal from a user (a recommender's onboarding flow, a preference quiz, a staged pick-and-cut) — distinct from UI-UX (visual interface/HUD/menu craft: what a screen shows and how it's laid out, not the elicitation technique used to gather the data driving it) — evidenced by zero coverage of elicitation/onboarding-flow design technique anywhere in the repository despite UI-UX's adjacent, extensive interface-craft coverage never touching how the underlying preference data itself gets collected. (Retroactively established for an entry already in the repository — see the note in WRITE DISCIPLINE: this is exactly the kind of judgment call the new incoming/ gate now routes to a human instead of leaving unresolved.)

SONGWRITING added 2026-07-15: writing and structuring lyrics for actual songs — prosody (unifying melody/rhyme/lyric around one emotional idea), rhyme-type and rhyme-scheme craft (how rhyme choice controls emotional resolution, not just sound), standard pop song structure and the bridge's structural job, melodic-hook-writing techniques, and AI-music-generation-tool prompting conventions (Suno's Custom Mode field split, Personas, negative prompting, and the unofficial-but-convergent bracket section-tag convention) — distinct from MUSIC (game-specific instrumental/adaptive-scoring composition craft, not lyric-writing, rhyme, or vocal song structure) and VOICE (directing TTS/spoken-word output, not sung lyrics or musical composition) — evidenced by zero coverage of lyric structure, rhyme/meter craft, hook-writing technique, or AI music-generation prompting anywhere in the repository.

NARRATION added 2026-07-13: audio-visual storytelling craft — layering sound design into distinct mood/tension/payoff roles (drone/riser/stinger) and the documentary-narration discipline of narrating only what the visual CAN'T already show, not restating it — distinct from VOICE (directing/producing TTS engine output at the SSML/markup level, not the narrative-pacing or sound-design layer above it) and MUSIC (composing musical themes/motifs, not narration restraint or non-musical sound-effect storytelling) and MOTION (the visual camera/layout/reveal-pacing engineering, not the audio or narrated-content layer riding on top of it) — evidenced by zero coverage of narration discipline or sound-design layering anywhere in the repository despite MOTION's extensive adjacent camera/pacing coverage never touching audio, and seeded by real external research plus a firsthand check against Brain's own cognitive-growth viz captions (which already follow the narrate-what-the-image-can't-show rule, unverified as a named principle until now).

ECONOMY added 2026-07-12: in-game currency/itemization/crafting systems as a designed economy — the faucets-and-sinks framework and its ~95-105% coverage target, rarity-tier itemization conventions, tiered crafting-cost curves, and hybrid random-rarity/deterministic-type loot distribution — distinct from RPG (which covers quest/progression/mechanic design broadly but has no economy-balancing or itemization-specific coverage) and MONETIZATION (real-money pricing/business model, not the in-fiction currency/item economy itself) — evidenced by zero coverage of faucets/sinks, rarity-tier conventions, or crafting-cost structure anywhere in the repository despite RPG's own adjacent quest/progression entries never touching item/currency balance.

UI-UX added 2026-07-12: game interface/HUD/menu craft — the diegetic/non-diegetic/spatial/meta taxonomy and when to use each, HUD information-minimalism and contextual fade, and controller-focus navigation conventions (consistency, global shortcuts, starting-position reachability) — distinct from SYSTEM (which covers accessibility-driven color/interaction concerns and general meta-architecture, not general interface craft for its own sake) and ART (visual/pixel-art craft, not information architecture or navigation) — evidenced by zero coverage of HUD, diegetic/non-diegetic framing, or focus-navigation conventions anywhere in the repository despite MOTION's adjacent camera/canvas coverage never addressing the UI-layer side of the same screens.

MONETIZATION added 2026-07-12: how a finished game actually earns money — pricing-model choice (premium vs. F2P vs. hybrid), pay-to-win vs. cosmetic-only ethics, virtual-currency psychology, and loot-box/gacha odds-disclosure law — distinct from DISTRIBUTION (getting a finished game discovered and played, not how it earns once played) — evidenced by zero coverage of pricing models, currency-obfuscation dark patterns, or disclosure requirements anywhere in the repository despite DISTRIBUTION's adjacent, extensive coverage of the "get discovered" half of the same business problem.

MOTION added 2026-07-12: the technical craft of procedural/generative animation and canvas visualization — camera framing and viewport-safety for dynamically-positioned content, collision-free radial/orbital layout algorithms, batch-reveal pacing, discrete growth-stage visual language, and using a project's own real data (e.g. git history) as generative-narrative input — distinct from ART (character/sprite-specific pixel-art and animation-craft, not general motion/camera/layout systems) and DATA-TOY (the conceptual framing of WHAT personal data to visualize and why, not the rendering/camera/layout craft of building the visualization itself) — evidenced by zero coverage of camera/viewport, procedural layout, or reveal-pacing techniques anywhere in the repository despite an existing "spatial stage" audio-camera kernel and multiple DATA-TOY chart entries never addressing the visual-system side, and seeded by a real, verified generative-visualization build (Brain's own cognitive-growth spiral-galaxy viz) rather than pure external research alone.

SEARCH added 2026-07-11: building search/retrieval systems (inverted indexes, ranking algorithms, vector/semantic search, query understanding) — distinct from DISTRIBUTION (getting a page indexed BY an external search engine like Google, not building one) and NPC-SIM's unrelated "relevance" scoring for game-NPC memory retrieval — evidenced by zero coverage of core IR concepts (inverted index, TF-IDF/BM25, embeddings/ANN, learning-to-rank) anywhere in the repository.

PATHFINDING added 2026-07-11: grid/graph pathfinding algorithms themselves (A*/Dijkstra correctness, heuristic admissibility, diagonal-movement cost conventions, per-agent vs. shared flow-field tradeoffs at scale) — distinct from NPC-SIM's decision-making architectures (utility AI/GOAP/behavior trees, which decide WHAT an NPC does, not HOW it physically gets somewhere) and PROCGEN (which generates the space being pathed over, not the path through it) — evidenced by zero coverage anywhere despite this saga's own shipped pursuit-enemy AI (the-recursion's "hunter"), and seeded by real sandbox builds matching the PROCGEN/sandbox-maze precedent.

PROCGEN added 2026-07-11: the generative ALGORITHMS themselves (cellular automata, wave function collapse, L-systems, noise-based generation) — distinct from SYSTEM's procgen-qa (testing/verifying a generator's output) and ART's procgen-sprites (a specific downstream application to pixel-art sprites) — evidenced by zero coverage of these named algorithms anywhere in the repository despite this saga's own recurring procedural-map build stages, and seeded by real sandbox builds (not just external research) matching this repo's own `sandbox-maze`/`sandbox-scatter`/`sandbox-collision` precedent for hands-on-verified algorithm lessons.

ART added 2026-07-11: visual craft for 2D/pixel-art games — pixel-art fundamentals (readability, shading, palette technique), sprite animation principles, and procedural/algorithmic sprite generation — distinct from SYSTEM (which covers accessibility/UI-driven color and interaction concerns, not visual craft for its own sake) — evidenced by this saga's own recurring "procedural sprites" build stage across all 5 games having no visual-craft knowledge to draw on, only accessibility-driven palette kernels (mirrors why MUSIC was split from DSP).

MUSIC added 2026-07-11: composing and structuring game music as a craft — thematic/motivic material (leitmotif), adaptive/dynamic scoring systems that react to gameplay state, and channel-constrained composition conventions (chiptune/retro) — distinct from DSP (low-level signal-correctness of synthesis/audio pipelines, not what notes/themes to write) and VOICE (directing spoken-word/TTS output, not instrumental composition) — evidenced by this saga's own recurring "procedural audio" build stage across all 5 games (ambience + SFX generated at runtime) having no composition-craft knowledge to draw on, only signal-processing correctness kernels.

DISTRIBUTION added 2026-07-11: getting an already-finished creative work actually discovered and played (platform/venue norms, listing-page conversion, cross-promotion) — distinct from every other domain, which is about building the thing, not getting it in front of anyone.

VOICE added 2026-07-11: directing and producing text-to-speech/synthesized-voice output (SSML and engine-specific markup, multi-voice script structuring, bulk-production workflows, consistent style/emotion across a long document) — evidenced by two real projects (pocketzane, warden-fables) whose lessons were scattered under memory's `[tts][ssml][elevenlabs]` pitfall tags with no corresponding ideas domain to hold the portable craft/technique kernels (as opposed to project-specific bug fixes).

DSP added 2026-07-11: low-level digital-signal-processing correctness for synthesized audio (synthesis-algorithm stability, FFT/resampling numeric correctness, noise-generator period verification) — distinct from VOICE (which covers directing/producing speech output at the API/markup level, not the sample-level math underneath) — evidenced by three real sandbox projects (sandbox-genesis-fm, sandbox-genesis-mix, sandbox-genesis-psg) whose memory lessons were bug-fix-specific with no corresponding ideas domain to hold the portable DSP craft/technique kernels behind them.

RIGGING added 2026-07-26: constructing a character's deformation system itself — skinning method choice (linear blend vs dual-quaternion/rotation-blend) and its volume-preservation trade-offs at twist joints, and bone-hierarchy structuring (twist bones, corrective joints) — distinct from MOTION (authoring/blending motion ON an already-built rig, e.g. camera paths and joint-rotation blending, not building the rig's deformation structure) and ART (visual craft/principles, not the underlying deformation math) — evidenced by zero coverage of skinning methods, the candy-wrapper/bulging artifact trade-off, or bone-hierarchy technique anywhere in the repository across eight independent query phrasings (rigging, weight paint, bone hierarchy, skinning, linear blend skinning, candy wrapper, vertex weight, auto rig), seeded from real external research (Kavan et al. on dual quaternion skinning; the SIGGRAPH 2014 "Skinning: Real-time Shape Deformation" course) and verified first-hand with a deterministic sandbox (exact cos(theta/2) volume-collapse measurement for LBS vs exact preservation for rotation-blend, at 7 twist angles).

SURVIVAL added 2026-07-26: survival-game design specifically — needs-meter/decay-model design (hunger/thirst/warmth and what their decay basis does to playstyle), scarcity and shelter/exposure pressure, and permadeath-adjacent stakes — distinct from ECONOMY (currency faucets/sinks and crafting-cost curves, which is resource FLOW rather than the bodily-need pressure loop) and RPG (character progression and party systems, not moment-to-moment subsistence) — evidenced by zero coverage across ten independent query phrasings (survival, crafting, hunger, inventory, crafting recipe, resource gathering, tech tree, durability, base building, farming), whose only real adjacent hit was one ECONOMY crafting-fee-scaling kernel, seeded from real external research (PC Gamer's hunger/thirst design critique; RetroStyleGames survival-systems practitioner writeup) and verified first-hand with a deterministic sandbox (measured 5.0x exploratory-playstyle food penalty under wall-clock decay vs 1.0x under per-action decay, and the hybrid weighting that bounds it under 2x without making idling free).

---

## EXPLORATION SECTION (`exploration.md`)

As of Phase 1 the frozen `creativity` node lives inside this repo as
[`exploration.md`](exploration.md) — the home for residue the artifact test
rejects but the system must not lose: experiments, syntheses staged against a
goal, and speculations.

- **Sorting rule (objective):** artifact test passes → kernel → `idea-repository.md`.
  Fails → residue → `exploration.md`, typed (`experiment`/`synthesis`/`speculation`)
  and stated (`live`/`promoted`/`spent`).
- **Parked alternatives are NOT residue** — a road not taken, kept with its
  reason, is fork-shaped and belongs in the `tension` ledger (type `alternative`).
- **Graduation:** when a live entry proves out, file its kernel here via FILING
  MODE (kernel-dedup applies) and flip the entry to `promoted → <where>` in the
  same commit. Entries are never deleted.
- Mining mode covers both files: kernels from the repository, plus live
  explorations worth resurfacing.
