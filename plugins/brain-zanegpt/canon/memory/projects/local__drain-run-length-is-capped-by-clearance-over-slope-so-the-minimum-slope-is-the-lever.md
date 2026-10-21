# local/drain-run-length-is-capped-by-clearance-over-slope-so-the-minimum-slope-is-the-lever — lessons

Project: local/drain-run-length-is-capped-by-clearance-over-slope-so-the-minimum-slope-is-the-lever. Newest first.

---

## E1 — drain run length is capped by clearance over slope so the minimum slope is the lever
- Date: 2026-10-18
- Project: local/drain-run-length-is-capped-by-clearance-over-slope-so-the-minimum-slope-is-the-lever
- Tags: [plumbing][model][testing]
- What: A gravity drain must fall slope times run length, so the longest run that fits a vertical clearance is clearance over slope: 14 ft at 3.5 in of clearance with 1/4 in per ft, 28 ft with 1/8 in per ft, and 24 and 48 ft at 6 in; building at 1/4 where 1/8 is allowed uses exactly twice the fall.
- Why built: Seeding a plumbing domain from a real layout question (will a drain fit the joist bay), since the domain had no kernel or lesson to detect gaps against.
- Design: Walk the run one foot at a time subtracting the slope from the available clearance with exact fractions until the next foot would go below zero; compare to clearance over slope; check the doubling across three clearances, the 2x fall over lengths 4 to 40 ft, and the percent form of 1/4 in per ft.
- Got right: The stepwise model gave 14, 28, 24 and 48 ft matching the closed form, 1/8 doubled 1/4 at 3.5, 6 and 9 in, and 1/4 in per ft came out 2.083 percent so a 2 percent grade (0.24 in per ft) misses that minimum.
- Where/why it failed: Nothing in the prediction failed, but the slope minimums (1/4 in per ft for small pipe, 1/8 for larger) are taken from the plumbing code as I know it and were not checked against a source here, and venting, trap-arm limits and fittings were not modeled.
- Fix: Compute the fall for the whole run as slope times length before roughing in, use the smallest slope the pipe size allows when clearance is tight, and convert a percent grade by 12 before comparing.
- Why this fix: Fall accumulates linearly with length, so the slope is the only free variable once the run and clearance are fixed, and halving it doubles the reachable length.
- Rule of thumb: Longest drain run equals clearance divided by slope, so at 3.5 in of clearance 1/4 in per ft reaches 14 ft and 1/8 in per ft reaches 28 ft; check the pipe size's minimum slope first and remember 2 percent is below 1/4 in per ft.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; the model is arithmetic on exact fractions, and the code minimum slopes are an unchecked assumption, so no code compliance is claimed.
- Composed: N/A
- Sandbox: sandboxes/2026-10-18__drain-run-length-is-capped-by-clearance-over-slope-so-the-minimum-slope-is-the-lever.py
- Prediction: Written into the script header before the first run: longest runs 14, 28, 24 and 48 ft for the four clearance and slope cases, 1/8 doubling 1/4, a 2x fall waste from 4 to 40 ft, and 2 percent failing the 1/4 minimum.
- Observed: RESULT: PASS longest runs [14, 28, 24, 48] ft at clearances 3.5/6 in for 1/4 and 1/8 per ft, 1/8 doubles 1/4 at 3 clearances, 1/4 wastes 2x fall over lengths 4..40, 1/4 in per ft = 2.083% so 2% fails the minimum
- Scenarios: 1) 3.5 in clearance at 1/4 and 1/8; 2) 6 in clearance at 1/4 and 1/8; 3) BREAK: a 2 percent grade and a 1/16 slope, built to show the percent form and the below-minimum slope mislead; 4) fall waste over lengths 4 to 40 ft
- ZaneGPT verdict: weak — the arithmetic is trivially true, but the PASS only shows the script agrees with the formula it was written from, and the rule omits the code limits that usually bind first.
- Hidden assumption: The run needs only slope × length of total fall, with the whole vertical clearance usable for that fall. That ignores the fixed drop at the fixture outlet, trap arm limits, pipe diameter and invert offsets, fittings, and the vent and trap-arm maximum lengths that cap a run before clearance does.
- Would prove it wrong: A code-compliant install, or a flow test, where a 14 ft run at 1/4 in per ft in 3.5 in of clearance can't be built or fails inspection. That could be because the pipe's own outside diameter or hub eats clearance, or because a trap arm limit (e.g. 5 ft for 1.5 in) caps it far below 14 ft.
- Break scenario: A 1.5 in fixture drain with 3.5 in of clearance. The rule says 14 ft at 1/4 in per ft, but the trap arm maximum is about 5 ft before a vent is needed, and a 3.5 in joist bay can't hold a 1.5 in pipe (1.9 in OD) plus a hub plus the fall once the trap and fitting offsets are counted. The script only tests arithmetic against arithmetic, and its own BREAK case checks the percent form rather than any physical constraint.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest 1a326d0cd62e
- Link: scheduled brain train auto loop 1 pass 6 (newdomain); session_01U1GJP4ePDFrmU7psLn9wKR

