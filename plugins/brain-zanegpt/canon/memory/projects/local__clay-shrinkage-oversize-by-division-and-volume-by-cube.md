# local/clay-shrinkage-oversize-by-division-and-volume-by-cube — lessons

Project: local/clay-shrinkage-oversize-by-division-and-volume-by-cube. Newest first.

---

## E1 — clay shrinkage oversize by division and volume by cube
- Date: 2026-10-20
- Project: local/clay-shrinkage-oversize-by-division-and-volume-by-cube
- Tags: [pottery][numerics][sandbox][testing]
- What: With a 12 percent total shrinkage, adding 12 percent to a 200 mm target throws 224.00 mm that fires to 197.12 mm, 2.88 mm short, while dividing by the retained fraction gives 227.27 mm and fires to exactly 200.00 mm; a 1 L target needs 1.467 L of clay by the cube rule, and the add-12-percent habit gives 0.763 L, 23.7 percent under.
- Why built: Seed run for a new pottery domain, starting from a real scenario where a thrower wants a fired size and the quoted clay shrinkage is a fraction of the wet size.
- Design: A plain function for fired size as wet times one minus s; naive oversize versus division at s of 0.12, the volume case with the cube of the retention, drying and firing of 6 percent each compounded, and a sweep of the naive error at s from 0.08 to 0.14.
- Got right: The naive shortfall grew with the rate (1.28, 2.00, 2.88 and 3.92 mm at 8, 10, 12 and 14 percent), and compounded drying plus firing shrinkage gave 11.64 percent and not 12.
- Where/why it failed: The exact-hit result for division follows from the algebra of the model, so it checks my arithmetic and not how clay behaves; the 12 percent value and the 6 plus 6 split are assumed round numbers and not a measured clay body, and warping and trimming loss were not modelled.
- Fix: Divide the target by the retained fraction (one minus shrinkage) for lengths, divide by its cube for volume or clay weight, and compound the drying and firing stages by multiplying their retained fractions.
- Why this fix: The shrinkage rate is defined against the wet size, so the wet size is the unknown in the denominator, and volume carries the retention three times.
- Rule of thumb: Throw wet size = target / (1 - s), not target * (1 + s) (2.88 mm short on 200 mm at 12 percent), and size clay by target volume / (1 - s)^3 (1.467 L for 1 L, not 1.12).
- Provenance: Verified first-hand by running the sandbox script in this session; the shrinkage figures are assumed and not measured on a real clay body.
- Composed: N/A
- Sandbox: sandboxes/2026-10-20__clay-shrinkage-oversize-by-division-and-volume-by-cube.py
- Prediction: The naive oversize of 200 mm at 12 percent fires about 2.9 mm short, division fires exactly to target, the naive 1 L clay is 23 to 24 percent under, and drying plus firing at 6 percent each compound to 11.64 percent.
- Observed: RESULT: PASS naive wet 224.0 mm fires 2.88 mm short; divide gives 227.27 mm; naive clay volume 23.7% under; two-stage 6+6 = 11.64% not 12%
- Scenarios: (1) length at 12 percent naive versus division; (2) volume by cube rule; (3) two-stage compounding of drying and firing; (4) BREAK: sweep of s from 0.08 to 0.14 to see whether the naive shortfall ever vanishes
- Link: scheduled brain train auto run, 2026-10-20; session_0193ruCZULAVFBK6Q3cwQk5z

