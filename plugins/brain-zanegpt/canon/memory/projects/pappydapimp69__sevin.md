# Pappydapimp69/Sevin — lessons

Project: Pappydapimp69/Sevin. Newest first.

---

## E20 — threejs datatexture srgb and relight
- Date: 2026-10-17
- Project: Pappydapimp69/Sevin
- Tags: [gamedev][3d][threejs][rendering]
- What: In SEVIN (three.js r160) the ground was a DataTexture built from 0-255 sRGB colours with no
  colorSpace set, so three treated the bytes as linear and the trail rendered washed-out beige.
  Setting tex.colorSpace = SRGBColorSpace and turning on ACES tone mapping fixed the look but made
  every night scene pitch black with the old ambient values.
- Why built: A render-only look pass (sky dome, sun shadows, tiered trees, ground cover) to make the
  woods read better without touching the sim.
- Design: Hand-authored hex material colours already go through ColorManagement as sRGB, but a
  DataTexture or CanvasTexture filled from byte arrays defaults to NoColorSpace (linear). Mark it
  sRGB, then enable ACESFilmic tone mapping with exposure about 1.15 and re-tune lights by screenshot.
- Got right: Keeping the per-cell trail and decoy-trail colours exactly where they were, so the
  information the ground carries did not move while its look changed; checked in before/after shots.
- Where/why it failed: Once textures were decoded correctly and tone mapped, albedo in linear light
  was much darker, so the old night hemisphere intensity (0.12) gave a black screen and dusk under
  low-sun shadows went muddy. Every light value tuned under the wrong colour pipeline was wrong.
- Fix: Set colorSpace on the byte-built texture, then raise the night sky light to about 1.1 with a
  cold blue tint (0x5a6f9a sky, 0x141a26 ground) and lerp it down as daylight rises; sun to 1.9.
- Why this fix: Fixing the colour pipeline is the correct root cause; boosting the light rather
  than brightening the texture keeps day colours true and only lifts the scenes that went black.
- Rule of thumb: In three.js, set colorSpace = SRGBColorSpace on any texture you fill from 0-255 colour bytes, and re-tune every light after fixing colour management or adding tone mapping, since values tuned on a linear-treated texture are all too low.
- Provenance (verified/assumed): verified first-hand with headless Chromium screenshots of the same
  seed and hours before and after each change (noon, dusk, night, fog, camp).
- Composed: N/A
- Link: session_017xp5qrXUFXs7kJFiyscvDL / commit f414699

## E19 — sky dome horizon equals fog
- Date: 2026-10-17
- Project: Pappydapimp69/Sevin
- Tags: [gamedev][3d][threejs][rendering]
- What: Replacing a flat scene.background with a gradient sky dome in a fogged three.js forest,
  where illusions also tint the sky and breathe the fog distance at runtime.
- Why built: A flat background colour looked like a void above the canopy; the dome adds a
  zenith, sun glow and stars without changing what the fog hides.
- Design: A BackSide ShaderMaterial sphere (fog:false, depthWrite:false, z forced to w, follows the
  camera) whose horizon uniform is copied every frame from the exact colour the fog uses, after
  all sky tints are applied. The fragment shader includes tonemapping_fragment and
  colorspace_fragment so it passes through the same output pipeline as fogged meshes.
- Got right: Driving the horizon from the final fog colour each frame, so the green-sky and
  fog-breathing hallucinations still apply to the dome without separate code.
- Where/why it failed: A custom ShaderMaterial skips tone mapping and output colour conversion
  unless those chunks are included; without them the dome horizon and fully-fogged trees end up
  as different colours and a seam shows where trunks fade out against the sky.
- Fix: Include both output chunks and feed linear Color uniforms; set the horizon from the fog
  colour after every tint; keep the zenith blend starting above the horizon band.
- Why this fix: Fogged geometry converges to fog colour and is then tone mapped; the dome only
  matches if it takes the same colour through the same transform.
- Rule of thumb: A sky dome behind three.js fog must take its horizon from the final fog colour every frame and include the tonemapping and colorspace chunks, or fogged trees seam against the sky.
- Provenance (verified/assumed): verified first-hand in headless screenshots at noon, dusk, night
  and in fog weather; no seam where trees fade out against the dome.
- Composed: N/A
- Link: session_017xp5qrXUFXs7kJFiyscvDL / commit f414699

## E18 — decor must not mimic hallucinated items
- Date: 2026-10-17
- Project: Pappydapimp69/Sevin
- Tags: [gamedesign][hallucination][rendering]
- What: Adding ground cover (grass, ferns, stones) to a game where a failing mind sees phantom
  sticks drawn exactly like real pickable sticks, and a hallucinated moon appears at night.
- Why built: The forest floor was a flat texture; scatter dressing makes the woods read as a
  place, which was the point of the look pass.
- Design: Dressing is placed from a hash of the cell and index (never the run stream) and uses
  only shapes that cannot be confused with a gameplay object: no twigs, branches or logs on the
  floor, and no real moon disc in the sky.
- Got right: Pressure-testing the dressing list against every hallucination before building it,
  which caught both clashes (twig litter, a normal moon) before they shipped.
- Where/why it failed: The obvious forest dressing (fallen twigs, a moon) collides with the
  hallucination grammar: twig litter would blur the line between real sticks and phantoms with a
  third class of non-pickable sticks, and a real moon turns the first wrong moon into a second moon.
- Fix: Dressing limited to green blades, ferns and small round stones; sky gets stars only, so
  the wrong moon stays the only moon.
