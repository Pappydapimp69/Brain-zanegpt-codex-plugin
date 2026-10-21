# local/sandbox-reverify-batch-compression-knee — lessons

Project: local/sandbox-reverify-batch-compression-knee. Newest first.

---

## E1 — batch compression knee is corpus and codec dependent
- Date: 2026-09-28
- Project: local/sandbox-reverify-batch-compression-knee
- Tags: [compression][performance][architecture][measurement]
- What: Re-verified from a new angle (different corpus + three codecs + explicit wait model) that batching-for-compression-ratio is buffering-for-latency, and found the knee location is NOT a constant: it depends on corpus and codec, so it must be measured per stream.
- Why built: The prior sandbox (sandbox-combined-august-10-batching-for-ratio-is-buffering-for-latency/E1) was single-source and reported a knee at batch 8 on one corpus with zlib; this pass tests whether that structure and knee transfer.
- Design: Deterministic sandbox, no RNG/timing: 1024 JSON telemetry records (~116 B each) generated from the index; ratio for batch B in {1..256} under zlib-9, bz2-9, lzma; buffering wait modeled as mean (B-1)/2, worst B-1 arrival ticks; plus a zlib streaming compressor with Z_SYNC_FLUSH per message (zero buffering wait).
- Got right: The tradeoff structure reproduces on every codec: each batch doubling doubles worst-case wait while the ratio gain per doubling decays (zlib 1.54 -> 1.47 -> 1.41 -> 1.36 -> 1.28 -> 1.18 -> 1.12). Per-message compression expands for bz2 (0.88x) and lzma (0.74x) and barely helps zlib (1.15x), matching august-10/E24's small-message finding.
- Where/why it failed: Copying "knee at batch 8" as a constant would be wrong here: on this corpus zlib still gains 1.47x per doubling at B=8 and only drops below ~1.2x per doubling past B=128 (9.42x@64, 11.08x@128, 12.40x@256). bz2/lzma keep gaining longer (bz2 17.18x@256 vs zlib 12.40x) and overtake zlib from B>=32, so the codec choice moves the knee.
- Fix: Measure ratio-vs-batch per corpus and codec, compute gain-per-doubling, and set B where that gain falls below the latency cost you accept (each doubling = 2x worst-case wait). Before buffering at all, try a streaming compressor with per-message sync-flush: here it gave 6.45x at zero buffering wait, equal to zlib batching at roughly B=16-32 (5.41x@16, 7.38x@32).
- Why this fix: Batching buys ratio only by holding messages (august-10/E22: buffers trade latency, they don't create capacity); a shared streaming dictionary gets the between-record redundancy without holding anything, so it dominates small/medium batches on latency.
- Rule of thumb: Batch size for compression is a latency budget, not a constant — measure the gain-per-doubling knee for your corpus+codec, and prefer a sync-flushed streaming dictionary over any batch whose ratio it matches.
- Provenance (verified/assumed): Verified first-hand — deterministic Python sandbox (stdlib zlib/bz2/lzma, 1024 index-generated records, 119,057 raw bytes) run 2026-09-28; all numbers above observed. Assumed: latency model is arrival-tick buffering only (compression CPU time not modeled); knee values are specific to this corpus.
- Composed: august-10/E22, august-10/E24, sandbox-combined-august-10-batching-for-ratio-is-buffering-for-latency/E1
- Link: scheduled brain train pass, session_01V7YD4FYfs8eKkpz3fWBxkf

