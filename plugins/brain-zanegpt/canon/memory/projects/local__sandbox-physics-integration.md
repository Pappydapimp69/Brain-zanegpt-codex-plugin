# local/sandbox-physics-integration — lessons

Project: local/sandbox-physics-integration. Newest first.

---

## E1 — explicit euler injects energy semi implicit doesnt
- Date: 2026-07-20
- Project: local/sandbox-physics-integration
- Tags: [algorithm][physics]
- What: Integrating a lossless oscillatory system (spring: `F=-k*x`, no
  damping) with explicit (forward) Euler — updating position using the
  OLD velocity, then velocity using the OLD position's acceleration —
  injects energy every step and diverges to a numerically explosive
  spiral-out, even at a modest fixed timestep. Semi-implicit
  (symplectic) Euler — the exact same formula, only the update ORDER
  swapped (velocity first, then position using the NEW velocity) —
  keeps the system's energy near-constant over the same run.
- Why built: `brain train new-domain`, seeding PHYSICS as a genuine gap
  (`brain query` returned only incidental tag-noise, nothing organized
  as integration-method craft). This is well-documented externally
  (Glenn Fiedler, "Integration Basics," gafferongames.com) but had
  never been verified first-hand in this system.
- Design: `sandbox.py` — 1D spring, k=4.0, dt=0.1 (deliberately coarse
  to make the drift visible quickly), 2000 fixed steps, zero RNG.
  `explicit_euler`: `x_new = x + v*dt; v_new = v + a*dt` (both computed
  from the OLD state). `semi_implicit_euler`: `v = v + a*dt` first,
  then `x = x + v*dt` using the just-updated v. Energy tracked as
  `0.5*k*x^2 + 0.5*v^2` (unit mass), which the exact solution keeps
  constant.
- Got right: kept every parameter (k, dt, step count, initial
  conditions) identical between the two integrators — the only
  difference is which velocity value the position update uses.
- Where/why it failed: explicit Euler's energy grew to ~1.2×10^34 times
  the starting value over 2000 steps (a numerically explosive,
  visibly-expanding oscillation) — because each step's position update
  uses last step's velocity/acceleration, systematically overshooting
  the true curve outward every cycle, and that overshoot compounds.
  Semi-implicit Euler's energy stayed within 1.04x of the start over
  the identical run.
- Fix: for any oscillatory/orbital simulation (springs, pendulums,
  simple orbital mechanics, camera follow-springs), use semi-implicit
  Euler — update velocity from the current acceleration FIRST, then
  update position using that new velocity — instead of explicit Euler,
  which updates both from the old state.
- Why this fix: semi-implicit Euler is symplectic (approximately
  conserves a shadow Hamiltonian close to the true energy) for this
  class of system, while explicit Euler has no such property — the
  practical consequence is that explicit Euler's error doesn't average
  out over time, it compounds in one direction (energy gain), which is
  exactly wrong for anything meant to oscillate or orbit stably over a
  long session.
- Rule of thumb: never trust "it's just Euler integration, order
  doesn't matter" for anything with restoring/oscillatory forces
  (springs, orbits, pendulums) — verify by tracking the system's own
  conserved quantity (energy, or angular momentum for orbits) over a
  long run at your actual timestep; a coarse timestep will show
  explicit Euler's divergence within a few thousand steps even for a
  simple 1D spring, and the fix (swap update order to semi-implicit) is
  a one-line change with no other cost.
- Provenance (verified/assumed): Verified first-hand — ran `sandbox.py`
  (zero RNG, fixed dt/steps), confirmed explicit Euler's energy ratio
  reached ~1.2×10^34 while semi-implicit Euler's stayed at 1.04x. Re-ran
  as two independent process invocations; output byte-identical both
  times. Externally sourced (not internal reasoning alone): Glenn
  Fiedler, "Integration Basics," https://gafferongames.com/post/integration_basics/.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  new-domain`, physics gap); sandbox
  `scratchpad/loop7/physics/sandbox.py`, run twice as independent
  process invocations, outputs diffed identical
- Cited-by: 2026-10-09 · projects/pappydapimp69__brain.md#E119 · compatible · sandboxes/2026-10-09__symplectic-euler-holds-only-at-fixed-dt-below-2-over-omega.py · observed RESULT: PASS (see script): explicit 4.39e8x, semi 1.0526x, dt=1.99 200x, dt=2.01 inf, 0.1/1.9 schedule 199.9x vs 2x fixed 1.0, accumulator 1.0526x. · brain train auto pass 1, unattended run 2026-10-09; session_01A7os5bwK2BHc7rwnvxx6Ts
