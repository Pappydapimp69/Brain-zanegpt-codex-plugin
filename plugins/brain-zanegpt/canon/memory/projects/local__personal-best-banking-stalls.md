# local/personal-best-banking-stalls — lessons

Project: local/personal-best-banking-stalls. Newest first.

---

## E1 — personal best banking stalls and a small capped per run term does not unstick it
- Date: 2026-10-15
- Project: local/personal-best-banking-stalls
- Tags: [gamedesign][balance][economy]
- What: Composed od76 E16 (bank only newly crossed personal-best levels, applied next run) with od76 E7
  (record-only rewards stall or snowball; pair with a capped per-run term), with brainwork E189's
  warning to audit what a saturating lever does, in an 80-run campaign model.
- Why built: E16's personal-best banking is a record-only reward, so by E7 it should stall or snowball; E7's
  remedy is a capped per-run term. The question was where banking lands and whether the remedy works
  at a realistic cap.
- Design: Deterministic (seeded luck 0.85 to 1.15). Stage s costs min(25, 4 + s); a run reaches the deepest
  stage its budget times luck covers; budget starts at 60. Banking adds k budget per newly crossed
  best stage (k 2 or 20); a variant adds +1 per run capped at +20. 80 runs, 20 seeds; longest drought
  without a new best, number of bests, final depth.
- Got right: With k 2 personal-best banking stalls hard: after about three bests the next one needs a luckier run
  than any so far, and the longest drought was 76 of 80 runs (median), in all 20 seeds.
- Where/why it failed: The capped per-run term did not unstick it: +1 a run capped at +20 still left a median drought of 57
  runs, because 20 extra budget is less than one deep stage (25) once costs saturate. And k 20 did not
  snowball the way I predicted: 25 bests in 80 runs with droughts up to 31, because the cost cap and
  luck still bound each step.
- Fix: Size the per-run term against the cost of the next stage, not as a token amount: its cap must exceed
  at least one stage's cost at the depth where bests stop, or tie it to the gap between budget and the
  next stage. Simulate the drought length, not just the final depth.
- Why this fix: A record-only reward stalls once beating the record needs luck beyond what has been seen, and
  records thin out like a logarithm; a per-run term only helps if it can move the budget past the next
  threshold on its own.
- Rule of thumb: Personal-best banking is a record-only reward and stalls: with small gains the median drought was 76
  of 80 runs, and E7's capped per-run term (+20 total) left 57 because it was smaller than one stage's
  cost; size the per-run term to the next stage, and measure droughts.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry; stage costs follow od76 E7's design (min(25, 4 +
  stage)), the rest is my fixture, not od76's real numbers.
- Composed: pappydapimp69__od76/E16, pappydapimp69__od76/E7, pappydapimp69__brainwork/E189
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__personal-best-banking-stalls-and-a-small-capped-per-run-term-does-not-unstick-it.py
- Prediction: k 2 banking: drought over 20 runs in most seeds; k 20 snowballs (a best nearly every run); the
  capped per-run term cuts the k 2 drought below 10 runs in most seeds.
- Observed: RESULT: FAIL 1/3; k2 PB-only drought>20 in 20/20 seeds; k2 + capped per-run drought<10 in 0/20; k20
  median PBs 25 of 80 runs
- Scenarios: 1) k 2 banking only; 2) k 2 plus capped per-run term (built to BREAK E7's remedy at a token cap: it
  failed); 3) k 20 banking; 4) k 20 plus per-run; 20 seeds each
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 3 pass 2 (edge brainwork + od76), 2026-10-15

