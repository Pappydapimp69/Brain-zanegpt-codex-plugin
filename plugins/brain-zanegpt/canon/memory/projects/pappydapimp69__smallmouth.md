# pappydapimp69/smallmouth — lessons

Project: pappydapimp69/smallmouth. Newest first.

---

## E3 — band must wrap every non firsthand term or extras reopen the gate
- Date: 2026-10-09
- Project: pappydapimp69/smallmouth
- Tags: [gamedesign][simulation][testing][state]
- What: smallmouth#E1's "talk can never start a scene, by construction" guarantee (hearsay channel banded at 0.25 inside a 0.30 confront gate) was composed with august-10#E6's additive-bonus-outside-the-gate anti-pattern. If a personality or mood bonus is added to the opinion total after the hearsay clamp, the band still reports 0.25 while gossip alone crosses the gate.
- Why built: to find out whether a structural band guarantee survives the ordinary later addition of trait bonuses, and whether smallmouth#E2's fires-at-least-once audit would notice if it did not.
- Design: Deterministic 8-agent, 168-tick sandbox with a fixed retelling schedule, every rumour negative (0.05 per retelling) about two subjects, one genuine firsthand incident at tick 100, confrontation at total <= -0.30 with a discharge reset. Four runs: band on the gossip channel only; the same plus a 0.10 bonus on two prickly listeners applied outside the band; a 0.04 bonus (inside the 0.05 slack, built to break the claim); and the band wrapped around hearsay plus bonus together.
- Got right: the channel-level clamp itself held in every run (max hearsay channel 0.25), and the 0.04 break scenario showed the claim must be narrowed rather than stated as "any extra breaks it" - slack under the gate is real and usable. The fires-at-least-once audit stayed green throughout.
- Where/why it failed: with the 0.10 bonus applied outside the band, 5 of 6 confrontations were hearsay-only (no firsthand cause) and the hearsay-side total reached the 0.30 gate, though the channel statistic still read 0.25. Every audit that inspects the channel, and the fires-at-least-once test, passed in all four runs because a firsthand incident exists; only the provenance check (every confrontation traces to a firsthand cause) failed. Predicted max total of about 0.35 was wrong in detail: it stops at 0.30 because the confrontation fires and discharges the moment the gate is touched.
- Fix: clamp the SUM of everything non-firsthand (gossip plus every trait, mood or role bonus) into the band, so extras share the band's headroom instead of stacking on top. Audit the gating quantity's hearsay-side total, not the channel, and keep E1's "every confrontation has a firsthand cause" assertion as the test, since E2's fires-at-least-once cannot see an extra gate-crossing path.
- Why this fix: wrapping makes the guarantee structural again at the point where the gate reads the value (S4: 0 hearsay-only confrontations, max 0.25, with the same 0.10 bonus), whereas picking a smaller bonus (S3, 0.04) only works while the bonus stays under the slack of 0.05 and silently fails when someone adds the next one.
- Rule of thumb: A band that keeps a diffusion channel strictly inside a behaviour gate must wrap the whole non-firsthand sum, because any bonus added after the clamp (august-10#E6's shape) reopens the gate while the channel statistic still looks safe; a fires-at-least-once test cannot catch this, so also assert that each gate-crossing traces to a firsthand cause, and for tested sizes keep band plus summed extras strictly below the gate.
- Provenance (verified): Verified first-hand in the sandbox run of this session: S1 0 hearsay-only, S2 5 hearsay-only of 6, S3 0, S4 0, fires-at-least-once audit green in all four, provenance audit red only in S2. Sandbox abstracts the social sim to a fixed schedule; real smallmouth code was not run here.
- Composed: smallmouth/E1, smallmouth/E2, august-10/E6
- Polarity: compatible
- Sandbox: sandboxes/2026-10-09__band-must-wrap-every-non-firsthand-term-or-extras-reopen-the-gate.py
- Prediction: Band only gives 0 hearsay-only confrontations; a 0.10 bonus outside the band gives at least 2 with max total about 0.35; a 0.04 bonus (break attempt) gives 0; wrapping gives 0; fires-at-least-once audit passes in all four.
- Observed: RESULT: PASS band alone gives 0 hearsay-only confrontations, extras outside the band give 5 (max total 0.30 vs gate 0.30) while the fires-at-least-once audit passes in all 4 runs; extras within slack stay 0; wrapping band over hearsay+extras restores 0. Max total was 0.30 not 0.35 (discharge at first touch). First run FAILED only because my assertion measured total including the firsthand term; harness fixed to measure the hearsay side, results unchanged.
- Scenarios: 1) band on channel only, no bonus; 2) 0.10 bonus added outside the band; 3) BREAK: 0.04 bonus inside the slack, tests whether any outside bonus breaks the band; 4) band wrapped around gossip plus bonus.
- Link: brain train pass 2 (edge), sandbox beside this file; session_01YFLLRpDsfZpRstb2KT2MQy
- Audited: 2026-10-13 · pass · Read the entry and its stored sandbox. The model computes confrontations tick by tick, so the counts are produced by the run, not assumed; the provenance audit separating S2 from the other runs is real. Two limits keep this at pass rather than anything stronger: S2 and S4 are close to arithmetic (a 0.25 band plus a 0.10 bonus must cross a 0.30 gate; a clamp of the sum cannot exceed the band), so only S3 genuinely probes the boundary, and only two bonus sizes (0.04 and 0.10) were run, so the Rule's "strictly below the gate" edge at exactly 0.05 was not exercised. The Rule of thumb is scoped to the tested sizes, which the sandbox covers, and the fires-at-least-once point holds because the scenario contains a firsthand incident. The claim concerns a design pattern, not the real smallmouth code, and the entry says so. · scheduled brain train loop 2 pass 3 audit, session_01BK3tgfuX3pNnFPwVrbmiSH

