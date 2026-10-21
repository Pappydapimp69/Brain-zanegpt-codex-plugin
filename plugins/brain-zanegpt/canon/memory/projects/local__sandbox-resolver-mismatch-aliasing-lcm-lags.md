# local/sandbox-resolver-mismatch-aliasing-lcm-lags — lessons

Project: local/sandbox-resolver-mismatch-aliasing-lcm-lags. Newest first.

---

## E1 — resolver mismatch aliasing lcm lags
- Date: 2026-09-30
- Project: local/sandbox-resolver-mismatch-aliasing-lcm-lags
- Tags: [ui][input][state][gamedev][testing]
- What: Re-verified that hint-versus-state mismatch aliases at cycle multiples while an age tag does not, using a resolved-action output from two roles with different periods instead of a single raw state wave.
- Why built: The aliasing lesson and the combined action resolver age-tag lesson were single-source together, and both looked at one period at a time; two coprime-ish role periods make the true repeat the least common multiple.
- Design: Deterministic 600 ticks, no RNG. Role B is available 5 of every 15 ticks, role C 4 of every 20 ticks at offset 3, C outranks B outranks A. Hint is the resolved action at t, compared to the action at t plus lag L; lags 2,15,20,30,40,45,60,120. Age tag flags hints when L exceeds 2.
- Got right: Mismatch was 240 at L=2,15,30,45, 320 at L=20 and 40, and 0 at L=60 and 120; the age tag flagged 600 of 600 at every lag above 2 and 0 at L=2.
- Where/why it failed: Agreement looked healthy at the individual role periods only in the sense that it stayed nonzero; the blind lags are the least common multiple 60 and its multiples, not 15 or 20, so a guard reasoning per role would place the blind spot wrongly.
- Fix: Stamp hints with emit time and gate on age, or compute blind lags from the least common multiple of all contributing periods.
- Why this fix: An emit-time stamp has no dependence on the waveform, whereas agreement is blind exactly where the combined output repeats.
- Rule of thumb: With several periodic inputs, mismatch-based staleness aliases at the least common multiple of their periods (0 of 600 flagged at L=60 and 120 here), so use an age tag; per-role periods do not locate the blind lag.
- Provenance (verified/assumed): Verified first-hand by running the sandbox and copying its counts; one priority resolver with periods 15 and 20 and one offset, other period pairs not run.
- Composed: local__age-cutoff-roll-up/E1, sandbox-combined-action-resolver-age-tag-staleness/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__resolver-mismatch-aliasing-lcm-lags.py
- Prediction: mismatch flags 0 of 600 at L=60 and 120 and above 0 at L=15,20,30,40,45, while the age tag flags 600 at all of them and 0 at L=2.
- Observed: RESULT: PASS resolved-action mismatch aliases to 0 at lcm multiples 60,120 (>0 at 15..45); age tag flags all 600
- Scenarios: 1) L=2 within threshold 2) L=15 and 20 single-role periods built to break a per-role blind-lag claim 3) L=30,40,45 partial multiples 4) L=60 and 120 least common multiple
- Link: scheduled train pass 3
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-lcm-blind-lags-three-roles.py · observed RESULT: PASS mismatch zero iff L%210==0 over L=1..450 (>0 at 6,10,14,30,42,70,105); age tag flags 840/840 for L>3; masked role shrinks blind lag to contributing lcm (4). Key counts: L=30 192, L=42 280, L=70 560, L=210 0, L=420 0. · I worked only from the What, Rule of thumb and Prediction. My own sandbox uses three roles (periods 6, 10, 14, lcm 210) with phase-encoded actions, a priority resolver, N=840 and age threshold 3. It sweeps every lag from 1 to 450, not only hand-picked ones. Mismatch was 0 if and only if L was a multiple of 210, and above 0 at each single-role period (6, 10, 14), at the pairwise lcms 30, 42 and 70, and at 105. The age tag flagged 840 of 840 at every L>3. The claim holds. I added a scoping control: when one role is always outranked, the blind lag shrinks to the lcm of the CONTRIBUTING roles (period 4, not lcm(4,9)=36). That matches the entry's Fix wording ("contributing periods") more closely than its Rule of thumb ("their periods"). After my run I opened the original sandbox for comparison. It uses two roles (15 and 20, one offset) with 3-symbol actions, N=600, threshold 2, and checks 8 chosen lags. Mine uses 3 roles, 3 pairwise lcms, an exhaustive lag sweep, phase-tagged action labels and a masked-role case. So the iff holds over the whole range, not just at sampled points. · session; brain train rebuild pass; session_01QGT1LfmPHPG99JEGaPhBwB