- Why this fix: The deception only works if the honest world has a clean vocabulary; dressing
  that shares a silhouette with a faked object adds noise to exactly the read the player relies on.
- Rule of thumb: In a game where hallucinations fake specific objects, set dressing must never share a silhouette with any faked object; check each decor item against the list of faked objects before building it.
- Provenance (verified/assumed): first-hand design decision, built and shipped in commit f414699;
  how players read it is an expectation pending a human play-through.
- Composed: N/A
- Link: session_017xp5qrXUFXs7kJFiyscvDL / commit f414699

## E17 — one use button starves one of two actions valid in the same state
- Date: 2026-10-15
- Project: Pappydapimp69/sevin
- Tags: [gamedesign][input][ui]
- What: Composed sevin E15 (gate each action on its state before ranking), sevin E16 (a ubiquitous tree
  class needs its own narrow cone, a handicap and pitch as intent) and brainwork E203 (gate on current
  state, never a has-fired flag) into one use-button resolver, run exhaustively over campfire states
  and woods poses.
- Why built: SEVIN's single use button now serves a campfire with three actions and a wood full of trees and
  sticks; each lesson fixed one starvation, and the question was whether together they leave every
  action reachable.
- Design: Exhaustive, no rng. Campfire: states fire out or lit by holding nothing or a branch, plus a relight
  after a first light; resolvers ungated priority, ungated with a branch bonus, state-gated then
  priority, state-gated plus held-item intent, and light gated by a has-lit flag. Woods: a sparse 3 m
  tree ring and a dense 1.5 m tree grid, six sticks (one 0.3 m from a tree base), poses on a 0.25 m
  grid by 5 degree headings by pitch; one wide cone against per-class tolerance.
- Got right: Ungated priority starved branch and light (4 cases); the has-lit flag never offered a relight; per-
  class tolerance with pitch intent cut stick hijacks by trees from 26.8 to 2.1 percent in the dense
  wood while keeping 92.8 percent of tree-aimed poses on the tree, and reached a stick at a tree's
  base in every aimed pose.
- Where/why it failed: State gating then priority still starved one action: at a lit fire while holding a branch, feed and
  branch-to-fire are both valid, so priority picked feed every time; adding held-item intent just
  moved the starvation to feed. Any static ranking over two actions valid in the same state starves
  one. The sparse wood barely hijacked (7.8 percent), so the tree problem needs density.
- Fix: Gate on current state (not flags) and give ubiquitous classes their own tolerance, and then check
  every state for two actions valid at once: make them not co-valid (feeding a fire uses the held
  branch) or give the second a separate input such as hold-to-use.
- Why this fix: Gating and tolerance decide which TARGET is chosen; they cannot split one target with two live
  actions, and a ranking only chooses which of them disappears, silently, in exactly the state where
  both make sense.
- Rule of thumb: A single use button with state gates and per-class tolerance reaches every target, but at one spot
  two actions valid in the same state always lose one to any ranking (feed vs branch at a lit fire);
  enumerate states for co-valid pairs and give one a second input or merge them.
- Provenance (verified/assumed): Verified first-hand by the exhaustive sandbox in this entry over a hand-built scene; SEVIN's real
  resolver code was not run.
- Composed: pappydapimp69__sevin/E15, pappydapimp69__sevin/E16, pappydapimp69__brainwork/E203
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__one-use-button-starves-one-of-two-actions-valid-in-the-same-state.py
- Prediction: iteration 1: ungated starves branch and light; state-gated starves nothing; flag never relights; one
  wide cone hijacks >= 30% of stick-aimed poses, per-class < 5% while keeping >= 90% of tree-aimed.
  Iteration 2: state gate plus held-item intent starves nothing; dense wood W1 >= 30%.
- Observed: RESULT: FAIL 7/9; campfire starved A 4 A2 4 B 1 B2 1 D 2; dense-wood stick hijack W1 0.268 W2 0.021;
  sparse W1 0.078 W2 0.019; tree kept W2 0.928; base stick W2 1.000
- Scenarios: 1) campfire under five resolvers in five states; 2) sparse tree ring; 3) dense tree grid; 4) built
  to BREAK it: a stick at a tree base (reached 100%); 5) built to BREAK E15: two actions valid in one
  state (it broke)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 1 pass 2 (edge brainwork + sevin), 2026-10-15

## E16 — ubiquitous target hijacks resolver
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [ui][gamedesign][input]
- What: Adding "cut down the tree" as an action target in a first-person woods game made the use button
  keep offering a tree when the player was reaching for sticks and dropped branches on the ground: trees
  line every path, so one is almost always the nearest thing in the wide (one radian) cone that small
  ground items need. The owner asked for the tolerances around trees and floor objects to be refined.
- Why built: The tree target was added with the same generic reach and cone as every other target.
- Design: One nearest-in-front resolver: score = angle x2 + distance x0.25 over all targets in a cone.
- Got right: The resolver suits sparse, distinct things (a fire, a pylon, a person).
- Where/why it failed: A target class that is everywhere wins ties against sparse ones by sheer
  presence; small ground items need a wide cone to be grabbable at all, and that same cone lets the
  ubiquitous class in.
- Fix: Per-class tolerance: trees need a narrow cone (0.45 rad) and 2.2 m reach and carry a small
  handicap; the camera's pitch is read as intent (eyes down favours items on the ground, eyes level the
  tree); ground items keep the wide cone.
- Why this fix: It uses a signal the player already gives (where they look) instead of adding a mode
  switch, and keeps the easy grab for small things.
