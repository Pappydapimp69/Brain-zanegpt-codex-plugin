# Deterministic: page through rows while a fixed schedule deletes rows already seen.
def run(mode, n=1000, page=50, del_every=1, del_count=10, unique=True):
    rows = [(i // 5 if not unique else i, i) for i in range(n)]  # (key,id); non-unique key groups of 5
    rows.sort()
    seen = []; off = 0; cur = None
    while True:
        if mode == "offset":
            batch = rows[off:off + page]; off += page
        else:
            if cur is None: batch = rows[:page]
            else:
                batch = [r for r in rows if (r > cur if unique else r[0] > cur[0])][:page]
            if batch: cur = batch[-1]
        if not batch: break
        seen += batch
        # delete the first del_count already-seen rows still present
        for r in batch[:del_count]:
            if r in rows: rows.remove(r)
    ids = [r[1] for r in seen]
    return n - len(set(ids)), len(ids) - len(set(ids))
res = {}
for name, args in [("offset", ("offset",)), ("cursor-unique", ("cursor",)), ("cursor-key-only", ("cursor", 1000, 50, 1, 10, False))]:
    res[name] = run(*args)
    print(name, "skipped,dups =", res[name])
res0 = run("offset", del_count=0)
print("offset no deletes", res0)
ok = res["offset"][0] == 160 and res["cursor-unique"] == (0, 0) and res0 == (0, 0) and res["cursor-key-only"] == (0, 0)
print("RESULT: %s offset skips %d of 1000 under deletes; unique cursor 0; key-only cursor skips %d (deletes alone do not break it)" % ("PASS" if ok else "FAIL", res["offset"][0], res["cursor-key-only"][0]))
