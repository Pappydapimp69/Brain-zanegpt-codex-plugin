"""Rebuild of seven E82 (one 55-gal barrel catches about a fifth of a 1000 sq ft roof's yearly runoff even when
emptied between storms; a 500-gal tank ~76%). Own fixture: 70 storms totalling 40 in with depths from an
EXPONENTIAL distribution (deterministic quantiles, mean 0.571 in) placed every 5.2 days on average with a
deterministic irregular spacing (2-12 days); 10% gutter loss; 12.5 gal first flush per storm (E82's numbers);
barrel drained (a) fully between storms (E82's best case) or (b) only by garden demand of 2, 10 or 25 gal/day.
Predictions written before running:
 P1 best case (emptied every storm): 55 gal catches 15-25% of net runoff; 500 gal 65-85%.
 P2 demand-limited at 10 gal/day: 55 gal catches at most 0.8x its best-case share.
 P3 at 2 gal/day even a 500 gal tank catches under 25%.
"""
import math

N, TOTAL = 70, 40.0
q = [-math.log(1 - (i + 0.5) / N) for i in range(N)]          # exponential quantiles
scale = TOTAL / sum(q); depths = [d * scale for d in q]
order = [(i * 37) % N for i in range(N)]                     # deterministic shuffle of sizes
depths = [depths[k] for k in order]
gaps = [2 + (i * 7) % 11 for i in range(N)]                  # 2..12 days
ROOF = 1000

def season(barrel, demand):
    store = caught = net_total = 0.0
    for d, gap in zip(depths, gaps):
        gross = ROOF * d * 0.623
        net = max(0.0, gross * 0.9 - 12.5); net_total += net
        if demand is None: store = 0.0
        take = min(barrel - store, net); store += take; caught += take
        if demand is not None: store = max(0.0, store - demand * gap)
    return caught / net_total

R = {}
for b in (55, 200, 500):
    R[(b, None)] = season(b, None)
    for dem in (2, 10, 25): R[(b, dem)] = season(b, dem)
    print(f"{b:3d} gal: best case {R[(b,None)]:.3f}; demand 2/10/25 gal/day {R[(b,2)]:.3f}/{R[(b,10)]:.3f}/{R[(b,25)]:.3f}")
p1 = 0.15 <= R[(55, None)] <= 0.25 and 0.65 <= R[(500, None)] <= 0.85
p2 = R[(55, 10)] <= 0.8 * R[(55, None)]
p3 = R[(500, 2)] < 0.25
checks = [("P1 best case matches E82's range", p1), ("P2 demand-limited 55 gal <= 0.8x best case", p2), ("P3 low demand caps a 500 gal tank under 25%", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; best case 55/200/500 {R[(55,None)]:.3f}/{R[(200,None)]:.3f}/{R[(500,None)]:.3f}; "
      f"55 gal at 2/10/25 gal/day {R[(55,2)]:.3f}/{R[(55,10)]:.3f}/{R[(55,25)]:.3f}; 500 gal at 2 gal/day {R[(500,2)]:.3f}")
