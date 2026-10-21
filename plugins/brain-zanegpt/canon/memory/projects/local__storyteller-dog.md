# local/storyteller-dog — lessons

Project: local/storyteller-dog. Newest first.

---

## E1 — storyteller dog interrupt at doubt not at climax
- Date: 2026-10-17
- Project: local/storyteller-dog
- Tags: [narrative][oral-storytelling][simulation][sandbox]
- What: Modelled The StoryTeller's frame device, a listening dog who interrupts the teller with questions, as a
  12-beat story where open doubt drags immersion down and each interruption answers the doubt but halves
  immersion, then compared where the interruptions land.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had information-gap tension, transportation and
  objection pre-emption, but nothing on when an in-story listener should break in to voice the audience.
- Design: Stdlib beat loop: stakes rise to a climax at beats 9-10, doubt is raised at beats 2 and 5, immersion grows
  with stakes and falls with open doubt, felt impact = immersion x stakes. Runs: story answers its own doubt at
  beat 8 or never; a one-interruption sweep over every beat; a doubt raised at the climax; a clear-story BREAK;
  a 9-cell sweep of break share and doubt drag (+-20%) with a small and a large doubt at the climax.
- Got right: With the story answering at beat 8, interrupting at the doubt beats scored 1.27x of none and the same two
  interruptions at the climax 0.89x; the sweep was positive only at beats 2-7 and negative at every beat from 8
  on; in a clear story the same interruptions scored 0.88x, so the help comes only from real doubt.
- Where/why it failed: The first model let doubt stay open forever, and there even a mid-climax answer beat silence (1.17x), so
  the climax rule needs the story to answer later. The refuted call: pre-empting a climax doubt with an aside at
  beat 7 scored 5.63, below letting it ride (5.68) or answering mid-climax (5.71); and the sweep showed riding a
  small climax doubt beats that aside in only 6 of 9 cells, so the small-doubt case is parameter-fragile, while a
  large climax doubt was best answered at once in 9 of 9.
- Fix: Put the listener's questions where doubt is born and immersion is still low; near the climax let the listener
  break in only for a large doubt or one the story will never answer, and spend no aside pre-empting a small one.
- Why this fix: A break costs a share of current immersion, so it is cheap early and expensive late, while an unanswered
  doubt costs a little on every beat it stays open; the crossover sits before the climax, not inside it.
- Rule of thumb: Let a listener character voice the audience's doubt early, at the beat it arises; near the climax let it
  speak only for a large doubt, since for a small one a break, even a pre-emptive aside, was a toss-up (6 of 9).
- Provenance (verified/assumed): Verified first-hand by the sandbox; the frame device details checked against
  Wikipedia's Storyteller article and a Den of Geek retrospective cited in the kernel. Model parameters are toy values.
- Composed: ideas:SYSTEM/narrative/tension-as-information-gap, ideas:ORAL-STORYTELLING/transportation/persuasion,
  ideas:PITCH/persuasion/preempt-objections-refutationally
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-17__storyteller-dog-interrupt-at-doubt-not-at-climax.py
- Prediction: v1: two climax interruptions score at least 10% below none. v2 (after v1 failed): with the story answering
  at beat 8, doubt-timed at least 10% above none and climax-timed below none; sweep positive only at beats 2-7;
  a climax doubt raised and answered at beat 7 scores at least 5% above letting it ride; clear story below none.
  D (after v2): small climax doubt, riding beats the beat-7 aside in 9/9 cells; large doubt, answer-now wins 9/9.
- Observed: RESULT: FAIL C refuted: pre-empting a climax doubt with an aside at beat 7 scored 5.63, below letting it ride
  (5.68) or answering mid-climax (5.71); held: doubt-timed 1.27x and climax-timed 0.89x of no-interrupt, never
  answered climax-timed 1.17x, clear story 0.88x; D sweep: small climax doubt ride>aside 6/9, large doubt
  answer-now>ride 9/9 (D prediction missed) (v1 FAIL: climax-timed 1.17x when doubt is never answered).
- Scenarios: 1) story answers its doubt at beat 8, doubt-timed vs climax-timed; 2) story never answers; 3) one
  interruption swept over all 12 beats; 4) doubt raised at the climax: ride, answer now, answer after, pre-empt at
  beat 7; 5) BREAK: clear story with no doubt, same interruptions; 6) sweep of break share and doubt drag with a
  small and a large climax doubt
- ZaneGPT verdict: weak — The rule has already failed two predictions (v1, then v2's pre-empt claim and D's 6/9 toss-up), so the surviving "early yes, large-doubt-at-climax yes" is a post-hoc fit to one hand-built model with one story shape and fixed constants, and none of it has been tested against real audiences.
- Hidden assumption: The simulator's hand-chosen rules (a flat halving of immersion per interruption, doubt drag as a fixed penalty, felt impact = immersion x stakes) are treated as a model of real listeners, so the margins between "toss-up" and "win" come from those constants and not from anything about audiences or stories.
- Would prove it wrong: A sweep over the halving factor (say 0.3 to 0.9) and over the doubt raise beats, not just break share and drag at ±20%, in which "early, at the beat it arises" stops beating no-interrupt, or in which large-doubt answer-now stops beating ride. The same result in a different story shape (climax at beats 5-6, or three doubts) would also break it.
- Break scenario: Move the climax to beats 4-5 and raise the doubt at beat 4 with the story answering at beat 6. The rule says to interrupt for a large doubt near the climax, but here the interruption would halve immersion at peak stakes and the doubt resolves itself two beats later. Run it with the halving factor at 0.7 and 0.3. If ride beats answer-now in either run, the "large doubt, speak" half is an artifact of this one 12-beat shape.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 81dbf6807798
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