- Rule of thumb: When one target class is everywhere, give it its own narrower cone and a handicap, and
  read camera pitch as intent between ground items and upright ones, rather than one cone for all.
- Provenance (verified/assumed): first-hand: owner report and the resolver change; shipped untested
  at the owner's request, so the exact cone values are unmeasured.
- Composed: local__sandbox-resolver-starves-tutorial/E1
- Link: Sevin commit f0e195e; session_0125c7UeqZXhwxqnu8spbVdh
- Cited-by: 2026-10-15 · projects/pappydapimp69__sevin.md#E17 · compatible · sandboxes/2026-10-15__one-use-button-starves-one-of-two-actions-valid-in-the-same-state.py · observed RESULT: FAIL 7/9; campfire starved A 4 A2 4 B 1 B2 1 D 2; dense-wood stick hijack W1 0.268 W2 0.021; sparse W1 0.078 W2 0.019; tree kept W2 0.928; base stick W2 1.000 · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 1 pass 2 (edge brainwork + sevin), 2026-10-15

## E15 — two actions one spot resolver
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [ui][gamedesign][input]
- What: At the campfire three actions share one spot: light, feed, and hold a glowing branch to it. A
  single nearest-in-front resolver picked feed over the branch, so the branch could never be used; the
  fix gave the branch a priority and showed it even with the fire out, which then hid "Light the fire",
  so a player carrying branches could not relight an out fire.
- Why built: Each action was added as another target at the fire's position with the generic score.
- Design: One resolver, one winner per press, score by angle and distance; one tie-breaking bonus.
- Got right: The resolver itself is right for picking what you face among different things.
- Where/why it failed: Co-located actions tie on the resolver's inputs, so the winner is set by a
  bonus that ignores state; each patch fixed one state and broke another.
- Fix: Offer an action only in the state where it makes sense (the branch only at a lit fire, so an
  out fire offers Light), then use the priority only among the actions valid in that state.
- Why this fix: State gating removes the conflict instead of re-ranking it, so no state starves another.
- Rule of thumb: When several actions share one spot under a single resolver, gate each on the state
  where it applies before ranking; a priority bonus alone just moves which state gets starved.
- Provenance (verified/assumed): first-hand: two owner reports in a row (branch unusable, then fire
  unlightable) and the two code changes that caused and fixed them.
- Composed: local__sandbox-resolver-starves-tutorial/E1
- Link: Sevin commits d9a574b, 8942aa6, 3447358; session_0125c7UeqZXhwxqnu8spbVdh
- Cited-by: 2026-10-15 · projects/pappydapimp69__sevin.md#E17 · compatible · sandboxes/2026-10-15__one-use-button-starves-one-of-two-actions-valid-in-the-same-state.py · observed RESULT: FAIL 7/9; campfire starved A 4 A2 4 B 1 B2 1 D 2; dense-wood stick hijack W1 0.268 W2 0.021; sparse W1 0.078 W2 0.019; tree kept W2 0.928; base stick W2 1.000 · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 1 pass 2 (edge brainwork + sevin), 2026-10-15
- Cited-by: 2026-10-15 · projects/pappydapimp69__seven.md#E105 · compatible · sandboxes/2026-10-15__green-wood-penalty-vanishes-into-whole-trips-at-camp-scale.py · observed RESULT: FAIL 3/5; green(0.5) feeds +11%, weight-limited trips x1.00, count-limited +11%; m 0.65 feeds +22%, trips x2.00 · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 2 pass 1 (kernel apply FIREWOOD), 2026-10-15

