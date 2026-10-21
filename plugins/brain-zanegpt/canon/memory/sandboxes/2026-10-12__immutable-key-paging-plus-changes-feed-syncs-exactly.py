"""New-idea loop 3 (API-DESIGN): to sync a mutable collection, page it by an IMMUTABLE key (created_at, id) from a
snapshot token, then replay a CHANGES feed since that token, applied as an idempotent upsert by id.
Composes API-DESIGN offset-vs-cursor, idempotency (a repeated apply must be harmless), and webhooks
at-least-once (the feed may redeliver). Deterministic: 1500 rows, page 50, 30 pages; between pages 3 edits
and 1 insert land; the changes feed redelivers every 4th change (at-least-once).
Clients:
  a  cursor on (updated_at, id), no feed
  b  cursor on (created_at, id), no feed
  c  cursor on (created_at, id) + changes feed, upsert by id
  d  same as c but the feed is APPENDED (not upserted)
Predictions written before running:
 P1 a misses rows (edited ahead of the cursor) and new inserts.
 P2 b misses no original row but holds stale versions of rows edited after they were read, and misses inserts.
 P3 c ends identical to the server: 0 missing, 0 stale, 0 duplicates.
 P4 d ends with duplicate records (> 0) from the redelivered changes.
"""
N, PAGE, PAGES = 1500, 50, 30

def server():
    rows = {i: {"created": i, "updated": i, "v": 0} for i in range(N)}
    return rows, N, N

def run(client):
    rows, clock, nid = server()
    token = clock
    got, appended, feed, cursor = {}, [], [], None
    for p in range(PAGES):
        if client == "a":
            key = lambda i: (rows[i]["updated"], i)
        else:
            key = lambda i: (rows[i]["created"], i)
        order = sorted(rows, key=key, reverse=True)
        page = [i for i in order if cursor is None or key(i) < cursor][:PAGE]
        if page: cursor = key(page[-1])
        for i in page: got[i] = dict(rows[i])
        for k in range(3):   # edits to rows spread across the table
            i = (p * 97 + k * 389) % N
            clock += 1; rows[i]["updated"] = clock; rows[i]["v"] += 1; feed.append((i, dict(rows[i])))
        clock += 1; rows[nid] = {"created": clock, "updated": clock, "v": 0}; feed.append((nid, dict(rows[nid]))); nid += 1
    if client in ("c", "d"):
        delivered = []
        for n, ch in enumerate(feed):
            delivered.append(ch)
            if n % 4 == 0: delivered.append(ch)     # at-least-once redelivery
        for i, rec in delivered:
            if client == "c": got[i] = rec
            else: appended.append((i, rec))
    missing = sum(1 for i in rows if i not in got and not any(j == i for j, _ in appended))
    stale = sum(1 for i in got if got[i] != rows[i])
    if client == "d":
        ids = list(got) + [i for i, _ in appended]
        dups = len(ids) - len(set(ids))
    else:
        dups = 0
    orig_missing = sum(1 for i in range(N) if i not in got)
    inserts_missing = sum(1 for i in rows if i >= N and i not in got and not any(j == i for j, _ in appended))
    return dict(missing=missing, orig_missing=orig_missing, inserts_missing=inserts_missing, stale=stale, dups=dups)

R = {c: run(c) for c in "abcd"}
for c, r in R.items(): print(f"client {c}: {r}")
p1 = R["a"]["orig_missing"] > 0 and R["a"]["inserts_missing"] > 0
p2 = R["b"]["orig_missing"] == 0 and R["b"]["stale"] > 0 and R["b"]["inserts_missing"] > 0
p3 = R["c"]["missing"] == 0 and R["c"]["stale"] == 0 and R["c"]["dups"] == 0
p4 = R["d"]["dups"] > 0
checks = [("P1 updated_at cursor misses edits and inserts", p1), ("P2 created_at cursor: none missing, stale, inserts missed", p2),
          ("P3 cursor + upsert feed exact", p3), ("P4 appended feed duplicates", p4)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; a missing orig/inserts {R['a']['orig_missing']}/{R['a']['inserts_missing']}; "
      f"b stale {R['b']['stale']} inserts missed {R['b']['inserts_missing']}; c missing/stale/dups {R['c']['missing']}/{R['c']['stale']}/{R['c']['dups']}; d dups {R['d']['dups']}")
