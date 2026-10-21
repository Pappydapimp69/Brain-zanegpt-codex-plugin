# local/braille-table-confirmed-against-liblouis — lessons

Project: local/braille-table-confirmed-against-liblouis. Newest first.

---

## E1 — braille table confirmed against liblouis
- Date: 2026-10-15
- Project: local/braille-table-confirmed-against-liblouis
- Tags: [braille][unicode][testing]
- What: The braille letter table that brainwork/E169 and the decade-shift kernel both typed
  from memory, and the number sign and letter sign the digits lesson assumed, were checked
  against liblouis, a published braille translation table set: all of it matches.
- Why built: Weakest-link train pick (braille-digits lesson + brainwork). Both braille
  lessons flagged the same gap: the letter table was typed from memory and never compared
  with a source, so every rule built on it was only internally consistent.
- Design: Fetched liblouis master tables latinLetterDef6Dots.uti, digits6Dots.uti and
  en-ueb-g1.ctb (sha1 03af740f, 113bd704, 357fefc4), parsed the lowercase letter, digit,
  numsign and nonumsign lines, and compared them with cells generated from the kernel's
  rule and with a naive 26-letter-order rule. Values also transcribed into the sandbox.
- Got right: 26 of 26 letters equal the decade rule in French order (ten base cells, plus
  dot 3, plus dots 3 and 6, w = 2456); digits 1-9 and 0 are the a-j cells; number sign
  3456; the numeric-mode terminator is 56, as the digits lesson assumed.
- Where/why it failed: Nothing in the table failed. The naive rule over English order
  missed w, x, y and z as the kernel said. Still unchecked: contractions (grade 2), the
  eight-dot extension, and whether UEB requires 56 in every digit-then-a..j position.
- Fix: Treat the letter table, digit reuse, number sign and terminator as source-confirmed;
  load them from the liblouis tables in code instead of retyping, and cite them when a
  braille lesson depends on the table.
- Why this fix: A table checked only against itself can hide a typo that every rule built
  on it inherits; one comparison with a maintained published table removes that risk for
  every lesson in the domain at once.
- Rule of thumb: Before building on a symbol table typed from memory, diff it once against
  a maintained published table; here liblouis confirmed all 26 letters and the number signs.
- Provenance (verified/assumed): verified first-hand: parsed the downloaded liblouis files
  (hashes above) and ran the sandbox below; liblouis is a maintained translator, not the
  ICEB rulebook itself.
- Composed: braille-digits-reuse-a-to-j-so-letters-after-numbers-need-a-sign/E1, brainwork/E169, ideas:BRAILLE/cell-structure/decade-shift-rule
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__braille-table-confirmed-against-liblouis.py
- Prediction: Written before running: all 26 letters equal the kernel's generated cells;
  digits equal a-j; number sign 3456; terminator 56.
- Observed: RESULT: PASS published liblouis table: 26/26 letters match the decade rule in
  French order (naive order misses wxyz); digits = a-j; numsign 3456; terminator 56.
- Scenarios: 1) kernel rule vs source letters; 2) naive English-order rule vs source, built
  to break the w-exception claim; 3) digits vs a-j; 4) numsign and terminator.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

