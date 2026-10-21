# local/sandbox-combined-save-system — lessons

Project: local/sandbox-combined-save-system. Newest first.

---

## E2 — combined persisted reference into versioned space
- Date: 2026-07-11
- Project: local/sandbox-combined-save-system
- Tags: [state][architecture][testing]
- What: A save (or any persisted state) that stores a REFERENCE into a
  space that can later be reshaped — a definition id, a quest-stage enum
  value, a cutscene program-counter, a dialogue-node index — silently
  repoints to the WRONG target the moment a migration inserts, reorders, or
  renames within that space, unless the migration explicitly remaps the
  stored references. Found stacking three save kernels each verified in
  isolation (reference-by-id, quest-as-stage-id, cutscene-serializable-PC);
  they turned out to be one bug in three costumes.
- Why built: A combined/integration sandbox — one RPG save/load/migration
  system stacking 8 persistence kernels (reference-by-id, migration
  idempotency, three-way version dispatch, undefined-on-serialize,
  quest-as-state-machine, cutscene-serializable, replay-fingerprint,
  canonical-tie-key) — to test whether the kernels compose.
- Design: Saves reference shared definitions by id and store quest stage
  ids and a cutscene PC; migrations reshape those spaces (rename a
  definition, insert an enum stage, insert a cutscene op).
- Got right: Each rule was correct in isolation; the failures are purely at
  the seam where a migration reshapes a space something else persisted a
  reference into.
- Where/why it failed: The stored reference and the space it points into
  drift apart on reshape. The decisive distinction is the FAILURE MODE: a
  SYMBOLIC/named reference (a string id) fails LOUD — a rename leaves a
  detectable dangling/missing sentinel; an ORDINAL/POSITIONAL reference (a
  raw integer index) fails SILENT — an insert shifts every id so the stored
  value resolves to a real-but-WRONG target with no error (stage 2 "fight"
  now reads as "sneak"; a mid-cutscene PC 2 now points at an inserted op and
  re-runs a beat). Silent-wrong is far more dangerous than loud-missing.
- Fix: (a) Prefer stable SYMBOLIC ids over ordinals in anything you persist,
  because silent-wrong is worse than loud-missing. (b) Any reshape of a
  referenced/indexed space must apply an explicit old→new VALUE MAP to every
  stored reference (a reference-remap pass). (c) That remap is itself a
  structural reshape, so guard it with an idempotency/version stamp, or a
  re-run double-shifts the value (2→3→4).
- Why this fix: A persisted reference is only valid relative to the version
  of the space it indexes; changing the space without remapping the stored
  references breaks that relationship silently for ordinals. An explicit
  value map re-establishes it, and the idempotency guard keeps the remap
  from compounding on re-run.
- Rule of thumb: Any save/persisted state that stores a reference into a
  reshapeable space (definition id, enum stage, program counter, node
  index, schema slot) must be remapped by an explicit old→new map when a
  migration reshapes that space — and ORDINAL/positional references fail
  SILENTLY (valid-but-wrong) while SYMBOLIC ids fail LOUDLY (detectable
  dangling), so persist stable symbolic ids, not positions. Guard the remap
  with an idempotency stamp so re-running a migration can't double-shift.
  Each such reference kernel looks correct alone because nothing reshaped
  its space in its own test.
- Provenance (verified/assumed): Verified first-hand this session in a
  combined save-migration sandbox and confirmed by an independent
  adversarial re-run: renaming a definition id left the save's reference
  `{__dangling:true}` (player entity lost) until a remap pass; inserting an
  enum stage silently made stored id 2 read as the wrong stage; an unguarded
  value-migration double-shifted 2→3→4 (the guard confirmed load-bearing via
  a forced-guard probe, since normal re-runs short-circuit on the version
  stamp); inserting a cutscene op repointed a mid-scene PC and re-ran a beat.
- Link: session (dog-game-continue-oc3xqh); combined sandbox
  combined-save-system. Kernel filed in ideas `idea-repository.md`
  (SYSTEM/data-model/a-persisted-reference-into-a-versioned-space-must-be-remapped-on-reshape).
- Cited-by: 2026-07-26 · projects/local__sandbox-combined-cutscene-resume.md#E1 · compatible · no sandbox · this session; sandbox scripts compose_cutscene_save.js and compose_testd_v2.js (scratchpad, not committed)
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-the-answering-deep.md#E13 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), sandbox scripts rng-ordinal-vs-symbolic.js and scan.js, no code change to a shipping project

