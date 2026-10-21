# local/sandbox-kernel-system-architecture — lessons

Project: local/sandbox-kernel-system-architecture. Newest first.

---

## E5 — trust provenance is laundered when payload values are stored unchecked
- Date: 2026-09-28
- Project: local/sandbox-kernel-system-architecture
- Tags: [architecture][security][state][pathfinding]
- What: Applied the ideas kernel that trust follows a value's source, not its type: a position maintained by state is safe to trust, a position read from a command payload is not. It held, and the rule fails if a payload value is written into state unchecked, since it is then trusted as state-maintained.
- Why built: brain train gap listed the kernel as unapplied. the-game-the-recursion/E19 stated the provenance rule and sandbox-astar-replan/E2 the trust-live-position rule; neither covered a payload value entering state.
- Design: A 16x16 grid with 25% walls, 2000 seeded sessions of 15 commands: sim-computed single steps, replans, and a client 'sync position' command carrying a claimed position. Designs: replan from the payload's claimed position; store the claimed position into state unchecked and replan from state; accept the claim only if it is not a wall and adjacent to the current position; and ignore client positions entirely. A session fails if the agent is ever in a wall or in a cell unreachable from the start.
- Got right: Adding the store-then-trust design. Comparing only payload against state makes the provenance rule look sufficient on its own.
- Where/why it failed: Trusting the payload position failed 1572 of 2000 sessions. Storing the payload into state unchecked and then trusting state failed 1573 of 2000, the same exploit laundered through state. Validating the claim at the point it is written failed 0, as did ignoring client positions.
- Fix: Validate a payload value at the moment it is written into state (legality, reachability, adjacency); after that, state can be trusted. Treat any command that writes state from its payload as an entry point to audit.
- Why this fix: State-maintained is only trustworthy if every write into state is either computed by the sim or checked. One unchecked write turns a payload value into a trusted state value.
- Rule of thumb: Trust by provenance only works if provenance is checked at the write: replanning from a payload position failed 1572/2000 fuzzed sessions, and storing that payload into state unchecked then trusting state failed 1573/2000, while validating the claim when writing it failed 0.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b10.py loop 50 in Pappydapimp69/Brain, deterministic fuzzed sessions. Observed: 1572, 1573, 0 and 0 failing sessions of 2000 for the four designs.
- Composed: ideas:SYSTEM/architecture/trust-by-source-not-by-value-type/a-safe-rule-for-one-value-can-be-an-exploit-for-the-same-type-elsewhere, the-game-the-recursion/E19, sandbox-astar-replan/E2
- Link: session 2026-09-28, brain train gap batch 10 loop 50
- Sandbox: sandboxes/2026-09-28__train-gap-b10.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

## E4 — stringify state save load needs json plain state and a read only view
- Date: 2026-09-28
- Project: local/sandbox-kernel-system-architecture
- Tags: [architecture][state][save][javascript]
- What: Applied the ideas kernel that a command, reduce, event seam with a view that never writes state makes replay trivial and save/load just stringify(state). Both reproduced in real Node, with one condition the kernel leaves implicit: the state must hold only values JSON round-trips.
- Why built: brain train gap listed the kernel as unapplied. The kernel's save/load claim is about JavaScript, so it ran in real Node.
- Design: A reducer over three entities' positions and HP driven by 60 seeded commands, 200 seeds; a view easing toward state each frame, either read-only or writing its eased position back into state 10% of the time. Replayed the command log from the initial state and compared with live state. Then round-tripped values of each kind through JSON.stringify and JSON.parse: integers, a float, nested objects, -0, NaN, Infinity, undefined, Map, Set, Date, a sparse array, and BigInt.
- Got right: Testing the save half separately from the replay half; the replay test passes for a read-only view whatever the state holds.
- Where/why it failed: With a read-only view the replay matched live state in 200 of 200 seeds; with the view writing eased positions back it mismatched in 200 of 200. The JSON round trip kept integers, the float and nested plain objects, but changed or dropped -0, NaN, Infinity, undefined, Map, Set, Date and array holes, and JSON.stringify threw on BigInt.
- Fix: Keep the view read-only, and keep authoritative state JSON-plain (arrays and plain objects of finite numbers, strings, booleans and null), or write an explicit serialiser and test that load(save(state)) equals state.
- Why this fix: stringify(state) is only a complete save if every value in state survives JSON; a Map or NaN in state fails silently, not with an error.
- Rule of thumb: A command/reduce seam gives exact replay only with a read-only view (200/200 seeds matched; a view writing eased positions back broke all 200), and 'save = JSON.stringify(state)' only holds for JSON-plain state: -0, NaN, Infinity, undefined, Map, Set, Date and array holes changed or vanished on a round trip and BigInt threw.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b10.py loop 49 in Pappydapimp69/Brain, running real Node v22.22.2, deterministic. Observed: 0 and 200 replay mismatches; round trip kept number, float and nested, changed or dropped the 8 other kinds, BigInt threw.
- Composed: ideas:SYSTEM/architecture/authoritative-reducer/command-event-seam
- Link: session 2026-09-28, brain train gap batch 10 loop 49
- Sandbox: sandboxes/2026-09-28__train-gap-b10.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

