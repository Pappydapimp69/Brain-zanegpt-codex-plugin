# local/sandbox-combined-sparse-map — lessons

Project: local/sandbox-combined-sparse-map. Newest first.

---

## E1 — truthy sparse map hides zero and nan
- Date: 2026-07-13
- Project: local/sandbox-combined-sparse-map
- Tags: [state][gamedev][testing][security]
- What: A truthy sparse-map read (`if (map[key])`) does not merely confuse legitimate zero with absence; it also hides NaN-corrupted numeric state behind the same default path. Existence and numeric validity are separate checks.
- Why built: `brain train` selected the high-value seam `the-game-the-recursion + the-game-wrong-sky`. The interaction claim was that recursion#E1's NaN-poisoning risk composes with wrong-sky#E5's sparse-map truthiness bug: a truthy check can make both a valid zero and a corrupted NaN look like a missing key.
- Design: Built `sandbox-sparse-map-zero-nan.js`, a deterministic model with: - A sparse `clarity` map containing `wall: 0` and `fog: NaN`. - A missing key control. - A truthy reader that returns default `1` when `map[key]` is falsy. - An existence-only reader using `hasOwnProperty`. - An existence+finite reader that distinguishes present valid values, corrupt numeric values, and absent defaults.
- Got right: The sandbox keeps three states separate: legitimate zero, corrupted NaN, and absent key. That exposes why one truthiness branch cannot encode the correct behavior.
- Where/why it failed: The truthy reader returned default `1` for all three cases: `wall` with actual `0`, `fog` with actual `NaN`, and `missing`. It erased a legitimate zero and masked a corrupted value as the same default used for absence.
- Fix: First check key existence with `hasOwnProperty`/`in`/`Map.has`. Then validate numeric values with `Number.isFinite` before using them. Only the absent case should take the default path; the NaN case should be treated as corruption.
- Why this fix: The existence+finite reader preserved `wall: 0` as present, flagged `fog: NaN` as `corrupt`, and returned default `1` only for `missing`. That separation is impossible with a truthy read.
- Rule of thumb: For sparse numeric maps, never use truthiness as presence. Presence, zero magnitude, and numeric corruption are three different states, and reducers/renderers need to keep them distinct.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-sparse-map-zero-nan.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: `wall` actual `0` had truthy read `1`, existence read `0`, finite status `present`, finite value `0`; `fog` actual `NaN` had truthy read `1`, existence read `NaN`, finite status `corrupt`; `missing` had truthy read `1`, existence read `1`, finite status `absent-default`.
- Composed: the-game-the-recursion/E1, the-game-wrong-sky/E5
- Link: Sandbox: `sandbox-sparse-map-zero-nan.js`

