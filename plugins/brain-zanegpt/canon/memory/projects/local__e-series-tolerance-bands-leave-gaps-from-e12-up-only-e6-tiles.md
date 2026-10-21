# local/e-series-tolerance-bands-leave-gaps-from-e12-up-only-e6-tiles — lessons

Project: local/e-series-tolerance-bands-leave-gaps-from-e12-up-only-e6-tiles. Newest first.

---

## E1 — e series tolerance bands leave gaps from e12 up only e6 tiles
- Date: 2026-10-19
- Project: local/e-series-tolerance-bands-leave-gaps-from-e12-up-only-e6-tiles
- Tags: [electronics][standards][simulation][method]
- What: A deterministic check of whether the plus-minus tolerance bands of the E6, E12, E24, E48, E96 and E192 resistor series cover a whole decade, seeding a new ELECTRONICS domain with a kernel.
- Why built: The brain had no electronics resistor lesson, and the common belief that each E series is spaced so tolerance bands meet is a testable, real-component claim with a concrete answer.
- Design: E6, E12 and E24 use the published rounded value tables; E48, E96 and E192 use 10^(k/N) rounded to 3 significant digits. Tolerances are 20, 10, 5, 2, 1 and 0.5 percent. For each series the script tests whether every adjacent band pair touches, and samples 200000 log-spaced resistances over one decade to count those not within tolerance of any stocked value.
- Got right: E6 is exactly tiled (every adjacent pair of bands touches and 0 percent of the decade is uncovered), and the worst steps in the tight series match the geometric ratio plus rounding (E192 2.0 percent against a nominal 1.2).
- Where/why it failed: My prediction that E6, E12 and E24 all tile and E48 to E192 do not was wrong: E12 leaves 1.16 percent of the decade uncovered and E24 4.11 percent, because the rounded tables are uneven (12 to 15 is a 25 percent step, 13 to 15 a 15.4 percent step), and E48, E96 and E192 leave 16.6, 16.85 and 18.13 percent.
- Fix: Treat the tolerance band as a spec on the part, not as coverage of the range: for an arbitrary target, expect a nearest E96 or E192 value to miss tolerance for about a sixth of targets, and add a series or parallel trim resistor when the value must be inside the tolerance.
- Why this fix: The coverage gap equals one minus tolerance-width over step size, so tightening tolerance faster than the series density opens a fixed-size hole, and only a second resistor can close it.
- Rule of thumb: Only the E6 series has tolerance bands that tile the decade; E12 leaves 1.2 percent, E24 4.1 percent and E48 to E192 about 17 percent of targets outside tolerance of any stocked value, so pick the series from the accuracy you need and trim with a second resistor.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox, deterministic output; the E-series tables and tolerance pairings come from my recollection of the standard and were not checked against the IEC document, and the tight series use a generated table, not the published one.
- Composed: N/A
- Sandbox: sandboxes/2026-10-19__e-series-tolerance-bands-leave-gaps-from-e12-up-only-e6-tiles.py
- Prediction: The bands tile the decade for E6, E12 and E24 and leave gaps for E48, E96 and E192.
- Observed: RESULT: FAIL bands tile the decade for ['E6'] but leave gaps for ['E12', 'E24', 'E48', 'E96', 'E192'] (uncovered E12 1.2%, E24 4.1%, E48 16.6%, E96 16.9%, E192 18.1%)
- Scenarios: 1) E6 published table; 2) E12 and E24 published tables; 3) BREAK: E48, E96 and E192 generated from 10^(k/N); 4) adjacent-band touch test against 200000 sampled resistances
- Link: scheduled brain train auto, loop 2 pass 6 (newdomain); session_01Q5Z2SdcUKr5yLCVU7Ma7tK
- Cited-by: 2026-10-19 · projects/pappydapimp69__brainwork.md#E494 · compatible · sandboxes/2026-10-19__second-resistor-trim-closes-e-series-tolerance-gaps-within-the-same-series.py · observed RESULT: PASS E6 miss 0.0% closed 0%/0%; E12 1.3% closed 100%/100%; E24 3.5% 100%/100%; E96 17.1% 100%/100% (quarter-tolerance prediction missed). · brain train auto pass 2, session 2026-10-19; session_01M3VVz3RFpipo1Jc6ecPoW2
