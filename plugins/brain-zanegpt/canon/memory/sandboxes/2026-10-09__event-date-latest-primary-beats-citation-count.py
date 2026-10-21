"""Sandbox: resolving a conflicting event date across scattered web listings.

Real case (Denton 31 Days of Halloween 2026, Blocktober Pumpkin Drop):
  - city calendar (2026 version, posted Sept) says Oct 8
  - a pre-season aggregator (posted Aug 24) says Oct 1 -- copied from the
    city's 2025 page, which said Oct 1
  - more listings echo each side.
Compare three resolvers. Deterministic, stdlib only.
Records: (source, value, published, is_primary, derived_from)
"""

def majority(recs):
    c = {}
    for r in recs:
        c[r["value"]] = c.get(r["value"], 0) + 1
    best = max(c.values())
    w = sorted(v for v, n in c.items() if n == best)
    return w[0] if len(w) == 1 else "TIE"

def root(r, by):
    seen = set()
    while r["derived_from"] and r["derived_from"] not in seen:
        seen.add(r["derived_from"]); r = by[r["derived_from"]]
    return r

def distinct_roots(recs):
    by = {r["source"]: r for r in recs}
    roots = {}
    for r in recs:
        if r["value"] == "?":
            continue
        roots.setdefault(r["value"], set()).add(root(r, by)["source"])
    best = max(len(s) for s in roots.values())
    w = sorted(v for v, s in roots.items() if len(s) == best)
    return w[0] if len(w) == 1 else "TIE"

def authority_only(recs, authority):
    return next(r["value"] for r in recs if r["source"] == authority)

def latest_primary(recs):
    prim = [r for r in recs if r["is_primary"]]
    pool = prim or recs
    return max(pool, key=lambda r: r["published"])["value"]

def verified(recs, value):
    # a primary source states it AND at least one other record agrees
    agree = [r for r in recs if r["value"] == value]
    return any(r["is_primary"] for r in agree) and len(agree) >= 2

R = lambda s, v, p, prim=False, d=None: dict(source=s, value=v, published=p, is_primary=prim, derived_from=d)

scenarios = {
    # 1) real Blocktober conflict
    "S1 blocktober": dict(truth="10-08", authority="city2026", recs=[
        R("city2025", "10-01", "2025-08-01", True),
        R("texashaunts", "10-01", "2026-08-24", d="city2025"),
        R("tiktok", "10-01", "2026-09-01", d="texashaunts"),
        R("city2026", "10-08", "2026-09-15", True),
        R("communityvoice", "10-08", "2026-10-01", d="city2026"),
    ]),
    # 2) BUILT TO BREAK authority-first: city page is stale, organizer posts a newer primary change
    "S2 stale authority": dict(truth="10-23", authority="city", recs=[
        R("city", "10-16", "2026-09-01", True),
        R("news", "10-16", "2026-09-05", d="city"),
        R("blog", "10-16", "2026-09-10", d="news"),
        R("organizer", "10-23", "2026-10-02", True),
    ]),
    # 3) single-source event: any resolver 'answers', but it must not be called verified
    "S3 single source": dict(truth="10-26", authority="instagram", recs=[
        R("instagram", "10-26", "2026-09-20", True),
    ]),
}

fails = 0
for name, s in scenarios.items():
    recs = s["recs"]
    m, d, a, l = majority(recs), distinct_roots(recs), authority_only(recs, s["authority"]), latest_primary(recs)
    v = verified(recs, l)
    print(f"{name}: truth={s['truth']} majority={m} roots={d} authority={a} latest_primary={l} verified={v}")
    if l != s["truth"]:
        fails += 1

exp = [
    majority(scenarios["S1 blocktober"]["recs"]) == "10-01",
    distinct_roots(scenarios["S1 blocktober"]["recs"]) == "TIE",
    authority_only(scenarios["S2 stale authority"]["recs"], "city") == "10-16",
    latest_primary(scenarios["S2 stale authority"]["recs"]) == "10-23",
    verified(scenarios["S3 single source"]["recs"], "10-26") is False,
    verified(scenarios["S2 stale authority"]["recs"], "10-23") is False,
    verified(scenarios["S1 blocktober"]["recs"], "10-08") is True,
]
print("checks:", exp)
if fails == 0 and all(exp):
    print("RESULT: PASS latest-primary correct 3/3; majority wrong on S1 (3v2), distinct-roots TIE on S1 (1v1), authority-first wrong on S2, S1 verified, S2+S3 (single agreeing record) flagged unverified")
else:
    print(f"RESULT: FAIL latest-primary wrong in {fails} scenario(s); checks={exp}")