## E14 — a scene that waits for a press never started
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [gamedesign][ux][scene]
- What: The evening at the fire (talk, a song of everyone's verses, then the call-learning game) was
  reported three times as "never starts" and once as "no minigame". Three causes stacked: it was skipped
  when nobody was at camp yet at dusk; when it ran, the song was a few chat lines with every member
  singing the same fact; and the song panel then waited for an unprompted "Go on" press, so the
  minigame after it never came for a player who just watched.
- Why built: Each step was added as its own small feature (song in chat, then a panel, then the call
  round chained after it) without checking how the whole evening reads from the player's chair.
- Design: A chained scene with a precondition (someone at camp), a low-salience first act (chat lines),
  and a hand-off gated on a button press.
- Got right: A browser repro showed the chain did run when its precondition held, which located the real
  causes (salience, the press, the precondition) instead of re-debugging logic.
- Where/why it failed: Every link was a place to fall out silently: a precondition that skipped instead
  of waiting, content that read as noise, and a press the player had no reason to make.
- Fix: Ending the day calls everyone in and waits for them; the song is its own titled screen with a
  different line per singer; it ends on its own and the call round follows with a spoken cue.
- Why this fix: A scene the owner should not miss must start where they are, look like a scene, and
  move on without needing a press; each fix removes one silent exit.
- Rule of thumb: A chained scene must not have silent exits: wait for (or fetch) its participants
  instead of skipping, make each act unmistakable, and auto-advance rather than wait on a press the
  player was never asked to make.
- Provenance (verified/assumed): first-hand: browser repro of the running chain (chat-only song, five
  identical verses) and the code paths for the skip and the press; the final auto-advance shipped
  without a re-run at the owner's request.
- Composed: dog/E62
- Link: Sevin commits ec5e47c, 7d06078, 25a07b9; session_0125c7UeqZXhwxqnu8spbVdh

## E13 — answer your own questions first
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [workflow][agent][questions]
- What: Across a long build session the owner repeatedly answered agent questions with "you're
  overthinking this", ignored them, or later instructed: answer your own questions with Brain and
  ZaneGPT first. Applied retroactively, the open questions the agent had left in its reports resolved
  without the owner: the rescue soft-lock (a missing person who answers only to a call you never
  learned) was settled by an existing Brain lesson (never gate a rescue on something the player may
  not have) plus a ZaneGPT pressure-test, and was fixed the same turn.
- Why built: The agent treated judgement calls and ambiguous wording ("which device?", "did you mean
  X?") as the owner's to settle, which stalled each build by a full round-trip.
- Design: Ask the owner at the end of a report; wait.
- Got right: Retrieval worked when actually run: Brain held directly applicable lessons (rescue gating,
  false cues, onboarding through real play) for most of the forks the agent had escalated.
- Where/why it failed: The two tools that could answer were run after asking, or not at all; questions
  went to the one participant whose time is the scarcest.
- Fix: Every question is first a `brain query` (1-2 keywords) and a ZaneGPT pass; build the answer,
  report it in one line as reversible; for an ambiguous request pick the likelier reading and fix both
  readings when that is cheap; revisit questions left open in earlier reports the same way.
- Why this fix: It converts a blocking round-trip into a reversible default and spends the agent's
  time instead of the owner's, which is the trade the owner asked for explicitly.
- Rule of thumb: Before asking the owner anything, ask Brain and ZaneGPT; build on their answer and
  report it as reversible; then go back through questions you already left open and close them too.
- Provenance (verified/assumed): first-hand: the owner's instructions in session and the rescue fix
  shipped from the Brain plus ZaneGPT answer (Sevin commit 4567c72).
- Composed: sevin/E?, seven/E24
- Link: Sevin commits 2bd39d4, 4567c72; session_0125c7UeqZXhwxqnu8spbVdh

## E12 — a mechanic behind a menu item is not found
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [gamedesign][ux][onboarding]
- What: The ocarina-style call system (learn each companion's four-note call, then play it to call
  them by name) shipped with exactly one entry point: an evening-only item in the camp menu. The owner,
  play-testing daily, asked twice where calls come into play and then how the player learns them at
  all; they had never seen the menu item.
- Why built: A menu item was the fastest way to expose a new minigame without touching the evening
  flow or the training.
- Design: Camp menu, shown only at camp between dusk and ten, "Learn their calls".
- Got right: The minigame itself (they whistle, you play it back, two tries, remembered under the name)
  worked when invoked.
- Where/why it failed: A conditional menu item is invisible unless the player opens that menu in that
  window, and nothing points at it; a core mechanic that the deduction depends on cannot live there.
- Fix: The call round became part of a scene that already happens every night (ending the day: talk,
  song, then each whistles their call), and the training teaches it with the two trainees through the
  same minigame (Brain: onboarding observes the real flow, not a separate mode); the menu item stays as
  a second door.
- Why this fix: The player meets the mechanic without looking for it, in the place the fiction says it
  belongs, and the training and the real game share one implementation.
- Rule of thumb: A mechanic the core loop depends on must be met inside a flow the player already goes
  through (and taught there); a conditional menu item is only a second door, never the first.
- Provenance (verified/assumed): first-hand: the owner's two questions in session, and the code showing
  the menu item as the only call site before the fix.
- Composed: the-game-prologue/E15, local__dbh/E5
- Link: Sevin commits 4ffdd9c, 62b7ba4; session_0125c7UeqZXhwxqnu8spbVdh

## E11 — a fake cue must answer the probe
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [gamedesign][disappearance][deduction]
- What: To stop the two o'clock whistle from announcing a take, a third of quiet nights got a false
  whistle from the dark. The owner woke to one, whistled back, and nothing answered; on a real night the
  missing person does answer. The obvious probe (whistle back) told the false cue from the true one in
  one press.
- Why built: The false cue was designed against the cue alone (does a whistle at wake mean a take?),
  not against what a player does next.
- Design: One unprompted whistle at wake from a hashed spot in a teammate's voice, nothing behind it.
- Got right: Whistles on quiet nights stopped the wake cue itself from being proof.
- Where/why it failed: Ambiguity has to survive the player's cheapest follow-up, not just the first
  impression; an answer-or-silence check resolved it immediately, moving the tell one step instead of
  removing it.
- Fix: The false source persists for the night and answers every whistle from the same spot in the
  same voice; only walking there and finding nobody resolves it.
- Why this fix: The cheapest probe now returns the same thing in both cases, so resolving it costs what
  the real rescue costs (time and distance in the dark), which is the trade the night is about.
- Rule of thumb: A false cue must also fake the response to the player's cheapest probe of it;
  otherwise the probe is the tell. Price the true resolution at what acting on the cue costs.
- Provenance (verified/assumed): first-hand: node run over six seeds before the fix (real missing
  answered, the false-whistle night did not) and after (the false source answers).
- Composed: sevin/E5, ideas:GAME-DESIGN/disappearance/call-without-a-name
- Link: Sevin commit 12095b4; session_0125c7UeqZXhwxqnu8spbVdh

## E10 — state without a render reads as broken
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [gamedev][state][rendering]
- What: A night rework added a sleeping flag to teammates (skipped by the sim, deaf to whistles) but no
  render path for it. At the two o'clock wake the owner saw everyone sitting up at the fire and
  reported that nobody went to sleep, although the sim had them all asleep.
- Why built: The sim change was made and checked in node; the renderer was not touched because nothing
  about it seemed to need changing.
- Design: A new boolean on an entity, read only by sim logic.
- Got right: The sim side was correct: sleeping members were not ticked and did not answer whistles.
- Where/why it failed: The player only sees what the renderer draws; a state with no visual is, to the
  player, a state that does not exist, and the report looks like a logic bug.
- Fix: Sleeping members are hidden in the tents at camp and drawn lying down elsewhere.
- Why this fix: It makes the new state visible at the moment the owner checks it, which is the only
  verification that counts for a play-tester.
- Rule of thumb: Every new entity state the player is meant to notice needs a render path in the same
  change; a state the renderer ignores gets reported as the logic not working.
- Provenance (verified/assumed): first-hand: the owner's report, the sim code (sleeping set at sleep),
  and the render code (no reference to sleeping) were all read before the fix.
- Composed: N/A
- Link: Sevin commit f94ce3f; session_0125c7UeqZXhwxqnu8spbVdh

## E9 — check the deploy before the design
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [github][pages][deployment][process]
- What: The owner tested a change ("building a camp is the sum of the hands on it") and said it did not
  work; the agent treated that as a design rejection and replaced the formula. Later the Actions list
  showed that exact commit's Pages run had FAILED, so the owner had been playing the previous build.
- Why built: Every quick patch was pushed straight to main and reported as deployed on push, without
  reading the Pages run.
- Design: Push to the branch and to main, report the commit as live.
- Got right: The run after it deployed, so the replacement shipped; the failure was found only because
  the owner later asked for a push and the run list was read.
- Where/why it failed: A push is not a deploy. One run in forty-four failed, and the report said
  "deployed" anyway; the owner's "that doesn't work" was about a build they never received, and the
  agent re-designed instead of re-deploying.
- Fix: After pushing, read the Pages workflow run for that commit; report it live only on success. When
  the owner says a change does not work, check that commit's run conclusion before touching the design.
- Why this fix: It costs one API call and separates "the idea is wrong" from "the idea never arrived",
  which otherwise look identical from the owner's side.
- Rule of thumb: A push is not a deploy; read the deploy run for the commit before calling it live,
  and before re-designing anything the owner says does not work.
- Provenance (verified/assumed): first-hand, verified in the Actions run list: run 43 (f31a67f)
  conclusion failure, run 44 success.
- Composed: dog/E5, the-game-prologue/E8
- Link: Sevin commits f31a67f, 6382018; session_0125c7UeqZXhwxqnu8spbVdh

## E8 — unreachable objective must stay visible
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [gamedesign][rendering][hallucination]
- What: A mirage object (castle, chest, hole) appears at the end of a dead-end clearing and draws away as
  the player walks at it. First placed fourteen metres ahead of the player along the spur, it landed
  past the clearing inside dense forest, and a headless screenshot showed only tree trunks; the
  stretch effect had nothing to stretch toward.
- Why built: The retreat had to read as the world stretching, which needs the object in view the
  whole time it recedes.
- Design: Anchor the object at the clearing's centre, the one open sightline, and scale it up as its
  distance grows (up to four times), so it stays above and between the trunks while it backs off;
  low kinds (chest, hole) carry their own light or glow.
- Got right: Driving the retreat from the player's attempt to walk (input forward while facing it), not
  only from closing distance, kept the stretch going when the player was pressed against the wall.
- Where/why it failed: A position computed from the player (ahead by a fixed distance) ignores what
  stands between, and a receding object falls behind occluders exactly when the effect should peak.
- Fix: Place from the level's open space, not from the viewer, and compensate recession with scale and
  light rather than letting it disappear.
- Why this fix: The illusion is about distance that will not close; an object you cannot see reads
  as a bug, not as distance.
- Rule of thumb: An objective that must stay out of reach must stay in sight: anchor it to open ground,
  grow it as it recedes, and drive the recession from the attempt, not just the distance.
- Provenance (verified/assumed): first-hand: verified with headless screenshots before (trunks only) and
  after (the chest visible and lit in the clearing).
- Composed: N/A
- Link: Sevin commit 6f53331; session_0125c7UeqZXhwxqnu8spbVdh

## E7 — split night draw once save between
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [gamedev][state][determinism]
- What: A night that used to resolve in one call (sleep to dawn, a fixed NIGHT_DRAWS from the run
  stream) was split so the player wakes at two and plays the small hours before dawn. The dawn half
  needs the weather, call and false-call rolls the night already owes.
- Why built: The owner wanted a rescue event in the dark, inside the night, with the player in control.
- Design: The evening sleep draws the WHOLE night's fixed count at once, uses the take rolls then, and
  stores the rest (weather, call, false call, bearing) in sim.night, which is plain save data. Dawn,
  whether reached by sleeping again or by staying awake to six, reads them from sim.night and clears it.
  A save from before the split (no sim.night) derives the dawn rolls from a side hash of seed and day.
- Got right: The roll count per night is unchanged, so a run resumed from any point regenerates the
  same world; stashing the draws instead of drawing at dawn keeps the count independent of what the
  player did in between (awake, asleep, saved and quit).
- Where/why it failed: The obvious split (draw the take at sleep, draw weather and call at dawn) makes
  the number of draws depend on the path to dawn and forks resumed runs; nothing errors.
- Fix: Draw once at the first boundary, persist the unused values as save state, consume them later.
- Why this fix: It is the house rule (anything that gates a draw is save state) applied across an
  interactive gap: the gap can be any length or saved mid-way without moving the stream.
- Rule of thumb: When a fixed-draw event is split by player time, draw it all at the first boundary
  and keep the unused rolls in save state for the later half, with a side-hash fallback for old saves.
- Provenance (verified/assumed): first-hand: verified in node that sleep then dawn (two calls) advanced
  the day and kept the night's draw count; the old-save fallback path was read, not run.
- Composed: seven/E27
- Link: Sevin commit f813ed7; session_0125c7UeqZXhwxqnu8spbVdh

## E6 — removed anchor strands workers
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [ai][gamedev][simulation]
- What: After the player took the camp down, every teammate on auto stood idle beside the player for
  the rest of the day, though the woodpile was still on the ground and the deadfall still needed
  cutting. Owner report; root cause read in sim.js.
- Why built: Teammates have tasks anchored to the camp: "keeping camp" (the auto default), and every
  shift's "home" was the camp. With no camp, the code's answer for both was "stay with the player":
  the keep-camp branch set called=true with no camp, the strike set called=true on keep-camp members,
  and the shift-end rule (from 16:30, an hour and a half before dusk) also set called=true with no
  camp. called is a per-day flag that only dawn clears.
- Design: One fallback (follow the player) for three different absences: no camp to keep, no camp to
  deliver to, and no camp to sleep at.
- Got right: Following the player IS right at dusk with nowhere to sleep; that was the case the
  fallback was written for.
- Where/why it failed: Removing the anchor fired the night-time fallback in the middle of the day, and
  the fallback was sticky (a day flag), so the utility re-scoring every hour could not undo it. The
  pile the camp left behind, and the deadfall, were still valid work that the fallback never looked
  at. A gate keyed to the shift end (16:30) instead of the event it stood for (dusk) widened it.
- Fix: When the camp goes, keep-camp becomes gather (keeping a camp is keeping its wood); gathered wood
  goes to the camp, else the marked site, else the pile the last camp left; the strike only forces
  auto members to re-score at once; "stay with the player" fires only at dusk with no camp and no
  site; with a site, the evening home is the site.
- Why this fix: Each absence gets the fallback that matches what still exists (a pile, a site, a
  deadfall), and the one sticky fallback is confined to the event that justifies it, so nothing
  strands the team for a whole day.
- Rule of thumb: When an agent's anchor object can be removed, give each task that references it a
  fallback that points at what still exists, and never let a removal trigger a sticky day-long
  fallback written for a different event; key that fallback to its event (dusk), not a nearby window.
- Provenance (verified/assumed): first-hand: root cause verified by reading the three code paths and
  by a node run showing all five auto members idle for three game hours after a strike; the fix was
  shipped without a re-run at the owner's request (no tests on quick patches).
- Composed: august-10/E8
- Link: Sevin commit after 68c7a7b (idle after strike fix); session_0125c7UeqZXhwxqnu8spbVdh

## E5 — day keyed false whistle leaks on the second night
- Date: 2026-10-12
- Project: Pappydapimp69/sevin
- Tags: [gamedesign][disappearance][deduction]
- What: Composed Sevin's false wake whistle (about a third of quiet nights, bearing drawn fresh from
  a side hash of seed and day) with Seven's cross-night bearing-consistency tell, read with a
  correct two-observation Bayes update, to see how long the false whistle keeps a take ambiguous.
- Why built: Sevin E1 shipped false whistles so the whistle no longer proves a swap. Seven E23 says
  the learnable tell is a call that repeats from the same direction. A missing member in Sevin
  whistles at the wake EVERY night, from a spot that barely moves; a day-keyed false whistle comes
  from a new random spot each time, so the two may not compose.
- Design: Seeded Monte Carlo, 30000 runs x 14 nights, take prior 0.15 per night, missing for 2-5
  nights, real spot drifts one of 24 sectors with chance 0.3, player hears 8 directions. Posterior
  P(someone missing) measured by frequency for a lone whistle after a silent night and for two
  consecutive whistles from the same heard direction, plus an exact two-night slice and E43's
  doubled-prior bug as a negative control. Alternatives tried: a per-run stable phantom spot, and
  phantom episodes that last and drift like a take.
- Got right: E1's fix does what it claims for one night: a lone whistle after silence is only 0.346
  sure (exact slice agrees in kind), so the wake no longer announces the swap the instant it happens.
- Where/why it failed: On the second night it is announced anyway: two whistles from the same heard
  direction mean someone is missing 0.957 of the time (exact slice 0.930). A fresh bearing per day
  is consistent across nights only 1 in 8 times, the missing nearly always. A stable phantom spot
  fixes pairs only to 0.792 and makes any whistle from another direction proof (1.000). Even
  take-shaped phantom episodes at equal rate gave 0.652, not the 0.500 predicted, because a take
  preempts a running phantom.
- Fix: Make false whistles come in EPISODES with the same shape as a take: start on a side-stream
  hazard, last the same 2-5 nights, hold a spot that drifts at the same rate, and never yield to a
  take mid-episode (run both independently), then tune the episode rate rather than the per-night
  rate. Coarser hearing helps only a little (4 directions with false rate 0.5 still gave 0.858).
- Why this fix: A tell built on consistency can only be neutralised by noise that is consistent
  too; a per-night false-positive rate attacks the single observation and leaves the sequence
  untouched, and the sequence is exactly what E23 trains the player to read.
- Rule of thumb: False positives that hide a hidden swap must match the real cue's behaviour over
  time, not just its per-night rate: a day-keyed false whistle (a third of quiet nights) hides a take
  for one night (0.346) but two same-direction whistles are 0.957 proof; give phantoms take-shaped
  episodes.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry; numbers are
  copied from its run. The take prior, drift rate, missing duration and 8 heard directions are
  design assumptions borrowed from Seven E23/E25, not read from Sevin's code.
- Composed: pappydapimp69__sevin/E1, pappydapimp69__seven/E23, pappydapimp69__seven/E43, ideas:GAME-DESIGN/disappearance/call-without-a-name
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__day-keyed-false-whistle-leaks-on-the-second-night.py
- Prediction: (written before the run) P1 lone whistle 0.25-0.45 and same-direction pair at least
  0.90; P2 stable phantom pair at most 0.60 with off-direction whistle at least 0.95; P3 phantom
  episodes pair within 0.05 of p/(p+q)=0.500 and at most 0.60; P4 4 directions with false rate 0.5
  drops the pair below 0.90; P5 doubled prior lowers the exact pair posterior by over 0.10.
- Observed: RESULT: FAIL 3/5 predictions held; S1 single 0.346 pair 0.957; stable pair 0.792 off-dir
  1.000; episodes pair 0.652 vs 0.500; break(4 dirs,F .5) pair 0.858; exact 0.930 vs doubled 0.732
- Scenarios: 1) Sevin as shipped, day-keyed false whistle at 1/3, 8 directions; 2) per-run stable
  phantom spot; 3) take-shaped phantom episodes at equal rate; 4) built to BREAK the claim: 4 heard
  directions and false rate 0.5 (pair still 0.858); 5) exact two-night slice with E43's doubled
  prior as negative control (0.930 vs 0.732).
