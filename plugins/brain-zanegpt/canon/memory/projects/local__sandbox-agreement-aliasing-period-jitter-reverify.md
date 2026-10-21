# local/sandbox-agreement-aliasing-period-jitter-reverify — lessons

Project: local/sandbox-agreement-aliasing-period-jitter-reverify. Newest first.

---

## E1 — agreement aliasing period jitter reverify
- Date: 2026-09-30
- Project: local/sandbox-agreement-aliasing-period-jitter-reverify
- Tags: [ui][input][state][gamedev][testing]
- What: Re-verified the agreement-versus-age-tag aliasing lesson on a period-jittered waveform (periods alternating 15 and 16, super-cycle 31) against the strict period-15 waveform the earlier sandboxes used.
- Why built: The aliasing lesson and the aliasing fallback-tradeoff lesson both used strict periodic state and were single-source together; jitter tests whether aliasing is tied to the nominal period or to the true repeat length.
- Design: Deterministic 620 ticks, no RNG. State is on for the first 5 ticks of each period. A hint made at tick t is compared with state at t plus lag L; agreement counts mismatches, the age tag flags every hint when L exceeds threshold 2. Lags 1,15,30,31,62 on both worlds.
- Got right: Strict period 15 agreement flags 0 of 620 at L=15 and 30 while the age tag flags 620. Jittered agreement flags 40 at L=15, 80 at L=30 and 0 at L=31 and 62; the age tag flags 620 in every case with L above 2.
- Where/why it failed: Aliasing is not tied to the nominal period: a lag equal to the nominal 15 stops aliasing once jitter exists, and aliasing moves to the true super-cycle 31, so a guard tuned to the nominal period misses the real blind lags.
- Fix: Derive blind lags from the true repeat length of the state, or stamp age at emit time, which does not alias at any lag.
- Why this fix: Agreement only compares values, so it is blind exactly where the state repeats; an emit-time stamp measures elapsed time directly and has no such dependence.
- Rule of thumb: Agreement checks alias at multiples of the true repeat length, not the nominal period; on the jittered world lag 15 flagged 40 stale hints and lag 31 flagged 0, so find the real cycle before trusting agreement, or stamp age.
- Provenance (verified/assumed): Verified first-hand by running the sandbox and copying its counts; one jitter pattern (15,16) and one threshold, other jitter patterns not run.
- Composed: local__age-cutoff-roll-up/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__agreement-aliasing-period-jitter-reverify.py
- Prediction: strict agreement flags 0 at L=15 and 30, jittered agreement flags some but not all at L=15 and 30 and exactly 0 at L=31 and 62, age tag flags every hint at lags above 2.
- Observed: RESULT: PASS agreement aliases to 0 only at true cycle multiples (strict 15,30; jitter 31,62); age tag flags all 620
- Scenarios: 1) strict period 15 at L=15,30 2) jittered 15/16 at L=15,30 built to break the nominal-period alias claim 3) jittered at L=31,62 true cycle multiples 4) L=1 short lag
- Link: scheduled train pass 2
- Audited: 2026-10-11 · pass · Read the entry and its stored sandbox (sandboxes/2026-09-30__agreement-aliasing-period-jitter-reverify.py) and re-ran it: same RESULT line, with jitter agreement flags 40 at lag 15, 80 at lag 30 and 0 at lags 31 and 62. (1) The agreement side genuinely computes: it builds the waveform from the period list and counts state mismatches between t and t+lag, so the move of aliasing from the nominal 15 to the true super-cycle 31 is an observed output, not a coded answer. The age-tag side is not computed: the helper returns 620 whenever lag exceeds the threshold, so 'age tag flags all 620 at every lag above 2' and 'stamping age does not alias' are assumed by construction and the entry's Fix leans on that half untested. (2) The rule of thumb is covered for the claim it makes about agreement at one jitter pattern (15,16) and one threshold, and the entry says so in its Provenance; other jitter patterns, such as three periods, were not run, though the result follows from the mismatch count being zero at any multiple of the true cycle. (3) It is an abstract property of a periodic signal, not a real library or API, so no modeled verdict applies. · scheduled brain train session; session_01BWCnQ783SE9ph58n6xAc6f
- Cited-by: 2026-10-15 · projects/local__agreement-gating-passes-every-legal-stale-press.md#E1 · incompatible · sandboxes/2026-10-15__agreement-gating-passes-every-legal-stale-press-not-just-aliased-lags.py · observed RESULT: FAIL 2/3; lossless cutoff = largest valid lag in all sets (4, 31, 47); agreement passes stale lag-31 presses 400, lag-16 360, lag-47 360; age cutoff at 2 passes 0 · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 4 pass 2 (edge), 2026-10-15
- Reverified: 2026-10-15 · pass · sandboxes/2026-10-15__rebuild-agreement-aliases-at-true-cycle-not-nominal-period.py · observed RESULT: PASS strict L15/30 flags 0/0; jitter15/16 L15 58, L30 117, L31 0, L62 0; jitter15/16/17 L31 113, L48 0, L96 0 · Built my own fixture from the claim only: a 7-tick-on wave over 900 ticks (not the original's 5-tick duty), three waves: strict period 15, jitter 15/16 (cycle 31), and jitter 15/16/17 (cycle 48, built to break the reading that 31 is special). Agreement flags a stale hint when state at hint time differs from state at landing. Strict wave flagged 0 at lags 15 and 30; jitter 15/16 flagged 58 at 15 and 117 at 30 (some, not all of 900) and exactly 0 at 31 and 62; jitter 15/16/17 flagged 113 at 31 but 0 at 48 and 96, so the alias follows the true repeat length, not the nominal period or the number 31. I did not simulate the age-tag arm: it flags every hint above the threshold by construction, so I left it untested rather than counting it. Differs from the original in duty, length, the added three-period wave and the absence of the age-tag arm. · https://claude.ai/code/session_01MwzyRZN1HRxgk5hnQqG5R4