## E2 — mechanic unreachable under real dynamics
- Date: 2026-08-05
- Project: pappydapimp69/smallmouth
- Tags: [gamedesign][simulation][testing][gamedev]
- What: Two of the simulation's advertised mechanics — a rumour mutating as it
  is retold, and an NPC publicly confronting someone — never fired once in a
  simulated week, across every seed. Both were implemented, both were
  documented in the README as things the town does, and both had passing unit
  tests. Neither had ever happened.
- Why built: Smallmouth is a village where the player's only verb is telling
  one person one sentence, and the week's outcome is whatever the town does
  with it. Distortion-on-retelling and public confrontation are the two beats
  that turn spread into a story rather than a diffusion curve.
- Design: Rumour tokens accrue `distortion` per hop (0.18) and mutate past 0.5; NPCs confront when a directed opinion edge passes -0.3, with opinion moved by hearing gossip; unit tests covered each mechanic in isolation with hand-authored inputs, and integration tests asserted spread reach and final standing.
- Got right: the integration tests measured real aggregate outcomes over a seed
  set rather than one week, which is why the numbers were trustworthy — and
  printing a full hour-by-hour event trace for a human to read, rather than
  only the summary, is what exposed it. The summary was accurate and said
  nothing about what was absent.
- Where/why it failed: each threshold was unreachable under the system's own
  dynamics, and nothing in the suite could notice. Mutation needed 3 hops at
  0.18/hop, but a separate correct feature (news having a ~20h half-life)
  caps real chains at 2 hops — 0.36, permanently short of 0.5. Confrontation
  needed a -0.3 grievance, but hearsay moved the most-affected edge in the
  entire town to -0.178. The unit tests passed because they hand-built a 4-hop
  chain and assigned an opinion directly — inputs the simulation cannot
  produce. Coverage was total and meaningless: the tests proved the mechanics
  worked given inputs, not that the inputs occur. Worse, the mechanics'
  absence is invisible in any aggregate metric, because a beat that never
  fires subtracts nothing from a number you are already watching.
- Fix: two changes, plus a test class. Change what the accumulating quantity
  is a function of, rather than the threshold: distortion now also accrues
  from how long the teller held the story and from their gossip trait, both
  available at hop 1, so 2 hops reaches 0.5 honestly. And add a second,
  unbanded input channel for the gate: hearsay stays capped below -0.3 by
  design, and firsthand events cross it. Then, for every mechanic gated on a
  threshold, an integration test that asserts it FIRES at least once over the
  seed set — and, for the ones that should stay rare, an upper bound too.
- Why this fix: raising or lowering the threshold would have been the wrong
  move in both cases and would have passed the same blind tests. The thresholds
  were right; what was missing was any path for the system to reach them. The
  transferable audit is cheap: for each threshold constant, compute or measure
  the maximum value actually observed under real dynamics and compare. Here
  that is a two-line log of max distortion and most-negative edge, and it
  answers the question instantly for every gate in the file.
- Rule of thumb: A mechanic with passing unit tests can still be dead code in
  the running system, because unit tests supply inputs the system cannot
  produce — for every threshold-gated mechanic, log the maximum value the
  gating quantity ACTUALLY reaches under real dynamics, and add an integration
  test asserting the mechanic fires at least once; when it does not fire,
  suspect that the quantity is bounded by an unrelated correct feature and
  change what it is a function of rather than moving the threshold.
- Provenance (verified): verified firsthand in this session. Instrumented the
  event log across 10 seeds and measured 0 mutations and 0 confrontations, with
  max distortion 0.36 against a 0.50 gate and most-negative edge -0.178 against
  a -0.30 gate. After the fix, the same 10-seed sweep shows mutations on 10/10
  seeds and confrontations arising only downstream of a firsthand event. Test
  count 16 -> 22, all green; determinism fingerprint stable across repeat runs.