- Link: session; brain train loop round 2; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__sevin.md#E11 · compatible · no sandbox · Sevin commit 12095b4; session_0125c7UeqZXhwxqnu8spbVdh
- Audited: 2026-10-12 · modeled · Read the entry and reran its stored sandbox (20 s, stdlib, fixed seeds). The numbers are computed, not built in: single whistle 0.346 and same-direction pair 0.957 come from 30000 seeded runs of 14 nights, the exact two-night slice (0.930, doubled-prior 0.732) is a separate hand calculation that agrees in kind, and the rerun printed identical figures, so the first claim (a day-keyed false whistle hides a take for one night only) is genuinely tested. Two limits keep this from a pass. First, the model is a re-implementation of Sevin's whistle from design assumptions borrowed from Seven (take prior 0.15, 24 sectors, 8 heard directions, drift 0.3); Sevin's actual code was never run, so the claim about the shipped game is only modeled. Second, the Rule of thumb recommends take-shaped phantom episodes as the fix, but the sandbox shows that fix still leaves a pair at 0.652 against its own 0.500 target (and a single whistle at 0.540), and the rerun printed 'RESULT: FAIL 3/5 predictions held' because P2 and P3 missed; the entry reports the misses in its body but the Rule does not carry the 0.652 residual, so it reads as stronger than the evidence. · scheduled brain train session; loop 1 pass 3 audit; session_01FbNV33qUVqkwoe1aojdkah

