"""Re-verify sandbox-kernel-api-design E1 (a unique (ts, id) cursor gives 0 missed, 0 duplicated)
from a new angle: the sort key MUTATES between page fetches (a feed ordered by updated_at,
newest first; editing a row bumps it to the top). Deterministic: 3000 rows, page 30, 60 pages (the newest 1800 are the paged range),
between fetches e rows NOT YET SEEN (chosen by a fixed stride) are edited, e = 0, 1, 3.
Predictions written before running:
 P1 with e = 0 the tuple cursor misses 0 and duplicates 0 (E1 reproduces).
 P2 with e >= 1 the tuple cursor misses exactly the edited unseen rows (60*e, minus edits on the last page) and duplicates 0.
 P3 offset paging under the same edits both misses and duplicates (dups > 0 and misses > 0).
 P4 a snapshot read (paging a frozen copy taken at page 1) misses 0 and duplicates 0 at every e.
"""
N, PAGE, PAGES = 3000, 30, 60

def run(mode, e):
    # rows: id -> updated_at; distinct initial timestamps
    ts = {i: i for i in range(N)}
    clock = N
    order = lambda: sorted(ts, key=lambda i: (ts[i], i), reverse=True)
    seen, dups, edited = set(), 0, set()
    initial_range = set(range(N - PAGES * PAGE, N))
    cursor, offset = None, 0
    frozen = order() if mode == "snapshot" else None
    for p in range(PAGES):
        if mode == "snapshot":
            page = frozen[p * PAGE:(p + 1) * PAGE]
        else:
            o = order()
            if mode == "offset":
                page = o[offset:offset + PAGE]; offset += PAGE
            else:
                page = [i for i in o if cursor is None or (ts[i], i) < cursor][:PAGE]
                cursor = (ts[page[-1]], page[-1])
        for i in page:
            if i in seen: dups += 1
            seen.add(i)
        # edit e unseen rows, picked deterministically from the not-yet-reached tail
        unseen = [i for i in sorted(initial_range) if i not in seen and i not in edited]
        for k in range(e):
            if unseen:
                victim = unseen[(k * 7 + p * 13) % len(unseen)]
                clock += 1; ts[victim] = clock; unseen.remove(victim); edited.add(victim)
    # missed: rows in the paged range at the first fetch that were never shown
    missed = len(initial_range - seen)
    EDITS[(mode, e)] = len(edited)
    return missed, dups

res, EDITS = {}, {}
for e in (0, 1, 3):
    for mode in ("cursor", "offset", "snapshot"):
        res[(mode, e)] = run(mode, e)
        print(f"e={e} {mode:8s}: missed {res[(mode, e)][0]:4d}  duplicated {res[(mode, e)][1]:4d}  edits landed {EDITS[(mode, e)]}")
p1 = res[("cursor", 0)] == (0, 0)
p2 = all(res[("cursor", e)][1] == 0 and res[("cursor", e)][0] >= 59 * e for e in (1, 3))
p3 = all(res[("offset", e)][0] > 0 and res[("offset", e)][1] > 0 for e in (1, 3))
p4 = all(res[("snapshot", e)] == (0, 0) for e in (0, 1, 3))
checks = [("P1 e=0 cursor 0/0", p1), ("P2 cursor misses ~60e, dups 0", p2), ("P3 offset misses and dups", p3), ("P4 snapshot 0/0", p4)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print("after the fact: cursor misses == edits landed: " + str(all(res[('cursor', e)][0] == EDITS[('cursor', e)] for e in (0, 1, 3))))
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; cursor missed/dup e0/1/3 " +
      " ".join(f"{res[('cursor', e)][0]}/{res[('cursor', e)][1]}" for e in (0, 1, 3)) + "; offset " +
      " ".join(f"{res[('offset', e)][0]}/{res[('offset', e)][1]}" for e in (0, 1, 3)) + "; snapshot " +
      " ".join(f"{res[('snapshot', e)][0]}/{res[('snapshot', e)][1]}" for e in (0, 1, 3)))
