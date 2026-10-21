# local/calendar-leap-rules-are-continued-fraction-convergents — lessons

Project: local/calendar-leap-rules-are-continued-fraction-convergents. Newest first.

---

## E1 — calendar leap rules are continued fraction convergents
- Date: 2026-10-17
- Project: local/calendar-leap-rules-are-continued-fraction-convergents
- Tags: [continued-fractions][calendar][testing][sandbox]
- What: The continued fraction of the leap days per year (0.2421897 from a tropical year of 365.2421897 days) is 0, 4, 7, 1, 3, 27, so its convergents 1/4, 7/29, 8/33, 31/128 are the Julian rule and the best small leap cycles, while the Gregorian 97/400 is not a convergent yet drifts a day only after 3,223 years against 4,264 for the 33-year cycle.
- Why built: To seed a continued-fractions domain from a real scenario, leap-year rules as rational approximations of a measured year length, and check the best-approximation property by brute force.
- Design: Exact Fraction arithmetic for the continued fraction expansion and convergents, a brute-force search over every denominator up to each convergent's denominator, and an error and years-to-drift table for 1/4, 97/400, 8/33 and 31/128.
- Got right: Every convergent from 4 up to 7106 was the closest fraction with denominator at or below its own, and 8/33 (error 2.35e-4) beat 97/400 (3.10e-4) with a twelfth of the denominator.
- Where/why it failed: Nothing refuted, but my written prediction was muddled in its wording on the Gregorian comparison; the numbers it was checked against were clear, and the model assumes a fixed year length when the real tropical year changes slowly.
- Fix: When choosing a periodic rule for a measured ratio, read candidates off the convergents (and add semiconvergents only if a calendar-friendly denominator is needed) instead of rounding the ratio to a convenient denominator.
- Why this fix: A convergent is provably the best approximation at its denominator, so a rule that is not one, like 97/400, buys convenience (a century-based cycle) at a measurable cost in drift.
- Rule of thumb: Expand a ratio as a continued fraction and read the cycle lengths from its convergents; a rule that is not a convergent is paying for convenience in drift.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session against the Meeus mean tropical year value; semiconvergents and the slow change of the real year length were not tested.
- Composed: N/A
- Picked-by: new-half
- ZaneGPT verdict: weak — the arithmetic holds, but it is a theorem restated, and the calendar lesson that a non-convergent "pays for convenience in drift" rests on a constant and a drift metric the data can't support.
- Hidden assumption: The tropical year is a fixed constant (0.2421897) whose precision supports the drift years you quote. In fact the mean tropical year shifts by about 6e-6 days per century. It also depends on which year you define (vernal equinox year versus mean tropical year), and the fifth convergent 845/3489 sits below the input's own 1e-7 resolution. "Not a convergent means paying in drift" also assumes drift is the only cost, when 97/400 buys week alignment and Julian compatibility.
- Would prove it wrong: Re-run with x moved by a plausible 2e-4 over the horizon (a 3,000-year shortening, or the vernal equinox year's 0.2424). If the ranking of 97/400 against 8/33 flips, or the drift years change by more than about 20%, the "3,223 vs 4,264" contrast is an artifact of the constant. If perturbing the last digit of x changes any convergent after 31/128 (it will), that part is noise. If a non-convergent, such as a semiconvergent with a smaller denominator than 400, beats 97/400 by more than a small margin, "convenience" is explained and nothing is being wasted.
- Break scenario: Set x = 365.2425 − 365 = 0.2425. Then 97/400 is exact and a convergent, [0;4,8,12], 7/29 and 8/33 vanish, and the same code "proves" the opposite lesson. This shows the rule only restates Lagrange's theorem for whichever x you feed it, and the brute-force "best at denominator ≤ q" check re-verifies a known theorem rather than testing the claim about calendars. Add a time-varying x(t) run and an x with the last digit changed.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 7bb69594c46e
- Sandbox: sandboxes/2026-10-17__calendar-leap-rules-are-continued-fraction-convergents.py
- Prediction: Convergents 1/4, 7/29, 8/33, 31/128; 97/400 not a convergent; 8/33 closer than 97/400; each convergent is the best fraction at or below its denominator.
- Observed: RESULT: PASS convergents ['1/4', '7/29', '8/33', '31/128', '845/3489']; Gregorian 97/400 not a convergent; 8/33 error 2.3e-04 vs 97/400 3.1e-04; drift 128, 3223, 4264, 454545 years for 1/4, 97/400, 8/33, 31/128.
- Scenarios: 1) expand the fractional year; 2) brute-force best-approximation check per convergent; 3) error and drift table for four calendar rules; 4) BREAK: 97/400 must not be a convergent and must not be the best at denominator 400
- Link: brain train auto loop 2 pass 6 newdomain; session_01S4WKoTG7YsrzCXAnXDQDg7
- Cited-by: 2026-10-20 · projects/pappydapimp69__brain.md#E238 · compatible · sandboxes/2026-10-20__leap-rule-choice-barely-moves-day-29-monthly-skip-loss.py · observed RESULT: PASS skip loses 75.00% to 75.76% of Februaries under all three rules (spread 0.76 pts); clamp loses 0 · brain train auto loop 2 pass 2 (scheduled run); session_015M3aNHgPBvuim7j4SH3Gd2
