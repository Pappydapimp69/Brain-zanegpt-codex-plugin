"""Seam: lockstep/E3 (a tracked stat needs a writer at its event) + brain/E2 (delta-sum over
history does not equal the true total; clamp to an independently computed truth) + brain/E3
(cross-check a silent total against ground truth).
World: 40 events each worth +v to a stat. Some events fire via a second code path that skips the
writer (lockstep failure). Separately a history has renames that re-add a file's lines with no offsetting negative.
PREDICTION: writer-counter undercounts by exactly the un-instrumented events' value (deterministic 3 of 40 paths -> 30),
delta-sum overshoots by exactly the renamed lines (200), both are silent (no error), and an independent
ground-truth recount catches both; clamping the stream to truth gives final==truth but leaves the
writer's missing events invisible mid-stream (clamp cannot repair undercount)."""
# path flag: True = went through writer
events = [(i, 10, not (i in (5, 6, 7))) for i in range(40)]
truth_events = sum(v for _, v, _ in events)
writer = sum(v for _, v, w in events if w)
print("truth", truth_events, "writer", writer, "under", truth_events - writer)
# history: file lines added per commit; rename at commits 3 and 8 re-adds 100 lines each, no negative
hist = [50, 30, 20, 100, 10, 40, 5, 25, 100, 15]      # deltas as seen (2 renames of 100)
true_total = sum(hist) - 200                          # HEAD parse (independent)
dsum = sum(d for d in hist if d > 0)
print("true", true_total, "delta-sum", dsum, "over", dsum - true_total)
run, stream = 0, []
for d in hist:
    run = min(run + max(d, 0), true_total); stream.append(run)
ok = (truth_events - writer == 30 and dsum - true_total == 200 and stream[-1] == true_total
      and all(a <= b for a, b in zip(stream, stream[1:])))
# cross-check catches both
caught = (writer != truth_events) and (dsum != true_total)
# breaker: clamp is NOT a repair for undercount: clamping writer stream to truth leaves it at writer
clamped_writer = min(writer, truth_events)
ok = ok and caught and clamped_writer == writer
print("stream tail", stream[-3:], "clamped writer", clamped_writer)
print(("RESULT: PASS" if ok else "RESULT: FAIL") + " writer undercount 30/400, delta-sum overshoot 200, both silent; ground-truth cross-check catches both; clamp fixes overshoot only")
