# local/sandbox-savemigrate — lessons

Project: local/sandbox-savemigrate. Newest first.

---

## E3 — sandbox15 undefined dropped on serialize
- Date: 2026-07-11
- Project: local/sandbox-savemigrate
- Tags: [state][testing]
- What: A migration step merging separate `x`,`y` fields into `position:
  {x, y}` was fed a save that only ever had `x` (no `y` at all). The
  resulting in-memory object is `{x: 7, y: undefined}` — `'y' in position`
  is `true`, the field looks present under every in-memory check. But
  `JSON.stringify({x: 7, y: undefined})` produces `{"x":7}` — the `y` key
  is silently gone the moment the save is actually persisted, even though
  nothing about inspecting the live object would show that.
- Why built: The merge step (`position: {x: save.x, y: save.y}`) is the
  obvious direct translation of "combine these two fields" and is correct
  for every save that actually has both `x` and `y` — which is what got
  tested first.
- Design: Deliberately fed the merge step a save missing `y`, then checked
  correctness two ways: inspecting the in-memory migrated object directly,
  and round-tripping it through `JSON.stringify`/`JSON.parse` (the actual
  persistence path a real save system would use) and inspecting that.
- Got right: The in-memory check alone would have passed — `position.x ===
  7` and `'y' in position` are both true right after migration, so a test
  that only asserts against the live JS object in the same process gives
  no signal that anything is wrong.
- Where/why it failed: JavaScript's `undefined`-as-a-value and
  key-genuinely-absent are different states in memory (`'y' in obj` tells
  them apart) but collapse into the same thing — key absent — under
  `JSON.stringify`, which drops any key whose value is `undefined`. A
  migration's correctness was validated against the wrong representation:
  the in-memory object, not the format the save actually round-trips
  through. The gap is invisible until the save is written to disk/storage
  and read back, at which point the key is just gone, no error anywhere in
  between.
- Fix: Build `position` by conditionally assigning only the keys that
  actually exist on the source object, rather than always including both
  `x` and `y` unconditionally — so a genuinely missing source field stays
  visibly missing (or gets an explicit default) instead of becoming a
  present-in-memory-but-vanishes-on-save `undefined`.
- Why this fix: It makes the migrated object's shape match what will
  actually survive serialization, closing the gap between "looks correct
  in this process" and "is correct once persisted" — the two stop being
  different questions.
- Rule of thumb: Never validate a data-migration/transform step by
  inspecting the in-memory JS object alone when the real destination is a
  serialized format (JSON, or anything else with its own undefined/missing
  semantics) — always round-trip through the ACTUAL persistence
  format (stringify/parse, or the real save/load path) before asserting
  correctness. `undefined`-vs-absent-key is invisible in memory and only
  manifests at the serialization boundary; a test suite that never crosses
  that boundary can pass forever while silently losing data on every real
  save.
- Provenance (verified/assumed): Verified first-hand — printed the
  in-memory migrated object (`{x:7, y:undefined}`, `'y' in position` →
  `true`) alongside its actual `JSON.stringify` output (`{"x":7}`) from the
  same run, confirming the discrepancy directly; confirmed the fix closes
  the gap under the same round-trip check.
- Link: session (dog-game-continue-oc3xqh); sandbox-15-savemigrate/pass4.js
  (Test G, `position` merge step).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-movement-stack.md#E2 · compatible · no sandbox · session (query brain for "brain analyze groups and train on edges"), sandbox script sweep.mjs/sweep_fixed.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-replan-save.md#E1 · compatible · no sandbox · this session's sandbox (sbR.py); source entries sandbox-astar-replan#E1, sandbox-combined-game-loop#E2, sandbox-savemigrate#E3.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-replan-save.md#E2 · compatible · no sandbox · session 01KxkbJUq8YajH8GokSZYYHy; `brain analyze graph` untested seam (sandbox-combined-replan-save + sandbox-savemigrate); sandbox `engine.mjs`, scratchpad `loop5-frontier-undefined-drop/` (run twice as separate process invocations, outputs diffed byte-identical)
