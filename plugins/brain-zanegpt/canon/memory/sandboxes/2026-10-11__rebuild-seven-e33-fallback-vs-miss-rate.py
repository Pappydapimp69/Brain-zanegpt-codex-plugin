"""Rebuild of seven E33 (a pylon fallback after a missed doppelganger rescue
window is cheap but buys little because misses are rare).
Own fixture: 2-night window, 8-night horizon (not 6), fallback tests from
night 3 at pick accuracy 0.40 then 0.55 then certain; rescue-narrows inside
the window with 1-of-2 pick 0.631 (wrong pick resolved next night). Search
rate swept 0.30..0.75 per night. Exact fractions.
PREDICTIONS (written before running):
 P1 the cut from two fallback tests is proportional to the miss rate (cut /
    miss rate is the same at every search rate)
 P2 at search 0.35 (miss 0.42) two tests cut held nights by >= 0.5, so
    'buys little' does not hold once misses are common
 P3 at every search rate the fallback costs under 1 pylon per disappearance
 P4 at search 0.6 (E33's rate) the cut is under 0.4 (E33's shape reproduces
    on a longer horizon)
"""
from fractions import Fraction as Fr
W, H = 2, 8
acc2 = Fr(1, 2) + Fr(1, 2)*Fr(3, 8)*Fr(7, 10)
FB = [Fr(40, 100), Fr(55, 100), Fr(1)]
def held(S, K):
    h = Fr(0); pyl = Fr(0); p = Fr(1)
    for n in range(1, W+1):
        f = p*S; h += f*(acc2*n + (1-acc2)*(n+1)); pyl += f*(2-acc2); p *= 1-S
    miss = p; q = miss
    for i in range(K):
        a = FB[i]; n = W+1+i
        pyl += q; h += q*a*n; q *= 1-a
    h += q*H
    return h, pyl, miss
rows = {}
for S in [Fr(30, 100), Fr(35, 100), Fr(45, 100), Fr(60, 100), Fr(75, 100)]:
    h0, p0, m = held(S, 0); h2, p2, _ = held(S, 2)
    rows[S] = (h0-h2, m, p2-p0)
    print(f"search {float(S):.2f} miss {float(m):.3f} held0 {float(h0):.3f} held2 {float(h2):.3f} "
          f"cut {float(h0-h2):.3f} cut/miss {float((h0-h2)/m):.3f} extra pylons {float(p2-p0):.3f}")
ratios = {v[0]/v[1] for v in rows.values()}
p1 = len(ratios) == 1
p2 = rows[Fr(35, 100)][0] >= Fr(1, 2)
p3 = all(v[2] < 1 for v in rows.values())
p4 = rows[Fr(60, 100)][0] < Fr(4, 10)
held_n = p1 + p2 + p3 + p4
print(f"RESULT: {'PASS' if held_n == 4 else 'FAIL'} {held_n}/4 predictions held; cut/miss constant "
      f"{float(next(iter(ratios))):.3f}; cut at search 0.35 {float(rows[Fr(35,100)][0]):.3f}, at 0.60 "
      f"{float(rows[Fr(60,100)][0]):.3f}; checks {[p1, p2, p3, p4]}")
