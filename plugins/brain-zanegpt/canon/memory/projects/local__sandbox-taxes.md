# local/sandbox-taxes — lessons

Project: local/sandbox-taxes. Newest first.

---

## E1 — marginal bracket raise never cuts takehome only cliffs do
- Date: 2026-10-09
- Project: local/sandbox-taxes
- Tags: [taxes][verification][method]
- What: A deterministic check of the progressive-bracket rule using the published 2025 US federal single-filer table (embedded in the sandbox from irs.gov): over taxable income 0 to 700,000 in one-dollar steps, take-home never falls, and the smallest one-dollar gain is 0.63 at the 37% top rate. Educational arithmetic only, not tax, legal or financial advice.
- Why built: Seeding a new TAXES domain with a claim that people routinely get wrong ("a raise can push me into a bracket where I take home less") and that a short test can settle both ways.
- Design: Exact fractions for the layered tax (each rate applied only to its own slice), a naive whole-income-at-one-rate model as the misreading, and a hypothetical cliff rule (a 2,000 benefit lost entirely above 60,000) as the case built to break the claim. No standard deduction, no state or payroll tax, no credits; the cliff is invented for the test and is not any real program.
- Got right: The layered model had 0 take-home decreases over 700,001 points; one dollar across the 12% to 22% edge (48,475 to 48,476) raised take-home by 0.78. Tax on 100,000 came out to exactly 16,914 (hand sum 1,192.5 + 4,386 + 11,335.5), an average of 16.914% against a 22% marginal rate.
- Where/why it failed: The naive model (whole income at the rate it reaches) produced exactly 6 decreases, one per threshold, which is the shape of the myth. The cliff model produced 1 decrease: a 1,000 raise from 60,000 to 61,000 changed take-home by -1,220. A compounding cross-check also missed a published figure by about 0.5% (398,298 and 184,816 against a stated 400,290 and 185,740), so the source's convention differs slightly from end-of-month deposits.
- Fix: Model tax as layers and test monotonicity at every threshold. Look for loss risk in rules that remove something all at once at a threshold (a hard eligibility line, a benefit that disappears) not in the bracket rates themselves. Treat the raw table as the input and check for a hard line in each rule that sits on top of it.
- Why this fix: The bracket rule by construction taxes only the slice above each threshold, so the loss from a raise needs a marginal effective rate over 100%, which only a discontinuity can supply. Testing every dollar of the range (not a few sample points) is what pins the 6 and 1 counts to the threshold edges.
- Rule of thumb: In a layered bracket system a raise cannot lower take-home on the brackets alone (tested on one table, 3 model variants plus an average-vs-marginal check); when someone reports a loss, look for a cliff in a benefit or eligibility line, and compare average against marginal rate before judging a pay decision.
- Provenance (verified/assumed): Verified first-hand in the sandbox (arithmetic above) and verified first-hand from the irs.gov page fetched this run (bracket table and the sentence that the higher rate applies only to the part in the new bracket). The cliff is hypothetical by design. Other years, filing statuses, and state rules were not run.
- Composed: ideas:TAXES/brackets/marginal-rate-is-not-the-whole-income-rate, ideas:PERSONAL-FINANCE/retirement/401k-match, ideas:PERSONAL-FINANCE/investing/compound-interest, ideas:PERSONAL-FINANCE/debt/payoff-vs-investing
- Polarity: compatible
- Sandbox: sandboxes/2026-10-09__marginal-bracket-raise-never-cuts-takehome-only-cliffs-do.py
- Prediction: Layered: 0 decreases, minimum gain 0.63; naive: exactly 6 decreases; cliff: exactly 1 decrease; tax on 100,000 = 16,914; 401k out-of-pocket 3,744 for 7,200 in the account.
- Observed: RESULT: PASS layered=0 decreases, naive=6, cliff=1, tax(100k)=16914, 401k oop=3744 (also: 401k at 80,000 salary, 6% pre-tax with a 50% match, saved 1,056 tax; avoided 22.15% card interest vs 8.17% taxed market return).
- Scenarios: 1) layered brackets over 0..700,000; 2) naive whole-income rate (built to reproduce the myth); 3) hypothetical benefit cliff (built to BREAK the rule); 4) average vs marginal rate over the range; 5) 401k pre-tax contribution at 80,000 with match; 6) compounding and payoff-vs-invest cross-checks.
- Link: session_01YFLLRpDsfZpRstb2KT2MQy
- Audited: 2026-10-12 · pass · Read the entry and its stored sandbox and re-ran it (it ends in a PASS line). The layered tax is computed with exact fractions from the embedded table, not hard-coded; the 0 decreases, 0.63 minimum gain, 6 naive decreases and 1 cliff decrease are counts over every dollar of 0..700,000. The Rule of thumb is scoped to brackets alone on one table and says to look for a cliff, which is what was tested. Caveat: monotonicity follows almost by construction since every marginal rate is below 100%, so the real information is the naive and cliff contrast; the table is the real published rule, so this is not only a hand-written model. · brain train auto audit session 2026-10-12; session_01QoYzipjYSp8DTBoAoj5Bdh
