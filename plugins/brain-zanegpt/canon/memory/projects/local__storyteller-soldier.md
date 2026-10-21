# local/storyteller-soldier — lessons

Project: local/storyteller-soldier. Newest first.

---

## E1 — soldier death nowhere won contests burn exits
- Date: 2026-10-17
- Project: local/storyteller-soldier
- Tags: [narrative][endings][simulation][sandbox]
- What: Modelled the ending of The StoryTeller's The Soldier and Death as reachability over final resting places: each
  gatekeeper the soldier beats refuses him, heaven refuses by rule, and his last route is a sack handed to a soul who must
  call him in after passing a gate that wipes memory.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had trapping Death as a sink, but nothing on how a trickster
  who wins every contest runs out of places that will take him, or on a handed-off key whose holder forgets it.
- Design: Stdlib BFS over a small map: earth to Death, earth to the hell gate, hell gate to hell and (via the devils' map)
  to heaven's gate, heaven's gate to heaven. A place admits him if its rule allows and, when it holds a grudge, he has not
  beaten it; heaven also opens if any handed-off key fires, which needs memory after the gate or a key that fires by itself.
- Got right: Canon (beat the devils and Death, heaven refusing, one forgetful holder) left 0 exits, so he wanders; exits fell
  2, 1, 0 after 0, 1, 2 won contests; handing sacks to all 250 souls still gave 0, while one self-firing key or a gate that
  keeps memory opened heaven; never trapping Death left Death as his one exit, and the control who wins no contest kept
  both Death and hell open even with grudges on and heaven refusing.
- Where/why it failed: The no-exit ending depends on grudges: in the BREAK where beaten gatekeepers bear no grudge, the
  soldier who won every contest still had 2 exits (Death and hell), so winning alone does not strand him. The model is a
  toy map with yes/no gates; the grudges, heaven's refusal and the memory wipe at heaven's gate are inputs taken from the
  episode, not derived. The win-nothing control was added after the first check.
- Fix: For a trickster who beats every authority, count his exits as you write: each beaten gatekeeper that holds a grudge
  closes one, and the ending should land on the last open route; if that route is a key handed to someone else, make it
  depend on the holder's memory across a boundary that wipes it.
- Why this fix: Exits are reachable terminal states, so each grudge-holding win removes an edge; the handed-off key is then
  the only edge left, and copies of a memory-dependent key all fail at the same gate, so redundancy cannot rescue it.
- Rule of thumb: A hero who wins every contest against gatekeepers who hold grudges runs out of places that will take him;
  his last way out is whatever key he handed on, and copies of a key that needs its holder to remember all fail at a gate
  that wipes memory. Without grudges, winning leaves the exits open.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode details checked against Wikipedia's
  Storyteller article and Ransome's text on Project Gutenberg cited in the kernel. The map and gates are toy structure.
- Composed: ideas:SYSTEM/procgen-qa/completability-check-algorithm, ideas:SYSTEM/backup/an-untested-backup-carries-no-assurance-of-recovery
- Sandbox: sandboxes/2026-10-17__soldier-death-nowhere-won-contests-burn-exits.py
- Prediction: Canon gives 0 exits (wanders); 250 forgetful holders still 0; one self-firing key gives heaven; never trapping
  Death gives Death; exits 2/1/0 after 0/1/2 wins; BREAK with no grudges gives 2 exits despite winning every contest.
  Added after the first check, before rerun: winning no contest with grudges on gives Death and hell.
- Observed: RESULT: PASS exits [2, 1, 0] after 0/1/2 wins; canon [] and 250 forgetful holders []; one self-firing key
  ['heaven'] and a memory-keeping gate ['heaven']; never trapping Death ['death']; winning none ['death', 'hell'];
  BREAK no grudges ['death', 'hell'].
- Scenarios: 1) canon, one forgetful holder; 2) 250 forgetful holders; 3) one self-firing key; 4) soldier never traps
  Death; 5) exits after 0/1/2 won contests; 6) gate keeps memory; 7) control: wins no contest, grudges on; 8) BREAK:
  beaten gatekeepers hold no grudge
- ZaneGPT verdict: weak — the 0/1/2 drop and the no-grudge BREAK show the grudge flag drives the result, but the rule claims "winning" does it. The "winning none" control was added after seeing output, and 250 forgetful holders is the same single boolean run 250 times, so it adds no evidence.
- Hidden assumption: The rule treats the model's encoding as the story: that "grudge" and "memory-wipe" are the only two mechanisms deciding exits, and that heaven's rule is a fixed refusal rather than a variable the author chose. The model was built to emit the canon ending, so 0 exits is a reproduction, not a finding. Several scenarios (the 0/1/2 sweep, "winning none") were also added or tuned after seeing the first run.
- Would prove it wrong: Gatekeepers with grudges that are not tied to having been beaten (e.g. hell refuses him by rule even if he lost) still give 0 exits with wins at 0. Or beaten gatekeepers with grudges still admit him via a different route, like Death re-admitting him because trapping her is the only thing that cost her anything. Either one shows that "winning" is not what closes the exits. That would mean the grudge flag is doing the work, not the winning.
- Break scenario: Keep grudges on and let the soldier lose every contest, but hold hell's admission rule fixed as refuses-on-rule. Then run the same BFS with winning none. If exits are still [] while the "winning none" control currently gives ['death', 'hell'], the control was passing only because hell's rule was permissive, and the 0/1/2 monotone drop is an artifact of which rules were set to allow.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest eefedaaf6784
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

