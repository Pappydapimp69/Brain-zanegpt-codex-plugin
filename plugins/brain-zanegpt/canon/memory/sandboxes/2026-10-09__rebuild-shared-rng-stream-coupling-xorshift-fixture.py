"""Prediction (before run): with a xorshift32 generator (different from an LCG), saving (seed, draw count) resumes exactly;
adding one unrelated consumer draw per tick to a SHARED stream changes the tested mechanic's outcome in a fraction of ticks of
about 2p(1-p) (so ~42% at p=0.3, ~18% at p=0.1, ~50% at p=0.5) over 400 ticks, i.e. clearly > 0 but NOT every tick; one
stream per mechanic (seed from a stable string id) changes 0. Built to break: a stream seeded from the mechanic's ORDINAL position
(not a stable id) re-couples when a mechanic is inserted before it. Deterministic, stdlib only."""
M = 0xFFFFFFFF
class X:
    def __init__(s, seed): s.s = (seed or 1) & M; s.n = 0
    def next(s):
        x = s.s; x ^= (x << 13) & M; x ^= x >> 17; x ^= (x << 5) & M; s.s = x; s.n += 1; return x / 2.0 ** 32
def resume(seed, n): 
    r = X(seed)
    for _ in range(n): r.next()
    return r
def h(name):                       # stable id -> seed (FNV-1a)
    v = 2166136261
    for ch in name.encode(): v = ((v ^ ch) * 16777619) & M
    return v
T = 400
def shared(p, extra):
    r = X(12345); out = []
    for _ in range(T):
        for _ in range(extra): r.next()
        out.append(r.next() < p)
    return out
def flips(a, b): return sum(x != y for x, y in zip(a, b))
# 1 resume
r = resume(777, 100); saved = (777, r.n); tail = [r.next() for _ in range(25)]
r2 = resume(*saved); tail2 = [r2.next() for _ in range(25)]
ok1 = tail == tail2
# 2 shared stream flips vs p
res = {}
for p in (0.1, 0.3, 0.5, 0.9):
    res[p] = flips(shared(p, 0), shared(p, 1)) / T
print("S2 shared-stream flip fraction", {k: round(v, 3) for k, v in res.items()})
ok2 = all(v > 0 for v in res.values()) and all(v < 0.9 for v in res.values())
# 3 per-mechanic streams by stable id
def split(p, extra):
    spread = X(h("spread")); other = X(h("enemy")); out = []
    for _ in range(T):
        for _ in range(extra): other.next()
        out.append(spread.next() < p)
    return out
res3 = {p: flips(split(p, 0), split(p, 3)) for p in (0.1, 0.3, 0.5, 0.9)}
print("S3 split flips", res3); ok3 = all(v == 0 for v in res3.values())
# 4 BREAK: ordinal-seeded streams
def ordinal(p, insert):
    names = (["new"] if insert else []) + ["spread"]
    streams = [X(1000 + i) for i, _ in enumerate(names)]; sp = streams[names.index("spread")]
    return [sp.next() < p for _ in range(T)]
f4 = flips(ordinal(0.3, False), ordinal(0.3, True)) / T
print("S4 ordinal-seeded flips when a mechanic is inserted before: %.3f" % f4); ok4 = f4 > 0.2
ok = ok1 and ok2 and ok3 and ok4
print("RESULT: %s resume_exact=%s shared flips p.1=%.3f p.3=%.3f p.5=%.3f p.9=%.3f (never all ticks); id-keyed split 0; ordinal-seeded flips %.3f" % (
    "PASS" if ok else "FAIL", ok1, res[0.1], res[0.3], res[0.5], res[0.9], f4))
