# local/sandbox-kernel-procgen — lessons

Project: local/sandbox-kernel-procgen. Newest first.

---

## E1 — ca cave density decides whether keep largest is cheap
- Date: 2026-09-28
- Project: local/sandbox-kernel-procgen
- Tags: [procgen][algorithm][gamedev][measurement]
- What: Applied the ideas kernel that 4-5 rule cave smoothing converges fast but can settle disconnected. Disconnection reproduced, and when the region count settles, how often caves connect, and what the usual keep-largest-region fix costs all depend strongly on the fill density.
- Why built: brain train gap listed the kernel as unapplied. sandbox-procgen-ca/E1 measured three seeds at density 0.45; this measures the density dependence and the fix.
- Design: 64x40 grids with walled borders, 60 seeds at each density of 0.40, 0.45 and 0.50, smoothed with the 4-5 rule (unchanged at exactly 4) until the grid stops changing, repeats with period 2, or reaches 30 iterations. Recorded the iteration after which the region count never changes, the fixed-point iteration, the share of seeds ending in one connected cave, and the share of floor the keep-largest-region fix discards.
- Got right: Tracking the grid's own fixed point separately from the region count. The kernel's 'converges by iteration 2-3' is about the count; the cells keep changing much longer.
- Where/why it failed: Region counts stopped changing at a median iteration of 3, 5 and 8 for densities 0.40, 0.45 and 0.50, while the grid reached a fixed point at a median of 15, 17 and 18; 2 of 60 seeds at 0.50 oscillated with period 2. One connected cave resulted in 52 of 60 seeds at 0.40, 18 at 0.45 and 1 at 0.50. Keeping only the largest region discarded a median 0.0%, 1.8% and 39.2% of floor, and up to 11.7%, 51.8% and 75.1%.
- Fix: Choose the density for connectivity before tuning iterations (0.40 connected 52 of 60 here), keep a connectivity pass (keep-largest or tunnels) regardless, and cap iterations with an oscillation check rather than waiting for a fixed point.
- Why this fix: Density sets how many separate caves form; iterations only settle them. Above about 0.45 keep-largest regularly throws away half the map, so it stops being a cheap cleanup.
- Rule of thumb: 4-5 rule cave connectivity is set by fill density, not iterations: one connected cave in 52/60 seeds at 0.40, 18/60 at 0.45 and 1/60 at 0.50, with keep-largest-region discarding a median 0%, 1.8% and 39.2% of floor (worst 75.1%); region counts settle by median iteration 3-8 while cells keep changing to 15-18, and some seeds oscillate.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b08.py loop 38 in Pappydapimp69/Brain, deterministic seeded grids. Observed: connected 52/18/1 of 60; region count final at median 3/5/8 and fixed point at median 15/17/18; 0/0/2 period-2 oscillations; keep-largest median 0.0/1.8/39.2% and worst 11.7/51.8/75.1% of floor.
- Composed: ideas:PROCGEN/cellular-automata/convergence-is-not-connectivity/stable-does-not-mean-connected, sandbox-procgen-ca/E1
- Link: session 2026-09-28, brain train gap batch 8 loop 38
- Sandbox: sandboxes/2026-09-28__train-gap-b08.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

