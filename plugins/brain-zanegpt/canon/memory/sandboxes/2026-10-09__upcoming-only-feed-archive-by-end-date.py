"""Sandbox: a feed that only returns not-yet-ended records. Refetch strategies compared.
Deterministic, stdlib only. Times are integer hours."""

def replace(archive, fresh, now):
    return dict(fresh)

def keep_all(archive, fresh, now):
    return {**archive, **fresh}

def end_date_rule(archive, fresh, now):
    kept = {k: r for k, r in archive.items() if k not in fresh and r["end"] <= now}
    return {**kept, **fresh}

def feed(db, now):
    return {k: r for k, r in db.items() if r["end"] > now and not r.get("cancelled_at", 1e9) <= now}

db = {
    "aged": {"end": 10},                         # ends before the 2nd fetch: must be kept
    "live": {"end": 50},                         # still running: must be kept
    "cancelled": {"end": 60, "cancelled_at": 15},  # BREAK case: vanishes before its end
    "late": {"end": 40, "added_at": 18},
}
def run(strategy):
    arch = {}
    for now in (5, 20):
        fresh = {k: r for k, r in feed(db, now).items() if r.get("added_at", 0) <= now}
        arch = strategy(arch, fresh, now)
    return sorted(arch)

want = ["aged", "late", "live"]
res = {s.__name__: run(s) for s in (replace, keep_all, end_date_rule)}
for k, v in res.items(): print(k, v, "OK" if v == want else "WRONG")
ok = res["end_date_rule"] == want and res["replace"] != want and res["keep_all"] != want
print("RESULT: " + ("PASS" if ok else "FAIL") + f" end-date rule {res['end_date_rule']}; replace loses aged {res['replace']}; keep-all resurrects cancelled {res['keep_all']}")
