"""Sandbox: testing a coarse-perception search with the target pinned at one sector that
happens to be a bin centre (seven E32's fixture) makes find chance a step function of search
size; averaging the target over every sector removes the step. Exact, no RNG.
Ring of S sectors heard at R directions (bin width w = S/R); heard = true + discrete
Gaussian noise, rounded to the nearest bin centre; the search covers the H sectors nearest
the heard centre.
PREDICTIONS (written before running):
 P1 pinned at a centre (sector 0), find chance is flat for H = 1..w (S=24, R=8, w=3: H 1-3 equal)
 P2 averaged over all target sectors, find chance strictly rises for every H = 1..2w
 P3 pinned at a bin EDGE instead, the plateau moves (H=1 gives less than H=2)
"""
import math
def offs(sig):
    w = {k: math.exp(-0.5*(k/sig)**2) for k in range(-12, 13)}; z = sum(w.values()); return {k: v/z for k, v in w.items()}
def find(S, R, sig, H, targets):
    w = S // R; tot = 0.0
    for t in targets:
        for k, pk in offs(sig).items():
            h = (round((t+k)/w)*w) % S
            order = sorted(range(S), key=lambda s: (min((s-h) % S, (h-s) % S), s))
            if t % S in order[:H]: tot += pk
    return tot/len(targets)
S, R, SIG = 24, 8, 4.0
pinned = [find(S, R, SIG, H, [0]) for H in range(1, 7)]
avg = [find(S, R, SIG, H, range(S)) for H in range(1, 7)]
edge = [find(S, R, SIG, H, [1]) for H in range(1, 7)]
print("pinned centre:", " ".join(f"{x:.3f}" for x in pinned))
print("averaged     :", " ".join(f"{x:.3f}" for x in avg))
print("pinned edge  :", " ".join(f"{x:.3f}" for x in edge))
p1 = max(pinned[:3]) - min(pinned[:3]) < 1e-12
p2 = all(avg[i+1] > avg[i] + 1e-9 for i in range(5))
p3 = edge[0] < edge[1] - 1e-9
held = p1 + p2 + p3
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3 predictions held; pinned H1-3 "
      f"{pinned[0]:.3f}/{pinned[1]:.3f}/{pinned[2]:.3f}; averaged {avg[0]:.3f}->{avg[5]:.3f} strictly rising {p2}; "
      f"edge H1 {edge[0]:.3f} H2 {edge[1]:.3f}")
