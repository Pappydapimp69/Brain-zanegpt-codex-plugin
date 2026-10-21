# local/rc-timer-fixed-threshold-delay-drifts-20-percent-with-supply-sag-ratiometric-does-not — lessons

Project: local/rc-timer-fixed-threshold-delay-drifts-20-percent-with-supply-sag-ratiometric-does-not. Newest first.

---

## E1 — rc timer fixed threshold delay drifts 20 percent with supply sag ratiometric does not
- Date: 2026-10-18
- Project: local/rc-timer-fixed-threshold-delay-drifts-20-percent-with-supply-sag-ratiometric-does-not
- Tags: [electronics][simulation]
- What: Seeded the electronics domain from an RC charging timer: with a fixed 3.0 V comparator threshold a supply sag from 5.0 V to 4.5 V stretches the delay by 19.9 percent (51.3 percent at 4.0 V), while a threshold set at two thirds of the same supply keeps the delay at 1.099 RC at every supply.
- Why built: Seed a new domain from a real scenario, a resistor-capacitor delay (a debounce, power-on reset or monostable) whose supply droops under load, where the usual datasheet figure of 0.693 or 1.099 time constants silently assumes a ratiometric threshold.
- Design: R 10 kohm, C 1 uF, RC 10 ms; dv/dt = (Vs - v)/RC integrated with Euler at 1 microsecond until v reaches the threshold; scenarios for the 63, 50 and 66.7 percent thresholds, a fixed 3.0 V reference at supplies 5.0, 4.5 and 4.0 V, a ratiometric 2/3 Vs threshold at the same supplies, and a closed-form check -RC ln(1 - Vth/Vs).
- Got right: Delays came out at 1.000 RC for 63.2 percent, 0.693 RC at half and 1.099 RC at two thirds; the fixed threshold gave 0.916, 1.099 and 1.386 RC at 5.0, 4.5 and 4.0 V; the ratiometric threshold gave 1.099 RC at all three; Euler matched the closed form within 0.005.
- Where/why it failed: Nothing in the prediction failed; the model is a single ideal RC with no comparator offset, leakage or temperature, so the 19.9 percent figure applies to that idealisation only.
- Fix: Derive the comparator threshold from the same supply as the RC (a divider) or from a regulated reference, and size the delay from -RC ln(1 - Vth/Vs) at the lowest supply the part must work at.
- Why this fix: The delay depends on the ratio Vth/Vs only, so a threshold that tracks the supply cancels the sag and a fixed one does not.
- Rule of thumb: An RC delay is only supply-independent when the threshold is a fixed fraction of the same supply; a fixed threshold stretches it by about 20 percent for a 10 percent sag, so size it at the lowest supply.
- Provenance (verified/assumed): Verified first-hand by running the sandbox below; one ideal RC and three supply voltages; real comparator offset and capacitor tolerance were not modelled.
- Composed: N/A
- Polarity: compatible
- Sandbox: sandboxes/2026-10-18__rc-timer-fixed-threshold-delay-drifts-20-percent-with-supply-sag-ratiometric-does-not.py
- Prediction: Written before the first run: delays of 1.000, 1.099 and 0.693 RC at 63, 66.7 and 50 percent, a fixed 3.0 V threshold drifting between 15 and 25 percent at 4.5 V, a ratiometric threshold drifting under 0.5 percent, and Euler within 0.5 percent of the closed form.
- Observed: RESULT: PASS fixed 3.0 V threshold stretches the delay 19.9% when supply sags 5.0 to 4.5 V (and 51.3% at 4.0 V), ratiometric 2/3 threshold drifts 0.000%, closed-form error 0.00%
- Scenarios: 1) classic threshold fractions; 2) fixed 3.0 V reference at three supplies, built to break the datasheet constant; 3) ratiometric threshold at the same supplies; 4) closed-form comparison. Isolated: no adjacent kernel or lesson was exercised.
- Link: https://claude.ai/code/session_01MRoVc2AE75bu8wwdpoV7jJ

