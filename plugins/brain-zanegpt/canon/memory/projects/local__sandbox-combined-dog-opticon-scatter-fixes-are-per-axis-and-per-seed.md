# local/sandbox-combined-dog-opticon-scatter-fixes-are-per-axis-and-per-seed — lessons

Project: local/sandbox-combined-dog-opticon-scatter-fixes-are-per-axis-and-per-seed. Newest first.

---

## E1 — sandbox combined dog opticon scatter fixes are per axis and per seed
- Date: 2026-08-29
- Project: local/sandbox-combined-dog-opticon-scatter-fixes-are-per-axis-and-per-seed
- Tags: [procgen][algorithm][testing][gamedev]
- What: A deterministic sandbox (40 fixed seeds, LCG scatter, no library RNG) placing procedural points against hand-placed fixed props and a hand-authored sub-zone, under four fix configurations, counting how many seeds produce each class of violation.
- Why built: dog#E17 records that min-distance-rejection scatter only protects against points it is told about, so every fixed prop must be seeded into the rejection set. dog#E18 records that a generic scatter needs an explicit exclusion for every hand-authored sub-zone, since a spawn-only exclusion list will not implicitly cover a themed zone added later. opticon#E16 records that content dependencies must be validated against the finished map because probabilistic placement makes them per-seed facts. This tests whether the two scatter fixes overlap and what the right measurement is.
- Design: Twelve scattered points per seed against two fixed props and one rectangular sub-zone, swept over 40 seeds under four configurations — neither fix, prop-seeding only, zone-exclusion only, and both — counting seeds exhibiting a prop overlap and seeds exhibiting a zone intrusion.
- Got right: Counting FAILING SEEDS rather than inspecting a single generated map, which is what makes the per-seed character of the failure visible rather than reducing it to a pass/fail on one arbitrary sample.
- Where/why it failed: Each fix closes only its own axis and neither touches the other. Seeding fixed props eliminates prop overlaps (24 seeds to 0) but leaves zone intrusions on 18 of 40 seeds. Excluding the zone eliminates intrusions (17 to 0) but leaves prop overlaps on 26 of 40. Only both together reach 0 and 0. Critically, no violation occurs on every seed, so a fixed handful of development seeds can show a clean map while a real player hits one.
- Fix: Apply both exclusions and verify by sweeping many seeds and reporting the count of failing seeds per violation class, rather than by inspecting a generated map or relying on a small fixed seed suite.
- Why this fix: dog#E17 and dog#E18 read as two instances of one idea — tell the rejection set about everything — which invites treating either as covering the class. The sweep shows their effects are disjoint. And because opticon#E16's per-seed character applies to both, the natural verification (look at a map, or check a few seeds) is exactly the one that can pass while a substantial fraction of the seed space is broken.
- Rule of thumb: dog#E17's fixed-prop seeding and dog#E18's sub-zone exclusion close disjoint axes and neither covers the other — sandbox-confirmed prop-seeding alone still intrudes into the zone on 18 of 40 seeds and zone-exclusion alone still overlaps props on 26 of 40; and per opticon#E16 the honest measure is the count of failing seeds, never a single map inspection.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b16/l34.py) over 40 seeds and confirmed violation counts of (24, 17) with neither fix, (0, 18) with prop-seeding only, (26, 0) with zone-exclusion only, and (0, 0) with both. dog#E17, dog#E18 and opticon#E16 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__dog/E17, pappydapimp69__dog/E18, pappydapimp69__opticon/E16
- Link: session_014mRpopK9xnhvk35tT8ozkX

