"""Rebuild (own fixture): credit attribution for deferred effects under a periodic sweep.
Three sources (player, ally, world) arm damage on 3 targets over 30 ticks; items fire after delay D at the
next sweep (every 2 ticks). Policies: naive(credit sweep/'world'), carry(item origin, no merge),
carry+coalesce single origin (merge same-target items due at one sweep, keep first origin),
carry+coalesce origin-set (merge, split credit by origin), apply-now (credit at arm time).
PREDICTION (before run): (1) final HP identical across all policies in every scenario; (2) D=0: every
policy credits player its full armed total; (3) D=3: naive credits player 0, carry/apply-now exact;
(4) with interleaved same-target items from 2 origins, coalesce-single-origin misattributes >0 damage while
origin-set is exact; (5) BREAK: if every merged group has ONE origin, coalesce-single is exact too (so the
rule's 'only while one item per origin' reading is about groups, not about coalescing as such)."""
from collections import defaultdict
def events(pattern):
    ev = []
    for t in range(0, 30):
        if pattern == "interleaved":     # player and ally hit same target on same tick
            ev += [(t, "player", t % 3, 3), (t, "ally", t % 3, 2)] if t % 2 == 0 else [(t, "world", (t + 1) % 3, 1)]
        else:                            # separated: each source owns its target
            ev += [(t, "player", 0, 3)] if t % 2 == 0 else [(t, "ally", 1, 2)]
            if t % 5 == 0: ev.append((t, "world", 2, 1))
    return ev
def run(policy, D, pattern, bypass=False):
    hp = defaultdict(int); credit = defaultdict(float); pend = []
    ev = events(pattern)
    for t in range(0, 30 + D + 4):
        for e in ev:
            if e[0] == t:
                if D == 0 or policy == "apply-now":
                    hp[e[2]] += e[3]; credit[e[1]] += e[3]
                else: pend.append((t + D, e[1], e[2], e[3]))
        if t % 2 == 0 and D > 0 and policy != "apply-now":
            due = [p for p in pend if p[0] <= t]; pend = [p for p in pend if p[0] > t]
            if policy in ("naive", "carry"):
                for _, o, tg, a in due:
                    hp[tg] += a; credit["sweep" if policy == "naive" else o] += a
            else:
                g = defaultdict(list)
                for _, o, tg, a in due: g[tg].append((o, a))
                for tg, items in g.items():
                    tot = sum(a for _, a in items); hp[tg] += tot
                    if policy == "coalesce-single": credit[items[0][0]] += tot
                    else:
                        for o, a in items: credit[o] += a
    return dict(hp), dict(credit)
armed = {}
for pat in ("interleaved", "separated"):
    armed[pat] = defaultdict(float)
    for _, o, _, a in events(pat): armed[pat][o] += a
pols = ["naive", "carry", "coalesce-single", "coalesce-set", "apply-now"]
res = {}
for pat in ("interleaved", "separated"):
    for D in (0, 3, 8):
        base = run("apply-now", D, pat)[0]
        for p in pols:
            hp, cr = run(p, D, pat)
            err = sum(abs(cr.get(o, 0) - armed[pat][o]) for o in armed[pat]) / 2 + (cr.get("sweep", 0) / 2)
            res[(pat, D, p)] = (hp == base, cr.get("player", 0), round(sum(abs(cr.get(o, 0) - armed[pat][o]) for o in set(cr) | set(armed[pat])) / 2, 1))
        print(pat, "D=%d" % D, "player armed", armed[pat]["player"], {p: (res[(pat, D, p)][1], "miscredit", res[(pat, D, p)][2]) for p in pols})
c1 = all(v[0] for v in res.values())
c2 = all(res[(pat, 0, p)][1] == armed[pat]["player"] for pat in armed for p in pols)
c3 = res[("interleaved", 3, "naive")][1] == 0 and res[("interleaved", 3, "carry")][2] == 0 and res[("interleaved", 3, "apply-now")][2] == 0
c4 = res[("interleaved", 3, "coalesce-single")][2] > 0 and res[("interleaved", 3, "coalesce-set")][2] == 0
c5 = res[("separated", 3, "coalesce-single")][2] == 0 and res[("separated", 8, "coalesce-single")][2] == 0
print("checks: hp-identical", c1, "D0-exact", c2, "naive0/carry-exact", c3, "interleaved-single-miscredit", c4, "separated-single-exact", c5)
print("RESULT: %s hp identical=%s; interleaved D=3 miscredit naive %s carry %s single %s set %s; separated single %s" % (
 "PASS" if all([c1,c2,c3,c4,c5]) else "FAIL", c1, res[("interleaved",3,"naive")][2], res[("interleaved",3,"carry")][2],
 res[("interleaved",3,"coalesce-single")][2], res[("interleaved",3,"coalesce-set")][2], res[("separated",3,"coalesce-single")][2]))
