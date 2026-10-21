"""Compose: Kawasaki exact on integer degrees (brainwork/E218) + Maekawa-valid not sufficient (origami E1).
Sectors are integer multiples of STEP degrees summing to 360. Crimp test: repeatedly remove a sector that is
<= both neighbours and whose bounding creases differ (M/V), merging neighbours: l - a + r. Flat iff the end is
two equal sectors with opposite creases."""
import itertools
STEP = 30  # degrees; integer arithmetic only
def comps(n, total):
    def rec(k, left):
        if k == 1:
            if left > 0: yield (left,)
            return
        for a in range(1, left - (k-1) + 1):
            for r in rec(k-1, left-a): yield (a,)+r
    yield from rec(n, total)
def kawasaki(s): return sum(s[0::2]) == sum(s[1::2]) == 180
def crimp(s, c):
    s, c = list(s), list(c)  # c[i] = crease between s[i-1] and s[i]
    while len(s) > 2:
        n = len(s); done = False
        for i in range(n):
            l, r = s[i-1], s[(i+1) % n]
            if s[i] <= l and s[i] <= r and c[i] != c[(i+1) % n]:
                new = l - s[i] + r
                if n == 3: return False
                idx = [(i-1) % n, i, (i+1) % n]
                keep = c[i]; 
                s2 = [s[j] for j in range(n) if j not in idx]
                c2 = [c[j] for j in range(n) if j not in idx]
                # place merged sector where sector i-1 was; its leading crease is c[i-1], trailing c[i+1]
                pos = (i-1) % n
                S = s[:]; C = c[:]
                S[pos] = new
                for j in sorted([i, (i+1) % n], reverse=True):
                    pass
                # rebuild: sectors without i and i+1 ... simpler: rotate so that i-1 is first
                ss = [s[(i-1+k) % n] for k in range(n)]; cc = [c[(i-1+k) % n] for k in range(n)]
                # ss[0]=l ss[1]=a ss[2]=r ; cc[0]=lead of l, cc[1]=between l,a, cc[2]=between a,r, cc[3]=between r,next
                ss2 = [new] + ss[3:]; cc2 = [cc[0]] + cc[3:]
                s, c = ss2, cc2; done = True; break
        if not done: return False
    return s[0] == s[1] and c[0] == c[1]
def assignments(n):
    for c in itertools.product("MV", repeat=n):
        if abs(c.count("M") - c.count("V")) == 2: yield c
def run(n):
    kv = mk_ok = lay_ok = ex = 0; none_found = 0
    for s in comps(n, 360//STEP):
        s = tuple(x*STEP for x in s)
        if not kawasaki(s): continue
        kv += 1
        mk = list(assignments(n)); good = [c for c in mk if crimp(s, c)]
        mk_ok += len(mk); lay_ok += len(good)
        if not good: none_found += 1
    return kv, mk_ok, lay_ok, none_found
res = {n: run(n) for n in (4, 6, 8)}
for n, (kv, mk, ly, nf) in res.items(): print(f"deg {n}: kawasaki-valid {kv}, maekawa-valid assignments {mk}, pass layer check {ly} ({ly/mk:.2%}), vertices with none {nf}")
# float vs exact on same grid: sum of sectors in float radians with 1e-9 vs exact integers
import math
bad = 0; tot = 0
for s in comps(6, 360//STEP):
    s = tuple(x*STEP for x in s)
    if kawasaki(s):
        tot += 1
        f = [math.radians(x) for x in s]
        if sum(f[0::2]) != math.pi: bad += 1
print(f"exact float == pi rejects {bad}/{tot} foldable degree-6 vertices; integers reject 0")
ok = all(nf == 0 for *_, nf in res.values()) and all(ly < mk for _, mk, ly, _ in res.values()) and bad > 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} every Kawasaki vertex has >=1 valid assignment but Maekawa alone over-accepts: " + ", ".join(f"deg{n} {ly}/{mk}" for n,(kv,mk,ly,nf) in res.items()) + f"; float equality rejects {bad}/{tot}")
