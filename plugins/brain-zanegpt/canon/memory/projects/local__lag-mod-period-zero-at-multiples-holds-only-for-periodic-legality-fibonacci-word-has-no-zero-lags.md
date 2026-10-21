# local/lag-mod-period-zero-at-multiples-holds-only-for-periodic-legality-fibonacci-word-has-no-zero-lags — lessons

Project: local/lag-mod-period-zero-at-multiples-holds-only-for-periodic-legality-fibonacci-word-has-no-zero-lags. Newest first.

---

## E1 — lag mod period zero at multiples holds only for periodic legality fibonacci word has no zero lags
- Date: 2026-10-19
- Project: local/lag-mod-period-zero-at-multiples-holds-only-for-periodic-legality-fibonacci-word-has-no-zero-lags
- Tags: [simulation][method][gate][testing]
- What: A deterministic model comparing gate-only invalid press counts at lags that are multiples of the period on period-12 width-5 legality against a Fibonacci-word legality signal, to test whether the lag-mod-period rule extends to aperiodic legality.
- Why built: One lesson says the gate invalid count depends on the lag only through L mod P so multiples of P give zero, another says on a Fibonacci word the count follows lag times phi near an integer; I predicted the zero-at-multiples result would not carry over and that the Fibonacci dips would still stay above zero.
- Design: N=600 ticks; invalid(L) counts t legal at t and illegal at t plus L. Periodic signal t mod 12 under 5 at lags 12,24,36,48,60,120; Fibonacci word by substitution at lags 8,13,21,34,55,89, with the median over lags 40 to 70 as the baseline; a nominal-period formula with P=13 and W taken from the first 13 symbols is scored against brute force on lags 1 to 120.
- Got right: All six multiples of 12 gave 0 invalid presses on the periodic signal, and the Fibonacci lags dipped far below the window median of 158 (55 gave 4 and 89 gave 3) in the order the rotation-proximity result predicts.
- Where/why it failed: The zero property did not carry over: no Fibonacci lag gave 0 (counts 33, 21, 12, 8, 4, 3), and the nominal-period formula with P=13 was off by more than 10 percent on 103 of 120 lags, so the mod-P reduction has no meaning for the aperiodic word.
- Fix: Use the lag-mod-period reduction only after confirming the legality signal is exactly periodic; for an aperiodic signal scan every lag by brute force and treat low counts at near-resonant lags as dips, not as zeros.
- Why this fix: The reduction is an identity that needs exact periodicity, and a brute-force scan is cheap at 120 lags, so checking periodicity first costs less than trusting a nominal period.
- Rule of thumb: A lossless cutoff past the period can admit zero invalid presses only at exact multiples of an exact period; on a Fibonacci-word signal the lowest counts were 4 and 3 at lags 55 and 89, never 0, so check periodicity before applying lag mod P and scan lags otherwise.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox, PASS with deterministic output on one aperiodic signal; random and other aperiodic signals were not run here.
- Composed: fibonacci-gate-drop-is-rotation-proximity-not-fibonacci-lags/E1, lossless-cutoff-is-worst-without-validity/E1, gate-invalid-formula-needs-lag-mod-period-for-lags-above-period/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — The PASS shows only that periodic gives 0 and Fibonacci gave nonzero at six lags, with the lowest counts shrinking toward 3 as lags grow. "Never 0" is untested beyond lag 89, so the rule is under-tested and may be a finite-window artifact. Next move: sweep every lag 1–300 across several widths and phases, normalise by 600 − L, and confirm whether any zero appears.
- Hidden assumption: Counts at 6 hand-picked Fibonacci lags on one 600-tick word stand in for "aperiodic legality" in general. The rule is also assumed to fail because the signal is aperiodic. A Sturmian word's near-periods, and the finite-N edge, could just as well explain the nonzero counts.
- Would prove it wrong: A zero at some lag on an aperiodic signal, e.g. a Fibonacci word with a different width or phase, or a lag past 89 such as 144 or 233 where the invalid count drops to 0 within N=600. A nonzero count at a multiple of the period on a truly periodic signal with a different period or width would also refute it. Either result would show that lag mod P, not exact periodicity, is not what separates the two cases.
- Break scenario: Keep the Fibonacci word and test lags 144, 233 and 377, plus other widths and the other phase. Near-periods are strongest at Fibonacci lags, and the lags are checked within a 600-tick window, so the effective sample shrinks to 600 − L. At L=377 only 223 ticks are scored, and the invalid count could be 0 from truncation alone. That would count as a zero on an aperiodic signal, which the rule says cannot happen.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-19 · digest 8c6d8195323a
- Sandbox: sandboxes/2026-10-19__lag-mod-period-zero-at-multiples-holds-only-for-periodic-legality-fibonacci-word-has-no-zero-lags.py
- Prediction: All multiples of 12 give 0 on the periodic signal; Fibonacci lags 8,13,21,34,55,89 each give at least 3 and lag 55 is under a fifth of the window median; lag 89 is below lag 13; the nominal P=13 formula is wrong on at least 80 of 120 lags.
- Observed: RESULT: PASS periodic multiples of 12 invalid [0, 0, 0, 0, 0, 0]; Fibonacci-word fib lags {8: 33, 13: 21, 21: 12, 34: 8, 55: 4, 89: 3} (never 0), window median 158; nominal-P13 formula wrong on 103/120 lags
- Scenarios: 1) periodic multiples of 12; 2) BREAK: Fibonacci word at Fibonacci lags; 3) Fibonacci word window median baseline; 4) nominal-period formula over lags 1 to 120
- Link: scheduled brain train auto, loop 1 pass 5; session_01W1FCx5tpnHusaTASoCMosY

