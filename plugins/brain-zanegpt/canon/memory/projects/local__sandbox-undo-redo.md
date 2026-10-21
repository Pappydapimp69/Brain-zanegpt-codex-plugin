# local/sandbox-undo-redo — lessons

Project: local/sandbox-undo-redo. Newest first.

---

## E5 — sandbox undo redo invalidation on new edit
- Date: 2026-07-11
- Project: local/sandbox-undo-redo
- Tags: [state][editor][testing]
- What: In a linear undo/redo system, making a NEW edit after one or more
  undos branches the timeline — the old redo "future" is now unreachable
  and must be discarded the instant the new edit commits. If the do/commit
  path does not clear the redo stack, `redo()` later replays a stale command
  against a document that has since diverged, silently corrupting it.
- Why built: An editor undo/redo core (do → push undo + clear redo; undo →
  move to redo; redo → move back), stress-tested with interleaved
  do/undo/redo sequences.
- Design: Undo and redo stacks of command objects; `do()` applies a command,
  pushes it to undo, and (correctly) clears redo; undo/redo move commands
  between the stacks and apply the inverse/forward.
- Got right: The stack mechanics and the inverse application were correct;
  the bug is solely the missing redo-clear on a branch.
- Where/why it failed: A command captured to transform one specific history
  (e.g. "insert 'b' at index 1") is only valid against the state it was
  computed for. After undo + a new edit, the document is a different
  history, but the stale command is still on the redo stack; replaying it
  applies an operation to state it was never computed for and produces
  garbage.
- Fix: Clear the redo stack on every genuine push in the do/commit path —
  one line, but it is the load-bearing invariant of the whole system.
  Coalescing corollary: a merge must fold only into the LIVE top-of-undo,
  never into a command that has already been undone (now on the redo stack).
- Why this fix: A new edit defines a new future; the abandoned future is
  unreachable by definition, so keeping it around is not just a leak but a
  correctness hazard the moment redo is offered. Discarding it at commit
  time is the only point where the branch is known.
- Rule of thumb: In any linear undo/redo (editor timeline, command-sourced
  state with a redo affordance), a new action after undo MUST discard the
  redo stack at commit time — otherwise redo replays a stale command against
  a diverged document and corrupts it. This is the system's core invariant,
  not an optimization; test it explicitly (undo, do a different edit, then
  attempt redo and assert it is a no-op, not a mutation).
- Provenance (verified/assumed): Verified first-hand this session and
  reproduced by an adversarial re-check: a build that omitted the redo-clear
  went `["a","X"]` → `redo()` returned true → `["a","b","X"]` (corrupt); the
  fixed build cleared redo and `redo()` correctly returned false with the
  document unchanged.
- Link: session (dog-game-continue-oc3xqh); sandboxes sb-undo-core
  (`engine.js` `do()`), sb-undo-coalesce (`undo.js` `push()`). Kernel filed
  in ideas `idea-repository.md`
  (SYSTEM/undo/a-new-edit-after-undo-must-discard-the-redo-future).

## E4 — sandbox undo inverse capture preimage
- Date: 2026-07-11
- Project: local/sandbox-undo-redo
- Tags: [state][editor]
- What: A command's inverse (or a history delta) must be derivable from its
  arguments PLUS the state captured DURING apply — never from the forward
  arguments alone. Destructive operations don't preserve the information
  needed to reverse them, so an inverse reconstructed from args only can't
  restore what was destroyed.
- Why built: An undo/redo core with command inverses, and a delta-based
  history variant, both stress-tested for exact round-trip (document before
  a command must equal the document after applying then undoing it).
- Design: Each command exposes apply and invert; a delta history stores a
  compact change per step and reconstructs by replaying inverses.
- Got right: The command dispatch and replay machinery were correct; the
  bug is specifically inverses/deltas that fail to record the pre-image.
- Where/why it failed: A delete-at-index whose `invert()` is built from just
  the index re-inserts a hole (undo yields `null` where the value was); a
  "clear all" that doesn't snapshot its contents undoes to empty; a lossy
  delta that forgot the pre-image guesses a default and poisons every step
  after it in the chain (an undo-all lands on the wrong value). The forward
  operation threw away exactly the data its inverse needs.