## E3 — derived pins need topological or versioned invalidation
- Date: 2026-09-28
- Project: local/sandbox-kernel-system-architecture
- Tags: [architecture][state][caching][correctness]
- What: Applied the ideas kernel that a privileged value pinned from a live formula goes stale unless an invalidation hook fires on the command that changes the formula's inputs. Pin-once staleness reproduced, and a hook only works if it covers every input and recomputes dependent values in dependency order; a version check at read time needed neither.
- Why built: brain train gap listed the kernel as unapplied. the-game-the-recursion/E18 recorded the stale derived pin; this measures which invalidation designs actually hold.
- Design: A gate derived from three inputs (base x mult + bonus) and a cap derived from the gate and bonus. 500 seeded runs of 20 input changes, each changing one of the three inputs, with the gate and cap read after each. Designs: pin once; a hook only on the mult-changing command; hooks on every command but recomputing the cap before the gate; hooks on every command in dependency order; and a lazy read that recomputes when the stored input versions differ from the current ones.
- Got right: Adding a value derived from the derived value. With a single pinned value, hook order cannot go wrong.
- Where/why it failed: Pin-once read a stale gate or cap in 500 of 500 runs. A hook on only the mult command failed 500 of 500, since base and bonus also change. Hooks on every command failed 500 of 500 when the cap was recomputed before the gate, from the old gate. Hooks in dependency order and the versioned lazy read both failed 0 of 500.
- Fix: Either attach recomputation to every command that changes any input and run it in dependency order, or store the input versions with the pinned value and recompute on read when they differ.
- Why this fix: A hook is only as complete as the list of commands and the order it runs in; a version check compares against the inputs themselves, so a missed command or a new input cannot leave it stale.
- Rule of thumb: An invalidation hook fixes a pinned derived value only if it covers every input-changing command and recomputes in dependency order: a hook on one of three inputs, or on all of them with a dependent cap recomputed before its gate, read stale values in 500 of 500 runs, while dependency-ordered hooks or a versioned recompute-on-read read none.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b09.py loop 45 in Pappydapimp69/Brain, deterministic seeded runs. Observed stale runs of 500: 500/500/500/0/0 for pin-once, one hook, wrong-order hooks, ordered hooks and versioned read.
- Composed: ideas:SYSTEM/architecture/pinned-privileged-values-need-invalidation-not-just-pinning/a-cache-that-never-invalidates-is-a-stale-value-waiting-to-happen, the-game-the-recursion/E18
- Link: session 2026-09-28, brain train gap batch 9 loop 45
- Sandbox: sandboxes/2026-09-28__train-gap-b09.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