## E4 — stop asking state the lean and build
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [workflow][agent][questions]
- What: In one design-and-build session the agent ended most turns with follow-up questions to the owner
  (about 14 closing question sets). Mined against the owner's replies: about half were never answered
  (the owner moved on with a new idea), one drew "you're overthinking this", and nearly every one that
  WAS answered went the way the agent had already said it leaned (tree outside the meter, the chop
  follows the body, nothing left behind, findable until the fruit). The owner said the questions slow
  the workflow and must be eliminated.
- Why built: The agent treated every open design edge as the owner's call and asked before proceeding,
  to avoid building the wrong thing and to preserve owner agency.
- Design: Each reply ended with a numbered list of decisions for the owner, often including edge cases
  of features not yet built (does the refusal zone lift, what happens to a body after a day, should
  the trunk turn true at dawn, is twenty minutes intended).
- Got right: Questions that changed what was built THAT turn and had no stated default were answered
  and used (whether the tree depends on the sanity meter; whether a wake gives the swap away).
- Where/why it failed: Most questions were about edges the owner had not reached yet, or re-asked a
  number the owner had already stated (twenty minutes). The owner answers by building forward, so a
  question about a later edge is dead weight, and asking about a stated number reads as not listening.
  When the agent already had a lean, the owner almost always took it, so the question bought nothing.
