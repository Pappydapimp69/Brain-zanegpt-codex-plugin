# local/sandbox-kernel-api-design — lessons

Project: local/sandbox-kernel-api-design. Newest first.

---

## E3 — dataloader batching vanishes under sequential awaits
- Date: 2026-09-28
- Project: local/sandbox-kernel-api-design
- Tags: [api][graphql][performance][async]
- What: Applied the ideas kernel that GraphQL's per-field resolvers turn one query into N+1 datastore calls, which a batching layer such as DataLoader must fix. The N+1 reproduced in real Node, and the batching only works when sibling resolvers are started together; awaiting them one by one restores every call.
- Why built: brain train gap listed the kernel as unapplied, and memory had no GraphQL entry.
- Design: A minimal DataLoader in real Node that collects keys until the microtask queue drains and then makes one batch call, optionally capped at 100 keys. A resolver tree: authors, then each author's address and books, then B review lookups per author. Counted datastore calls for 50 authors with 0 and 3 reviews each and 500 authors with 3, resolving siblings with Promise.all or with sequential awaits.
- Got right: Running it on real Promise scheduling rather than a model, since whether keys share a batch depends entirely on microtask timing.
- Where/why it failed: For 50 authors, naive resolvers made 101 calls (1 + 50 addresses + 50 book lists) against 3 batched. With 3 reviews each, 251 against 4; with 500 authors, 2501 against 4. The same DataLoader under sequential awaits made 101, 251 and 2501 calls, exactly the naive count, because each await flushes a batch of one. A 100-key cap turned the 500-author query into 26 calls.
- Fix: Start sibling resolvers together (Promise.all or the GraphQL executor's own parallel field resolution) and never await loader calls in a loop; size the batch cap to the datastore's limit and count calls per query in a test.
- Why this fix: A loader can only batch keys requested before its flush runs; a sequential await forces a flush after each key.
- Rule of thumb: DataLoader turns N+1 resolver calls into one per level (2501 naive vs 4 for 500 authors x 3 reviews) only when siblings are started together: awaiting loader calls in a loop made exactly the naive count (2501), and a 100-key cap made it 26, so resolve siblings concurrently and assert calls per query.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b08.py loop 37 in Pappydapimp69/Brain, running real Node v22.22.2, deterministic. Observed calls: naive 101/251/2501, batched 3/4/4, sequential 101/251/2501, capped 3/5/26. The loader is a minimal reimplementation, not the dataloader npm package.
- Composed: ideas:API-DESIGN/graphql/n-plus-one-resolvers/graphql-fixes-client-round-trips-and-moves-the-same-problem-to-the-server
- Link: session 2026-09-28, brain train gap batch 8 loop 37
- Sandbox: sandboxes/2026-09-28__train-gap-b08.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-08 · projects/pappydapimp69__brain.md#E94 · compatible · sandboxes/2026-10-08__dataloader-cache-scope.py · observed RESULT: PASS per-request (5, 0), shared (1, 200), no-loader (250, 0) (queries,stale); the no-stale-reads half of the prediction was refuted. · brain train pass 3
- Cited-by: 2026-10-10 · projects/pappydapimp69__brainwork.md#E88 · compatible · sandboxes/2026-10-10__n-plus-one-lazy-property-vs-batch-vs-join-latency-thresholds.py · observed RESULT: PASS N=500 naive 501 queries ~1002ms vs batch 2 / join 1; zero-RTT naive still 501 queries; inner join dropped 6; cap100 -> 6 · brain train auto loop 1 pass 5 (gap mode); session_01LphKr4r2NDaVJxz3d1yx7B
- Cited-by: 2026-10-12 · projects/pappydapimp69__brain.md#E143 · compatible · sandboxes/2026-10-12__batched-resolver-with-per-parent-limit-overfetches.py · observed RESULT: PASS 4/4; skewed k3 rows naive/IN/window 1500/13852/1500 (x9.2); uniform k3 x1.33; aliases 3 queries · session; brain train pass 2 (aim: n-plus-one-resolvers single-source edge); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E2 — webhook dedupe must be atomic with the effect and version checked
- Date: 2026-09-28
- Project: local/sandbox-kernel-api-design
- Tags: [api][webhooks][correctness][security]
- What: Applied the ideas kernel that webhook delivery is at least once, so handlers must log processed event ids and verify signatures. Duplicates reproduced, and an event-id log alone left four gaps: where the id is written relative to the effect, concurrent retries, out-of-order delivery, and replayed signed events.
- Why built: brain train gap listed the kernel as unapplied. garden/E3 recorded a check-then-insert race on a quota; the same shape sits inside a naive dedupe log.
- Design: 50 runs of 200 events with 10% ack loss causing retries and a 2% handler crash that also causes a retry. Handlers: no dedupe, id recorded after the effect, id recorded before the effect, and effect plus id committed together. Then every interleaving of two concurrent deliveries of one event, check-then-record against atomic insert-if-absent. Then 200 subscriptions whose status events (active, past_due, canceled) arrive with late retries and a shuffled tail. Then 200 validly signed events replayed 10 minutes to a day later, with and without a 5-minute timestamp window.
- Got right: Making a crash trigger a retry. Without retries after a crash, every variant appears to lose events and the atomic handler looks no better than the others.
- Where/why it failed: Without dedupe, 1129 effects were duplicated. Recording the id after the effect still duplicated 165 (crash between effect and record); recording it before lost 158 events (crash between record and effect); committing both together gave 0 and 0. Two concurrent deliveries under check-then-record double-applied in 18 of 20 interleavings, against 0 of 6 for insert-if-absent. With dedupe, the final subscription status was wrong in 63 of 200 because an older event arrived after a newer one; an event-version check made it 0. A signature check alone accepted all 200 replays; a 5-minute timestamp window accepted 0.
- Fix: Commit the effect and the processed event id in one transaction, or make the effect itself keyed on the event id; claim ids with an atomic insert-if-absent; apply state changes only if the event is newer than the stored version; and verify the signature over the timestamp with a short tolerance window.
- Why this fix: An id log fixes duplicates only if nothing can happen between the effect and the record, and says nothing about order or replay; each gap needs its own guard.
- Rule of thumb: A webhook id log stops duplicates only if the id is committed atomically with the effect (after: 165 duplicates, before: 158 lost, atomic: 0 and 0) and claimed with insert-if-absent (check-then-record double-applied 18/20 interleavings); it does not fix out-of-order status (63/200 wrong without a version check) or replays of signed events (200/200 accepted without a timestamp window).
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b07.py loop 34 in Pappydapimp69/Brain, deterministic seeded deliveries and exhaustive interleavings. Observed: 1129/165/0/0 duplicated and 0/0/158/0 lost; 18/20 vs 0/6; 63 vs 0 wrong status; 200 vs 0 replays accepted. Stripe's actual retry schedule was not modelled.
- Composed: ideas:API-DESIGN/webhooks/delivery-guarantees/webhook-delivery-is-at-least-once-so-handlers-must-be-idempotent-and-verified, garden/E3
- Link: session 2026-09-28, brain train gap batch 7 loop 34
- Sandbox: sandboxes/2026-09-28__train-gap-b07.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

## E1 — a cursor must be a unique key or it skips or repeats ties
- Date: 2026-09-28
- Project: local/sandbox-kernel-api-design
- Tags: [api][data][correctness][performance]
- What: Applied the ideas kernel that offset pagination scans more rows with depth and duplicates rows under inserts, while cursor (keyset) pagination does neither. Both held exactly, and the cursor's advantage depends on the cursor key being unique.
- Why built: brain train gap listed the kernel as unapplied, and memory had no pagination entry. The kernel rests on a database reference and was never modelled.
- Design: A 20000-row feed ordered newest first, paged 25 rows at a time for 60 pages. Offset pages skip page*25 rows; cursor pages continue after the last row seen. Runs with 0 and 3 inserts at the top between page fetches. Then rows written in bursts of 10 sharing a timestamp, paged by a timestamp-only cursor using < and using <=, and by a (timestamp, id) cursor.
- Got right: Adding the non-unique key case. With unique ids the cursor wins on every measure and the kernel reads as unconditional.
- Where/why it failed: Offset scanned 45750 rows over 60 pages against 1500 for the cursor, 1500 for the last page alone against 25. With 3 inserts per page, offset returned 177 duplicates (3 per page after the first) and the cursor 0. With a timestamp-only cursor on burst-written rows, `ts < last` missed 295 of 1500 rows paged and `ts <= last` duplicated 295; the (timestamp, id) cursor missed 0 and duplicated 0.
- Fix: Make the cursor a unique, totally ordered key: the sort column plus a unique tiebreaker such as the id, compared as a tuple.
- Why this fix: A cursor marks a point in the order. If several rows share the key at a page boundary, < skips the ones not yet shown and <= re-reads the ones already shown; only a unique key names one position.
- Rule of thumb: Cursor pagination beats offset (1500 rows scanned vs 45750 over 60 pages, 0 duplicates vs 177 with 3 inserts per page) only on a unique key: a timestamp-only cursor on rows written in bursts of 10 skipped 295 of 1500 rows with < and repeated 295 with <=, while a (timestamp, id) cursor did neither.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b03.py loop 13 in Pappydapimp69/Brain, deterministic. Observed: rows scanned 45750 vs 1500; duplicates 177 vs 0 under inserts; timestamp-only cursor 295 missed or 295 duplicated; tuple cursor 0 and 0. Assumed: rows scanned stands in for database cost, which also depends on indexes the model does not include.
- Composed: ideas:API-DESIGN/pagination/offset-vs-cursor/offset-pagination-gets-slower-with-depth-cursor-pagination-does-not
- Link: session 2026-09-28, brain train gap batch 3 loop 13
- Sandbox: sandboxes/2026-09-28__train-gap-b03.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-08 · projects/pappydapimp69__brain.md#E92 · compatible · sandboxes/2026-10-08__cursor-vs-offset-under-deletes.py · observed RESULT: PASS offset skips 160 of 1000; unique cursor 0; key-only cursor 0 (prediction missed on both counts). · brain train pass 1
- Cited-by: 2026-10-08 · projects/pappydapimp69__brainwork.md#E12 · compatible · sandboxes/2026-10-08__mod-load-stages-vs-single-pass.py · observed RESULT: PASS additive 4-mod perms single=8 staged=1; +SET conflict staged=2; tie sort priority-only=2 tuple=1. The first conflict attempt predicted more than 1 and observed 1 because a final cap masked it. · scheduled brain train auto pass 1
- Cited-by: 2026-10-12 · projects/pappydapimp69__brain.md#E142 · incompatible · sandboxes/2026-10-12__tuple-cursor-misses-rows-whose-sort-key-moves.py · observed RESULT: FAIL 3/4; cursor missed/dup e0/1/3 0/0 58/0 162/0; offset 0/0 59/59 177/177; snapshot 0/0 0/0 0/0; cursor misses equal the edits that landed · session; brain train pass 1 (aim: offset-vs-cursor single-source edge); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__brain.md#E145 · incompatible · sandboxes/2026-10-12__as-of-filter-on-live-rows-is-not-a-snapshot.py · observed RESULT: FAIL 2/3; missed(non-deleted)/dup mvcc 0/0 asof 70/0 of 90 edits; created 0/0 · session; brain train round 2 (API paging); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__brain.md#E146 · compatible · sandboxes/2026-10-12__refreshed-average-stats-cannot-see-skew.py · observed RESULT: FAIL 3/4; open actual 19000 est stale 20 refreshed 393; cost idx stale/fresh/full 950/950/980; rare idx/full 1/600; stat4 False · session; brain train auto pass 5 (gap); session_01KGZvxv8BDgpDMRFTYMfJoJ
