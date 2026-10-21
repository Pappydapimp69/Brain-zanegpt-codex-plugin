# local/sandbox-split-state-with-rng-state-words — lessons

Project: local/sandbox-split-state-with-rng-state-words. Newest first.

---

## E1 — sandbox split state with rng state words
- Date: 2026-10-15
- Project: local/sandbox-split-state-with-rng-state-words
- Tags: [sandbox][determinism][gamedev][state]
- What: A toy sim with a discrete authoritative core (zone, hp, sfc32 rolls) and a frame-rate-dependent float position, run at 1/2/4/7 render frames per tick, with and without a mid-run save/reload through the four sfc32 state words.
- Why built: The state-split kernel says no authoritative outcome may read a float, and the state-words entry says to save PRNG words; the run checks they stay exact together and where the pair stops being enough.
- Design: Variants: split (zone and roll threshold from the tick), coupled (zone and roll threshold read the float x), and split with the camera-shake draws taken from the same stream as the rolls. Float drift adds a per-frame bias proportional to frames per tick, mimicking Euler error.
- Got right: Split state with a separate cosmetic stream gave identical (zone, hp) logs at every frame rate and an exact log after reloading from the four state words at tick 30; coupled state diverged at 3 of 3 other frame rates.
- Where/why it failed: Split state alone was not enough: when the render-time shake draws shared the roll stream, the log diverged across frame rates although the float never fed a roll, because the number of draws per tick changed. State-word reload stayed exact, so reload proves nothing about frame-rate isolation.
- Fix: Give cosmetic and presentation code its own PRNG stream in addition to splitting float values out of authoritative reads; test invariance across frame rates and reload exactness as two separate checks.
- Why this fix: Determinism needs both no float value upstream of a roll and no variable-rate consumer on the roll stream; the split kernel covers the first and the state-words entry covers save fidelity, neither covers the second.
- Rule of thumb: Split state by determinism need and save PRNG state words, but also give every frame-rate-dependent consumer its own stream; verify with a frame-rate sweep, since reload-exactness passed in the case that was broken.
- Provenance (verified/assumed): Verified first-hand: sandbox ran, first run FAILED because the float drift was too small to cross a zone boundary, the drift was raised and the rerun printed PASS; the drift model is a stand-in for integration error, not a measured engine.
- Composed: ideas:SYSTEM/determinism/seeded-rng, ideas:SYSTEM/determinism/split-state-by-determinism-need, sandbox-seeded-rng-state-words/E1
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__sandbox-split-state-with-rng-state-words.py
- Prediction: Split+separate stream is identical at fps 1/2/4/7 and exact on reload; coupled diverges at at least 1 of 3 other frame rates; shared cosmetic stream diverges across fps even when split.
- Observed: RESULT: PASS split+separate stream invariant over fps 1/2/4/7 and exact on reload; coupled float diverged 3/3 fps; shared cosmetic stream diverged although state split (reload still exact)
- Scenarios: 1) split with own cosmetic stream, fps sweep; 2) split with reload at tick 30; 3) coupled float-fed zone and roll; 4) BREAK: split but cosmetic draws on the roll stream, fps sweep; 5) same with reload
- Link: brain train auto, scheduled run; session_01DvSHWZUgPrcaEhdbqtMZR2

