# local/cribbage-subdeck-impossible-scores-grow-monotonically — lessons

Project: local/cribbage-subdeck-impossible-scores-grow-monotonically. Newest first.

---

## E1 — cribbage subdeck impossible scores grow monotonically
- Date: 2026-10-17
- Project: local/cribbage-subdeck-impossible-scores-grow-monotonically
- Tags: [cribbage][exhaustive][testing][sandbox]
- What: Exhaustive scoring of cribbage hands over two restricted decks (ranks ace to eight in four suits, and one suit of all thirteen ranks) to see how the impossible-total list changes versus the full deck.
- Why built: The full-deck exhaustive lesson lists 19, 25, 26 and 27 as impossible, and the brainwork exhaustive-search lessons use gate lists on small spaces; unclear whether a small-space gap list can stand in for the full one.
- Design: Python enumerates every five-card set with each card as starter (201,376 sets for ace to eight, 1,287 for one suit), scores with a hand-checked scorer (29 and 0 cross-checks first) and prints totals from 0 to 29 that never occur.
- Got right: The four full-deck gaps stay impossible in both restricted decks, so a restricted space never invents a reachable total the full deck lacks.
- Where/why it failed: The prediction missed extra gaps: ace to eight also loses 0, 1, 3 and 22 (22 is reachable in the full deck) and the one-suit deck loses 0 to 4 and 19 to 29.
- Fix: Treat a restricted-space gap list as a superset of the full-space gaps, usable to flag impossible targets but never to declare a total reachable in the full space.
- Why this fix: Removing cards can only remove outcomes, so gaps carry upward as lower bounds only, and the extra gaps show a small space cannot confirm reachability.
- Rule of thumb: In a restricted exhaustive space the impossible set only grows (ace to eight: 10 gaps versus 4 in the full deck), so use it to rule totals out, never to rule them in, and run the full space before claiming a total is reachable.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the full-deck gap list comes from the existing lesson and was not re-enumerated here.
- Composed: cribbage-hand-scores-19-25-26-27-are-impossible/E1, brainwork/E243
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__cribbage-subdeck-impossible-scores-grow-monotonically.py
- Prediction: Assumed removing cards only removes reachable totals; expected 19, 25, 26, 27 to stay impossible and 28 and 29 to join them with max score 24.
- Observed: RESULT: PASS subdeck A-8 impossible=[0, 1, 3, 19, 22, 25, 26, 27, 28, 29] max=24; one-suit gaps 0-4 and 19-29.
- Scenarios: 1) scorer cross-check on 29 and 0; 2) ace to eight four-suit deck; 3) one-suit full-rank deck built to break the superset claim, which held.
- Link: brain train auto pass 2; session_011LtaNZCrPYhhAtwJpZ1y8i

