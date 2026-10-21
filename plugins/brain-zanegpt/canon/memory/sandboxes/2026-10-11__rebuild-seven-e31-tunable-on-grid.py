"""Rebuild of seven E31 (spatial find chance is tunable per depth with two
knobs) on a DIFFERENT map shape: a 17x17 grid, camp at centre, member uniform
over cells >= 2 from camp, the call gives a bearing only (no distance), angle
noise Gaussian sigma. Knobs: sigma 5..60 deg (cap 60 = 4 of 24 sectors) and
search effort K cells (2..40, the K cells closest in bearing to the heard
one). Naive = K random cells. Own targets 0.85 / 0.60 / 0.40 / 0.25.
Selection rule as E31 prescribes: per depth, least sigma (not below the
previous depth's) that hits the target within 0.05 with skill gap >= 0.20.
Exact by 1-degree integration of the heard bearing.
PREDICTIONS (written before running):
 P1 every target hit within 0.05
 P2 every chosen setting keeps skill gap >= 0.20
 P3 with least-noise selection, difficulty rises through NOISE (sigma strictly
    higher at the deepest depth than at depth 0), as E31 reported
"""
import math
N = 17; C = N//2
cells = [(x, y) for x in range(N) for y in range(N) if max(abs(x-C), abs(y-C)) >= 2]
NC = len(cells)
def bdeg(c): return math.degrees(math.atan2(c[1]-C, c[0]-C)) % 360
def angd(a, b): d = abs(a-b) % 360; return min(d, 360-d)
B = [bdeg(c) for c in cells]
rank = {}
for h in range(360):
    order = sorted(range(NC), key=lambda i: (round(angd(B[i], h), 9), abs(cells[i][0]-C)+abs(cells[i][1]-C)))
    rank[h] = {i: r for r, i in enumerate(order)}
def find(sig, K):
    w = [math.exp(-0.5*(d/sig)**2) for d in range(-180, 180)]; z = sum(w)
    tot = 0.0
    for i in range(NC):
        b = round(B[i]) % 360
        for j, d in enumerate(range(-180, 180)):
            if rank[(b+d) % 360][i] < K: tot += w[j]/z
    return tot/NC
SIG = list(range(5, 61, 5)); KS = list(range(2, 41, 2))
table = {(s, k): find(s, k) for s in SIG for k in KS}
targets = [0.85, 0.60, 0.40, 0.25]
chosen = []; prev = 5; ok = True
for t in targets:
    pick = None
    for s in SIG:
        if s < prev: continue
        cands = [(abs(table[(s, k)]-t), k) for k in KS
                 if abs(table[(s, k)]-t) <= 0.05 and table[(s, k)] - k/NC >= 0.20]
        if cands: pick = (s, min(cands)[1]); break
    if pick is None: ok = False; chosen.append(None); continue
    prev = pick[0]; chosen.append(pick)
for t, c in zip(targets, chosen):
    if c: print(f"target {t:.2f}: sigma {c[0]} K {c[1]} find {table[c]:.3f} gap {table[c]-c[1]/NC:.3f}")
    else: print(f"target {t:.2f}: no setting")
p1 = all(c and abs(table[c]-t) <= 0.05 for t, c in zip(targets, chosen))
p2 = all(c and table[c]-c[1]/NC >= 0.20 for c in chosen)
p3 = bool(chosen[0] and chosen[-1] and chosen[-1][0] > chosen[0][0])
held = p1 + p2 + p3
desc = "; ".join(f"t{t} s{c[0]} K{c[1]} p{table[c]:.3f}" for t, c in zip(targets, chosen) if c)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3 predictions held; {desc}; checks {[p1, p2, p3]}")