- Fix: Capture the destroyed/overwritten state at APPLY time (in the
  command's closure or undo-record), so the inverse derives from
  (args + captured pre-image). If an operation truly can't be inverted
  (external side effect), mark it a history barrier. Note full snapshots are
  immune by construction — this hazard is specific to compact command/delta
  representations.
- Why this fix: Reversibility is a property of information, not of the
  forward call signature; only the moment of apply still has the pre-image,
  so that's where it must be captured. Deriving the inverse later from args
  alone assumes an information-preserving operation, which destructive edits
  are not.
- Rule of thumb: An undo inverse (or history delta) must derive from command
  args PLUS state captured during apply — capture the pre-image at apply
  time for any destructive/overwriting op (delete, clear, set), or the undo
  restores a hole/default/empty instead of the real prior value, and in a
  delta chain one lossy delta corrupts everything after it. Snapshots avoid
  this at a memory cost; if you use deltas, pre-image capture is mandatory.
  Test by asserting byte-equality of the document before-do vs after-undo.
- Provenance (verified/assumed): Verified first-hand this session and by an
  adversarial re-check: a delete whose inverse used the index only undid
  `["a","b","c"]`→`["a","c"]`→undo→`["a",null,"c"]`; a clear-all undid to
  `[]`; a lossy delta left `arr[5]=0` after undo-all where 5 was expected;
  capturing the pre-image at apply fixed all three and a full-snapshot
  variant never exhibited it.
- Link: session (dog-game-continue-oc3xqh); sandboxes sb-undo-core
  (`engine.js` Delete/ClearAll invert), sb-undo-history (`sim.js` lossy
  delta). Kernel filed in ideas `idea-repository.md`
  (SYSTEM/undo/an-inverse-must-capture-the-destroyed-pre-image-at-apply-time).

## E3 — sandbox undo history aliasing deep copy
- Date: 2026-07-11
- Project: local/sandbox-undo-redo
- Tags: [state][editor]
- What: An undo history is only trustworthy if every entry — a recorded
  state snapshot AND the undo-data captured inside a command — is a deep,
  private, unshared copy. Three aliasing traps all silently rewrite the
  past: storing a reference to the live mutable document as a "snapshot,"
  storing a shallow copy, or reusing one command instance for two history
  entries.
- Why built: An undo/redo core and a snapshot-history variant, tested for
  whether past history stays intact after later mutations.
- Design: History stores per-step state (snapshot model) or per-step
  commands with captured undo-data; undo restores the recorded entry.
- Got right: The restore machinery was correct; the failure is entirely
  that the recorded entries shared mutable storage with live state.
- Where/why it failed: (1) Storing a REFERENCE to the live document makes
  every snapshot point at the same object, so a later edit retroactively
  changes all past snapshots and undo restores the CURRENT state, not the
  historical one. (2) A SHALLOW copy is the nastiest — top-level scalar
  fields restore correctly (so it looks fixed) while nested arrays/objects
  are still aliased and corrupt. (3) Reusing one command INSTANCE for two
  stack entries shares its captured-value closure, so the second push
  overwrites the first entry's undo data.
- Fix: Deep-clone on commit (both recorded state and any captured pre-image),
  and give each history entry its own command instance. The memory cost of
  deep snapshots is exactly what motivates the compact command/delta
  representation — but a delta must still own a private copy of the pre-image
  it captured.
- Why this fix: Time-travel is only sound if the past is immutable; sharing
  any mutable storage between live state and a history entry means a present
  mutation edits the past. A deep private copy severs that link; a shallow
  copy severs it only one level deep, which is why it's a deceptive
  half-fix.
- Rule of thumb: Every undo/history entry (state snapshot or captured
  undo-data) must be a DEEP, private, unshared copy — storing a reference, a
  shallow copy, or a reused command instance lets a later mutation silently
  rewrite recorded history so undo restores the current state, not the
  historical one. Shallow copies are the trap: scalar fields look restored
  while nested structures corrupt. Applies to any state-versioning /
  time-travel store (undo, Redux time-travel, config history, a row cache).
- Provenance (verified/assumed): Verified first-hand this session and by an
  adversarial re-check: a reference-snapshot history read `"abc"` for all
  three steps after later edits (undo restored current, not historical); a
  shallow copy restored a scalar `text` correctly while a nested `tags`
  array stayed corrupted to `["x","y","z"]`; reusing one command instance
  twice gave `["a","c","c"]`; deep-clone-on-commit fixed all.
- Link: session (dog-game-continue-oc3xqh); sandboxes sb-undo-core
  (`engine.js` instance reuse / stored ref), sb-undo-history (`sim.js`
  reference & shallow snapshot). Kernel filed in ideas `idea-repository.md`
  (SYSTEM/undo/history-entries-must-own-private-deep-unshared-copies).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-undo-replan.md#E1 · compatible · no sandbox · this session's sandbox build (sandbox_undo_replan.py); source entries sandbox-astar-replan#E2 and sandbox-undo-redo#E3.

## E2 — sandbox undo coalescing correctness
- Date: 2026-07-11
- Project: local/sandbox-undo-redo
- Tags: [state][editor][input]
- What: Merging rapid consecutive edits into one undo step (so one Ctrl+Z
  removes a typed word, not one letter) has two correctness rules a
  time-window-only merge violates: it must gate the merge on same command
  KIND and spatial ADJACENCY (not just "within the window"), and the merged
  command's undo data must describe the transition from BEFORE the first
  sub-edit to AFTER the last (not let the newest sub-edit overwrite the
  burst-start anchor).
- Why built: A coalescing undo layer over a command stack, tested with
  scripted keystroke/backspace bursts (timestamps passed in explicitly for
  determinism) asserting undo-step counts and exact document round-trip.
- Design: A new command merges into the top-of-undo command if compatible;
  merging extends the top command's captured payload so one undo reverses
  the whole burst.
- Got right: The stack and single-undo-reverses-burst goal were right; the
  bugs are in the merge predicate and the merge's bookkeeping.
- Where/why it failed: (1) Gating merges on the time window ALONE collapsed
  a type-then-delete and a caret-jump insert into one step, and undoing the
  jump-merged group deleted unrelated earlier text (the group spanned
  non-contiguous positions). "Consecutive in time" is not "consecutive in
  intent." (2) The naive merge set the group's position to the LATEST
  sub-edit, so undo removed the wrong range (typing "hello" undid to
  "hell"); backspace runs also reversed the text under naive concatenation
  because order was not preserved.
- Fix: Gate the merge on three conditions — same kind, within the window,
  AND spatial adjacency (`newPos === top.pos + top.len` for inserts, mirror
  for backspace). Preserve the original burst-start anchor and only extend
  the payload, ordering it so the reconstructed undo spans before-first →
  after-last.
- Why this fix: A coalesced undo unit must be reversible as the single
  transition it represents; that requires it to describe both true
  endpoints (first-before, last-after) and to only group edits that are
  actually the same contiguous operation. Adjacency + kind is what makes
  "the same operation"; the anchor is what makes the reverse land on the
  right range.
- Rule of thumb: When coalescing edits into one undo step, gate the merge on
  same-kind AND spatial-adjacency, not just a time window (else unrelated
  edits collapse into one step and undo deletes text the user never
  grouped), and make the merged undo data span BEFORE-the-first-subedit →
  AFTER-the-last — the classic bug is letting the newest sub-edit overwrite
  the burst-start anchor so undo removes the wrong range (and watch ordering
  for backspace runs). Test by asserting byte-equality against the pre-burst
  document.
- Provenance (verified/assumed): Verified first-hand this session and by an
  adversarial re-check: a window-only merge collapsed type+delete and a
  caret-jump into one step whose undo turned `"ab"` into `""`; a naive merge
  undid typing "hello" to "hell" and reversed a backspace burst to "tac";
  gating on kind+adjacency and preserving the anchor made all cases
  byte-equal to the pre-burst state.
- Link: session (dog-game-continue-oc3xqh); sandbox sb-undo-coalesce
  (`undo.js` `_canMerge` / `_merge`). Kernel filed in ideas
  `idea-repository.md`
  (SYSTEM/undo/coalesce-only-same-kind-adjacent-edits-and-span-first-to-last).

## E1 — sandbox cursor into bounded buffer invariant
- Date: 2026-07-11
- Project: local/sandbox-undo-redo
- Tags: [state][algorithm]
- What: Whenever a cursor/index points into a buffer that also gets trimmed
  from the far end (a bounded undo history, a ring buffer, a windowed log, a
  capped scrollback), the cursor and the buffer are a SINGLE coupled
  invariant — the cursor must stay a valid index into the buffer — and
  updating only one of them breaks it silently. Capping undo history by
  dropping the oldest entry with `shift()` but NOT decrementing the cursor
  leaves the cursor pointing past the array; the next undo dereferences
  `undefined` and crashes.
- Why built: An undo history with a size cap (drop the oldest step when over
  N), tested by exceeding the cap and then undoing.
- Design: An array of history entries plus a separate integer cursor
  tracking the current position; commit appends and advances the cursor;
  cap enforcement drops the oldest entries.
- Got right: Append, undo, and redo were correct while under the cap; the
  bug only appears once truncation fires.
- Where/why it failed: `shift()` removes index 0 and shifts every element
  down one, so every valid index — including the cursor — decreases by one.
  Decrementing the buffer's length without decrementing the cursor leaves
  the cursor one-too-high per dropped entry; after enough edits it points
  beyond the end, and undo reads `undefined` (which then crashed the
  deep-clone / JSON path).
- Fix: Adjust the cursor in the same operation that evicts from the front —
  `while (len > cap) { shift(); cursor--; }` — so the two variables that
  must satisfy "cursor indexes buffer" are updated together, atomically.
- Why this fix: Two variables bound by a relationship are really one piece
  of state; any operation that can break the relationship must restore it in
  the same step. A "drop the oldest" that touches the buffer but not its
  cursor is a half-applied invariant, and the failure surfaces later, at
  undo time, looking like an unrelated crash.
- Rule of thumb: A cursor/read-position into a buffer that's trimmed from
  the far end (bounded undo history, ring buffer, windowed log, capped
  scrollback) is ONE coupled invariant — evicting from the front must adjust
  the cursor in the same operation, or the cursor drifts past the end and a
  later read dereferences undefined and crashes. Whenever two variables must
  satisfy a relationship, update them together atomically; editing one and
  not the other is a silent half-applied invariant.
- Provenance (verified/assumed): Verified first-hand this session and by an
  adversarial re-check: a cap that `shift()`ed without decrementing the
  cursor reached `cursor=5` with array length 3, and the next undo read
  `stack[4]=undefined` and crashed; decrementing the cursor on each shift
  (`len=3, cursor=2`) undid cleanly with no crash.
- Link: session (dog-game-continue-oc3xqh); sandbox sb-undo-history
  (`sim.js` capped-history commit). Kernel filed in ideas
  `idea-repository.md`
  (SYSTEM/data-structure/a-cursor-into-a-bounded-buffer-is-one-coupled-invariant).

