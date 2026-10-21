# local/bike-drivetrain-usable-gears — lessons

Project: local/bike-drivetrain-usable-gears. Newest first.

---

## E1 — a 2x bike drivetrain has far fewer usable gears than chainrings times cogs
- Date: 2026-10-15
- Project: local/bike-drivetrain-usable-gears
- Tags: [bicycle][gearing][arithmetic][sandbox]
- What: A compact double (50/34) with a 12-speed 11-34 cassette has 24 nominal gears, 21 of which differ by 3% or
  more in ratio, 18 once the big ring is kept off the 3 biggest cogs and the small ring off the 3 smallest, and
  17 distinct at 3% steps among those; 3 big-ring gears are matched within 3% by a small-ring gear.
- Why built: New-domain seed (bicycle gearing, no records): a shop-floor claim that a 2x12 has 24 gears is a count of
  combinations, not of different ratios you can ride.
- Design: Exact fractions chainring/cog for the 24 combinations; ratios merged when less than 3% (or 5%) apart;
  a cross-chain rule removes big ring on the 3 largest cogs and small ring on the 3 smallest; overlap is the
  number of big-ring ratios within 3% of a small-ring ratio; gear inches use a 27-inch wheel. No random numbers.
- Got right: Nominal 24 shrinks to 17 distinct usable gears, and the overlap count (3) shows where a front shift
  and a rear shift give almost the same gear; range is 27.0 to 122.7 gear inches.
- Where/why it failed: My first assertion compared the 3%-distinct count of all 24 gears with the 18 usable ones, which is not the same set, so the first
  run reported FAIL; I fixed the comparison. The drivetrain, the 3% step and the cross-chain rule are my choices, not a manufacturer's spec.
- Fix: Quote the usable distinct count (17 here), not the combination count, and plan front shifts at the overlap
  gears, where a ring change replaces a rear shift.
- Why this fix: Duplicate and cross-chained ratios add no new choice for the rider, so only the distinct, safe set measures range and step size.
- Rule of thumb: Count a double-ring drivetrain's gears as distinct usable ratios, not chainrings times cogs: 24 nominal became 17 here after merging 3% steps and avoiding cross-chaining.
- Provenance (verified/assumed): Verified first-hand by running the exact-arithmetic sandbox; the tooth counts are a common compact-double layout used as the example, the 3% threshold and cross-chain rule are my assumptions, and no real bike or rider was measured.
- Composed: N/A
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__a-2x-bike-drivetrain-has-far-fewer-usable-gears-than-chainrings-times-cogs.py
- Prediction: Hidden assumption: 24 nominal gears are 24 usable gears. Expected at most 18 usable and at most 17 distinct at 3% steps, with at least 3 overlapping gears; it would be wrong if the usable distinct count stayed at 24. This domain is isolated: no existing kernel or lesson applies.
- Observed: RESULT: PASS 24 nominal gears -> 18 cross-chain-safe -> 17 distinct at 3% steps; 3 big-ring gears duplicated by the small ring; 27.0-122.7 gear inches
- Scenarios: 1) all 24 combinations exact; 2) merge at 3% and 5%; 3) cross-chain rule applied, built to BREAK the nominal-equals-usable claim; 4) overlap between rings.
- Link: scheduled brain train auto loop 2 pass 6 (newdomain); session_01Twuh3aqxvcX5mmf7uhRTr7

