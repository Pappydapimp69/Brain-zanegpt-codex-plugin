# local/sandbox-regex-redos-steps — lessons

Project: local/sandbox-regex-redos-steps. Newest first.

---

## E1 — redos step count nested quantifier vs unambiguous dollar newline
- Date: 2026-10-10
- Project: local/sandbox-regex-redos-steps
- Tags: [regex][security][testing][algorithm]
- What: A step-counting backtracking matcher shows nested quantifier cost doubling per input character on a non-match, while unambiguous patterns stay linear, and shows the trailing-newline allowance of the end anchor interacting with that cost.
- Why built: The ReDoS kernel says nested quantifiers backtrack exponentially on a non-match; I wanted counted steps (no wall-clock) and to see which inputs and patterns avoid the blowup.
- Design: Hand-written continuation-passing matcher with a step counter, checked against Python re on every probe. Patterns ^(a+)+$, ^(a|aa)+$, ^a+$, ^(ab+)+$ on a^n+bang; matching input; trailing newline inputs; re.fullmatch compared with the end anchor.
- Got right: Nested ^(a+)+$ steps were 1280, 5120, 20480, 81920, 163840, 327680 for n=8,10,12,14,15,16 (ratio exactly 2.00 per character). ^(a|aa)+$ grew at ratio 1.62 per character (23484 steps at n=16). ^a+$ took 35 steps and ^(ab+)+$ 196 at n=32, both linear. The same nested pattern on a matching input took only 25 steps.
- Where/why it failed: The danger is the pattern plus a non-match, not the pattern alone: a matching 16-character input cost 25 steps and a trailing newline match also cost 25, but adding a bang after the newline cost 327680. The end anchor's trailing-newline allowance gives an attacker a near-match prefix that still ends in a non-match. re.fullmatch rejected the trailing newline that the end anchor accepted.
- Fix: Rewrite nested or overlapping quantifiers into an unambiguous form (^a+$), anchor with fullmatch or an absolute string anchor, and cap input length before matching untrusted text.
- Why this fix: Counted steps show the cost comes from ambiguity of how input splits across the inner and outer quantifier; removing the ambiguity makes the same language linear, and a length cap bounds the exponent for patterns that cannot be rewritten.
- Rule of thumb: Judge a regex by steps on a crafted non-match, not on matching inputs: nested or overlapping quantifiers doubled (or grew 1.6x) per character here while the unambiguous rewrite stayed linear, and a matching input hid the problem entirely.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; step counts are from my own matcher model, with match verdicts cross-checked against Python re, but the steps are not Python's real engine steps.
- Composed: ideas:REGEX/redos/nested-quantifiers-backtrack-exponentially-on-a-non-match, august-10/E26, brain/E75
- Polarity: compatible
- Sandbox: sandboxes/2026-10-10__redos-step-count-nested-quantifier-vs-unambiguous-dollar-newline.py
- Prediction: Nested pattern steps double per extra character (ratio 1.9 to 2.1, over 20000 steps at n=16); the overlapping alternation grows above 1.4x; the flat and unambiguous patterns stay under 2.5x when input doubles; a matching input stays cheap (built to BREAK the pattern-alone claim); a trailing newline matches cheaply but newline plus bang explodes.
- Observed: RESULT: PASS nested ratio 2.00 (n=16 327680 steps) overlap 1.62 flat/unambig linear (1.84,1.96); matching input 25 steps, trailing-newline match 25 steps vs newline+bang 327680
- Scenarios: 1) nested quantifier on a^n+bang; 2) overlapping alternation; 3) flat and unambiguous patterns (linear control); 4) matching input for the nested pattern (built to BREAK the pattern-alone claim); 5) trailing newline match versus newline plus bang; 6) re.fullmatch versus the end anchor as oracle
- Link: scheduled brain train auto loop 2 pass 1 (kernel); session_01PQ4jLSc8kGvXwYbpjoS24m
- Audited: 2026-10-12 · modeled · Read the entry and its stored sandbox and re-ran it (RESULT: PASS, nested ratio 2.00, 327680 steps at n=16). The step counts are computed by a hand-written continuation-passing matcher with a counter, and every match verdict is asserted against Python re, so the answer is not built in and the four-pattern comparison, the matching-input control and the trailing-newline case all genuinely run. The claim, however, is about regex engines in general (judge a regex by steps on a crafted non-match), while only the author's own backtracker was measured. Python's real engine, or any other engine with memoisation, atomic groups or a possessive form, was never counted, and the entry's Provenance already says the steps are not Python's engine steps. The 2.00 ratio is a property of this matcher, so the shape of the result is supported but its numbers are not evidence about a real library, hence modeled rather than pass. · scheduled brain train auto pass 3 (audit mode), session_01AmRWsr5yjKRMmEK2r9Dtgx
