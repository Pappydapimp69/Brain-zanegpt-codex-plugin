# local/sandbox-kernel-presentation-layout — lessons

Project: local/sandbox-kernel-presentation-layout. Newest first.

---

## E1 — per screen word budget is set by the shortest viewport
- Date: 2026-10-09
- Project: local/sandbox-kernel-presentation-layout
- Tags: [layout][viewport][mobile][testing][text]
- What: Applied the PRESENTATION kernel that per-screen word count and viewport fill must be measured per viewport, not eyeballed. A deterministic layout model (greedy wrap, fixed glyph width) was swept across five viewports; the kernel's measurement claim held, and the model showed the usable word budget is a function of the shortest viewport and the body font size.
- Why built: brain train kernel listed this kernel as unapplied, with brain/E13 (short mobile viewports that tests never simulate) and sandbox-kernel-motion-camera/E1 (a fit tested in one orientation fails in the other) as the memory entries it could re-verify.
- Design: One slide = title 56px + paragraph + 64px controls row with 24px padding, 16px body at 1.5 line height, text column capped at 66ch and at viewport minus gutters. Viewports 1440x900, 1280x720, 412x641 and 375x560 (the measured-chrome sizes from brain/E13) and 412x915. Swept word counts 1 to 400 and computed lines, characters per line, overflow in px and whether the controls row stays above the fold. Also compared centered against top-aligned placement, and 16px against 20px body.
- Got right: Measuring found near-miss bands the eye cannot see: at every viewport there is a window of word counts that overflow by only 1 to 24px, so the controls slip below the fold while the slide looks fine. The 66ch cap held desktop at 66 characters per line against 176 uncapped, and phones landed at 47 and 42 characters per line, inside the 35 to 50 target.
- Where/why it failed: My prediction that a 100-word paragraph overflows the 375x560 phone was wrong: it fits with 8px of slack, and the cliff is 106 words. So the kernel's under-about-100 words ceiling is not conservative, it sits within 5 words of the worst phone's limit at 16px. The budgets per viewport were 319, 242, 141, 105 and 235 words (desktop, laptop, phone, worst phone, tall phone), and at 20px body the worst phone budget drops to 68. A height-fixed-900 test (the brain/E13 habit) passed 86 word counts (142 to 227) that fail at 412x641, and centering 45 words on the 412x915 phone stranded a 290px gap that top-alignment removes (0px).
- Fix: Compute the word budget as the minimum over the target viewport set at the actual body font size, then set copy to roughly half of that minimum rather than at it, and assert controls-above-fold in the same sweep. Top-align one-thing-per-screen content.
- Why this fix: The budget is a minimum over viewports, so a single remembered number is only right for one font size and one viewport set; the 5-word margin to the cliff means ordinary variation in wrapping tips it over. Same shape as sandbox-kernel-motion-camera/E1: a bound derived from one orientation or height silently assumes it.
- Rule of thumb: Measure controls-above-fold per viewport and derive the word budget from the shortest one at the real font size: here 105 words at 16px but 68 at 20px on 375x560, and a 900px-tall-only test missed 86 failing word counts. Write copy to about half the measured budget and top-align.
- Provenance (verified/assumed): Verified first-hand in the sandbox file named below, deterministic, run to RESULT: PASS 9/9 checks. The model uses a fixed 0.5em average glyph and 6 characters per word, so absolute numbers depend on those; the shape (minimum over viewports, font-size dependence, fixed-height false passes) does not. Not run in a real browser, and the NN/g and whitespace-folklore claims in the kernel were not exercised.
- Composed: ideas:PRESENTATION/layout/measure-per-screen-word-count-and-viewport-fill-dont-eyeball, brain/E13, sandbox-kernel-motion-camera/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-09__per-screen-word-budget-is-set-by-the-shortest-viewport.py
- Prediction: A 45-word paragraph fits all five viewports, a 100-word paragraph overflows 375x560, and a 900px-only test passes counts that fail at 641px.
- Observed: RESULT: PASS 9/9 checks; budgets 319/242/141/105/235 words; 100 words fits 375x560 with 8px slack (prediction wrong there), cliff at 106; 20px body budget 68; 86 false passes at 412x900; centered gap 290px vs 0.
- Scenarios: 1) per-viewport budget sweep; 2) 45 vs 100 words; 3) near-miss overflow band; 4) BREAK: height-fixed-900 vs 641; 5) centered vs top-aligned tall phone; 6) characters-per-line with and without the cap; 7) BREAK: 20px body against 16px
- Link: brain train auto pass 1 (kernel mode)

