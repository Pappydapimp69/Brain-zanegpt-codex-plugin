# local/2026-10-08__a-size-only-cover-keeps-only-the-flat-at-n-equals-p-and-loses-2p-3p-so-the-multiple-of-p-plateau-needs-the-exact-subset-test — lessons

Project: local/2026-10-08__a-size-only-cover-keeps-only-the-flat-at-n-equals-p-and-loses-2p-3p-so-the-multiple-of-p-plateau-needs-the-exact-subset-test. Newest first.

---

## E1 — a size only cover keeps only the flat at n equals p and loses 2p 3p so the multiple of p plateau needs the exact subset test
- Date: 2026-10-08
- Project: local/2026-10-08__a-size-only-cover-keeps-only-the-flat-at-n-equals-p-and-loses-2p-3p-so-the-multiple-of-p-plateau-needs-the-exact-subset-test
- Tags: [testing][state][input]
- What: The size-only ('sloppy') cover test has a single flat at N=P and none at 2P, 3P or 4P for P=5 to 12, and its totals differ from the exact subset cover at N=P for every P (for example 100 vs 10 at P=5), so the multiple-of-P plateau pattern discriminates the exact cover from the sloppy one.
- Why built: A repeated 'sloppy differs' control in the family only compared single values; with the full plateau pattern known, the control can be made sharper.
- Design: The C program's mode switch replaces the subset test with a landing-count comparison, run for P=5 to 12 at base 5051 with N up to 4P+1; flats and N=P totals are compared with the exact cover.
- Got right: The totals differ at N=P for every P, matching the recorded control.
- Where/why it failed: The prediction that the sloppy cover would also keep flats at every multiple of P was wrong: it keeps only the flat at N=P, so the plateau is a property of the exact cover.
- Fix: Use the full flat set (every multiple of P) as the discriminating control in future sandboxes of this family, not only one total.
- Why this fix: Sloppy and exact covers coincide on one plateau but diverge on the periodic structure, which a single value cannot show.
- Rule of thumb: When testing a cover implementation, check the whole plateau pattern (flats at every multiple of P), because a size-only cover reproduces only the first flat at N=P.
- Provenance (verified/assumed): First-hand run of the shipped sandbox this session (needs gcc): RESULT: FAIL size-only cover keeps flats at every multiple of P: False (it has a single flat at N=P: True); its total at N=P differs from the exact cover for every P: True
- Composed: local__age-cutoff-roll-up/E1
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-08__a-size-only-cover-keeps-only-the-flat-at-n-equals-p-and-loses-2p-3p-so-the-multiple-of-p-plateau-needs-the-exact-subset-test.py
- Prediction: The size-only cover also has flats at every multiple of P for P=5..12 (the pattern is independent of the cover rule), but its total at N=P differs from the exact cover for every P.
- Observed: RESULT: FAIL size-only cover keeps flats at every multiple of P: False (it has a single flat at N=P: True); its total at N=P differs from the exact cover for every P: True
- Scenarios: 1) sloppy flats for P=5..12; 2) totals at N=P versus exact; 3) multiples of P built to break the claim that the pattern is cover-independent (it is not)
- Link: scheduled brain train pass, boundary hunt on the cover-test family
- Audited: 2026-10-09 · pass · Read the entry and its stored C-bitset sandbox and reran it (gcc present): it computes totals for P=5..12 up to N=4P+1 from the landing model rather than assuming them, and printed single flats [P] for the size-only mode and differing N=P totals versus the exact subset test, the same RESULT: FAIL line the entry records (the FAIL is the refuted prediction, filed as incompatible, which is correct). Limits: only one size-only variant is tested (count of b not above count of a), so the rule covers that variant rather than every size-based cover; and this script never recomputes the exact cover's flats at 2P, 3P, 4P, relying on other entries for that half of the contrast. Neither gap contradicts the claim as worded. · scheduled brain train pass 3 audit, rerun of the stored sandbox
- Audited: 2026-10-09 · fail · Read the entry and its stored C-plus-Python sandbox. The model computes its answer (landing bitsets, exact shadow counts, flats found by differencing), so nothing is built in, and it honestly reports its own wrong prediction. But the sandbox tests exactly one size-only rule, count(b) <= count(a), while the Rule of thumb says a size-only cover reproduces only the first flat. I patched a copy of the sandbox with three other size-only rules and ran P=5 and P=8 at bases 5051 and 17. Strict count(b) < count(a) kept every flat (5,10,15,20 and 8,16,24,32) just like the exact cover; count(b) == count(a) kept only the flat at N=P; count(b) >= count(a) kept no flats at all. So the claim holds for the rule tested but not for size-only covers in general, and the plateau check discriminates some size-only rules and not others. The entry should be narrowed to the specific rule, and the strict-less-than variant is a counterexample to the general wording. · https://claude.ai/code/session_01GfAHwy3Bruhswzp52FBWqr