- Cited-by: 2026-08-10 · projects/pappydapimp69__august-10.md#E2 · compatible · no sandbox · August-10 gossip/canon.py field()
- Audited: 2026-10-14 · pass · The entry has no stored sandbox, but its claim is about the real JSON.stringify of a real object, not a hand model, and I re-ran it in Node: {x:7,y:undefined} gives 'y' in obj true and JSON.stringify output {"x":7}, so the key vanishes on persistence while in-memory checks pass. The answer is computed by the runtime, not assumed. The Rule of thumb's wider scope (any serialized format) is only backed for JSON; I also saw that arrays turn undefined into null and NaN into null, which supports the general point that the persistence boundary changes values. The claim is supported at the scope tested and the extension to other formats is an unverified generalisation. · scheduled brain train auto loop 1 pass 3, audit of savemigrate E3; session_01EU6f7a12wCvzUSXEbn87pv
- Reverified: 2026-10-14 · pass · sandboxes/2026-10-14__rebuild-json-undefined-key-vanishes-at-serialization.py · observed RESULT: PASS onlyX inMem y=True but roundtrip has y=False; null kept, NaN->null, array undefined->null · Built my own fixture before reading the entry's design: four saves (only x, both, y null, y NaN) through a position-merge migration, driven through real Node JSON stringify and parse from a Python harness. The claim reproduced: with only x, the in-memory position has the y key present yet the round-trip drops it. My fixtures went further than the claim in three places, all consistent with it: an explicit null survives, NaN becomes null (a type change), and undefined inside an array becomes null instead of being dropped. The entry's own sandbox is not stored in sandboxes/, so the difference in fixture could only be judged from its Design text: it used one case, the missing y, while mine added the null, NaN and array cases and ran the real engine rather than a model. · scheduled brain train auto loop 1 pass 4; session_01BwMXpnGN7oKqipFnskBS6R

## E2 — sandbox15 migration idempotency structural reshape
- Date: 2026-07-11
- Project: local/sandbox-savemigrate
- Tags: [algorithm][state][testing]
- What: A single-step schema migrator that reshapes data structurally
  (`migrate_v2_to_v3`: flat `inventory: [string]` → `inventory: [{id, qty}]`)
  was written unconditionally — `inventory.map(item => ({id: item, qty: 1}))`
  — with no check of the input's existing shape. Running it once on a raw
  v2 save is correct. Running it a second time on its own output (a real
  scenario: a retried migration, a save re-processed after a crash, a patch
  re-applied) silently double-wraps every item: `{id:"torch",qty:1}` becomes
  `{id:{id:"torch",qty:1},qty:1}`.
- Why built: `migrateToLatest` chains single-step migrators by version
  number, so `migrate_v2_to_v3` only needed to handle "a v2 save" as input —
  nothing in the migration's own contract flagged that it might see its own
  output again.
- Design: Built a v1→v2→v3 chain (v1→v2 = field rename + default; v2→v3 =
  structural reshape) plus a version-dispatching `migrateToLatest`. Tested
  idempotency directly by calling `migrate_v2_to_v3` twice in a row on the
  same object and diffing the result against a single call.
