"""Re-verify brain E142's Fix (when the sort key moves, page a snapshot: 'a read-consistent transaction,
a frozen result id, or an as-of timestamp filter', or sort by an immutable key). Own fixture: 2400 rows,
page 40, 45 pages over the newest 1800, e = 2 edits per page to unseen rows in range, plus d = 1
delete per page. Readers:
  mvcc      true snapshot (rows as of the first fetch, old versions kept)
  asof      WHERE updated_at <= t0 on LIVE rows, cursor on (updated_at, id)
  created   cursor on immutable (created_at, id), live rows
Predictions written before running:
 P1 mvcc misses 0 rows of the original range and shows 0 duplicates.
 P2 the as-of filter misses as many rows as there were edits that landed (edited rows leave the filter).
 P3 the immutable created_at cursor misses only deleted rows (0 for edits) and duplicates 0.
"""
N, PAGE, PAGES, E, D = 2400, 40, 45, 2, 1

def run(mode):
    created = {i: i for i in range(N)}
    upd = dict(created); alive = set(range(N)); clock = N
    rng_range = set(range(N - PAGES * PAGE, N))
    t0 = clock
    frozen = sorted(rng_range, key=lambda i: (upd[i], i), reverse=True) if mode == "mvcc" else None
    seen, dups, edits, dels, cursor = set(), 0, 0, set(), None
    for p in range(PAGES):
        if mode == "mvcc":
            page = frozen[p * PAGE:(p + 1) * PAGE]
        else:
            key = (lambda i: (created[i], i)) if mode == "created" else (lambda i: (upd[i], i))
            rows = [i for i in alive if (mode != "asof" or upd[i] <= t0)]
            rows.sort(key=key, reverse=True)
            page = [i for i in rows if cursor is None or key(i) < cursor][:PAGE]
            if page: cursor = key(page[-1])
        for i in page:
            if i in seen: dups += 1
            seen.add(i)
        unseen = sorted(i for i in rng_range if i not in seen and i in alive)
        for k in range(E):
            if unseen:
                v = unseen[(k * 11 + p * 17) % len(unseen)]; clock += 1; upd[v] = clock; edits += 1; unseen.remove(v)
        for k in range(D):
            if unseen:
                v = unseen[(k * 5 + p * 23) % len(unseen)]; alive.discard(v); dels.add(v); unseen.remove(v)
    missed = rng_range - seen
    return len(missed), len(missed - dels), dups, edits, len(dels)

res = {m: run(m) for m in ("mvcc", "asof", "created")}
for m, (mi, me, du, ed, de) in res.items():
    print(f"{m:8s}: missed {mi:4d} (of which not deleted {me:4d})  duplicated {du}  edits landed {ed}  deletes {de}")
p1 = res["mvcc"][0] == 0 and res["mvcc"][2] == 0
p2 = res["asof"][1] == res["asof"][3]
p3 = res["created"][1] == 0 and res["created"][2] == 0
checks = [("P1 mvcc 0/0", p1), ("P2 as-of misses = edits", p2), ("P3 created_at misses only deletes", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; missed(non-deleted)/dup mvcc {res['mvcc'][0]}/{res['mvcc'][2]} "
      f"asof {res['asof'][1]}/{res['asof'][2]} of {res['asof'][3]} edits; created {res['created'][1]}/{res['created'][2]}")
