"""Prediction (before run): on 24x24 binary chance fields (deterministic integer hash, seeds 1..12, density 0.5), choosing the 5 best
NON-OVERLAPPING 3x3 patches and editing only them into a ring motif (8 ones around a 0 centre) needs a mean of <= 1.5 cell changes per
motif, versus exactly 8 per motif when planning the same motif on a blank field; touching only ~5% of cells leaves >= 90% of the chance
texture untouched. Built to BREAK: (a) density 0 (chance gives no material) must cost ~8 like blank; (b) a tiny 6x6 field (scarce material)
must cost more than the 24x24 field. Colour kernel: perceived = cell - mean(8 neighbours); editing one cell must shift the perceived value of
all 8 neighbours (an 'isolated correction' is not isolated). Deterministic, stdlib only."""
from fractions import Fraction as F
RING = ((1,1,1),(1,0,1),(1,1,1))
def field(n, seed, dens_pct):
    return [[1 if ((x*73856093 ^ y*19349663 ^ seed*83492791) * 2654435761 >> 7) % 100 < dens_pct else 0 for x in range(n)] for y in range(n)]
def dist(g, x, y):
    return sum(g[y+j][x+i] != RING[j][i] for j in range(3) for i in range(3))
def best_k(g, k):
    n = len(g); cand = sorted((dist(g,x,y), y, x) for y in range(n-2) for x in range(n-2))
    chosen = []
    for d, y, x in cand:
        if all(abs(x-cx) >= 3 or abs(y-cy) >= 3 for _, cy, cx in chosen): chosen.append((d, y, x))
        if len(chosen) == k: break
    return chosen
def run(n, dens, seeds, k=5):
    tot = F(0); cnt = 0; touched = F(0)
    for s in seeds:
        ch = best_k(field(n, s, dens), k)
        tot += sum(d for d,_,_ in ch); cnt += len(ch); touched += F(sum(d for d,_,_ in ch), n*n)
    return tot / cnt, touched / len(seeds)
S = range(1, 13)
mean24, frac24 = run(24, 50, S); mean0, _ = run(24, 0, S); mean6, _ = run(6, 50, S, 2)
blank = F(8)
rows = {d: run(24, d, S)[0] for d in (0, 10, 30, 50, 70, 90)}
# colour cascade: perceived = cell - mean(neighbours)
def perceived(g, x, y):
    nb = [g[y+j][x+i] for j in (-1,0,1) for i in (-1,0,1) if (i or j)]
    return F(g[y][x]) - F(sum(nb), 8)
g = field(24, 3, 50); before = {(x,y): perceived(g,x,y) for y in range(1,23) for x in range(1,23)}
g[10][10] ^= 1
shifted = sum(1 for k,v in before.items() if perceived(g,*k) != v and k != (10,10))
print("mean cost/motif by density", {d: float(v) for d,v in rows.items()})
print("24x24 mean", float(mean24), "touched frac", float(frac24), "dens0", float(mean0), "6x6", float(mean6), "neighbours shifted", shifted)
ok = mean24 <= F(3,2) and frac24 <= F(1,10) and mean0 >= 7 and mean6 > mean24 and shifted == 8
print("RESULT:", "PASS" if ok else "FAIL", f"chance+select costs {float(mean24):.2f} edits/motif vs blank 8, touching {float(frac24)*100:.1f}% of cells; density0 {float(mean0):.2f}, 6x6 {float(mean6):.2f}; one-cell edit shifts {shifted} neighbours")
