"""Prediction (before run): with N authors and 3 books each, a lazy per-author property inside a loop issues 1+N queries,
an IN-batch issues 2 (or 1+ceil(N/cap) with a key cap), a JOIN issues 1. With a simulated 2 ms round trip per query,
N=500 naive costs ~1002 ms (crosses a 1000 ms 'user loses flow' line) while batch/join stay under 100 ms ('feels instant');
at round trip 0 (in-process) the naive version is NOT slow, so query count, not time, is the invariant. BREAK cases: an
INNER JOIN silently drops authors with no books (batch keeps them); the cap of 100 keys gives 1+5 queries for N=500."""
import sqlite3, math

def make(n, books_per=3, childless_every=0):
    db = sqlite3.connect(":memory:")
    db.execute("create table author(id integer primary key, name text)")
    db.execute("create table book(id integer primary key, author_id int, title text)")
    bid = 0
    for a in range(1, n + 1):
        db.execute("insert into author values(?,?)", (a, f"a{a}"))
        if childless_every and a % childless_every == 0: continue
        for k in range(books_per):
            bid += 1; db.execute("insert into book values(?,?,?)", (bid, a, f"b{bid}"))
    counter = {"q": 0}
    db.set_trace_callback(lambda s: counter.__setitem__("q", counter["q"] + 1) if s.lstrip().lower().startswith("select") else None)
    return db, counter

class Author:  # looks innocent: a property that hides a query
    def __init__(self, db, row): self.db, self.id = db, row[0]
    @property
    def books(self):
        return [r[0] for r in self.db.execute("select title from book where author_id=?", (self.id,))]

def naive(db):
    return {a.id: a.books for a in (Author(db, r) for r in db.execute("select id from author").fetchall())}

def batch(db, cap=None):
    ids = [r[0] for r in db.execute("select id from author")]
    out = {i: [] for i in ids}
    for s in range(0, len(ids), cap or len(ids) or 1):
        chunk = ids[s:s + (cap or len(ids))]
        q = "select author_id,title from book where author_id in (%s)" % ",".join("?" * len(chunk))
        for aid, t in db.execute(q, chunk): out[aid].append(t)
    return out

def join(db, inner):
    out = {}
    kind = "join" if inner else "left join"
    for aid, t in db.execute(f"select a.id,b.title from author a {kind} book b on b.author_id=a.id"):
        out.setdefault(aid, []);
        if t is not None: out[aid].append(t)
    return out

RT_MS, FEELS_INSTANT, LOSES_FLOW = 2, 100, 1000
res = []; ok = True
for n in (10, 100, 500):
    d, c = make(n); a = naive(d); qn = c["q"]
    c["q"] = 0; b = batch(d); qb = c["q"]
    c["q"] = 0; j = join(d, False); qj = c["q"]
    same = a == b == j
    lat = {k: v * RT_MS for k, v in (("naive", qn), ("batch", qb), ("join", qj))}
    res.append((n, qn, qb, qj, same, lat["naive"]))
    print(f"N={n} queries naive/batch/join={qn}/{qb}/{qj} same_result={same} latency_ms={lat}")
    ok &= qn == 1 + n and qb == 2 and qj == 1 and same
n500 = res[-1]
ok &= n500[5] > LOSES_FLOW and 2 * n500[2] < FEELS_INSTANT and res[0][5] < FEELS_INSTANT
# BREAK 1: zero round trip -> naive is fast in wall terms but still 1+N queries
zero_lat = 0 * n500[1]; ok &= zero_lat < FEELS_INSTANT and n500[1] == 501
# BREAK 2: inner join drops childless authors
d, c = make(30, childless_every=5); full = batch(d); inner = join(d, True); left = join(d, False)
dropped = len(full) - len(inner); ok &= dropped == 6 and left == full
print(f"inner-join dropped {dropped} childless authors; left join matches batch={left == full}")
# BREAK 3: key cap
d, c = make(500); c["q"] = 0; batch(d, cap=100); capq = c["q"]; ok &= capq == 1 + 5
print(f"cap=100 batch queries={capq} (1 author query + 5 chunks)")
print("RESULT:", "PASS" if ok else "FAIL",
      f"N=500 naive {n500[1]} queries ~{n500[5]}ms vs batch {n500[2]} / join {n500[3]}; zero-RTT naive still {n500[1]} queries; inner join dropped {dropped}; cap100 -> {capq}")
