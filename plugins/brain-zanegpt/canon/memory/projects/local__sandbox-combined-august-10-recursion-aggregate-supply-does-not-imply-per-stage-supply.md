# local/sandbox-combined-august-10-recursion-aggregate-supply-does-not-imply-per-stage-supply — lessons

Project: local/sandbox-combined-august-10-recursion-aggregate-supply-does-not-imply-per-stage-supply. Newest first.

---

## E1 — sandbox combined august 10 recursion aggregate supply does not imply per stage supply
- Date: 2026-08-29
- Project: local/sandbox-combined-august-10-recursion-aggregate-supply-does-not-imply-per-stage-supply
- Tags: [gamedesign][testing][process][balance]
- What: A deterministic sandbox (fixed content table, integer arithmetic, no RNG) running august-10#E7's total-demand-versus-total-supply check and recursion#E7's per-stage quota check against the same six-building progression across two resources.
- Why built: august-10#E7 records that content can be unreachable BY ARITHMETIC while presenting as merely slow, and prescribes summing total demand against total supply before tuning and re-summing whenever a new consumer is attached. recursion#E7 records that a sub-progression quota must be derived from the actual per-item tags rather than a generic formula over aggregate counts that assumes even distribution. This tests whether E7's aggregate check is sufficient.
- Design: Six buildings across three stages with a deliberately uneven resource mix — stage 1 needs both resources in small amounts, stage 2 needs only stone, stage 3 only wood — against a supply of 60 stone and 60 wood, which exactly equals total demand on each resource. The per-stage check is run under an even-split quota formula and under recursion#E7's tag-derived quota.
- Got right: Setting total demand exactly equal to total supply on both resources, so the aggregate check passes at its tightest rather than with slack that would make the result look like a tuning margin issue.
- Where/why it failed: The aggregate check passes on both resources — 60 demand against 60 supply each — while stages 2 and 3 are unaffordable under an even-split quota, which allots 20 of each resource per stage against needs of 50 stone and 50 wood respectively. Deriving the quota from the stage's actual tags makes every stage affordable from the identical supply.
- Fix: Treat august-10#E7's aggregate sum as a necessary precondition and add recursion#E7's per-stage, tag-derived affordability check as the sufficient one — and re-run both whenever content is added, since a new item can preserve aggregate balance while breaking its own stage.
- Why this fix: E7's remedy is stated as an arithmetic sufficiency test and reads as conclusive, but it silently assumes the supply is fungible across stages. As soon as content is gated into stages with differing resource mixes, aggregate sufficiency and per-stage sufficiency come apart, and the symptom is identical to the one E7 describes — content that presents as merely slow while being arithmetically unreachable.
- Rule of thumb: august-10#E7's total-demand-vs-total-supply sum is necessary but not sufficient once content is staged with an uneven resource mix — sandbox-confirmed an aggregate PASS at exactly 60/60 on both resources while two of three stages were unaffordable under an even-split quota; add recursion#E7's tag-derived per-stage check.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b9/l24.py) and confirmed aggregate demand equals supply at 60 on each resource with verdict PASS, while stages 2 and 3 fail under an even split (allot 20 against needs of 50 stone and 50 wood) and all three pass under the tag-derived quota. august-10#E7 and the-game-the-recursion#E7 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__august-10/E7, pappydapimp69__the-game-the-recursion/E7
- Link: session_014mRpopK9xnhvk35tT8ozkX