## E1 — combined content versioned saves reconcile freshness and replay
- Date: 2026-07-11
- Project: local/sandbox-combined-save-system
- Tags: [architecture][determinism][state]
- What: "A save references its definitions live by id so it picks up content
  patches" (freshness) and "a replay must reproduce a bit-identical
  fingerprint" (determinism) look like an irreducible conflict — patch a
  referenced definition between record and replay and the replay diverges.
  They are NOT irreducible: content-versioned saves reconcile both with one
  rule. (Notably, the first pass of this combined test declared the conflict
  "fundamental / resolve per-use"; the adversarial re-verification found the
  cleaner single-rule reconciliation — a case of the verify pass improving
  the finding, not just confirming it.)
- Why built: A combined save/load/migration sandbox stacking a
  reference-by-id save representation with a replay-fingerprint determinism
  guard, to see whether the two kernels can coexist.
- Design: Entities resolve their definition live by id (so patches flow into
  old saves); a separate replay system re-runs from seed+input and hashes
  canonical state into a fingerprint that must match.
- Got right: Both kernels are individually correct and desirable — the
  tension is real, they optimize opposite things (live freshness vs
  bit-identical reproducibility).
- Where/why it failed: Under naive live reference, buffing a definition's
  damage between save and load changed the referenced content, so the
  replayed run diverged and the fingerprint flipped
  (`523f1b1b` → `36d8c2e6`, `playerHp 15 → 0`). Referencing-at-latest
  everywhere loses determinism; snapshotting content into every save loses
  freshness and duplicates content per save. Neither pole satisfies both.
- Fix: Make CONTENT an immutable, versioned store addressable by revision,
  advance a HEAD pointer on each patch, and stamp every save with the
  `contentVersion` it was recorded against. One reference mechanism, one
  rule: a REPLAY resolves content pinned to `save.contentVersion`
  (bit-identical), while normal PLAY resolves at HEAD (fresh). Same save can
  produce a faithful replay (pin) or a what-if-at-latest run (HEAD) with
  zero code change.
- Why this fix: The reproducible path (replay) by definition must use the
  content it was recorded against; binding it to a pinned revision and
  leaving live play at HEAD satisfies both goals from one shared immutable
  substrate, instead of copying that substrate into every save. It
  dominates both naive poles and localizes the choice to one principled
  boundary rather than a per-read-site policy.
- Rule of thumb: When live-freshness and reproducibility both matter for the
  same referenced data (reference-by-id saves vs replay/lockstep
  determinism; live config vs deterministic re-run; event-sourcing with
  evolving rules), don't choose one globally and don't snapshot the
  substrate into every record — VERSION the shared substrate (immutable,
  revision-addressed, a HEAD pointer) and stamp each record with the
  revision it was made against, so the reproducible path pins its revision
  while live use tracks HEAD. The only true residual is definitional: one
  replay can't be both faithful to the original AND reflect newer patches —
  but that's resolved at one boundary, not scattered per use.
- Provenance (verified/assumed): Verified first-hand this session — a
  patched definition flipped the replay fingerprint under live reference
  (reproduced), and a content-versioned save reproduced the original
  fingerprint on replay (`@pinned=1` → `523f1b1b`, match) while live play
  still saw the patch (`@HEAD=2` → damage 8); confirmed by an independent
  adversarial re-run that built the content-versioned reconciliation and
  showed both saves sharing one pinned revision with no per-save content
  copy.
- Link: session (dog-game-continue-oc3xqh); combined sandbox
  combined-save-system. Kernel filed in ideas `idea-repository.md`
  (SYSTEM/architecture/content-versioned-saves-reconcile-freshness-with-replay-determinism).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E6 · compatible · no sandbox · session (query brain for "train seams combination 3 sandboxes 5 loops" — loop 4/5), sandbox script loop4_savesystem.mjs, no code change to a shipping project
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-architecture.md#E2 · compatible · sandboxes/2026-09-28__train-gap-b05.py · session 2026-09-28, brain train gap batch 5 loop 22
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-wrong-sky.md#E18 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 2), sandbox script verify_content_freshness.mjs (live import of real repo source, real localStorage shim), architectural gap flagged, not applied
