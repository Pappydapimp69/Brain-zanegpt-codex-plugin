# local/dew-point-rule-of-five-holds-above-half-humidity-and-fails-below — lessons

Project: local/dew-point-rule-of-five-holds-above-half-humidity-and-fails-below. Newest first.

---

## E1 — dew point rule of five holds above half humidity and fails below
- Date: 2026-10-19
- Project: local/dew-point-rule-of-five-holds-above-half-humidity-and-fails-below
- Tags: [meteorology][humidity][simulation][method]
- What: A sweep of the dew-point shortcut Td = T - (100 - RH)/5 against the Magnus formula (a 17.625, b 243.04 C) over 0 to 35 C and 1 to 100 percent relative humidity, plus below-freezing and round-trip checks, seeding a new METEOROLOGY domain.
- Why built: The domain did not exist in the brain; a humidity and condensation rule is a real thing a thermostat, greenhouse or fog script needs, and the usual wording says the shortcut is good to 1 C above 50 percent humidity.
- Design: Stdlib functions for the Magnus dew point, its inverse (relative humidity from dew point) and the shortcut; max absolute error over integer temperature and humidity grids; a scan at 30 C for the humidity where the error first passes 1 C; a search for the lowest humidity from which the shortcut stays inside 1 C at every temperature.
- Got right: The formula round-trips (humidity error 4e-14), the dew point equals the air temperature at 100 percent humidity, and the shortcut is the intended approximation: it never exceeds 2 C above 50 percent humidity.
- Where/why it failed: My prediction that the shortcut stays within 1 C for all humidity of 50 percent and above was wrong: the worst error there is 1.97 C (35 C, 50 percent), and at 30 C it first passes 1 C at 55 percent. Across 0 to 35 C it is inside 1 C only from 79 percent upward, and below 50 percent it reaches 18.15 C at 10 percent.
- Fix: Use the shortcut only at or above about 80 percent humidity, or keep a 2 C margin if it must run down to 50 percent, and call the Magnus formula below that.
- Why this fix: The shortcut is a straight line in humidity while the true dew point curves away from it as the air gets drier, so the gap grows steadily below the high-humidity end where the line was fitted.
- Rule of thumb: The minus-RH-over-five dew-point shortcut stayed inside 1 C only from 79 percent humidity up (1.97 C off at 50 percent and 35 C, 18.15 C at 10 percent), so guard it by humidity and use the Magnus formula below about 80 percent.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox against the Magnus formula, with deterministic output; the Magnus constants and the 1 C at 50 percent wording come from my recollection of the published paper and were not checked against the source, and Magnus itself is an approximation to real vapour pressure.
- Composed: N/A
- Sandbox: sandboxes/2026-10-19__dew-point-rule-of-five-holds-above-half-humidity-and-fails-below.py
- Prediction: The shortcut stays within 1 C of the Magnus dew point for every humidity from 50 to 100 percent over 0 to 35 C, and exceeds 1 C somewhere below 50 percent.
- Observed: RESULT: FAIL rule within 1.97C for RH>=50 over 0..35C but off by up to 18.15C below 50; at 30C first >1C at RH=55; within 1C only from RH=79
- Scenarios: 1) humidity 50 to 100 over 0 to 35 C; 2) humidity 10 to 49 over the same temperatures; 3) BREAK: 30 C scan of falling humidity for the first 1 C miss; 4) below freezing, -10 to -1 C, humidity 50 and up; 5) inverse round trip and 100 percent check
- Link: scheduled brain train auto, loop 1 pass 6 (newdomain); session_01Q5Z2SdcUKr5yLCVU7Ma7tK

