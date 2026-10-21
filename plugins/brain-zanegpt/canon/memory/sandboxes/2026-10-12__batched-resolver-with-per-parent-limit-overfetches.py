"""Re-verify sandbox-kernel-api-design E3 (DataLoader makes N+1 resolver calls into one call per
level) from a new angle: the child field takes a PER-PARENT argument, authors { reviews(first: k) }.
A batch keyed by author id becomes ONE query, but 'first k per author' is not expressible as a
plain IN (...) query, so the loader either over-fetches every review and slices, or needs a
window query (ROW_NUMBER() OVER (PARTITION BY author)). Deterministic: 500 authors, skewed review
counts c_i = 2000 // (i + 1) + 1 (a few prolific authors), k = 3 and 10. Also: two aliases asking
different k in one query (loader keyed on (id, k)).
Predictions written before running:
 P1 queries: naive 1 + 500, batched 2, window 2 (E3's 'one per level' holds on query count).
 P2 rows read by the plain batched IN query exceed the window query's by at least 5x at k = 3.
 P3 with uniform review counts (c = 4 each) the over-fetch falls under 1.5x at k = 3.
 P4 two aliases with different k keyed on (id, k) cost 3 queries, not 2.
"""
AUTH = 500
skew = [2000 // (i + 1) + 1 for i in range(AUTH)]
flat = [4] * AUTH

def cost(counts, k, mode):
    if mode == "naive":      # one LIMIT k query per author
        return 1 + AUTH, sum(min(c, k) for c in counts)
    if mode == "batched_in": # WHERE author IN (...) then slice in memory
        return 2, sum(counts)
    if mode == "window":     # ROW_NUMBER() <= k per author
        return 2, sum(min(c, k) for c in counts)

rows = {}
for name, counts in (("skewed", skew), ("uniform", flat)):
    for k in (3, 10):
        for mode in ("naive", "batched_in", "window"):
            rows[(name, k, mode)] = cost(counts, k, mode)
        r = rows
        print(f"{name:7s} k={k:2d}: naive {r[(name,k,'naive')]}  batched IN {r[(name,k,'batched_in')]}  window {r[(name,k,'window')]}  (queries, rows)")
over = {(n, k): rows[(n, k, "batched_in")][1] / rows[(n, k, "window")][1] for n in ("skewed", "uniform") for k in (3, 10)}
for key, v in over.items(): print(f"over-fetch {key}: x{v:.2f}")
# aliases: a: reviews(first: 3) b: reviews(first: 10) -> loader keyed on (id, k) -> two child batches
alias_queries = 1 + len({3, 10})
print(f"two aliases with different k: {alias_queries} queries")
p1 = rows[("skewed", 3, "naive")][0] == 501 and rows[("skewed", 3, "batched_in")][0] == 2 and rows[("skewed", 3, "window")][0] == 2
p2 = over[("skewed", 3)] >= 5
p3 = over[("uniform", 3)] < 1.5
p4 = alias_queries == 3
checks = [("P1 query counts", p1), ("P2 skewed over-fetch >= 5x", p2), ("P3 uniform over-fetch < 1.5x", p3), ("P4 aliases 3 queries", p4)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; skewed k3 rows naive/IN/window "
      f"{rows[('skewed',3,'naive')][1]}/{rows[('skewed',3,'batched_in')][1]}/{rows[('skewed',3,'window')][1]} "
      f"(x{over[('skewed',3)]:.1f}); uniform k3 x{over[('uniform',3)]:.2f}; aliases {alias_queries} queries")
