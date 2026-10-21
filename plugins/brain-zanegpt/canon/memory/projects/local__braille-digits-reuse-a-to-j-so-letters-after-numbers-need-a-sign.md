# local/braille-digits-reuse-a-to-j-so-letters-after-numbers-need-a-sign — lessons

Project: local/braille-digits-reuse-a-to-j-so-letters-after-numbers-need-a-sign. Newest first.

---

## E1 — braille digits reuse a to j so letters after numbers need a sign
- Date: 2026-10-15
- Project: local/braille-digits-reuse-a-to-j-so-letters-after-numbers-need-a-sign
- Tags: [braille][unicode][sandbox][testing]
- What: Extended the braille decade-shift kernel to numbers: digits reuse the a-j base cells
  after a number sign, so a converter built from the kernel's ten base cells misreads
  every string where a letter a-j directly follows a digit, unless it emits a letter sign.
- Why built: Weakest-link train pick: the kernel says store ten base cells plus shift rules
  for a converter, but tested letters only (numbers untested); the same ten cells are the
  digits, so a converter that follows the kernel inherits that collision.
- Design: Encoder generated only from the kernel's rule (ten base cells, plus dot 3, plus
  dots 3 and 6, w as dots 2456, French order), cells as Unicode code points; number sign
  dots 3456 with numeric mode lasting to the next non-digit cell; optional letter sign dots
  56. Round-tripped every string of length 1 to 3 over a-z and 0-9.
- Got right: The kernel's 26 letter cells came out distinct, and with the letter sign
  inserted before an a-j letter that follows a digit, all 47,988 strings round-tripped.
- Where/why it failed: Without the letter sign 7,300 strings (15.2%) failed, exactly the
  set with a digit immediately followed by a-j (0a reads as 01); digit then k-z never failed,
  since those cells are not digit cells. The kernel's store-ten-cells advice is safe for
  letters only.
- Fix: When a converter reuses the ten base cells for digits, track numeric mode and emit a
  letter sign before a-j after a digit; test the round trip on digit-letter adjacency, not
  on words.
- Why this fix: The collision is structural: the decade rule makes a-j the digits, so the
  ambiguity sits exactly where the two meet, and a mode flag plus one indicator removes it.
- Rule of thumb: Braille digits are the a-j cells, so a letter a-j right after a number
  needs a letter sign; round-trip digit-then-letter strings when building a converter.
- Provenance (verified/assumed): verified first-hand by the exhaustive sandbox below; the
  number sign (3456), digit mapping and letter sign (56) are the standard as I know it, not
  re-checked against a published rulebook in this run; grade 1 only, no contractions.
- Composed: ideas:BRAILLE/cell-structure/decade-shift-rule
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__braille-digits-reuse-a-to-j-so-letters-after-numbers-need-a-sign.py
- Prediction: Written before running: without a letter sign exactly the strings with a digit
  followed by a-j fail (digit then k-z safe); with the letter sign 0 fail.
- Observed: RESULT: PASS 7300/47988 strings misread without a letter sign, all and only
  digit-then-a..j; 0 with it; digit-then-k..z failures 0.
- Scenarios: 1) all 1-3 character strings, no letter sign; 2) same with letter sign;
  3) digit followed by k-z, built to break the "only a-j collide" claim.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/local__braille-table-confirmed-against-liblouis.md#E1 · compatible · sandboxes/2026-10-15__braille-table-confirmed-against-liblouis.py · observed RESULT: PASS published liblouis table: 26/26 letters match the decade rule in French order (naive order misses wxyz); digits = a-j; numsign 3456; terminator 56. · https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Audited: 2026-10-15 · modeled · Read the entry and its stored sandbox. Q1: the result is computed, not asserted: the encoder and decoder run over all 47,988 strings of length 1 to 3 and the failure set is compared to an independently written predicate (digit directly before a-j), so the 7,300 count is a real measurement. Q2: coverage matches the Rule of thumb (a letter a-j right after a number needs a letter sign) within grade 1, but the mode-ending behaviour is whatever the author's own decoder does: numeric mode ends on any non-digit cell, so the 'exactly the digit-then-a-j set' equality follows from decoder design, and real numeric mode also persists through some punctuation and ends at a space, none of which is modelled. Q3: the claim is about the real braille standard (number sign 3456, letter sign 56, digits as a-j), but only a hand-written encoder and decoder from the author's reading were tested, and the entry itself says the signs were not checked against a published rulebook or a library such as liblouis. The direction matches what I know of the standard, but the sandbox cannot prove it, so modeled rather than pass. · https://claude.ai/code/session_01MwzyRZN1HRxgk5hnQqG5R4