- Fix: Replace the closing question with the decision: state the lean as the default, build it, and
  report it in one line as a call the owner can reverse. Park edges of not-yet-built features in the
  project working list, not in the reply. Never re-ask a value the owner stated; use it.
- Why this fix: The owner's replies show the cost of a wrong default is one line of correction, while
  the cost of a question is a full round-trip that stalls the build. Reversible defaults reported
  plainly keep owner agency without blocking.
- Rule of thumb: Ask only if the answer changes what gets built right now, nothing the owner said
  settles it, there is no defensible default, and a wrong guess is costly to undo; otherwise state the
  lean, build it, and report the call in one line.
- Provenance (verified/assumed): first-hand, verified by reading the owner's replies to each question
  set in this session's transcript and counting which were answered, ignored, or answered with the
  agent's stated lean.
- Composed: N/A
- Link: Sevin session 2026-10-11/12, commits f813ed7..b49f218; session_0125c7UeqZXhwxqnu8spbVdh

## E3 — never reask a stated number
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [workflow][agent][questions][pacing]
- What: The owner specified that the small-hours rescue window should always take twenty real minutes.
  The agent questioned the number (suggesting five, citing a four-minute day) and asked whether twenty
  was intended. The owner replied that the agent was overthinking it, and later said "ready to build"
  without answering; the agent then built twenty anyway.
