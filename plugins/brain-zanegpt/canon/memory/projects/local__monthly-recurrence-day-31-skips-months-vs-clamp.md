# local/monthly-recurrence-day-31-skips-months-vs-clamp — lessons

Project: local/monthly-recurrence-day-31-skips-months-vs-clamp. Newest first.

---

## E1 — monthly recurrence day 31 skips months vs clamp
- Date: 2026-10-17
- Project: local/monthly-recurrence-day-31-skips-months-vs-clamp
- Tags: [scheduling][calendar][testing][sandbox]
- What: Enumerated three ways to implement a monthly repeat on a late day (skip months that lack the day, clamp to the month's last day, carry forward from the previous clamped date) over 36 months from January 2025 using the standard library calendar.
- Why built: A real recurring reminder set for the 31st is a common scheduling bug, and no existing lesson covers calendar recurrence semantics, so this seeds the domain from a concrete case.
- Design: Python datetime and calendar.monthrange; three generators for days 31, 30, 29 and a control day 15; count how many dates each fires and which days of the month occur after February.
- Got right: Day 31 fires 21 times under skip (7 of 12 months), 36 under clamp, and the day 15 control behaves identically in all three (36 and always day 15).
- Where/why it failed: Carry-forward silently ratchets down: after the first February every later date lands on the 28th for days 29, 30 and 31, so 36 fires happen but on the wrong day (only day 15 is unaffected); and day 29 under skip fires 33 times because 2025 to 2027 have no leap February.
- Fix: Store the anchor day (31) separately from the last fire date and recompute each month as min(anchor, month length) for clamp, or skip when the month is too short, never derive the next date from the previous clamped one.
- Why this fix: Clamp from the stored anchor keeps 36 fires on 28 to 31 with the right day recovered after short months, while carry loses information at the first short month and never gets it back.
- Rule of thumb: For a monthly repeat on day 29 to 31, pick skip or clamp explicitly and always compute from the stored anchor day; deriving from the previous fire drifted to day 28 in all three late-day cases (31, 30, 29) and only the day 15 control was safe.
- Provenance (verified/assumed): Verified first-hand by running the sandbox with the real calendar module; I did not check any particular calendar app or the iCalendar standard's wording, and the skip meaning is my assumption about common practice.
- Composed: N/A
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__monthly-recurrence-day-31-skips-months-vs-clamp.py
- Prediction: Day 31 fires 21 times under skip and 36 under clamp, carry lands only on day 28 after February, day 29 skip fires 33 times, day 15 control is unaffected. Assumption: implementers mean skip or clamp, not carry.
- Observed: RESULT: PASS day31 skip 21 clamp 36 carry-days-after-Feb [28]; day29 skip 33; day15 control skip 36
- Scenarios: 1) day 31 three semantics; 2) day 30; 3) day 29 with no leap year in range, built to break the 21-count pattern; 4) day 15 control.
- Link: scheduled brain train auto loop 1 pass 6 (newdomain; isolated, no adjacent lesson cited); session_011LtaNZCrPYhhAtwJpZ1y8i
- Cited-by: 2026-10-20 · projects/pappydapimp69__brain.md#E234 · compatible · sandboxes/2026-10-20__age-threshold-overdue-flag-misfires-on-clamped-monthly-gaps.py · observed RESULT: PASS T=30 flags 20 of 35 clamp gaps with 0 lapses; T=32 flags 0 clamp and 15 skip gaps = true lapses · brain train auto pass 2 (scheduled run); session_015M3aNHgPBvuim7j4SH3Gd2
- Cited-by: 2026-10-20 · projects/pappydapimp69__brain.md#E238 · compatible · sandboxes/2026-10-20__leap-rule-choice-barely-moves-day-29-monthly-skip-loss.py · observed RESULT: PASS skip loses 75.00% to 75.76% of Februaries under all three rules (spread 0.76 pts); clamp loses 0 · brain train auto loop 2 pass 2 (scheduled run); session_015M3aNHgPBvuim7j4SH3Gd2
