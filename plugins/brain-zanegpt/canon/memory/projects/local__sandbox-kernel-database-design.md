# local/sandbox-kernel-database-design — lessons

Project: local/sandbox-kernel-database-design. Newest first.

---

## E2 — composite index cuts write tax a third and strands trailing column reads
- Date: 2026-10-12
- Project: local/sandbox-kernel-database-design
- Tags: [database][performance][indexing][measurement]
- What: Tested whether merging two single-column indexes (a), (b) into one composite (a,b) halves the index
  write tax, as reading sandbox-kernel-database-design/E1 (tax grows per index) suggests. It does not:
  the composite cut the per-INSERT tax only 36% (11 to 7 VM ops), and it stranded b-only reads at a full scan.
- Why built: Brain train loop round 2 re-verified the single-source write-cost kernel from a new angle.
  E1 counted cost against index COUNT; nothing had tested index SHAPE, where consolidation is the usual
  advice for cutting write cost.
- Design: SQLite 3.45.1 in memory, 2000 seeded rows, columns a, b and a pad. Three index sets (none,
  singles (a)+(b), composite (a,b)), each in three fixtures: 1000 distinct a with and without ANALYZE,
  and 4 distinct a with ANALYZE. Counted VM instructions per statement over 100 inserts, 20 a=? selects
  and 20 b=? selects, and recorded EXPLAIN QUERY PLAN for b=?.
- Got right: The read side of the composite-index kernel held exactly: a=? cost 21.1 ops on both shapes,
  and b=? on (a,b) was a SCAN USING COVERING INDEX at 6311 ops, identical to no index at all, with or
  without ANALYZE. The low-cardinality breaker held too: with 4 distinct a and ANALYZE, SQLite chose
  skip-scan (ANY(a) AND b=?) and b=? fell to 48.7 ops, 0.8% of a full scan.
- Where/why it failed: My prediction of at least a 40% cut in write tax was wrong. Inserts cost 15 ops
  with no index, 26 with two singles and 22 with the composite: the composite costs 7, well over half of
  the 11 two singles cost, because a wider key has more to encode and compare. Index count is not the unit.
- Fix: Weigh consolidation by measured write cost per index shape, not by the number of indexes removed.
  Merging (a),(b) into (a,b) saves about a third of the index write tax and costs every b-only query a
  full scan, unless a has very few distinct values and ANALYZE has run so skip-scan applies.
- Why this fix: An index entry's maintenance cost scales with its key width as well as with the number
  of indexes, so dropping one index while widening another recovers less than the count suggests; and
  the trailing column of a composite only bounds a scan when the planner can enumerate leading values.
- Rule of thumb: Replacing indexes (a) and (b) with composite (a,b) cut SQLite's per-insert index tax
  only 36% (11 to 7 VM ops), not half, and b=? fell back to a 6311-op full scan unless a had few
  distinct values and ANALYZE enabled skip-scan (48.7 ops); keep (b) if b-only reads matter.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry, deterministic VM
  instruction counts and query plans from real SQLite 3.45.1. VM instructions stand in for time, and the
  skip-scan threshold is SQLite-specific; PostgreSQL 18 skip scan was outside this run.
- Composed: ideas:DATABASE-DESIGN/indexing/write-cost, sandbox-kernel-database-design/E1, ideas:SYSTEM/database/a-composite-index-is-sorted-by-its-leading-column-so-column-order-is-the-design-decision
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__composite-index-cuts-write-tax-a-third-and-strands-trailing-column-reads.py
- Prediction: Written before the run: the composite cuts the per-INSERT index tax by at least 40% versus
  two singles, keeps a=? within 2x, makes b=? cost at least 50% of a full scan at 1000 distinct a, and
  under 10% of a full scan at 4 distinct a after ANALYZE.
- Observed: RESULT: FAIL tax cut S1 36% S3 36%; b=? on (a,b) costs 100%/100% of full scan at 1000
  distinct a, 0.8% at 4 distinct a after ANALYZE (skip-scan). Inserts none/singles/composite 15/26/22
  ops; a=? 21.1 on both shapes; b=? singles 17.7, composite 6311.4 (S1, S2) and 48.7 (S3).
