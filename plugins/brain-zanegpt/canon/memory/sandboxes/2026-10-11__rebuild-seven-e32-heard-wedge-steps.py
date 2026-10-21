"""Rebuild of seven E32 (at 8 heard directions, find chance becomes a step
function of search hours; a 0.90-0.35 target table misses by ~0.2).
Own fixture: 40 internal sectors (5 per heard wedge, so each wedge has a
centre sector), heard direction = true sector + discrete Gaussian noise
(sigma in sectors) rounded to the nearest of 8 wedge centres. A search of H
sectors covers the H sectors nearest the heard centre (ties alternate
sides). Exact. Own targets 0.85 / 0.65 / 0.45 / 0.30, sigma 1..6.5 non
decreasing, H 1..20, skill gap >= 0.20 (naive = H/40).
PREDICTIONS (written before running):
 P1 (E32's claim) at sigma 6.5, find chance is flat over H = 1..4 (within 0.01)
 P2 (E32's claim) the target table misses by more than 0.05 somewhere
 P3 every depth can keep a skill gap >= 0.20
"""
import math
M, R = 40, 8; WS = M//R
def wedge(x): return int(((x % M) + WS/2) // WS) % R   # centre of wedge w is sector w*WS
def order(w):
    c = w*WS; out = [c]
    for d in range(1, M):
        for s in (c+d, c-d):
            if len(out) < M and s % M not in out: out.append(s % M)
    return out
ORD = {w: order(w) for w in range(R)}
def find(sig, H):
    ws = {d: math.exp(-0.5*(d/sig)**2) for d in range(-20, 21)}; z = sum(ws.values())
    tot = 0.0
    for s in range(M):
        for d, w in ws.items():
            if s in ORD[wedge(s+d)][:H]: tot += w/z
    return tot/M
SIG = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5]
curve = [find(6.5, h) for h in range(1, 11)]
print("sigma 6.5 by H 1..10:", " ".join(f"{x:.3f}" for x in curve))
print("sigma 2.0 by H 1..10:", " ".join(f"{find(2.0, h):.3f}" for h in range(1, 11)))
targets = [0.85, 0.65, 0.45, 0.30]; prev = 0; worst = 0; picks = []
for t in targets:
    best = None
    for s in SIG:
        if s < prev: continue
        for h in range(1, 21):
            p = find(s, h)
            if p - h/M < 0.20: continue
            e = abs(p-t)
            if best is None or e < best[0] - 1e-12: best = (e, s, h, p)
        if best and best[0] <= 0.01: break
    picks.append(best); prev = best[1]; worst = max(worst, best[0])
for t, b in zip(targets, picks):
    print(f"target {t}: sigma {b[1]} H {b[2]} find {b[3]:.3f} miss {b[0]:.3f} gap {b[3]-b[2]/M:.3f}")
p1 = max(curve[:4]) - min(curve[:4]) <= 0.01
p2 = worst > 0.05
p3 = all(b[3]-b[2]/M >= 0.20 for b in picks)
held = p1 + p2 + p3
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3 predictions held; sigma6.5 H1-4 "
      f"{curve[0]:.3f}/{curve[1]:.3f}/{curve[2]:.3f}/{curve[3]:.3f}; worst target miss {worst:.3f}; checks {[p1, p2, p3]}")
