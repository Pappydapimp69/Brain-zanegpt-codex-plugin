# local/storyteller-heartless-giant — lessons

Project: local/storyteller-heartless-giant. Newest first.

---

## E1 — heartless giant each nested layer needs its own key
- Date: 2026-10-17
- Project: local/storyteller-heartless-giant
- Tags: [narrative][quest-design][simulation][sandbox]
- What: Modelled the nested hiding place of the giant's heart (lake, church, duck, well, egg) as a quest where each
  layer names the helpers that can open it, and counted new beats against padding and where a missing helper stops it.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had the distinct-role test for enemies and OR prereqs
  for quests, but nothing on what nesting a villain's weak point in containers does to the quest that retrieves it.
- Design: Stdlib walk from the outermost layer inward; a layer is a new beat if its solver has not been used yet and
  padding if it has; the walk stops at the first layer no held helper can open; order and helpers taken from Dasent's
  translation (wolf swims the lake, raven fetches the keys, hero coaxes the duck, salmon fetches the egg, hero squeezes).
- Got right: The tale's 5 layers gave 5 new beats and 0 padding; adding 3 boxes locked with the raven's keys made 8
  layers but still 5 beats; without the salmon the walk stopped at the well; an OR route there (salmon or a rope) got through.
- Where/why it failed: The first run put the well before the duck, so the missing-salmon run stopped after 2 layers; the text
  has the duck coaxed first and the egg dropped into the well, so it is 3. The BREAK, one helper opening everything, gave 1
  beat from 5 layers, so nesting shapes the quest only when each layer needs a different solver.
- Fix: Give every layer of the hiding place its own solver and earn each solver earlier in the story, count beats by
  solver rather than by layer, and add an OR route on any layer whose single helper the player could have missed.
- Why this fix: A layer that reuses a solver adds distance but no new obstacle, and one missing solver on a single-route
  layer vetoes the whole retrieval no matter how many outer layers were cleared.
- Rule of thumb: Nest the weak point only as deep as you have distinct solvers; a layer reusing a key is padding, a
  universal key flattens the nest to one beat, and a single-helper layer needs a second way in.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode details checked against Wikipedia's
  Storyteller article and TheTVDB, and the layer order against Dasent's text on Project Gutenberg cited in the kernel.
- Composed: ideas:RPG/level-design/enemy-role-not-headcount, ideas:NPC-SIM/decision-making/multiplicative-combination-preserves-vetoes, ideas:RPG/progression/quests/or-prereq-branch
- Sandbox: sandboxes/2026-10-17__heartless-giant-each-nested-layer-needs-its-own-key.py
- Prediction: Tale nesting 5 layers, 5 beats, 0 padding, heart reached; with 3 raven-key boxes 8 layers, 5 beats, 3 padding;
  salmon missing stops at the well; OR route at the well gets through; one universal helper gives 1 beat.
- Observed: RESULT: PASS 5 layers give 5 beats; 3 key-locked boxes add 3 padding and 0 beats; missing salmon stops at the well
  after 3 layers unless the well has an OR route; one universal helper turns 5 layers into 1 beat.
- Scenarios: 1) tale nesting; 2) padded with 3 raven-key boxes; 3) salmon never helped; 4) OR route at the well;
  5) BREAK: one helper opens every layer
- ZaneGPT verdict: weak — the five scenarios confirm the counter's own definition (distinct solvers = beats, missing solver = stop, universal key = one beat), which the model already assumed, so the rule describes the simulation rather than what makes a nested weak point work.
- Hidden assumption: Narrative value is fully captured by solver-distinctness, so "new beat" means "first use of a helper"; the simulation only counts that, and the rule is true by construction rather than tested against whether a reader finds a layer fresh.
- Would prove it wrong: A nest where a repeated helper is paired with a changed obstacle or cost (the raven opens a second box but the keys are now guarded or the price is the hero's own eye) and still reads as a new beat, or one where five distinct solvers give five interchangeable "helper does a thing" beats that feel like padding.
- Break scenario: A layer needing two helpers in combination (wolf carries the hero while the raven distracts the guard), or the same helper twice with escalating stakes. The walk counts the first as one beat or a stall, and the second as padding, so any real storyteller's judgment of "new beat" contradicts the counter.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 8b89b82e01b5
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