## E2 — live content references need stable step ids not indexes
- Date: 2026-09-28
- Project: local/sandbox-kernel-system-architecture
- Tags: [architecture][save][state][content]
- What: Applied the ideas kernel that snapshotting content into a save makes every later content patch silently miss continued saves, with a wholesale wipe as the only remedy in that architecture. The staleness reproduced, and a live reference removes it without a wipe only if saved progress names steps by a stable id rather than an index.
- Why built: brain train gap listed the kernel as unapplied. the-game-wrong-sky/E18 recorded the scope problem and sandbox-combined-save-system/E1 the freshness-versus-replay trade; neither measured how many saves each alternative breaks under a realistic patch mix.
- Design: 30 quests with 3 to 6 steps, 400 saves each holding a snapshot of its quest and a current step. 40 seeded content patches split between text edits, reward changes, step insertions and step removals. Four designs on load: the snapshot, a wholesale version wipe, a live reference with progress stored as a step index, and a live reference with progress stored as a stable step id.
- Got right: Splitting patches by kind. Text and reward edits, 24 of 40 here, are safe under any live reference, and a mix of only those would make the index design look fine.
- Where/why it failed: 318 of 400 saves pointed at a patched quest, and all 318 loaded stale content under the snapshot; a version wipe fixed that by discarding all 400 saves' progress. A live reference storing a step index pointed 105 saves at the wrong step or none, because insertions and removals shift indexes. Storing a stable step id left only 23 saves needing handling, those whose current step had been removed.
- Fix: Reference content live and store progress as stable step ids, with one explicit rule for a removed current step (for example, resume at the next surviving step). Reserve a version wipe for changes no rule can map.
- Why this fix: Most content edits do not move steps, so a live reference fixes them for free. Of the rest, an id survives insertions and only needs handling on the step actually removed, which touches a small fraction of saves instead of all of them.
- Rule of thumb: A content patch misses every snapshot save (318 of 400 here) and a version wipe costs every save's progress (400), but a live reference only helps if progress is a stable step id: stored as an index, 105 saves pointed at the wrong step after insertions and removals; stored as an id, only the 23 whose current step was removed needed a rule.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b05.py loop 22 in Pappydapimp69/Brain, deterministic seeded content and patches. Observed: 318 stale snapshot loads, 400 wiped, 105 wrong-index and 23 removed-step saves. The patch mix is a model; a real game's ratio of structural to cosmetic edits will differ.
- Composed: ideas:SYSTEM/architecture/a-scope-local-snapshot-technique-silently-inherits-staleness-cost-at-a-longer-scope/ask-what-content-the-snapshot-freezes-and-for-how-long, the-game-wrong-sky/E18, sandbox-combined-save-system/E1
- Link: session 2026-09-28, brain train gap batch 5 loop 22
- Sandbox: sandboxes/2026-09-28__train-gap-b05.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

## E1 — a pinned gate value must be unwritable by the client not just prior
- Date: 2026-09-28
- Project: local/sandbox-kernel-system-architecture
- Tags: [architecture][security][state][testing]
- What: Applied the ideas kernel that a value gating a transition must be fixed in state before the command that crosses the gate, never read from that command's payload. The payload bypass reproduced even for an honest client, and pinning the value in state only closed it when no client command could write that state.
- Why built: brain train gap listed the kernel as unapplied. the-game-the-recursion/E2 and E17 recorded the payload bypass and the pin-in-state rule; neither fuzzed a design where the pinned value is prior state but still client-writable.
- Design: A stage gate that advances when completed tasks reach a threshold of 5. Three designs: threshold read from the ADVANCE payload (defaulting to 0 when omitted), threshold pinned in state but settable by a client SET_DIFFICULTY command, and threshold pinned at construction. 5000 streams of 12 commands from an honest client that never sends the optional param, and 5000 fuzzed streams of any command with any param. A stream counts when a design advances further than the real rule allows.
- Got right: Including the honest client. The kernel frames the payload bug as a bypass; the stream count shows it fires without any attacker.
- Where/why it failed: Reading the threshold from the payload over-advanced 4801 of 5000 honest streams, because an omitted param defaulted to 0, and 4604 of 5000 fuzzed streams. Pinning it in state closed every honest stream, but when a client command could write it, 2435 of 5000 fuzzed streams still over-advanced by lowering the threshold one command earlier. Pinning at construction over-advanced 0 in both sets.
- Fix: Pin the gate value in state that only privileged code writes (construction, a server rule, an authoritative event), and audit every command that can write that field, not only the command that crosses the gate.
- Why this fix: Moving the value out of the crossing command only moves the attack one command earlier if another client command can still set it. What matters is who can write the value, not when it was written.
- Rule of thumb: A gate value pinned in state is only safe if no client command can write it: reading the threshold from the crossing command's payload over-advanced 4801 of 5000 honest streams (an omitted param defaulted to 0), and a state-pinned but client-settable threshold still let 2435 of 5000 fuzzed streams through, against 0 for one fixed at construction.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b04.py loop 18 in Pappydapimp69/Brain, deterministic seeded streams. Observed: payload design 4801 honest and 4604 fuzzed; client-writable state 0 honest and 2435 fuzzed; construction-pinned 0 and 0. The reducer is a model, not The Recursion's code.
- Composed: ideas:SYSTEM/architecture/gate-and-perturbation-params-must-precede-the-command/never-let-the-gated-command-supply-its-own-threshold, the-game-the-recursion/E2, the-game-the-recursion/E17
- Link: session 2026-09-28, brain train gap batch 4 loop 18
- Sandbox: sandboxes/2026-09-28__train-gap-b04.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

