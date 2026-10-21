"""Sandbox: benign-violation + escalation-needs-matching-distance + rule card.
Beat is funny iff a violation exists (sev>=1) AND it is benign (sev <= frame distance).
Score = sum of severity over funny beats (escalation earns more). Deterministic."""
FRAMES = {"grounded": 2, "sitcom": 4, "cartoon": 6}
SCHEDULES = {"flat-mild": [1]*6, "go-big": [1, 2, 3, 4, 5, 6], "flat-max": [6]*6}

def run(sched, dist, ceiling=None):
    sev = [min(s, ceiling) if ceiling is not None else s for s in sched]
    funny = [s for s in sev if 1 <= s <= dist]
    return len(funny), sum(funny)

res = {}
for f, d in FRAMES.items():
    for n, s in SCHEDULES.items():
        res[(f, n, "nocard")] = run(s, d)
        res[(f, n, "card")] = run(s, d, ceiling=d)       # ceiling = frame distance
        res[(f, n, "badcard")] = run(s, d, ceiling=6)    # BREAK: ceiling ignores frame
for k, v in sorted(res.items()):
    print(k, v)

ok = True
# 1) card+go-big is best score in every frame among all card schedules except flat-max, and >= nocard go-big
for f, d in FRAMES.items():
    cg = res[(f, "go-big", "card")]
    ok &= cg[0] == 6 and cg[1] >= res[(f, "go-big", "nocard")][1]
# 2) grounded: unclamped go-big only 2/6 funny, card makes 6/6
ok &= res[("grounded", "go-big", "nocard")][0] == 2 and res[("grounded", "go-big", "card")][0] == 6
# 3) BREAK: wrong ceiling (6) in grounded frame gives no help
ok &= res[("grounded", "go-big", "badcard")] == res[("grounded", "go-big", "nocard")]
# 4) matched distance: cartoon needs no card for go-big
ok &= res[("cartoon", "go-big", "nocard")][0] == 6
# 5) card trades escalation: grounded card go-big score 1+2+2+2+2+2=11 vs sitcom 1+2+3+4+4+4=18
ok &= res[("grounded", "go-big", "card")][1] == 11 and res[("sitcom", "go-big", "card")][1] == 18
g = res[("grounded", "go-big", "nocard")]; c = res[("grounded", "go-big", "card")]
print(f"RESULT: {'PASS' if ok else 'FAIL'} grounded go-big funny {g[0]}/6 -> {c[0]}/6 with ceiling=distance card; wrong ceiling stays {res[('grounded','go-big','badcard')][0]}/6; score {g[1]}->{c[1]}")
