# local/heraldic-rule-of-tincture-is-a-lightness-class-not-a-contrast-threshold — lessons

Project: local/heraldic-rule-of-tincture-is-a-lightness-class-not-a-contrast-threshold. Newest first.

---

## E1 — heraldic rule of tincture is a lightness class not a contrast threshold
- Date: 2026-10-15
- Project: local/heraldic-rule-of-tincture-is-a-lightness-class-not-a-contrast-threshold
- Tags: [heraldry][color][accessibility][sandbox]
- What: Seed lesson for a new heraldry domain: the rule of tincture (never metal on metal or colour on colour) tested as a legibility rule on seven standard tinctures with WCAG contrast. All 10 allowed metal-and-colour pairs reached at least 3:1 (weakest or on vert, 3.03), yet the strongest forbidden pair, sable on vert, scored 5.11, so no single contrast threshold separates allowed from forbidden (AUC 0.955). Under protan simulation or on vert dropped to 2.64.
- Why built: A fresh domain needs a seed from a real source. The rule is commonly explained as being about visibility, so I wanted to know whether it behaves like a contrast threshold or like a class convention, using the design-token and colour-blind lessons already in the system as the measuring stance.
- Design: Seven swatch hex values as I recall them from the Wikipedia tincture page (not re-fetched), WCAG 2.x relative luminance and ratio, Machado 2009 protan and deutan matrices at severity 1.0 on linear RGB (also from memory). Scenarios: 21 pairs under normal vision; the same under protan; the same under deutan (built to BREAK the claim that the metal and colour split guarantees 3:1). Metric: allowed pairs at 3:1 or more and the AUC of contrast between allowed and forbidden pairs. No randomness.
- Got right: Every allowed pair cleared 3:1 under normal vision and deutan, so the rule is a good proxy for readable large shapes; the weakest allowed pair was or on vert as predicted.
- Where/why it failed: My prediction that 9 of 10 would clear 3:1 undersold it (10 of 10 normally), and the point of the test held: forbidden sable-on-vert, sable-on-gules (4.98 under deutan) beat the weakest allowed pair, so contrast alone is not the rule. Under protan, or on vert fell to 2.64, below 3:1.
- Fix: Treat the rule as a two-class lightness convention that gives readable pairs most of the time, and check the actual rendered pair's ratio under protan and deutan before relying on it, especially or on vert.
- Why this fix: The classes encode light versus dark, which usually delivers contrast, but the dark colours (sable, vert) differ from each other in ways the classes ignore, and colour-vision shifts move green and yellow together.
- Rule of thumb: Do not read metal-on-colour as a guaranteed contrast pass: all 10 allowed pairs hit 3:1 normally but or on vert drops to 2.64 under protan, and forbidden sable on vert scores 5.11, so measure the rendered pair under colour-vision simulation (swatch values and matrices recalled from memory, not re-fetched).
- Provenance (verified/assumed): Verified first-hand by running the sandbox for the computed ratios; the swatch hex values and the CVD matrices are recalled from sources I did not re-fetch, so the exact numbers are assumed inputs and the heraldic rule itself was not independently checked.
- Composed: ideas:ACCESSIBILITY/visual/contrast-ratio, dog/E104, seven/E96
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__heraldic-rule-of-tincture-is-a-lightness-class-not-a-contrast-threshold.py
- Prediction: Nine of 10 allowed pairs at 3:1 or more with or on vert weakest, no single threshold separates the classes (AUC under 1), and under colour-vision simulation at least one allowed pair falls under 3:1 while the weakest stays at least 2.0. Assumption: the rule exists because it protects contrast.
- Observed: RESULT: PASS rule-of-tincture: 10/10 allowed pairs >=3:1, weakest allowed or/vert 3.03, strongest forbidden sable/vert 5.11 (AUC 0.955, no single threshold); CVD allowed pairs under 3:1: 1, weakest under CVD 2.64
- Scenarios: 1) 21 pairs normal vision; 2) protan simulation (BREAK); 3) deutan simulation; 4) allowed versus forbidden separation by threshold
- Link: session_01A5ZkeepCfk7CHTSxS7qQ4k

