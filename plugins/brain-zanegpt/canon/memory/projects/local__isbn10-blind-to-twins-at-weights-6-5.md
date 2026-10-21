# local/isbn10-blind-to-twins-at-weights-6-5 — lessons

Project: local/isbn10-blind-to-twins-at-weights-6-5. Newest first.

---

## E1 — isbn10 blind to twins at weights 6 5
- Date: 2026-10-15
- Project: local/isbn10-blind-to-twins-at-weights-6-5
- Tags: [check-digits][error-detection][sandbox][exhaustive]
- What: The weighted mod-11 check (ISBN-10, weights 10 down to 1), which the Luhn kernel recommends
  where transpositions are common, misses every twin error (aa typed as bb, all 90) at the one
  position whose adjacent weights are 6 and 5, because 6 + 5 = 11; Luhn misses the same 6 of
  90 twin pairs (22/55, 33/66, 44/77) at every position.
- Why built: Weakest-link train pick: the newly promoted check-digit kernel tested twin errors for Luhn
  but only adjacent swaps for mod 11 (on a sample), then recommends mod 11 for transposition-
  heavy input; twin errors are a common keying slip that its recommendation does not cover.
- Design: Exhaustive: every pair a != b (90 ordered pairs) placed as a twin at every adjacent position
  of a 16-digit Luhn number and of a 10-digit ISBN; a miss is a twin error that leaves the
  checksum unchanged.
- Got right: Re-verified the kernel's Luhn twin figure exactly: 6 of 90 ordered twin pairs missed (its
  30,000 of 450,000), and the same 6 at every position; ISBN-10 caught every twin error at 8
  of its 9 adjacent positions.
- Where/why it failed: ISBN-10 is completely blind to twins at positions 5-6 (weights 6 and 5): a twin aa to bb
  changes the sum by (b - a)(6 + 5) = 11(b - a), which is 0 mod 11, so all 90 are missed
  there. The kernel's advice to prefer mod 11 for transpositions does not mention this hole.
- Fix: When choosing a weighted mod-11 check, list adjacent weight pairs that sum to the modulus
  (here 6 and 5 for ISBN-10) and either accept the twin blind spot there or use weights with
  no adjacent pair summing to 11; test twin errors alongside swaps.
- Why this fix: A twin error adds (b - a) times the sum of the two weights, so detection depends only on
  whether that weight sum shares a factor with the modulus; one bad pair makes a whole
  position blind regardless of the digits.
- Rule of thumb: A weighted mod-11 check misses every twin error where two adjacent weights sum to 11
  (ISBN-10: weights 6 and 5, 90/90 missed); Luhn misses 22/55, 33/66, 44/77 everywhere.
- Provenance (verified/assumed): Verified first-hand by the exhaustive sandbox below on the standard Luhn and ISBN-10
  definitions; real typing-error frequencies are not modelled.
- Composed: ideas:CHECK-DIGITS/luhn
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__isbn10-blind-to-twins-at-weights-6-5.py
- Prediction: Written before running: Luhn misses exactly 22<->55, 33<->66, 44<->77 (6 of 90) at every
  position; ISBN-10 catches every twin error except at the position with weights 6 and 5,
  where it misses all 90.
- Observed: RESULT: PASS Luhn misses 6/90 twin errors (22/55, 33/66, 44/77) at every position; ISBN-10
  misses twin errors only at position 4 (90/90) where weights (6, 5) sum to 11.
- Scenarios: 1) Luhn twins at all 15 positions; 2) ISBN-10 twins at all 9 positions, built to break the
  kernel's mod-11 recommendation.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

