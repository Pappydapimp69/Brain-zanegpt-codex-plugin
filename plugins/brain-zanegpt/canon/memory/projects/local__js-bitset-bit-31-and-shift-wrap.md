# local/js-bitset-bit-31-and-shift-wrap — lessons

Project: local/js-bitset-bit-31-and-shift-wrap. Newest first.

---

## E1 — js bitset bit 31 and shift wrap
- Date: 2026-10-17
- Project: local/js-bitset-bit-31-and-shift-wrap
- Tags: [bitset][javascript][testing][sandbox]
- What: Ran real JavaScript in node 22 on a 64-flag bitset stored in one number, with set as OR of 1 shifted left by the flag and has as AND with the same mask compared to greater than zero, then a two-word version and a hybrid.
- Why built: Seeds a bit-manipulation domain from a common real bug: JavaScript bitwise operators work on signed 32-bit integers and wrap shift counts, and no existing lesson covers it.
- Design: Python calls node for exact JavaScript semantics; count false negatives setting each of 64 flags alone, false positives testing flags 32 to 63 after setting 0 to 31, then a two-word bitset with a not-equal-zero test, and a hybrid of two words with the greater-than-zero test.
- Got right: The two-word bitset with a not-equal-zero test had 0 false negatives and 0 false positives for all 64 flags.
- Where/why it failed: The single-number version failed in two ways at once: flag 31 (and 63, which wraps to the same bit) gave false negatives because the mask is negative, and 31 of 32 flags above 31 read as set because the shift count wraps modulo 32; my first prediction of 1 and 32 was off by one each because flag 63 also hits the sign bit.
- Fix: Use one 32-bit word per 32 flags indexed by the flag shifted right by 5, mask with the flag and 31, and test the AND result against zero with not-equal, never with greater-than.
- Why this fix: Two words keep every shift count below 32 so nothing wraps, and not-equal zero is correct for the negative mask of bit 31; the hybrid proved the test operator alone leaves bit 31 broken in both words.
- Rule of thumb: In JavaScript test a bitmask with not-equal zero and split flags across 32-bit words: the single-number bitset gave 2 false negatives and 31 false positives over 64 flags, the greater-than-zero test alone still failed 2 of 64 flags, and only the two-word not-equal-zero form was clean.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in node v22.22.0; other engines were not run, although the 32-bit rule comes from the language definition.
- Composed: N/A
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__js-bitset-bit-31-and-shift-wrap.py
- Prediction: Naive single number: 1 false negative (flag 31) and 32 false positives; two words with not-equal zero: none; hybrid with greater-than zero: 2 false negatives. Run 1 missed the naive counts (actual 2 and 31). Assumption: the failure is only at bit 31.
- Observed: RESULT: PASS naive false negatives 2 false positives 31; fixed 0/0; hybrid false negatives 2
- Scenarios: 1) naive set-then-test on 64 flags; 2) naive after setting 0 to 31, test 32 to 63; 3) two-word not-equal-zero fix; 4) hybrid two-word with greater-than-zero, built to break the fix by keeping the test operator.
- Link: scheduled brain train auto loop 2 pass 6 (newdomain; isolated, no adjacent lesson cited); session_011LtaNZCrPYhhAtwJpZ1y8i

