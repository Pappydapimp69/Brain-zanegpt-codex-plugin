# Own fixture, own Edmonds-Karp. Prediction (before run): with open engines the ceiling is
# min(16, 6R) -> 6,12,16,16 for R=1,2,3,6. With round-robin 1-axis engines (8 engines over 5 axes)
# the same numbers. Hidden assumption: restriction only bites if axis supply is lopsided.
# BREAK: every engine pinned to the same single axis -> ceiling drops to min(6, 6R) = 6 even at R=6.
from collections import deque
def maxflow(cap, s, t):
    flow = 0
    while True:
        par = {s: None}; q = deque([s])
        while q and t not in par:
            u = q.popleft()
            for v, c in cap[u].items():
                if c > 0 and v not in par: par[v] = u; q.append(v)
        if t not in par: return flow
        v = t; b = 10**9
        while par[v] is not None: b = min(b, cap[par[v]][v]); v = par[v]
        v = t
        while par[v] is not None:
            cap[par[v]][v] -= b; cap[v][par[v]] = cap[v].get(par[v], 0) + b; v = par[v]
        flow += b
def ceiling(R, allowed, tropes=6, axes=5, engines=8, skels=2):
    cap = {}
    def add(u, v, c): cap.setdefault(u, {})[v] = c; cap.setdefault(v, {}).setdefault(u, 0)
    for t in range(tropes):
        add("S", ("T", t), R)
        for a in range(axes):
            add(("T", t), ("C", t, a), 1)
            for e in range(engines):
                if a in allowed[e]: add(("C", t, a), ("E", e), 1)
    for e in range(engines):
        for k in range(skels): add(("E", e), ("X", e, k), 1); add(("X", e, k), "Z", 1)
    return maxflow(cap, "S", "Z")
open_ = [set(range(5))] * 8
rr = [{e % 5} for e in range(8)]
three = [{(e + i) % 5 for i in range(3)} for e in range(8)]
pinned = [{0}] * 8
res = {}
for name, al in (("open", open_), ("three", three), ("roundrobin1", rr), ("pinned", pinned)):
    res[name] = [ceiling(R, al) for R in (1, 2, 3, 6)]
    print(name, res[name])
ok = all(res[n] == [6, 12, 16, 16] for n in ("open", "three", "roundrobin1")) and res["pinned"] == [6, 6, 6, 6]
print(f"RESULT: {'PASS' if ok else 'FAIL'} ceilings R=1,2,3,6 {res}")
