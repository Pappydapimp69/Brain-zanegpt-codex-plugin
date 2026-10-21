# local/gravity-drain-first-half-empties-in-29-percent-of-the-time — lessons

Project: local/gravity-drain-first-half-empties-in-29-percent-of-the-time. Newest first.

---

## E1 — gravity drain first half empties in 29 percent of the time
- Date: 2026-10-18
- Project: local/gravity-drain-first-half-empties-in-29-percent-of-the-time
- Tags: [hydraulics][simulation]
- What: Seeded the hydraulics domain from Torricelli's law for a tank draining through a bottom orifice: the first half of the volume leaves in 29.3 percent of the total drain time, doubling the head multiplies the time by 1.414 and not 2, and a discharge coefficient rescales the time without moving that fraction.
- Why built: Seed a new domain from a real scenario, gravity-fed draining of a tank or lock chamber, where the tempting estimate is to extrapolate the opening flow rate and so to halve the time for half the volume.
- Design: dh/dt = -cd (a/A) sqrt(2 g h) integrated with Euler at dt 0.001 for A 1.0, a 0.01, head 1.0, compared with the closed form T = (A/(cd a)) sqrt(2 h0 / g); scenarios for half-volume time, double head, discharge coefficient 0.6, and the constant-flow estimate.
- Got right: Half volume at 13.22 of 44.70 gave 0.2929 of the total (theory 1 - 1/sqrt 2 = 0.2929); head 2.0 against 1.0 gave a time ratio of 1.418 against 1.414; discharge coefficient 0.6 changed the total to 74.50 and the fraction only to 0.296.
- Where/why it failed: My first pass check demanded the constant-flow estimate be off by more than 50 percent; it is off by only 15 percent (11.29 against 13.22), so the check was wrong, not the model, and the threshold was corrected; the tail near empty is truncated at 1e-4 of head, which makes the integrated total 1 percent short of the closed form.
- Fix: Estimate a gravity drain from the closed form, time proportional to the square root of the head, and plan the early phase as fast and the last phase as slow; never schedule a half-way event at half the total time.
- Why this fix: Flow falls with the square root of the remaining head, so most of the volume leaves early and the final liters take disproportionately long.
- Rule of thumb: In a gravity drain through a fixed orifice the first half of the volume leaves in 29 percent of the total time, so time scales with the square root of the head and half-way events come early, not at half time.
- Provenance (verified/assumed): Verified first-hand by running the sandbox below; one tank shape (constant cross-section) and one orifice; real pipes with friction and air entry were not tested.
- Composed: N/A
- Polarity: compatible
- Sandbox: sandboxes/2026-10-18__gravity-drain-first-half-empties-in-29-percent-of-the-time.py
- Prediction: Written before the first run: half-volume fraction 0.293 within 0.005, double-head ratio 1.414 within 0.01, discharge coefficient leaving the fraction within 0.005, and the constant-flow estimate being clearly wrong; the first run refuted the size of the last (expected over 50 percent, observed 15 percent).
- Observed: RESULT: PASS half the volume leaves in 0.293 of the drain time, doubling the head costs x1.418 time, discharge coefficient leaves the fraction at 0.296, constant-flow estimate is off by 15%
- Scenarios: 1) half-volume time against closed form; 2) double head; 3) discharge coefficient 0.6; 4) constant-flow estimate, built to break the idea that half the volume takes half the time. Isolated: no adjacent kernel or lesson was exercised.
- Link: https://claude.ai/code/session_01MRoVc2AE75bu8wwdpoV7jJ