- Link: https://github.com/Pappydapimp69/smallmouth commit 395c933
- Cited-by: 2026-10-09 · projects/pappydapimp69__smallmouth.md#E3 · compatible · sandboxes/2026-10-09__band-must-wrap-every-non-firsthand-term-or-extras-reopen-the-gate.py · observed RESULT: PASS band alone gives 0 hearsay-only confrontations, extras outside the band give 5 (max total 0.30 vs gate 0.30) while the fires-at-least-once audit passes in all 4 runs; extras within slack stay 0; wrapping band over hearsay+extr… · brain train pass 2 (edge), sandbox beside this file; session_01YFLLRpDsfZpRstb2KT2MQy
- Cited-by: 2026-10-11 · projects/pappydapimp69__brainwork.md#E121 · compatible · sandboxes/2026-10-11__ending-passes-hand-built-state-test-but-dynamics-cannot-reach-it.py · observed RESULT: PASS hand-built 4/4; K3 3/4, K6 4/4; lost share K6 0.0014, start(3,3,3) 0.0686; lost at threshold 1: 0 · scheduled brain train session; session_018Fx6YUUQMABGNn8Depe7Ek loop 2 pass 2

## E1 — banded hearsay plus firsthand channel makes antagonists
- Date: 2026-08-05
- Project: pappydapimp69/smallmouth
- Tags: [gamedesign][simulation][ai][narrative-design]
- What: Making an emergent antagonist out of a social simulation, without
  authoring one — and without letting ambient gossip alone be enough to start
  a fight.
- Why built: the town needed a week to escalate into something a player would
  call a story. The obvious lever was to let accumulated gossip drive an NPC
  past a grievance threshold into a public confrontation, so the villain is
  produced by the player's own opening move rather than assigned in the cast.
- Design: A single directed opinion scalar per relationship pair, moved both by hearing gossip about someone and by things that happen to you directly, gating a `confront` exchange at -0.3, with a public confrontation deepening the confronter's own grievance.
- Got right: refusing to raise the gossip contribution until the confrontation
  fired. That would have worked and would have been wrong, and the reason it
  is wrong is already canon — a diffusion channel strong enough to cross a gate
  is strong enough to cross it for the wrong reasons.
- Where/why it failed: one scalar fed by two very different kinds of input
  cannot be tuned. Weak enough that hearsay never starts a brawl means weak
  enough that nothing ever crosses the gate, which is the state it shipped in
  (most-negative edge in the whole town: -0.178 against a -0.30 gate). And the
  confrontation itself was balanced rather than decaying: it deepened the
  grievance that triggered it, so once two agents did cross, they re-enacted an
  identical scene every hour they shared a room, for the rest of the week.
- Fix: split the scalar into two channels summing to the opinion — an ambient
  `gossip` channel hard-banded at 0.25, strictly inside the 0.3 gate, and an
  uncapped `firsthand` channel. Talk can therefore never start a scene, by
  construction. Then notice that the firsthand event needed already emerges for
  free: the utility scorer picks the juiciest novel claim for a present
  listener, and being the SUBJECT of a claim is none of those tests, so agents
  repeat stories to the subject's face unprompted. Tag that as pivotal and
  non-decaying, route it to the firsthand channel, and let the graph's chain of
  custody name who to blame. Finally, make confronting DISCHARGE the grievance
  and transfer a fresh one to the person confronted, so feuds alternate and
  burn down.
- Why this fix: the two-channel split makes the guarantee structural instead of
  a tuning result — no seed and no future coefficient change can let hearsay
  cross the gate. Sourcing the crossing from an incident the scorer already
  produces means the antagonist is genuinely made by the week's events, and the
  measured result is a real strategic axis rather than a slider: over 20 seeds,
  telling the town's biggest gossip reaches 4.45 of 8 people but the subject
  learns of it 4 times in 20, while telling a housebound widow whose day
  intersects his reaches only 2.55 people yet produces 13 face-tellings and 53
  public rows for comparable damage. Reach and drama became independent axes,
  which is what makes "who do you tell" a decision.
- Rule of thumb: When one score is fed by both ambient diffusion and direct
  experience and also gates behaviour, split it into a banded hearsay channel
  sitting strictly inside the gate plus an uncapped firsthand channel, and
  source the gate-crossing from an incident the existing utility scorer already
  produces incidentally — an emergent antagonist needs a firsthand cause, and
  any escalating exchange needs a discharge term or the pair locks into
  repeating the same scene forever.
- Provenance (verified): verified firsthand in this session by 20-seed sweeps
  over six choices of confidant, with the reach / subject-learns / public-rows
  figures above read from the event log, plus a test asserting every
  confrontation in every run is traceable to a firsthand cause and that
  hearsay-only edges never exceed the band. Feud non-locking confirmed by
  trace: 5 alternating rows across a week that decay rather than repeat hourly.
- Link: https://github.com/Pappydapimp69/smallmouth commit 395c933
- Cited-by: 2026-10-09 · projects/pappydapimp69__smallmouth.md#E3 · compatible · sandboxes/2026-10-09__band-must-wrap-every-non-firsthand-term-or-extras-reopen-the-gate.py · observed RESULT: PASS band alone gives 0 hearsay-only confrontations, extras outside the band give 5 (max total 0.30 vs gate 0.30) while the fires-at-least-once audit passes in all 4 runs; extras within slack stay 0; wrapping band over hearsay+extr… · brain train pass 2 (edge), sandbox beside this file; session_01YFLLRpDsfZpRstb2KT2MQy
