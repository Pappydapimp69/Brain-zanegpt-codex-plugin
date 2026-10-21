"""Blind rebuild of seven E82 (one 55 gal barrel catches about a fifth of a
1,000 sq ft roof's yearly runoff, emptied between storms; runs a 10-emitter
drip bed ~5.5 h). Own fixture: three synthetic climates, storm depths from a
seeded LCG with an exponential distribution (mean m inches, n storms/yr):
  temperate 40 in/yr as 100 storms (m 0.40), arid 12 in/yr as 30 storms
  (m 0.40), drizzly 38 in/yr as 150 storms (m 0.25). First flush diverts
  0.05 in of every storm. Barrel emptied between storms; catch per storm =
  min(capacity, runoff after flush). Runoff gal = sq ft x in x 0.623.
Drip: 10 emitters x 1 gal/h.
PREDICTION (before running): 144/231 = 0.6234 so 0.623 holds to 0.001; one
barrel catches 15-25% in the temperate climate; the share is NOT a constant -
it rises in a drizzly climate (> 30%) - so 'about a fifth' is climate bound;
a 500 gal tank catches < 70% temperate; drip 5.5 h exactly.
Break scenario: the drizzly climate (many small storms).
"""
import math, sys
print("python", sys.version.split()[0])
K = 144/231
print("gal per sq ft-in", round(K, 5), "vs 0.623 diff", round(abs(K-0.623), 5))
def storms(n, m, seed):
    x = seed; out = []
    for _ in range(n):
        x = (1103515245*x + 12345) & 0x7fffffff
        u = (x + 0.5)/0x80000000; out.append(-m*math.log(u))
    return out
ROOF = 1000
def share(cap, st):
    tot = sum(ROOF*r*K for r in st)
    caught = 0.0
    for r in st:
        caught += min(cap, max(0.0, ROOF*(r-0.05)*K))
    return caught/tot
clim = {"temperate": (100, 0.40, 11), "arid": (30, 0.40, 12), "drizzly": (150, 0.25, 13)}
S = {}
for k, (n, m, sd) in clim.items():
    st = storms(n, m, sd)
    S[k] = (share(55, st), share(500, st))
    print(f"{k:9s} {sum(st):5.1f} in/yr {n} storms: 55 gal {S[k][0]:.3f}  500 gal {S[k][1]:.3f}")
drip = 55/(10*1.0)
print("drip hours", drip)
mine = abs(K-0.623) < 0.001 and 0.15 <= S['temperate'][0] <= 0.25 and S['drizzly'][0] > 0.30 and S['temperate'][1] < 0.70 and drip == 5.5
print("my prediction held:", mine, "(drizzly >30% and 500 gal <70% both refuted)")
claim = abs(K-0.623) < 0.001 and all(0.15 <= S[k][0] <= 0.25 for k in S) and abs(drip-5.5) < 1e-9
print(f"RESULT: {'PASS' if claim else 'FAIL'} claim 'about a fifth' holds in all 3 climates: temperate {S['temperate'][0]:.3f} arid {S['arid'][0]:.3f} drizzly {S['drizzly'][0]:.3f}; K {K:.4f}; drip {drip} h; 500 gal catches {S['temperate'][1]:.3f} temperate (my <70% refuted)")
