# local/sandbox-combined-wrong-sky-waiting-city-centralizing-does-not-cross-repos — lessons

Project: local/sandbox-combined-wrong-sky-waiting-city-centralizing-does-not-cross-repos. Newest first.

---

## E1 — sandbox combined wrong sky waiting city centralizing does not cross repos
- Date: 2026-08-29
- Project: local/sandbox-combined-wrong-sky-waiting-city-centralizing-does-not-cross-repos
- Tags: [process][architecture][saga][method]
- What: A deterministic sandbox (fixed repo/path topology, no RNG) counting residual buggy code paths across three sibling repos under four remediation strategies — no fix, patching instances in one repo, centralizing within one repo, and centralizing across every sibling.
- Why built: wrong-sky#E14 records that a UI-hint source-of-truth fix in one code path did not prevent the identical bug class reappearing in a NEW path in the sequel that copied the architecture, and concludes that two instances of an untestable-by-unit-test bug class is the signal to CENTRALIZE. waiting-city#E8 records that a gap catalogued in one project can silently exist un-fixed in every sibling that copied the boilerplate. This tests whether E14's prescribed remedy actually addresses the evidence E14 itself cites.
- Design: Three repos each carrying existing buggy paths plus two new paths added after the fix, scored under each strategy by residual buggy path count per repo and in total.
- Got right: Scoring future paths separately from existing ones, which is what makes centralizing measurably better than patching instances rather than merely equivalent.
- Where/why it failed: Centralizing within one repo cuts the total from 12 to 8 and is strictly better than patching instances (10), because it also covers that repo's future paths. But 8 of 12 buggy paths remain, all in sibling repos. wrong-sky#E14's own cited evidence is that the bug reappeared in the SEQUEL — a different repo — which is waiting-city#E8's cross-repo axis, not the within-repo axis centralization operates on. The prescribed remedy cannot reach the instance that motivated it.
- Fix: Count instances per-repo and cross-repo separately before choosing a remedy — a second instance within one repo argues for centralization, a second instance in a sibling repo argues for propagation, and the two remedies are not substitutes. Where both apply, centralize and then propagate the centralization itself.
- Why this fix: "Two instances means centralize" collapses a two-dimensional signal into one. The sandbox shows centralization strictly dominating instance-patching on the within-repo axis while leaving the cross-repo axis untouched, so a team following E14's rule after observing a sequel recurrence will do real work, see the count drop, and still leave the majority of instances live in siblings.
- Rule of thumb: wrong-sky#E14's "two instances means centralize" measures the wrong axis when the second instance is in a sibling repo (waiting-city#E8) — sandbox-confirmed centralizing in one repo cuts 12 residual buggy paths to 8 while leaving every sibling untouched; count within-repo and cross-repo instances separately, since centralization and propagation are not substitutes.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b5/l16.py) and confirmed totals of 12 (no fix), 10 (patch instances in one repo), 8 (centralize in one repo) and 0 (centralize everywhere), with all 8 residual paths sitting in sibling repos. the-game-wrong-sky#E14 and the-game-the-waiting-city#E8 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__the-game-wrong-sky/E14, pappydapimp69__the-game-the-waiting-city/E8
- Link: session_014mRpopK9xnhvk35tT8ozkX

