# local/luck-child-out-and-back — lessons

Project: local/luck-child-out-and-back. Newest first.

---

## E1 — out and back errand pays questions in reverse
- Date: 2026-10-17
- Project: local/luck-child-out-and-back
- Tags: [narrative][structure][storytelling][sandbox]
- What: Modelled the errand in Grimm KHM 29, a source of The StoryTeller's "The Luck Child": three
  questions collected on the way out (fountain, tree, ferry), answers learned at the far end, the
  return path revisiting the stops, and the ferryman's oar rule that traps whoever asks next.
- Why built: Brain train external research on The Luck Child; canon had no kernel for how an
  out-and-back quest schedules its payoffs or why one answer is held back until the teller is past it.
- Design: Stdlib model of the route as positions 0-4 and back; each stop opens a question on first
  visit; answers unlock at the far node or, in a control, on arrival; per-beat count of open
  questions is the tension proxy (withheld outcomes, per the information-gap kernel); a toy greed lure
  picks who reaches the ferry next.
- Got right: The tale's route held all three questions open at the far point and put every reward in the
  return leg; the identical events with answers known on arrival scored tension 0 against 12, so the
  deferral to the return leg, not the content, makes the suspense.
- Where/why it failed: The reverse order itself did no work: paying the same answers in forward order on a loop
  route also scored 12, so last-asked-first-answered is only what a straight road forces. A one-way
  route left all three open, and answering the ferryman before crossing trapped the boy wherever
  the ferry sat (first stop or last), because the oar goes to the next person who asks to cross.
- Fix: Keep a return leg so each question is paid at its own stop, let the road set the order, and
  deliver any answer that turns a service against its giver only after the service is used, so the
  trap passes to the next taker, here the king sent by the boy's story of gold on the far bank.
- Why this fix: The return leg is the whole source of the suspense and costs nothing, and the single
  withheld answer is what lets the ending punish the villain without a new act from the hero.
- Rule of thumb: In an out-and-back quest, collect questions on the way out and pay them on the way home;
  the order is just the road's, but hold any answer that turns a service against the teller until
  they have used it, and let that trap pass to the villain.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the tale's order of questions,
  answers and the oar rule checked against the Margaret Hunt translation of KHM 29, and the
  episode's sources against Wikipedia's Storyteller article. The greed lure is a toy parameter.
- Composed: ideas:SYSTEM/narrative/tension-as-information-gap, ideas:SONGWRITING/endings/mundane-conflict-plus-unresolved-exit
- Sandbox: sandboxes/2026-10-17__out-and-back-errand-pays-questions-in-reverse.py
- Prediction: The tale's route closes in exact reverse with 3 open at the far end and all rewards in
  the return half; same content answered on arrival gives zero open questions; a one-way route
  leaves 3 open; answering the ferry before crossing traps the boy. Scenarios 5-7 were added after
  the separate ZaneGPT check, with no prediction written before they ran.
- Observed: RESULT: PASS return leg gives tension 12 vs 0 answered on arrival, one-way leaves 3 open;
  forward-order payment also 12, so the order adds nothing; ferry answered before crossing traps the
  boy at either end of the route, after is safe; the oar then passes to the king.
- Scenarios: 1) out-and-back as told; 2) same content, answers on arrival; 3) one-way route;
  4) BREAK: ferryman answered before crossing; 5) control: answers paid in forward order;
  6) ferry as the first stop, answered after crossing; 7) BREAK: ferry first, answered before
- Sandbox: sandboxes/2026-10-17__out-and-back-errand-pays-questions-in-reverse.py
- Prediction: The tale's route closes in exact reverse with 3 open at the far end and all rewards in
  the return half; same content answered on arrival gives zero open questions; a one-way route
  leaves 3 open; answering the ferry before crossing traps the boy. Scenarios 5-7 were added after
  the separate ZaneGPT check, with no prediction written before they ran.
- Observed: RESULT: PASS return leg gives tension 12 vs 0 answered on arrival, one-way leaves 3 open;
  forward-order payment also 12, so the order adds nothing; ferry answered before crossing traps the
  boy at either end of the route, after is safe; the oar then passes to the king.
- Scenarios: 1) out-and-back as told; 2) same content, answers on arrival; 3) one-way route;
  4) BREAK: ferryman answered before crossing; 5) control: answers paid in forward order;
  6) ferry as the first stop, answered after crossing; 7) BREAK: ferry first, answered before
- ZaneGPT verdict: weak — the supported claims (defer answers, answer the ferry after crossing) are real but trivial, the "pay them on the way home" and "out-and-back" parts are not isolated by any control, and the ordering control that was run showed the order adds nothing.
- Hidden assumption: Tension equals the count of open questions per beat, so any structure that holds questions open longer counts as "more tension"; the model never tests whether a reader or listener feels that count, and the open-question count is largely set by the answers-at-far-node rule, not by the out-and-back route.
- Would prove it wrong: A one-way route with the same answers deferred to the end scoring the same as the tale's route. The model already shows forward-order payment ties at 12, and the one-way route leaves 3 open (never paid, a different failure). If a one-way route that pays all answers at its far end also scores 12, the "out-and-back" part of the rule does no work.
- Break scenario: Run a one-way route (positions 0-4) with the three questions collected on the way, all answers unlocked at node 4, and the ferry answered after crossing. If it matches the tale's 12, the rule reduces to "defer answers" and the road shape adds nothing. Run a second variant in which the greed lure sends the villain to the ferry before the boy, to test whether the trap passing to the king depends on the lure's toy ordering. The result is currently one fixed seed's outcome.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 91729e16b02f
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

