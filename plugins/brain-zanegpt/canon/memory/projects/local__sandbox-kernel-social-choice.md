# local/sandbox-kernel-social-choice — lessons

Project: local/sandbox-kernel-social-choice. Newest first.

---

## E1 — condorcet cycle exact small electorates
- Date: 2026-10-12
- Project: local/sandbox-kernel-social-choice
- Tags: [social-choice][condorcet]
- What: Exact probability that a 3-candidate impartial-culture election has no Condorcet winner, computed
  by a DP over pairwise margin vectors for n = 1..61 voters, checked against Guilbaud's 8.77% limit.
- Why built: The 8.77% Guilbaud figure is quoted as "the" chance of a Condorcet cycle; a voting-rule
  model or a small-committee simulation needs to know whether that number is right at n = 3..61.
- Design: Isolated. Each voter adds one of 6 sign vectors (m_ab, m_bc, m_ac) to the margin state; a
  cumulative dict DP keeps integer counts so every probability is an exact Fraction over 6^n.
  Cycle = (ab>0, bc>0, ac<0) or the reverse; no-CW = no candidate strictly beats both others.
- Got right: For odd n the exact cycle probability is 1/18 = 5.556% at n=3 (matches Wikipedia), then
  6.944, 7.502, 7.798, 7.981% (n=5..11), 8.499% at n=31, 8.635% at n=61: strictly rising, always below
  8.774%, and odd n has no-CW == cycle exactly.
- Where/why it failed: The 8.77% figure is NOT a bound on "no Condorcet winner" for even n: pairwise
  ties leave no strict winner 66.7% of the time at n=2, 55.6% at n=4 and still 29.1% at n=30, while
  true cycles stay below 3.3%. Quoting the limit for a small or even committee is off by 3x or more.
- Fix: Quote the limit only for large odd electorates; for small n use the exact DP value, and for even
  n report cycles and pairwise ties separately (or fix a tie-break rule) before citing a frequency.
- Why this fix: Exact enumeration is cheap (n=61 in ~4 s stdlib) and removes both errors at once: the
  small-n overstatement (8.77 vs 5.56% at n=3) and the even-n tie mass the asymptotic formula ignores.
- Rule of thumb: Guilbaud's 8.77% is an upper limit only for odd electorates (5.56% at n=3, 8.64% at
  n=61); with an even electorate ties make "no Condorcet winner" 29-67% for n<=30, so compute exactly.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry; Wikipedia's Condorcet
  paradox page (n=3 5.556%, n=101 8.690%, limit 8.77%) was fetched and matched. Assumption: impartial
  culture, 3 candidates, strict ballots; real electorates are not uniform.
- Composed: N/A
- Sandbox: sandboxes/2026-10-12__condorcet-cycle-exact-small-electorates.py
- Prediction: odd n: p3 = 1/18 = 5.556%, p5 ~ 6.94%, p7 ~ 7.50%, p9 ~ 7.80%, strictly increasing and
  all below 8.77%, p101 = 8.690%; even n (break): no strict CW > 8.77% for every even n <= 30, n=2 = 2/3.
- Observed: RESULT: PASS odd-n IC cycle prob exact: n=3 1/18=5.556%, n=51 8.607%, n=61 8.635%, strictly
  rising and below Guilbaud 8.774%; even n<=30 noCW 29.1-66.7% (bound fails). An earlier NMAX=101 run
  gave 0.08690 at n=101, matching Wikipedia, but took ~45 s so the shipped script stops at 61.
- Scenarios: 1) n=3 exact 1/18; 2) odd n 1..61 monotone and below the limit; 3) n=61 below Wikipedia's
  n=101 value (and n=101 itself in iteration 2); 4) BREAK: even n 2..30 no-strict-CW vs 8.77%.
- Link: session; brain train newdomain 5 loops; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__brainwork.md#E157 · compatible · sandboxes/2026-10-12__condorcet-exact-dp-vs-brute-force-and-seeded-sfc32-sampling-power.py · observed RESULT: PASS dp==brute n1-7; odd cycles<8.774; even n30 nocw 29.1%; sfc32 20000-sample n=31 z_limit=-1.13 not rejectable. n=3 z_limit=-19.80. · scheduled brain train session; session_01FbNV33qUVqkwoe1aojdkah