- Scenarios: 1) 1000 distinct a, no ANALYZE; 2) 1000 distinct a, ANALYZE; 3) BREAKER: 4 distinct a,
  ANALYZE, built so skip-scan rescues trailing-column reads and breaks the stranded-read half of the claim.
- Link: session; brain train loop round 2; session_01QGT1LfmPHPG99JEGaPhBwB

## E1 — indexes tax inserts and deletes but not updates of other columns
- Date: 2026-09-28
- Project: local/sandbox-kernel-database-design
- Tags: [database][performance][indexing][measurement]
- What: Applied the ideas kernel that every index is kept in sync on every write, so unused indexes tax every INSERT, UPDATE and DELETE. In a real SQLite engine the tax scaled with index count for inserts and deletes, but an UPDATE paid only for indexes on the columns it changed.
- Why built: brain train gap listed the kernel as unapplied, and memory had no indexing entry. The kernel quotes PostgreSQL's documentation; this measures a real engine instead.
- Design: SQLite 3.45.1 in memory, a table of 10 integer columns and a text note, with 0, 1, 3 or 10 single-column indexes. 1000 seeded rows, then counted VM instructions per statement with a progress handler that fires on every opcode: 200 inserts, 200 updates of the unindexed note, 200 updates of indexed column c0, 100 deletes, and 100 equality selects on c0.
- Got right: Splitting UPDATE by which column changes. Measured on inserts alone, the cost looks proportional to index count for every write.
- Where/why it failed: An INSERT took 20 VM instructions with no indexes, 26 with 1, 36 with 3 and 71 with 10; a DELETE took 10, 14, 20 and 41. An UPDATE of the unindexed note took 26 at every index count, and an UPDATE of c0 took 28 without indexes and 37 with 1, 3 or 10, paying only for the index on c0. The equality select on c0 fell from 3307 instructions to 9 once c0 was indexed.
- Fix: Count index cost against the write mix: every index taxes inserts and deletes, but an update only pays for indexes covering the columns it changes. Drop indexes no query uses, and weigh the rest against insert and delete volume.
- Why this fix: An insert or delete must add or remove an entry in every index; an update that leaves an index's columns unchanged has nothing to change there. PostgreSQL's HOT updates, which the kernel mentions, are the same idea under different rules.
- Rule of thumb: In SQLite each index added cost to every INSERT (20 to 71 VM instructions from 0 to 10 indexes) and DELETE (10 to 41), but an UPDATE paid only for indexes on the columns it changed (26 at any count for an unindexed column; 37 with 1 or 10 indexes when the changed column had one), while the indexed select dropped from 3307 to 9.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b09.py loop 41 in Pappydapimp69/Brain against real SQLite 3.45.1, deterministic VM instruction counts. Observed: INSERT 20/26/36/71, DELETE 10/14/20/41, UPDATE note 26 throughout, UPDATE c0 28/37/37/37, SELECT 3307/9/9/9. PostgreSQL was not run; VM instructions stand in for time.
- Composed: ideas:DATABASE-DESIGN/indexing/write-cost/indexes-speed-reads-and-tax-every-write
- Link: session 2026-09-28, brain train gap batch 9 loop 41
- Sandbox: sandboxes/2026-09-28__train-gap-b09.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-12 · projects/local__sandbox-kernel-database-design.md#E2 · incompatible · sandboxes/2026-10-12__composite-index-cuts-write-tax-a-third-and-strands-trailing-column-reads.py · observed RESULT: FAIL tax cut S1 36% S3 36%; b=? on (a,b) costs 100%/100% of full scan at 1000 distinct a, 0.8% at 4 distinct a after ANALYZE (skip-scan). Inserts none/singles/composite 15/26/22 ops; a=? 21.1 on both shapes; b=? singles 17.7, compo… · session; brain train loop round 2; session_01QGT1LfmPHPG99JEGaPhBwB
