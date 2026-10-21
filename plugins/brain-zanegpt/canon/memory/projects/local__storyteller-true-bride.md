# local/storyteller-true-bride — lessons

Project: local/storyteller-true-bride. Newest first.

---

## E1 — true bride third try must change one stated thing
- Date: 2026-10-17
- Project: local/storyteller-true-bride
- Tags: [narrative][structure][simulation][sandbox]
- What: Modelled the three nights of The True Bride as an attribution test: an observer sees only visible
  variables and names as the cause any variable that all failed nights share and the winning night changes,
  then a counterfactual replay checks whether that cause really mattered.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had a rule-of-three kernel for spoken lists but
  nothing on what makes a three-try story beat teach the audience why the third try worked.
- Design: Stdlib, deterministic. Outcome rule reads present and drugged; warning is upstream of the drink.
  Five runs: as told; night 3 changes two visible things; drugging kept off-screen; the two failures have
  different causes; BREAK where hidden state lets the spell give way on any third visit.
- Got right: As told gave exactly one cause (the drink) and the counterfactual confirmed it; two changes gave two
  candidates; off-screen drugging and mixed failure causes each gave zero; only 1 of 5 runs was attributable,
  as predicted before the first run.
- Where/why it failed: The BREAK run still named one clean cause (the drink) but the counterfactual showed he wakes
  anyway, and a fourth drugged night also wakes: a hidden build-up across tries makes a single visible change
  look causal when it is not. The rule only holds when the repeats are true repeats.
- Fix: Make the first two tries fail for the same stated reason the audience sees, change exactly one visible
  thing on the third, show what caused that change, and keep any hidden build-up out of the beat.
- Why this fix: The audience reads the third try as a controlled experiment; a second change, an unseen blocker or
  a hidden build-up each leave them with zero, two or a wrong answer to why it worked.
- Rule of thumb: In a three-try beat, fail twice for the same visible reason and change exactly one visible thing on
  the third; if the tries quietly build on each other, the change you show is not why it worked.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode details checked against
  Wikipedia's Storyteller article and the source-tale pages cited in the kernel. The observer rule is a toy model.
- Composed: ideas:PUBLIC-SPEAKING/rhetoric/rule-of-three, ideas:STATISTICS/correlation-vs-causation/confounding
- Sandbox: sandboxes/2026-10-17__true-bride-third-try-must-change-one-stated-thing.py
- Prediction: As told gives 1 confirmed cause; two changes give 2; off-screen drugging gives 0; mixed failure
  causes give 0; BREAK hidden build-up gives 1 cause that the counterfactual shows is wrong; 1 of 5 attributable.
- Observed: RESULT: PASS only the as-told three nights give 1 correct cause; two changes give 2, hidden or mixed
  blockers give 0, and hidden accumulation (BREAK) gives 1 wrong cause; matched on the first run.
- Scenarios: 1) as told; 2) two visible changes on night 3; 3) drugging off-screen; 4) failures with different causes; 5) BREAK: hidden build-up across tries
- ZaneGPT verdict: weak — the 1-of-5 result is true by construction (the outcome rule reads exactly the variables you then "discover"), and the rule is a sound writing heuristic, but nothing in the model shows an observer could detect hidden build-up, which is the exact failure the rule's second clause warns about.
- Hidden assumption: The observer's visible variables include the true cause, and the tries are conditionally independent, so "shared by both failures, changed on the winner" means "caused the win"; the only history-dependence considered is a hidden counter (BREAK), not the audience's or characters' own knowledge, which also carries over between nights.
- Would prove it wrong: A run where the attribution test names a single cause from a clean one-change setup and the counterfactual replay agrees, but swapping the order of the tries (or replaying night 3 first) flips the outcome. That would show history-dependence the scenarios never probe. The same goes for a hidden-accumulation variant in which the build-up is correlated with the visible change, so the replay can't separate them. The current BREAK's counterfactual only works because the harness lets you reset the hidden state.
- Break scenario: Hidden state is a "wear" counter that makes the spell give way on any third visit, and the visible change on night 3 (the real drink, not the drugged one) is also the only thing that varies. Run attribution, then the counterfactual with the drink changed back, and a hidden "night" counter that the replay doesn't reset. The test confirms the visible cause, and the replay (reset to night 3 with the old drink) still wins, so the rule's own check says "cause wrong" only because you built the harness to know. Without a hidden-state oracle, a real reader or writer gets the same single confirmed cause and has no way to tell this case from the as-told case.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 50b18ce3012b
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