- Why built: The agent pressure-tested every premise, including explicit numbers, to catch pacing
  problems before they shipped.
- Design: A pacing concern was raised as a blocking question in the middle of a design discussion,
  alongside four other concerns.
- Got right: The underlying concern (drain per game hour would vary with the wake time) was real, and
  the owner's own next idea (always wake at two) removed it without the agent's suggestion.
- Where/why it failed: An explicit owner number is a decision, not a premise. Questioning it costs a
  round-trip and signals the instruction was not taken, while the tuning risk is cheap to fix after
  play. The real concern dissolved once the owner's design moved on.
- Fix: Build the owner's stated value as a named constant, mention the risk once in the report as a
  tuning note with the alternative, and let play decide.
- Why this fix: It honours the instruction, keeps the build moving, and still surfaces the risk where
  the owner can act on it after seeing the game, which is where pacing is actually judged.
- Rule of thumb: An explicit value from the owner is built as stated; a concern about it goes in the
  report as a one-line tuning note with the named constant, never as a question.
- Provenance (verified/assumed): first-hand, verified against the transcript of this session: the
  question, the reply, and the constant SMALL_HOURS_SEC = 300 shipped in sim.js.
- Composed: N/A
- Link: Sevin commit f813ed7; session_0125c7UeqZXhwxqnu8spbVdh

## E2 — menu focus survives repaint
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [ui][input][gamepad]
- What: Every choice on a DOM menu (team cards, the dusk plan, the game-show lifelines) rebuilt part of
  the panel with replaceChildren, which destroyed the focused button; on gamepad the selection jumped
  back to the top-left item (or the primary button) after every press. Mouse and touch never showed it.
- Why built: Menus repaint by rebuilding their content, the simplest way to reflect new state.
- Design: A focus memory per menu name, recorded on focusin as (label, which occurrence of that label,
  index in the focusable list). A MutationObserver on the modal restores it whenever focus has left
  the modal; show() restores it when the same menu opens again, else focuses the primary button.
  Spent options (used lifelines) stay focusable with aria-disabled and a no-op click instead of the
  disabled attribute, so focus has somewhere to stay.
- Got right: Matching by label first survives a rebuilt node; falling back to index survives a label
  that changes on press ("Light the fire" becomes "Feed the fire").
- Where/why it failed: A disabled button leaves the focusable list, so when the option the pad was on
  became disabled the index fallback landed on an unrelated control (an answer button).
- Fix: Keep spent controls focusable (aria-disabled, greyed, inert click) rather than disabled, and
  restore by label, then nth, then index.
- Why this fix: It is one generic mechanism for every menu, no per-screen focus code, and it holds for
  rebuilt nodes, relabelled nodes and spent nodes alike; verified in a headless browser on the dusk
  plan, the team select and the lifeline row.
- Rule of thumb: When pad-driven menus rebuild on choice, restore focus by label then index from a
  per-menu memory, and keep spent options focusable but inert instead of disabled.
- Provenance (verified/assumed): first-hand, verified in Playwright: focus stayed on the pressed control
  after repaint on three menus; not tested on a physical gamepad.
- Composed: N/A
- Link: Sevin commits a2e9c19, b49f218; session_0125c7UeqZXhwxqnu8spbVdh

## E1 — false wake cue
- Date: 2026-10-12
- Project: Pappydapimp69/Sevin
- Tags: [gamedesign][disappearance][deduction]
- What: A night rework woke the player at two every night and had the missing person whistle from
  the dark a few seconds later, but only on nights when someone had been taken. Since a take always
  installs a same-name fake at camp, the whistle announced the swap the instant it happened.
- Why built: The whistle was the cue to go out on the timed rescue window.
- Design: Unprompted answer scheduled for every active missing person at the wake.
- Got right: Waking every night (not only on takes) already stopped the wake itself from being news.
- Where/why it failed: The cue was present if and only if a swap happened, so it carried the full
  answer to the deduction game; the existing Brain idea that false calls keep a rescue cue from
  announcing applied but was not consulted at that fork.
- Fix: About a third of quiet nights now carry a whistle too, in a teammate's real voice from a spot
  thirty to fifty-five metres off, with nobody there; derived from a side hash of seed and day.
- Why this fix: The cue still sends the player out on a real night, but its presence alone no longer
  proves a take; measured 13 of 39 quiet test nights produced a false whistle.
- Rule of thumb: Any cue that fires only when a hidden swap happened is the answer, not a cue; give it
  false positives from a side stream before shipping.
- Provenance (verified/assumed): first-hand, verified with a node run over 39 seeds (13 false whistles)
  after the fix.
- Composed: ideas:GAME-DESIGN/disappearance/call-without-a-name
- Link: Sevin commit 0772b64; session_0125c7UeqZXhwxqnu8spbVdh
- Cited-by: 2026-10-12 · projects/pappydapimp69__sevin.md#E5 · incompatible · sandboxes/2026-10-12__day-keyed-false-whistle-leaks-on-the-second-night.py · observed RESULT: FAIL 3/5 predictions held; S1 single 0.346 pair 0.957; stable pair 0.792 off-dir 1.000; episodes pair 0.652 vs 0.500; break(4 dirs,F .5) pair 0.858; exact 0.930 vs doubled 0.732 · session; brain train loop round 2; session_01QGT1LfmPHPG99JEGaPhBwB