- Got right: The v1→v2 rename migrator (`{playerName, ...rest} → {name:
  playerName, ...rest}`, plus a `gold: 0` default) needed no such guard and
  never broke under the same double-call test — renaming/adding a field is
  naturally idempotent (applying it twice yields the same output as once,
  since there's no prior-output shape to mistake for prior-input shape).
  The defensiveness gap is specific to structural reshapes, not migrations
  in general — a useful split for scoping review effort: audit reshape
  steps for idempotency, renames don't need it.
- Where/why it failed: Nothing in the dispatcher or the migrator's own code
  distinguishes "this is a raw v2 save" from "this is already-migrated v3
  data mislabeled/reprocessed as v2" — both are plain objects with an
  `inventory` array, and a reshape transform applied to already-reshaped
  data produces another syntactically valid (but semantically corrupt)
  object, so nothing crashes or errors. It only surfaces if you explicitly
  test double-application, which nothing about writing or running the
  migration once would prompt.
- Fix: Guard the reshape on the item's actual current shape before
  transforming: `item && typeof item === 'object' && 'id' in item ? item :
  {id: item, qty: 1}`. Re-running the migrator on already-v3-shaped
  inventory is now a no-op instead of a second wrap.
- Why this fix: The reshape's real invariant isn't "input is a v2 save" —
  it's "every item ends up in `{id,qty}` shape." Checking the item's actual
  shape makes the transform match that invariant directly (idempotent by
  construction) instead of relying on an assumption about which version the
  caller claims to be passing in.
- Rule of thumb: A migration step that RENAMES or ADDS fields is idempotent
  for free — there's no prior-shape ambiguity to get wrong. A migration
  step that RESHAPES structure (flat → nested, string → object, one field →
  split into several) is NOT automatically idempotent and needs an explicit
  "is this already in the target shape" check, because reprocessing its own
  output is syntactically indistinguishable from processing fresh input of
  the shape it expects. Test every structural migrator by calling it twice
  in a row on the same object before trusting it in a pipeline that could
  ever retry, resume, or re-apply a step.
- Provenance (verified/assumed): Verified first-hand — built and ran a
  working v1→v2→v3 migration chain in Node.js; confirmed the double-wrap
  bug by printing actual before/after JSON (`after 1 call:
  [{"id":"torch","qty":1},...]` vs `after 2 calls:
  [{"id":{"id":"torch","qty":1},"qty":1},...]`); confirmed the fix resolves
  it and confirmed the v1→v2 rename migrator has no equivalent issue under
  the same double-call test.
- Link: session (dog-game-continue-oc3xqh); sandbox-15-savemigrate/pass3.js,
  pass4.js (`migrate_v2_to_v3`).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-bloom-audio.md#E6 · compatible · no sandbox · session (query brain for "loop: aim, compose from recorded lessons, sandbox, file" — loop 2), sandbox script reverify2_bloom_savemigrate.mjs, no code change to a shipping project

## E1 — sandbox15 migration dispatcher version comparison
- Date: 2026-07-11
- Project: local/sandbox-savemigrate
- Tags: [algorithm][state]
- What: A `migrateToLatest(save)` dispatcher decided whether to keep
  migrating with a single comparison: `while (save.version <
  LATEST_VERSION) { ... }`. In JavaScript, `undefined < 3` and `99 < 3` both
  evaluate to `false`, so a save with a missing `version` field, or a
  `version` from a newer app than this code knows about, both fall straight
  through the loop untouched and get returned as-is — no migration applied,
  no error, no warning. The save just silently keeps whatever (possibly
  very old, possibly incompatible) shape it walked in with.
- Why built: `<` reads as the natural, minimal check for "still behind
  latest, keep migrating" — it's correct for the one case it was tested
  against (a valid old version), and nothing about that case reveals it's
  wrong for the other two.
- Design: Tested the dispatcher against three distinct save states: a save
  already at latest version (should no-op), a save with no `version` field
  at all, and a save claiming `version: 99` (newer than any migrator this
  code has).
- Got right: The "already at latest" case worked correctly by the same `<`
  check (`3 < 3` is `false`, loop doesn't run) — the bug isn't in that case,
  it's specifically that the same operator conflates "not yet migrated"
  with "invalid/unknown" and "from the future," when those are three
  logically distinct situations that call for three different responses
  (migrate, reject, reject).
- Where/why it failed: "Not yet at latest" is not the logical complement of
  "already at latest" once the input can be malformed — `<` only correctly
  distinguishes those two when `version` is guaranteed to be a valid
  integer somewhere in the known range. A single relational operator can't
  express "valid-and-behind" vs "invalid" vs "valid-and-ahead" as three
  outcomes; it silently folds the latter two into "false," which this
  dispatcher treats identically to "already done."
- Fix: Replace the bare `<` loop guard with explicit checks before
  migrating: throw if `version` isn't a recognized number, return as-is
  only on exact equality to latest, throw if `version > LATEST_VERSION`
  ("save is from a newer version of this app than this migrator knows"),
  and only then loop while `<`.
- Why this fix: It makes the three cases the code actually needs to
  distinguish syntactically distinct in the code, instead of relying on one
  comparison operator's incidental behavior on out-of-range/non-numeric
  inputs to (mis)represent two of the three.
- Rule of thumb: When a dispatcher's only signal for "is there work to do"
  is a single relational comparison against a boundary value, check what
  that comparison actually evaluates to for EVERY input outside the
  expected valid range (missing, wrong type, above the max) — not just the
  two cases (behind, at-target) the happy path was designed around. If any
  out-of-range input silently reads as "already done" instead of "invalid,"
  the dispatcher will pass corrupted or unmigrated data through as if
  nothing were wrong, with no error to catch it downstream.
- Provenance (verified/assumed): Verified first-hand — ran the dispatcher
  against `{}` (no version field) and `{version: 99, ...}` and confirmed
  both round-tripped through `migrateToLatest` completely unchanged instead
  of being rejected; confirmed the fix throws clearly on both cases while
  leaving the at-latest no-op and normal migration paths unaffected.
- Link: session (dog-game-continue-oc3xqh); sandbox-15-savemigrate/pass3.js
  (`migrateToLatest`).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-bloom-audio.md#E1 · compatible · no sandbox · session (query brain for "train yourself on that file and connected blobs, query and analyze brain, train on groups and edges, 5 loops" — loop 1/5), sandbox script loop1_bloom_save.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-bloom-audio.md#E6 · compatible · no sandbox · session (query brain for "loop: aim, compose from recorded lessons, sandbox, file" — loop 2), sandbox script reverify2_bloom_savemigrate.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-rpg-progression.md#E6 · compatible · no sandbox · session (query brain for "stress test mega group in a sandbox environment"), sandbox script stress.mjs, no code change to a shipping project
