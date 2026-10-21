# local/slide-rule-relative-error-is-flat-across-the-scale-so-three-digits-holds-above-3-and-fails-near-1-and-the-decade-must-be-tracked-by-hand — lessons

Project: local/slide-rule-relative-error-is-flat-across-the-scale-so-three-digits-holds-above-3-and-fails-near-1-and-the-decade-must-be-tracked-by-hand. Newest first.

---

## E1 — slide rule relative error is flat across the scale so three digits holds above 3 and fails near 1 and the decade must be tracked by hand
- Date: 2026-10-19
- Project: local/slide-rule-relative-error-is-flat-across-the-scale-so-three-digits-holds-above-3-and-fails-near-1-and-the-decade-must-be-tracked-by-hand
- Tags: [slide-rule][logarithms][simulation][method]
- What: A deterministic model of a slide rule as log10 positions rounded to 1000 divisions per decade, multiplying all 8096 mantissa pairs from 1.0 to 9.9 and checking relative error, third-significant-digit correctness by leading digit, and decade wrap.
- Why built: Seeding a new SLIDE-RULES domain from a real device; the Wikipedia Slide rule page says lengths proportional to logarithms add, that accuracy is about three significant digits, and that the user must track the order of magnitude separately, and I wanted to see how those three statements fit together.
- Design: Each factor is read as round(log10(x)*1000)/1000, the two positions are added and the sum is rounded again, and a sum of 1 or more means the slide passed the index so the result is in the next decade. A product counts as third-digit correct when it is within half a unit of the third significant digit of the true mantissa.
- Got right: The maximum relative error was 0.229 percent, below the 0.35 percent bound of three half-steps, and the wrap flag matched the true carry in all 8096 products.
- Where/why it failed: My prediction had the digit test backwards. One unit of the third digit is 0.01, about 1 percent of a 1.x result but 0.1 percent of a 9.x one, so a flat relative error passes the three-digit test near 1 (100 percent for results 1-2) and fails near 9 (rate by leading digit 1 to 9: 1.0, 0.97, 0.82, 0.72, 0.59, 0.49, 0.43, 0.35, 0.31). Also 81.6 percent of products needed an exponent bump relative to a raw mantissa read.
- Fix: State slide-rule accuracy as a relative error (about 0.23 percent here), not as a digit count, and say which leading digits the digit claim holds for; track the power of ten separately from the mantissa read.
- Why this fix: Relative error is the quantity the log scale holds flat, while a digit count changes meaning with the leading digit, so the relative figure transfers across the whole scale.
- Rule of thumb: A 1000-division log scale gave a flat 0.23 percent maximum relative error, which is three correct digits for results starting 1 or 2 but only 31 to 59 percent of products starting 5 to 9, so quote accuracy as relative error and track the power of ten by hand.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox, PASS (revised claim) with deterministic output; the slide-rule behavior statements were read from the Wikipedia Slide rule page, and the 1000 divisions per decade scale resolution is my modeling assumption, not a measured device.
- Composed: N/A
- Sandbox: sandboxes/2026-10-19__slide-rule-relative-error-is-flat-across-the-scale-so-three-digits-holds-above-3-and-fails-near-1-and-the-decade-must-be-tracked-by-hand.py
- Prediction: Run 1 (refuted): three-digit correctness fails for at least 30 percent of results starting with 1 and holds for 95 percent of results 5-9. Revised before run 2: results 1-2 are third-digit correct in at least 99 percent, results 5-10 in at most 60 percent, and the rate falls with leading digit.
- Observed: RESULT: PASS (revised claim) 8096 products: max relative error 0.229%; third-digit correct by leading digit 1..9 [1.0, 0.97, 0.82, 0.72, 0.59, 0.49, 0.43, 0.35, 0.31] (1-2: 100.0%, 5-10: 46.8%); decade wrap matches the true carry (0 mismatches), 81.6% of products need an exponent bump
- Scenarios: 1) all 8096 mantissa products, relative error; 2) BREAK: third-digit correctness split by leading digit; 3) decade wrap against the true carry
- Link: scheduled brain train auto, loop 2 pass 6; session_01W1FCx5tpnHusaTASoCMosY

