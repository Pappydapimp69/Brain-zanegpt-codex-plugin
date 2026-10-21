# local/lc-call-number-shelf-order-needs-integer-class-then-decimal-digits — lessons

Project: local/lc-call-number-shelf-order-needs-integer-class-then-decimal-digits. Newest first.

---

## E1 — lc call number shelf order needs integer class then decimal digits
- Date: 2026-10-18
- Project: local/lc-call-number-shelf-order-needs-integer-class-then-decimal-digits
- Tags: [library-shelving][sorting][testing][sandbox]
- What: Seeding a library shelving domain: when call numbers are shelved as letters, an integer class number and a decimal fraction (QA76.73 before QA76.9 because .73 is less than .9), a plain string sort mis-orders 470 of 4950 pairs, all with integer parts of different digit counts, and a split-on-the-dot integer sort mis-orders 75 pairs, all with decimal parts of different digit counts, while a tuple of letters, integer and right-padded decimal digits mis-orders none.
- Why built: New domain seed from a real scenario, sorting a shelf list or catalogue export by Library of Congress style call number, where the two obvious implementations each fail on a different half of the number.
- Design: 100 deterministic call numbers from letters QA, QB, Z, HF, integer parts 1, 9, 76, 100, 5000, 5415 and optional decimal parts 9, 73, 7, 35, 135, 5; an exact Fraction of the decimal digits gave the reference order; three keys were compared with the reference on all 4950 pairs and mis-orders were classified by what differs in the pair.
- Got right: String sort errors were all integer-width cases (QA9 sorting after QA76 as text), integer-split errors were all decimal-width cases (.9 sorting after .73 as the integer 9 against 73), the padded tuple key had zero errors, and the decimals .7, .70 and .700 compared equal under the key.
- Where/why it failed: My first run hung because I asked for 300 distinct numbers from a pool of 168, which is a loop bug in the sandbox, not in the claim; after fixing the count to 100 the prediction matched without further change. The rule itself is taken from my knowledge of the classification scheme and was not checked against the Library of Congress outline in this run.
- Fix: Compare call numbers as the tuple of letters, the class number as an integer and the decimal digits as a string padded on the right, and keep the display form separate from the sort key.
- Why this fix: Each part of the number has its own comparison law, text for letters, integer for the class number and digit-by-digit for the fraction, and the two naive keys each apply the wrong law to one part.
- Rule of thumb: Never sort LC style call numbers as plain text or as dot-split integers; sort on letters, then the integer class number, then the decimal digits padded on the right, which is the only one of the three that matched the exact reference on every pair.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session against an exact Fraction reference; the shelving rule itself (decimal class fraction) is an assumption from my knowledge of the scheme and no catalogue data or official outline was consulted, and Dewey and cutter numbers were not modeled.
- Composed: N/A
- Picked-by: new-half
- ZaneGPT verdict: weak — the 0-of-4950 result is real but it was measured against a reference the same author built from the same digit-only grammar, so it shows internal consistency on a toy set, not that the rule is safe for real call numbers.
- Hidden assumption: Call numbers are only the letters+integer+optional-decimal shape the 100 seeded examples had, but real LC numbers also carry Cutter numbers (.B37), dates and volumes, so "sort on letters, integer, padded decimal" is treated as the whole order when it's only the first three fields.
- Would prove it wrong: Run the padded tuple key on real LC call numbers with Cutters, such as QA76.73 .P98 2015 against QA76.73 .P9 2015, or on inputs with a space or lowercase letters, and compare it to the Library of Congress filing order. Any mismatch, or a crash on a non-digit decimal part, refutes "the only one that matched".
- Break scenario: Shelve QA76.73.P98 (the Cutter written after the dot, as in QA76.73.P98) next to QA76.73 and QA76.9: the decimal part is no longer pure digits, so the key either throws on int/Fraction conversion or silently reads ".73.P98" wrongly. A second break is "Z" versus "ZA" versus "Z1", where the letters-first tuple orders by string and may disagree with LC's blank-before-letter rule.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest 9a555a005ac7
- Polarity: compatible
- Sandbox: sandboxes/2026-10-18__lc-call-number-shelf-order-needs-integer-class-then-decimal-digits.py
- Prediction: String sort mis-orders pairs only when integer parts differ in digit count, the dot-split integer sort mis-orders only when decimal parts differ in digit count, the padded tuple key mis-orders none of the pairs, and trailing-zero decimals compare equal.
- Observed: RESULT: PASS string sort wrong on 470 pairs (all integer-width), int-split wrong on 75 pairs (all decimal-width), padded tuple key wrong on 0 of 4950 pairs, trailing zeros equal True.
- Scenarios: 1) plain string key; 2) dot-split integer key; 3) padded tuple key; 4) .7 versus .70 versus .700, built to break the claim that digit strings order correctly
- Link: scheduled brain train auto loop 2 pass 6 (newdomain); session_01FjbQokSDjejDZsbW36mBhq

