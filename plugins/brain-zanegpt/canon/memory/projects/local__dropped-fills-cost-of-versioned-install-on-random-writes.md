# local/dropped-fills-cost-of-versioned-install-on-random-writes — lessons

Project: local/dropped-fills-cost-of-versioned-install-on-random-writes. Newest first.

---

## E1 — dropped fills cost of versioned install on random writes
- Date: 2026-10-19
- Project: local/dropped-fills-cost-of-versioned-install-on-random-writes
- Tags: [caching][invalidation][simulation][tradeoff]
- What: A 5-slot LRU cache simulated over 3000 accesses with randomly spaced writes, fill latency D of 3, 8 or 16, mean write gaps of 2, 4 and 20 (uniform 1 to 2x gap), a loop or skewed access order, and an install cost G of 0 or 30 per installed fill; naive install compared with versioned install that drops a fill older than the latest invalidation, 20 seeds per cell, 36 cells.
- Why built: The earlier writes lesson says versioned install costs within 2 percent of naive and has zero stale reads, but its ZaneGPT check noted dropped fills were never costed and the writes were evenly spaced on a pure loop. The size-sweep lesson says to judge by cost, and the GC kernel says allocation work is a real cost, so I added both.
- Design: Hit costs 1, miss 100, plus G per installed fill. A write bumps one random item's version and evicts it. A miss issues one fill per key that reads the current version and installs D accesses later. Naive install always installs; versioned install drops the fill if the version moved. Stale means a hit on a version below the current one.
- Got right: Versioned install gave 0 stale reads in all 36 cells while naive install served stale reads in all 36, so the correctness half of the earlier lesson held on random writes and skewed access too.
- Where/why it failed: The cost half did not hold. I expected versioned install to cost within 5 percent of naive in nearly every cell (at most 6 of 36 dearer by more than 2 percent), but it was dearer by more than 2 percent in 32 of 36 cells and cheaper in none, worst 1.350x (261514 against 193689 at skew, D 16, gap 2, G 0) with about 423 dropped fills per run. Naive looks cheap only because it counts stale hits as hits.
- Fix: Keep versioned install for correctness but state its price: when D exceeds the write gap the dropped fills turn into repeat misses, so budget the extra misses, or shorten the fill latency or coalesce fills per key, instead of quoting the 2 percent figure from evenly spaced writes.
- Why this fix: The extra cost is the refetch of every item whose fill was overtaken by a write, which scales with D over the write gap; only reducing D or the write rate shrinks it, while the version check itself stays cheap.
- Rule of thumb: Versioned install removed all stale reads (0 of 36 cells against 36 for naive) but cost more than 2 percent extra in 32 of 36 cells, up to 1.35x when fill latency was 8x the write gap, so the within-2-percent claim only holds for slow evenly spaced writes and the price of dropped fills must be measured, not assumed.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox, which printed FAIL against my prediction with deterministic output; the model has one cache, one fill in flight per key, no real network, and the costs 1, 100 and 30 are assumed constants.
- Composed: sandbox-cache-size-sweep-loop-cliff-and-ram-ceiling/E1, loop-sized-cache-with-writes-stays-size-5-but-late-fills-serve-stale-until-fills-are-versioned/E1, ideas:PERFORMANCE/memory/garbage-collection
- Picked-by: new-half
- ZaneGPT verdict: weak — the 0 stale versus 36 stale result is solid, but the cost claim is a single-policy, single-grid count that the prediction (at most 6 dearer cells) already failed (32 observed), so the rule is better read as "versioned install is unsafe to assume cheap" than as a general threshold.
- Hidden assumption: Dropped fills cost only the miss they already paid, so the extra cost scales with the ratio of fill latency to write gap, and the 2% bar was fixed after seeing one benign cell (loop, D 3, gap 20, G 0) and not derived from the mechanism; the rule also assumes 5 slots, 3000 accesses and uniform 1-2x gap spacing carry over to other cache sizes and bursty writes.
- Would prove it wrong: A cell with D at or below the minimum write gap (e.g. D 3, gap 20) where versioned costs more than 2% above naive, or any cell with D at least 8x the gap where it costs under 2% more. Either breaks the "only slow evenly spaced writes" boundary. A wider grid (more slots, bursty or Poisson writes) showing the 32/36 count moving sharply would also show the count belongs to this grid and not to the mechanism.
- Break scenario: D 16 with gap 2 and G 0 under skewed access, then re-run with a retry-on-drop policy: if each dropped fill is reissued, versioned install may beat naive on cost. That would show "dearer" comes from the drop-and-forget policy, not from versioning itself, and the rule's "price of dropped fills" claim would need re-scoping.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-19 · digest 32af76bde45c
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-19__dropped-fills-cost-of-versioned-install-on-random-writes.py
- Prediction: Versioned install stays at 0 stale reads and is dearer than naive by more than 2 percent in at most 6 of 36 cells (worst ratio under 1.10).
- Observed: RESULT: FAIL versioned stale in 0/36 cells vs naive 36; versioned cheaper in 0, dearer by >2% in 32; worst cost ratio 1.350
- Scenarios: 1) loop access, D 3, gap 20, G 0 (the case the earlier lesson measured); 2) skewed access with D 8 and gap 4; 3) BREAK: D 16 with gap 2 so several writes overtake each fill; 4) G 30 install cost on every cell
- Link: scheduled brain train auto, loop 1 pass 1; session_01Q5Z2SdcUKr5yLCVU7Ma7tK

