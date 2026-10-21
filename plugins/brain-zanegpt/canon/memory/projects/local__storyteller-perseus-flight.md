# local/storyteller-perseus-flight — lessons

Project: local/storyteller-perseus-flight. Newest first.

---

## E1 — perseus fleeing a stale sighting runs alongside the threat
- Date: 2026-10-17
- Project: local/storyteller-perseus-flight
- Tags: [narrative][ai][simulation][sandbox]
- What: Modelled Acrisius fleeing the prophecy in Perseus and the Gorgon as avoidance on a line of 21 places: the
  threat walks toward its own destination, and the avoider stays put, flees from its one stale sighting,
  or flees from the threat's live position; contact is ending a turn within one place.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had a flee-AI speed-parity kernel but nothing on
  avoidance that routes back to the outcome because it steers by where the threat used to be.
- Design: Stdlib deterministic turn loop, no randomness: avoider speed 1, threat speed 2 (1 in one scenario), 15 or
  30 turns; scenarios where the threat settles near home, departs toward the avoider's side, departs the
  other way, moves no faster than the avoider, and a 41-place line with the destination mid-line or at the edge.
- Got right: When the threat departed toward the avoider's side, fleeing the stale sighting gave 8 contact turns against
  2 for staying put and ended on the threat's destination; live tracking gave 2; when the threat stayed
  near home the same flight cut contact from 15 to 0.
- Where/why it failed: When the threat departed the other way, stale flight and staying both gave 0, and at equal speed the
  flight looked better over 15 turns (2 against 3) and only turned worse over 30 (17 against 3). A separate
  check asked whether the wall made the result; on a 41-place line with the avoider mid-line the flight still
  gave 6 against 2, but the long dwell (15 against 2) appeared only when the threat's destination sat at the
  end of the flight.
- Fix: Treat a sighting as a position and a heading: anything that has left its last-known spot is moving away
  from it, so before fleeing from an old sighting check whether its likely direction matches yours.
- Why this fix: Fleeing away from where the threat was correlates the avoider's motion with the threat's own departure,
  so the flight runs alongside it and ends where it ends instead of opening distance.
- Rule of thumb: Fleeing an old sighting runs you alongside a threat that left toward you, and parks you on it if its
  destination is where your flight ends; for flee AI, never flee a stale sighting without a heading.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the tale details checked against
  Wikipedia's Storyteller and Acrisius articles and Apollodorus 2.4.1 and 2.4.4 on theoi.com.
  The line world, speeds and contact radius are toy values.
- Composed: ideas:NPC-SIM/decision-making/movement-speed-parity-dominates-flee-ai-quality
- Sandbox: sandboxes/2026-10-17__perseus-fleeing-a-stale-sighting-runs-alongside-the-threat.py
- Prediction: Settles near home: stay 15, stale flight 0; departs toward: stay 2, stale 8, live 2; departs away:
  stay 0, stale 0; equal speed: stay 3 vs stale 2 at 15 turns, stay 3 vs stale 17 at 30 turns; added before
  the second run, 41-place line over 30 turns: destination mid-line stay 2 vs stale 6, at the edge 2 vs 15.
- Observed: RESULT: PASS fleeing a stale sighting: 8 contacts vs 2 for staying when the threat departs toward the
  avoider (live tracking 2); 0 vs 15 when it stays home; no effect when it departs away; at equal speed
  2 vs 3 at 15 turns becomes 17 vs 3 at 30; on a 41-place line 6 vs 2 with the destination mid-line, 15 vs 2
  when it sits at the end of the flight
- Scenarios: 1) threat settles near home; 2) threat departs toward the avoider (stay, stale, live); 3) BREAK: threat
  departs the other way; 4) BREAK: threat no faster than the avoider, 15 and 30 turns; 5) BREAK: 41-place line,
  avoider mid-line, destination mid-line or at the edge
- ZaneGPT verdict: weak — the predictions were largely written to match the geometry (even the 41-place cases were added to the design before the second run), so the PASS shows the mechanism exists in tuned cases, while the "never flee a stale sighting without a heading" rule is stronger than a single fixed-geometry, no-randomness toy can support.
- Hidden assumption: The result generalizes beyond a toy where the threat's heading is fixed and straight-line and the avoider's flight is a fixed-rule path, so "stale flight parks you on the destination" is a property of one chosen geometry (flight ends where the threat is going), not of stale sighting as such.
- Would prove it wrong: A sweep over avoider start, destination, and sighting age showing stale-flight contacts at or below stay-put contacts in most departs-toward cases, with the 8-vs-2 and 17-vs-3 gaps appearing only where the flight's end coincides with the destination.
- Break scenario: Put the destination on the opposite side of home from the flight direction (or randomize destination, start, and sighting age over many seeds), so the stale flight ends far from where the threat settles and a fixed-heading threat at speed 2 can't be both chasing and parked on it.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 9a0efcbdc899
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

