# local/fibonacci-world-older-presses-look-fresher — lessons

Project: local/fibonacci-world-older-presses-look-fresher. Newest first.

---

## E1 — on a fibonacci world older presses look fresher to a mismatch gate
- Date: 2026-10-15
- Project: local/fibonacci-world-older-presses-look-fresher
- Tags: [testing][state][input]
- What: Composed the lossless age-cutoff lesson (cutoff on top of validity is lossless exactly at the
  largest valid lag, never derived from the period) with the quasi-periodic mismatch-aliasing lesson
  (mismatch goes blind at a Fibonacci word's near-period lags), on a world with no period at all.
- Why built: Both lessons warn against deriving staleness from a period; on a quasi-periodic world there is no
  period to derive from, and the question was whether the lossless rule still holds and where a
  mismatch gate leaks.
- Design: Deterministic. Fibonacci word of 2,200 symbols (1 = role B available); hint at t says B when
  available; press lands at t + L. Lag sets {1,2,34}, {1,2,30}, {3,55,60}: largest valid lag against
  smallest lossless cutoff. Mismatch rate (state at t differs from state at t + L) at lags 13 to 89.
- Got right: The smallest lossless cutoff equalled the largest valid lag in all three sets (34, 30, 60), so the
  rule needs no period. Mismatch read near zero at Fibonacci lags (13: 0.069, 21: 0.042, 34: 0.026,
  55: 0.016, 89: 0.010) against 0.764 at 30 and 0.558 at 40.
- Where/why it failed: I predicted lag 60 would show high mismatch like 30; it read 0.164, because 60 sits near 55 + 5, a
  sum of Fibonacci numbers, where the word nearly repeats too. And the blindness deepens with age: the
  older the Fibonacci lag, the lower the mismatch, so a mismatch gate trusts the stalest presses most.
- Fix: Gate staleness on age with the cutoff at the largest valid lag; never use mismatch, and do not try
  to blacklist 'bad' lags, since near-returns sit at Fibonacci numbers and their sums.
- Why this fix: Age measures what the rule is about and needs no knowledge of the world's structure; a list of
  aliased lags is incomplete by construction on a quasi-periodic world.
- Rule of thumb: On a quasi-periodic (Fibonacci) world the lossless cutoff is still the largest valid lag, but a
  mismatch gate trusts older presses more: mismatch fell 0.069, 0.042, 0.026, 0.016, 0.010 at lags 13
  to 89 and stayed low near Fibonacci sums (60: 0.164); gate on age.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry.
- Composed: local__age-cutoff-lossless-threshold-exceeds-period-p12/E1, local__sandbox-mismatch-aliasing-quasiperiodic-fibonacci-lags/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__on-a-fibonacci-world-older-presses-look-fresher-to-a-mismatch-gate.py
- Prediction: lossless cutoff = largest valid lag in all sets; mismatch under 0.10 at 34 and 55, over 0.30 at 30
  and 60.
- Observed: RESULT: FAIL 2/3; lossless cutoff = largest valid lag (34, 30, 60); mismatch at Fibonacci lags 34
  0.026, 55 0.016 vs 30 0.764, 60 0.164
- Scenarios: 1) Fibonacci lag set; 2) non-Fibonacci set; 3) mixed set; 4) built to BREAK the 'only Fibonacci lags
  alias' reading: lag 60 (low too, 0.164)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 5 pass 2 (edge), 2026-10-15

