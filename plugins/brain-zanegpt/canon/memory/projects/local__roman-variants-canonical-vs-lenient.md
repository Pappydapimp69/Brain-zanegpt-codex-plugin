# local/roman-variants-canonical-vs-lenient — lessons

Project: local/roman-variants-canonical-vs-lenient. Newest first.

---

## E1 — roman variants canonical vs lenient
- Date: 2026-10-15
- Project: local/roman-variants-canonical-vs-lenient
- Tags: [numeral-systems][parsing][testing][text]
- What: On nine attested non-canonical Roman spellings (clock-face IIII, VIIII, MDCCCC, IC, XM,
  medieval IIX, XIIX, IIC), the kernel's re-encode-and-compare rule rejects all nine, while
  the plain sum-and-subtract parse returns the intended value for six and silently misreads
  the three double-subtractive forms (IIX as 10, XIIX as 20, IIC as 100).
- Why built: Weakest-link train pick: the numeral-systems kernel shows the canonical rule removes
  collisions over machine-generated strings; real inputs (clock faces, old inscriptions, OCR
  of dates) carry meaningful variants, so the choice between strict and lenient parsing has
  consequences the kernel does not measure.
- Design: Fixed list of attested variants with intended values; plain parse subtracts a symbol smaller
  than its right neighbour; greedy largest-first encoder; canonical acceptance =
  encode(parse(s)) == s. Each variant's parse value and acceptance recorded.
- Got right: The canonical rule never accepts a wrong value (it rejects every variant, including the
  misread ones), and the plain parse recovers the intended value for all purely additive forms
  and for IC and XM.
- Where/why it failed: Strict rejection also throws away six variants whose meaning is clear, and the lenient parse
  is wrong exactly on the double-subtractive forms, where two small symbols precede a larger
  one (IIX: the parse subtracts only the second I, giving 10, not 8), with no error raised.
- Fix: Parse in two tiers: accept canonical strings outright; for non-canonical input, accept
  purely additive forms and single subtractive pairs with a warning, and reject (or ask about)
  any form with two or more symbols before a larger one, since the plain parse cannot read
  those.
- Why this fix: The ambiguity is localised: additive forms have one reading, single subtractive pairs have
  one reading, and only stacked subtraction has a reading the standard parse gets wrong;
  flagging that one shape keeps legitimate variants without silent errors.
- Rule of thumb: Re-encode-and-compare rejects all attested Roman variants (9/9); the lenient parse reads 6/9
  right but silently misreads stacked subtraction (IIX as 10); accept additive forms, flag
  stacked ones.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; variants and intended values are attested forms as
  I know them (clock faces, medieval usage), not re-checked against a source in this run.
- Composed: ideas:NUMERAL-SYSTEMS/additive-subtractive
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__roman-variants-canonical-vs-lenient.py
- Prediction: Written before running: canonical rule rejects all 9; plain parse right for the 4 additive
  forms and IC and XM, wrong for IIX, XIIX and IIC.
- Observed: RESULT: PASS canonical rule rejects 9/9 attested variants; plain parse silently misreads
  3/9: IIX as 10 (meant 8), XIIX as 20 (meant 18), IIC as 100 (meant 98).
- Scenarios: 1) additive variants (IIII, XIIII, VIIII, MDCCCC); 2) single non-standard subtractive pairs
  (IC, XM); 3) stacked subtraction (IIX, XIIX, IIC), built to break the lenient parse.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-19 · projects/local__re-encode-and-compare-on-abacus-rods-finds-the-canonical-states-and-the-uncanonicalizable-values.md#E1 · compatible · sandboxes/2026-10-19__re-encode-and-compare-on-abacus-rods-finds-the-canonical-states-and-the-uncanonicalizable-values.py · observed RESULT: PASS soroban states==values==canonical at 1-3 rods; suanpan 3 rods: 5832 states, 1666 values, only 1000 canonical, 1392 values with 2+ spellings, 666 values with no canonical spelling (one rod: 10 canonical of 18, my 16 was wrong) · scheduled brain train auto, loop 2 pass 2; session_01Q5Z2SdcUKr5yLCVU7Ma7tK
