# local/storyteller-theseus-thread — lessons

Project: local/storyteller-theseus-thread. Newest first.

---

## E1 — theseus thread tether guarantees the way back only while intact
- Date: 2026-10-17
- Project: local/storyteller-theseus-thread
- Tags: [pathfinding][navigation][simulation][sandbox]
- What: Modelled Ariadne's thread as a tether paid out while exploring and compared the way back with it, with a memory of
  4 junction choices, and with no aid (right-hand wall rule) over 56 deterministic grid mazes from 5x5 to 21x21.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had A*, smoothing and a found path that must be consumed,
  but nothing on the cost of getting back out of a maze explored with no map, or what breaks a tether.
- Design: Stdlib; mazes from a recursive backtracker with a hashed neighbour order (8 per size), door at a corner,
  Minotaur at the centre; Theseus finds him by depth-first search; looped variant turns the centre into a free-standing
  pillar with a ring round it and puts the Minotaur on the ring; thread variants are wound in at dead ends, left lying,
  one cell too short, cut at the fight, and cut at every cell of the route with a wall-rule fallback from the cut.
- Got right: The wound thread got him out of all 56 mazes and at the shortest distance in all 32 perfect ones; a memory of
  4 junctions overran in 0, 2, 5 and 7 of 8 perfect mazes as size grew 5, 9, 15, 21; a thread left lying cost 1.20x the
  wound one at 5x5 and 1.98x at 21x21; the wall rule exited every perfect maze but circled the pillar in all 24 looped
  ones; cut at any cell of the route he still got out from every cut in perfect mazes and 1659 of 1750 in looped ones.
- Where/why it failed: The first maze hash made pure corridors so every aid tied; one maze per size then missed two
  predictions that hung on the maze drawn, so the run moved to 8 per size. With loops the wound thread was longer than the
  shortest route in 11 of 24 mazes (worst 79 against 47). The BREAK, thread cut at the fight, left him lost in all 24
  looped mazes. Traps were predicted only on the ring, but 47 cut points off the ring also trapped him: each circled a
  free-standing wall made of the pillar plus wall stubs that opening the ring cut loose.
- Fix: Give the explorer a tether and have it wound in at dead ends, size it to the route the search will actually take
  and not the shortest one, and give a second way back (marks, a map) near anything that makes a free-standing wall, since
  a cut there leaves a wall-rule fallback circling forever; a cut on the loop-free part costs extra steps, not the exit.
- Why this fix: The tether's guarantee comes from recording the route, not from knowing the maze, so it holds in looped
  mazes where the wall rule fails, but only for the length laid and only while unbroken; left lying it also records every dead end.
- Rule of thumb: A tether paid out while exploring always leads back, at the shortest cost only in a loop-free maze; wind
  it in at dead ends, size it to the search, and protect it most where a loop has left a free-standing wall, where a cut traps for good.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode's thread checked against Wikipedia's
  Storyteller article and the myth against Apollodorus' Epitome on theoi.com cited in the kernel.
- Composed: ideas:PATHFINDING/integration/a-found-path-must-be-consumed-not-re-derived
- Sandbox: sandboxes/2026-10-17__theseus-thread-tether-guarantees-the-way-back-only-while-intact.py
- Prediction: Wound thread exit equals the shortest distance in every maze; memory of 4 matches the thread route exactly
  when the route has 4 or fewer junctions and overruns more often as size grows; left-lying ratio higher at 21x21 than
  5x5; wall rule exits all perfect, no looped; one cell short never reaches; BREAK cut at the fight: perfect exit, looped
  none; cut at every cell: perfect all exit, looped at least 80 percent exit, trapped only on the ring.
- Observed: RESULT: PASS the wound thread exits in all 56 mazes, at the shortest distance in all 32 perfect ones and longer
  in 11/24 looped ones (worst 79 vs 47); memory of 4 junctions overruns in [0, 2, 5, 7] of 8 perfect mazes at sizes
  5/9/15/21; a thread left lying costs 1.20x then 1.98x; wall rule circles the pillar in all 24 looped mazes; BREAK one
  cell short never reaches the Minotaur, cut at the fight leaves him lost in every looped maze; cut at any cell of the
  route he still gets out of 1659/1750 looped positions, every trap circling the pillar and the wall stubs the loops cut
  loose (47 of them starting off the ring)
- Scenarios: 1) perfect mazes 5, 9, 15, 21 with wound, lying, wall and memory returns; 2) looped mazes 9, 15, 21 with a
  pillar ring; 3) thread one cell too short; 4) BREAK: thread cut at the fight, perfect and looped; 5) thread cut at every
  cell of the route with a wall-rule fallback
- ZaneGPT verdict: weak — the thread results are solid inside the tested family (perfect mazes, one pillar ring), but "shortest only in a loop-free maze" and "protect free-standing walls" are extrapolated from a single loop type that was built to trap the wall rule, so the rule is partly circular.
- Hidden assumption: A maze's walls and loops are only ever static features the thread-versus-wall-rule comparison can be generalised from, yet every result comes from one generator (recursive backtracker with hashed neighbour order, 8 mazes per size, centre goal, corner door) and one hand-built loop type (a ring around a pillar). The rule's "protect it most where a loop has left a free-standing wall" claim also assumes the pillar ring is typical of loops, and that the thread's only failure is being cut. Cost is measured by exit distance only, so a thread that is lost, tangled or snagged is never tested.
- Would prove it wrong: A looped maze whose loop doesn't leave a free-standing wall, such as a loop that touches the outer wall or a braid maze with many small loops, in which a cut thread still traps, or an intact wound thread exits at a distance far longer than 79 vs 47. Also, if the wall-rule fallback gets trapped on the ring in under 80 percent of positions once the loop is not a centred pillar, then "protect it most at the free-standing wall" is an artefact of where the pillar was placed.
- Break scenario: Generate looped mazes by removing 10 to 30 percent of interior walls at random, which gives many loops and several free-standing wall islands. Put the Minotaur off-centre and the door at a random cell, and cut the thread at every route cell with the wall-rule fallback. Also wind the thread through those loops (it is "wound in at dead ends" only, so a loop with no dead end may leave it unwound). Check whether trapped positions still cluster on the one ring the rule names, or spread across every island. Add a second wall-follower (left-hand) to see whether trapped starts depend on chirality.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest b8fdf02e9c7f
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

