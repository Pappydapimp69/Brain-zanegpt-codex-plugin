# local/storyteller-hans — lessons

Project: local/storyteller-hans. Newest first.

---

## E1 — hans blind promise binds the dearest
- Date: 2026-10-17
- Project: local/storyteller-hans
- Tags: [narrative][bargains][simulation][sandbox]
- What: Modelled the blind promise in The StoryTeller's Hans My Hedgehog, the lost king's "first thing to greet me at home",
  as a household race to the gate, and compared its expected cost with the dog he pictured and with named or narrowed promises.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had the term-limited cure from the same episode and the
  kind-versus-instance quest match, but nothing on how an open-ended promise prices itself by who is likely to arrive first.
- Design: Stdlib, exact fractions. Greeters dog (worth 1; loose arrives at 2, chained never), servant (worth 5, arrives at 2.5)
  and daughter (worth 100; at the window 1, in the chapel 3, away never), with integer weights per state; every state
  combination is enumerated, the first arrival is bound, and cost = sum of weight share x value of the first arrival.
- Got right: Lost for days (daughter at the window 2 of 3) the daughter was first 2/3 of the time and the promise cost 67.67
  against an imagined 1; after a day's hunt it cost 3.00; naming the dog fixed it at 1.00 and "the first animal" at 0.50,
  while "the first person" still cost 68.33 because the daughter is a person; with her watching and nobody else free it
  reached her full worth, 100.
- Where/why it failed: The gap only exists when the dearest person can plausibly arrive first: in the BREAK where the dog
  always waits at the gate, the blind promise cost 1.00, the same as imagined. Absence is not a variable in the model: a day's
  hunt with her watching anyway cost the same 67.67, so her watching drives the cost and the claim that a long absence makes
  her watch is assumed from the episode. The weights and times are toy numbers; scenarios 6 and 7 were added after the first check.
- Fix: Before an open-ended promise, list who could plausibly meet the condition first and multiply each one's chance by
  their worth; price it by that sum, and if it is too high, name the thing (my dog) or narrow the class so it excludes the
  people you value.
- Why this fix: The promise binds whichever arrival satisfies its condition, so its cost is a probability-weighted sum over
  arrivals; one dear arrival with a real chance outweighs the cheap one you pictured, and naming an instance removes it.
- Rule of thumb: An open-ended promise binds to whoever arrives first, so price it by the chance the dearest person is
  first times their worth, not by the thing you pictured; it is costliest when the people who love you are watching for
  you, which a long absence makes likely. Name the thing, or a class that leaves them out.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode details checked against Wikipedia's
  Storyteller article and the Grimm KHM 108 text page cited in the kernel. Values, times and weights are toy numbers.
- Composed: ideas:RPG/quest-design/existence-gating-solves-when-not-which, ideas:DECISION-MAKING/cognitive-bias/base-rate-neglect
- Sandbox: sandboxes/2026-10-17__hans-blind-promise-binds-the-dearest.py
- Prediction: Lost for days: daughter first 4/6, cost 67.67 vs imagined 1; day's hunt: daughter 0, cost 3.0; named dog 1.0;
  first animal 0.5; first person 68.33; BREAK dog always at the gate: 1.0. Added after the first check, before rerun: day's
  hunt with her watching anyway 67.67; she always watches with nobody else free 100.
- Observed: RESULT: PASS lost for days cost 67.67 vs imagined 1 (daughter first 2/3); day's hunt 3.00; named dog 1.00;
  first animal 0.50; first person 68.33; day's hunt with her watching anyway 67.67; she always watches with nobody else
  free 100.00; BREAK dog always waits at the gate 1.00.
- Scenarios: 1) lost for days (canon); 2) a day's hunt; 3) named promise "my dog"; 4) class promise "first animal";
  5) class promise "first person"; 6) a day's hunt but she watches anyway; 7) she always watches, dog chained, servant
  away; 8) BREAK: the dog always waits at the gate
- ZaneGPT verdict: weak — the rule is arithmetic on invented weights, and the "long absence makes love-watchers likely" link is assumed rather than modelled, so the run shows the sum is consistent, not that the rule is true.
- Hidden assumption: The cost ranking is driven by the chosen weights (daughter 100 vs dog 1) and by the arrival times and state weights being right, and that "first to greet" means earliest to reach the gate. The "watch for a long absence" claim is encoded as a state weight, not derived, so the model assumes its conclusion.
- Would prove it wrong: Vary the daughter's weight and watching probability. If the cost ordering (lost for days > day's hunt > named dog) survives only when the daughter's "watching" weight is raised for long absences, or if it flips at plausible values (say daughter 10, watch 1/6), the rule is a parameter artefact. Also, a result where the lost-for-days daughter-first probability is the same as the day's-hunt one under identical weights would show absence length is not doing the work.
- Break scenario: The daughter waits in the chapel (arrives at 3) and the dog is loose at the gate (arrives at 2), with the servant away, in every state, regardless of absence length. The daughter is never first, so cost is 1.0 for all promise types. The "price by the dearest person's chance" rule then predicts nothing, and the only thing that matters is who is physically nearest. The existing BREAK (dog always at the gate: 1.0) only tests this partly, because it was built so the rule's own formula still gives 1.0.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 0720668fca81
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

