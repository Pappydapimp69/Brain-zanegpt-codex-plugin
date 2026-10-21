# local/storyteller-heartless-giant-custody — lessons

Project: local/storyteller-heartless-giant-custody. Newest first.

---

## E1 — heartless giant custody decides not intent
- Date: 2026-10-17
- Project: local/storyteller-heartless-giant-custody
- Tags: [narrative][concurrency][simulation][sandbox]
- What: Modelled the ending of The Heartless Giant, where Leo brings the giant his heart and a brother grabs and squeezes
  it, as a schedule problem: one actor's plan, a third party with one action, and a count of the orderings that kill.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had race conditions and preemption-bounded schedule
  search for code, but nothing on a story resolution that hangs on one actor's choice while another can reach the item first.
- Design: Stdlib; Leo's plan is a list of steps and after each prefix the heart is hidden, exposed or back in the giant;
  the brother's single action is inserted at every position; when he stands r steps away he must see it exposed at
  position p and find it exposed again at p+r; Leo's intent is fixed (give it back), so only reachability varies.
- Got right: The tale's ordering (heart shown on arrival, a speech, then given) killed in 2 of 4 schedules; three steps
  of bargaining raised it to 4 of 6; hidden until a hand-to-hand give made it 0 of 5; a brother who wanted the giant
  spared made the same exposure harmless; a brother 2 steps away killed in 0 of 4 tale schedules and 2 of 6 bargain
  ones; showing it, hiding it, showing it again killed 2 of 6 at hand and 0 of 6 one step away.
- Where/why it failed: The BREAK, Leo keeping the heart hidden on his person the whole way but handing it over by setting
  it down for the giant to pick up, still killed in 1 of 5, so carrying it yourself is not custody. A rule of unbroken
  exposure runs minus the rival's reach missed one case, as predicted: show, hide, show with the brother 2 steps away
  killed 1 of 6, because he saw the first showing and arrived at the second. The reach and split scenarios were added
  after earlier runs, each with its prediction written before the run that tested it.
- Fix: When a resolution rests on one character's choice over an object, list every moment between retrieval and use
  when someone with a different motive can reach it; keep each such window shorter than that person's travel time and
  never re-show the item at the moment a rival who saw it earlier would arrive; to make a reversal land, open one window on purpose.
- Why this fix: The count of deadly orderings depends only on when the item is reachable and how far the rival is, so the
  holder's intent never enters it; a set-down handoff reopens a window even when the carrier never let go along the road.
- Rule of thumb: A choice over a shared item is settled by who can reach it, not by what the holder means; count the
  moments it sits within a rival's reach, a set-down handoff is one, and a second showing can meet a rival already on his way.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode ending checked against Wikipedia's
  Storyteller article and TheTVDB synopsis cited in the kernel.
- Composed: ideas:CONCURRENCY/testing/enumerate-schedules-by-preemption-count, ideas:CONCURRENCY/correctness/race-conditions
- Sandbox: sandboxes/2026-10-17__heartless-giant-custody-decides-not-intent.py
- Prediction: Tale 2 of 4 schedules kill; long bargain 4 of 6; hidden hand-to-hand give 0 of 5; aligned brother 0 of 4;
  BREAK set-down handoff 1 of 5; tale with brother 1 step away 1 of 4, 2 steps 0 of 4; long bargain 2 steps 2 of 6;
  split showing 2 of 6 at hand, 0 of 6 one step away, 1 of 6 two steps away (run rule misses); set-down 2 steps 0 of 5.
- Observed: RESULT: PASS deadly schedules follow the exposure runs minus the rival's reach except when a re-showing meets
  his arrival: tale 2/4, long bargain 4/6, hidden hand-to-hand 0/5, aligned brother 0/4; BREAK set-down handoff still 1/5
  though Leo carried it hidden all the way; a brother 2 steps away kills in 0/4 of the tale and 2/6 of the long bargain;
  split exposure kills 2/6 at hand, 0/6 one step away, but 1/6 two steps away, where the rival who saw the first showing
  arrives at the second
- Scenarios: 1) tale ordering; 2) long bargain; 3) hidden until a hand-to-hand give; 4) brother would spare; 5) BREAK
  set-down handoff; 6-7) tale, brother 1 and 2 steps away; 8) long bargain, 2 steps away; 9-10) split showing at hand and
  1 step away; 11) set-down, 2 steps away; 12) split showing, 2 steps away
- ZaneGPT verdict: weak — the rule's "who can reach it" part is supported by the 0/4 aligned and 0/5 hidden results, but the stated rule already needs two patches (set-down as a moment, re-showing meeting an arrival) that the "exposure runs minus reach" model doesn't predict. Its core claim is also never tested against a differing rival intent, because Leo's intent is fixed and the brother's isn't varied, so "not what the holder means" is an untested contrast.
- Hidden assumption: Reach is a fixed, binary property of a step-count distance, and the rival is a single, always-attentive observer who acts only on what he saw exposed; the rule also assumes "within reach" is the only variable, so Leo's intent, the rival's intent and what the rival can learn from earlier exposure (the observed 1/6 at two steps shows he can) don't change the count.
- Would prove it wrong: A run where the deadly count changes with the rival's intent or knowledge while the exposure timeline and distance stay identical, for example "brother would spare" at 0/4 against a malicious brother at the same positions, or a rival who has not seen the first showing killing in a split-exposure case where the current rule predicts 1/6.
- Break scenario: Hide-then-expose with a moving rival: the heart is shown at p, hidden for several steps, and shown again at p+r with the brother starting r+k steps away. The rule counts exposure runs minus reach and predicts few or no kills, but a brother who approaches during the hidden stretch and arrives exactly as it reappears kills anyway, which is the split-showing 1/6 at two steps again. Separately, the set-down handoff showed 1/5 with the heart hidden throughout Leo's carry, so "exposed moments" undercounts, and the rule needs a case where a set-down is not a handoff (heart set down and picked up by Leo himself) to show the set-down itself is the variable.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 933b9fd4e37c
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

