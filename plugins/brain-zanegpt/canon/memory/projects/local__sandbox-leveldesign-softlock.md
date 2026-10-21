# local/sandbox-leveldesign-softlock — lessons

Project: local/sandbox-leveldesign-softlock. Newest first.

---

## E1 — ability gated oneway drop softlock is bfs detectable
- Date: 2026-07-20
- Project: local/sandbox-leveldesign-softlock
- Tags: [gamedesign][algorithm]
- What: A Metroidvania-style one-way drop/shortcut with no ability
  requirement to FALL, landing in a room whose only way out is gated on
  an ability acquired through a completely different path, is a
  structural soft-lock — and it is detectable by pure graph reachability
  (BFS over the level's room graph with an "abilities held so far" state),
  with no player-skill simulation needed at all.
- Why built: `brain train new-domain`, seeding LEVEL-DESIGN as a genuine
  gap (`brain query` returned only broad tag-noise, nothing organized as
  level-graph/gating craft, distinct from WORLDBUILDING's lore/canon
  focus and PROCGEN's algorithmic-generation focus).
- Design: `sandbox.py` — a fixed 5-room level graph (zero RNG): a hub
  with a one-way drop into `drop_room`, which has a SECOND one-way drop
  into `sealed_pit`; the hub also has a normal two-way path to
  `ability_room` (where `double_jump` is acquired) and onward to a
  `vault`. `sealed_pit`'s only exit back to the hub requires
  `double_jump`. `find_softlock()` computes reachability from the start
  room assuming NO abilities held yet, then for every no-ability
  one-way edge taken while in that "no abilities" reachable set, checks
  whether the room on the far side of the drop can reach BACK to either
  the ability's own pickup room or the drop's origin. A second,
  otherwise-identical graph adds a plain (ability-free) ladder back out
  of the pit as the fix.
- Got right: the check needs no simulated player behavior, timing, or
  luck — it's a structural property of the level graph alone, checkable
  offline before any playtesting.
- Where/why it failed: the buggy graph's check flags exactly the
  two-drop chain (`hub→drop_room`, `drop_room→sealed_pit`) as leading
  to a soft-lock — from `sealed_pit`, with no abilities assumed held,
  there is no path back to the hub, the ability room, or anywhere the
  ability could be acquired.
- Fix: for any one-way drop/shortcut in a Metroidvania-style level, BFS-
  verify (with the "no abilities yet" assumption, since players CAN and
  do sequence-break) that every room reachable through it either (a)
  has a return path requiring no ability, or (b) can reach the specific
  ability needed to escape it. The sandbox's fix adds a plain ladder
  back up from the pit.
- Why this fix: a level designer reasoning "the player will have
  double_jump by the time they get here" is an assumption about
  INTENDED ORDER, not a guarantee about what the graph's edges actually
  allow — any one-way edge without its own ability gate is reachable
  the moment its origin room is reachable, regardless of intended
  pacing, so the check must assume the worst case (zero abilities) to
  be a real guarantee rather than a hopeful one.
- Rule of thumb: before shipping any one-way drop, shortcut, or point-
  of-no-return in a Metroidvania/ability-gated level, run a BFS from
  spawn assuming ZERO abilities held (not "abilities the player should
  have by now") and check whether every room reachable that way has
  either an ability-free return path or a reachable path to the
  ability that would unlock its exit — this is checkable purely from
  the level graph, independent of playtesting, and catches soft-locks
  before a human ever falls into one.
- Provenance (verified/assumed): Verified first-hand — ran `sandbox.py`
  (zero RNG, fixed level graph), confirmed the buggy graph's soft-lock
  detector flags the two-drop chain and the fixed graph (plain return
  ladder) reports none. Re-ran as two independent process invocations;
  output byte-identical both times.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  new-domain`, level-design gap); sandbox
  `scratchpad/loop7/leveldesign/sandbox.py`, run twice as independent
  process invocations, outputs diffed identical
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-level-design.md#E1 · compatible · sandboxes/2026-09-28__train-gap-b07.py · session 2026-09-28, brain train gap batch 7 loop 35
- Audited: 2026-10-15 · fail · There is no stored sandbox: the entry's Link names scratchpad/loop7/leveldesign/sandbox.py, nothing under sandboxes/ matches, so whether the detector computes its result or builds it in cannot be checked from canon. I rebuilt the described 5-room graph and the entry's method (BFS with zero abilities, then for each ability-free one-way edge test whether the landing can get back to the origin or a pickup room) and compared it with a full-state search over (room, abilities held) that marks every reachable state unable to reach the goal. On the entry's graph both agree (hub to drop_room and drop_room to sealed_pit). On a second graph with a one-way ledge reachable only with double_jump, dropping into a chasm whose exit needs wall_climb, the zero-ability check flags nothing new while the full search finds a softlock at (chasm, double_jump held). So the Rule of thumb's claim that a zero-ability BFS catches soft-locks before a human falls into one covers only one-way edges with no ability gate; softlocks behind an ability-gated one-way edge need the search over ability sets. Fail on the missing sandbox and on the scope of the rule; the narrower claim (an ungated one-way drop is reachable regardless of intended pacing) holds. · brain train auto pass 3 (audit); session_01Hecxxt7Wfrejc8A3YVX1ht
