# Batched loader with memo cache: query count and staleness, per-request vs shared-across-requests scope.
class DB:
    def __init__(s): s.rows = {i: "v0" for i in range(100)}; s.queries = 0
    def batch(s, keys): s.queries += 1; return [s.rows[k] for k in keys]
class Loader:
    def __init__(s, db): s.db = db; s.cache = {}
    def load_many(s, keys):
        miss = sorted({k for k in keys if k not in s.cache})  # dedupe within batch
        if miss:
            for k, v in zip(miss, s.db.batch(miss)): s.cache[k] = v
        return [s.cache[k] for k in keys]
def serve(db, loader_factory, requests=5):
    stale = 0; shared = loader_factory(db) if loader_factory.__name__ == "mk_shared" else None
    for r in range(requests):
        ld = shared or loader_factory(db)
        keys = [i % 10 for i in range(50)]            # 50 fields, only 10 distinct keys
        out = ld.load_many(keys)
        if r == 2: pass
        stale += sum(1 for k, v in zip(keys, out) if v != db.rows[k])
        for k in range(10): db.rows[k] = "v%d" % (r + 1)  # a write lands between requests
    return db.queries, stale
def mk_per(db): return Loader(db)
def mk_shared(db): return Loader(db)
def mk_none(db):
    l = Loader(db); l.load_many = lambda keys: [db.batch([k])[0] for k in keys]; return l
res = {}
for name, f in [("per-request", mk_per), ("shared", mk_shared), ("no-loader", mk_none)]:
    res[name] = serve(DB(), f); print(name, "queries,stale =", res[name])
ok = res["per-request"] == (5, 0) and res["shared"][0] == 1 and res["shared"][1] == 200 and res["no-loader"] == (250, 0)
print("RESULT: %s per-request %s, shared %s, no-loader %s (queries,stale)" % ("PASS" if ok else "FAIL", res["per-request"], res["shared"], res["no-loader"]))
