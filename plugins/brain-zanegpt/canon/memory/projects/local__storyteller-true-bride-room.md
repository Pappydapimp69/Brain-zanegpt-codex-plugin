# local/storyteller-true-bride-room — lessons

Project: local/storyteller-true-bride-room. Newest first.

---

## E1 — true bride bottomless room standing trap on pursuit path
- Date: 2026-10-17
- Project: local/storyteller-true-bride-room
- Tags: [narrative][level-design][simulation][sandbox]
- What: Modelled The StoryTeller's The True Bride as a palace graph with one room that opens onto nothing: the troll
  falls in while inspecting his palace, and later his daughter, chasing the lovers and misled by their
  scent and voices, falls into the same room.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had set-up and payoff (Chekhov's gun) and
  antagonists who remember, but nothing on when one trap placed once can fairly defeat a second villain.
- Design: Stdlib BFS over gate-hall-east/west, west-door (trap), east-garden-road. Villain 1 inspects every room;
  villain 2 follows a lure if one is placed, else the lovers' trail, and an informed chaser steps around
  a known trap. Measured catches, setups needed (traps plus extra defeats), author-added detour steps,
  and whether the lovers' own route crosses the trap. Five runs incl. a BREAK informed chaser.
- Got right: Standing trap with the lure on the chase gave 2 catches from 1 setup and 0 added steps; a one-shot
  trap gave 1 catch and 2 setups; a standing trap off the chase with no lure needed a 2-step author
  detour; a chokepoint trap at the hall caught both with no lure but also lay on the lovers' route.
- Where/why it failed: The BREAK informed chaser who saw the first fall stepped around the trap and reached the lovers even
  with the lure, so reuse only works on a villain who has not seen it work. A first run left the
  one-shot chaser stranded at the sealed door because the lure had no fallback; fixed so she resumes
  the chase, which then reached the lovers as predicted.
- Fix: Place the trap where the second villain's own drive (pursuit, greed, inspection) carries her onto it,
  make sure she never saw it take the first one, and add a lure only if it follows from her drive (the
  lovers' scent); if the catch needs an author detour, give her a defeat of her own instead.
- Why this fix: The reuse reads as fitting when the second fall comes from the villain's own goal and ignorance with
  no extra steps from the author, and as contrived exactly when those added steps are needed.
- Rule of thumb: Reuse one trap for a second villain only when her own drive walks her onto it and she never saw it
  work; if the author must add a detour, or she watched the first fall, give her a separate defeat.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode details (the Lion's palace with a
  room onto nothing, the troll's fall, the daughter misled by scent and voices into the same room)
  checked against Wikipedia's Storyteller article and an episode review cited in the kernel.
  The graph layout is a toy.
- Composed: ideas:STORYTELLING/economy/chekhovs-gun-is-a-promise-not-just-foreshadowing, ideas:narrative-design/antagonist/escalating-competence-via-memory-not-difficulty
- Sandbox: sandboxes/2026-10-17__true-bride-bottomless-room-standing-trap-on-pursuit-path.py
- Prediction: 1) standing trap plus lure: 2 catches, 1 setup, 0 added steps; 2) one-shot: 1 catch, chaser reaches the
  lovers, 2 setups; 3) off-path, no lure: 1 catch, 2-step detour; 4) BREAK informed chaser: 1 catch;
  5) chokepoint at the hall: 2 catches, 0 added steps, lovers' route crosses it.
- Observed: RESULT: PASS standing trap on the lured pursuit path: 2 catches from 1 trap, 0 added steps; one-shot
  needs 2 setups; off-path needs a 2-step detour; informed chaser escapes; chokepoint catches both but
  exposes the lovers (first run had the lure-without-fallback bug in scenario 2, fixed and rerun).
- Scenarios: 1) standing trap plus lure at the door; 2) one-shot trap; 3) standing trap off the pursuit path;
  4) BREAK informed chaser who saw the first fall; 5) chokepoint trap with no bypass for the lovers
- ZaneGPT verdict: weak — the five scenarios were written to match the rule (the prediction was fixed before the run, and scenario 2 needed a bug fix to match), so a PASS shows the sim is consistent with the rule, not that the rule holds on a graph the author didn't design; the rule needs one graph with a different topology and a partial-knowledge chaser before it earns "holds".
- Hidden assumption: Whether the second villain "walks onto the trap" is decided by the author's own path model (BFS toward lure or trail), so the rule assumes her drive is deterministic and knowable in advance. It also assumes a trap's "never saw it work" status can be judged separately from her drive.
- Would prove it wrong: A run where the chaser is on the lure path, has not seen the fall, and still avoids the trap, or one where she saw the fall and walks in anyway. Either shows that drive and knowledge are not the only variables. A rerun with a different BFS tie-break or room-visit order that flips scenario 1 from 2 catches to 1 would do the same, because then the result comes from the graph layout.
- Break scenario: Put the trap on a room that is on the chaser's shortest path in the graph but that she reaches only after a second lure or a blocked door reroutes her. Variant: she hears the troll fall (sound, not sight) and treats the trap as known. The informed-chaser run only models "saw", so "heard" or "was told" is untested. The "never saw it work" clause is a single binary flag in the sim and could be too coarse.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 3cfcbc6e8817
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

