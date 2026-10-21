# local/seeded-rng-state-save-canonical-fingerprint-transcendental-roll-divergence — lessons

Project: local/seeded-rng-state-save-canonical-fingerprint-transcendental-roll-divergence. Newest first.

---

## E1 — seeded rng state save canonical fingerprint transcendental roll divergence
- Date: 2026-10-11
- Project: local/seeded-rng-state-save-canonical-fingerprint-transcendental-roll-divergence
- Tags: [gamedev][determinism][testing][state]
- What: A deterministic sandbox that exercises three linked determinism rules together: save the full sfc32 state words instead of seed plus count, fingerprint authoritative state with a canonical sorted-key serializer, and keep transcendental float math out of anything that feeds a roll. A 20000-tick sim was run with a float-fed and an integer-fed threshold on two stand-in math runtimes.
- Why built: The seeded-rng and replay-fingerprint kernels were only quoted in prose by the-game-prologue E1; this run declares and re-verifies the link first-hand, and measures how often a float-fed roll actually breaks determinism.
- Design: sfc32 with state in the world; resume at tick 12000 from saved words compared to full replay; canonical versus insertion-order dump of equal states; an ambient-source leak that must change the fingerprint; two sin implementations differing by about 3e-12 over 20 seeds with a float threshold and an integer-threshold control.
- Got right: Restoring four state words at tick 12000 gave the identical final fingerprint while the seed-plus-count route had to replay 12000 draws. The canonical serializer made two logically equal states match where the insertion-order dump differed. Clean runs matched and the leaked-source runs differed. The integer-fed control was identical on both runtimes for all 20 seeds.
- Where/why it failed: Float-fed rolls diverged between the two runtimes on only 1 of 20 seeds over 20000 ticks, so the hazard is rare per run but then permanent: after one flipped roll the shared stream and the log hash differ for the rest of the run. A short golden replay would most likely miss it.
- Fix: Keep the authoritative layer integer-only (or quantize before comparing), keep the golden fingerprint canonical, and run the replay long enough or across runtimes, since a single-runtime golden cannot see this class.
- Why this fix: The control shows integer thresholds are immune (0 of 20), and the float case diverged only on a rare boundary crossing, so evidence has to come from many ticks or a second runtime, not one short replay.
- Rule of thumb: Saving the four sfc32 words restores in O(1) versus a 12000-draw replay, but the golden fingerprint only protects the sim if it is canonical and long, because a float-fed roll diverged across runtimes on just 1 of 20 seeds in 20000 ticks while an integer-fed roll never did.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; counts are exact and deterministic. The two runtimes are simulated by two sin implementations, not real browsers or engines, and the key-order case models insertion order generally rather than the JavaScript integer-key rule.
- Composed: ideas:SYSTEM/determinism/seeded-rng, ideas:SYSTEM/testing/replay-fingerprint, the-game-prologue/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__seeded-rng-state-save-canonical-fingerprint-transcendental-roll-divergence.py
- Prediction: State restore exact with 12000 replayed draws avoided; canonical equal where insertion dump differs; leak runs differ; float-fed fingerprint diverges on at least 1 of 20 seeds; integer control 0 of 20.
- Observed: RESULT: PASS S1 resume exact (replay=12000 draws); S2 canon equal vs insertion dump differs; S3 clean runs equal and leak runs differ; S4 float-fed fingerprint diverged on 1/20 seeds; S5 integer control 0/20
- Scenarios: 1) state-word save and resume at tick 12000; 2) canonical versus insertion-order serialization; 3) ambient-source leak against clean reruns; 4) float-fed threshold on two runtimes over 20 seeds (built to BREAK the claim that float is risky: it showed only 1 of 20); 5) integer-fed control
- Link: scheduled brain train loop 2 pass 1; session_015bpfiyHog3CaYStqh5GY3K

