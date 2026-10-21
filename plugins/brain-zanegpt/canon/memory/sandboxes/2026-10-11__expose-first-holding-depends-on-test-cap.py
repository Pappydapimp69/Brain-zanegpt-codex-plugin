"""Rebuild of seven E29 (expose-first holds the fake longer than
rescue-narrows; the missed window dominates holding time).
Own fixture: party of 4 with one fake, 3-night rescue window, 8-night horizon,
search finds 0.45 per night. Expose-first (A): one pylon test per night, pick
accuracy derived 1/n + 0.25(1-1/n) over the n untested (1-of-4 0.4375, 1-of-3
0.5, 1-of-2 0.625, last certain); exposure ends holding. Rescue-narrows (B):
search each window night; a find brings two to the fire, the 1-of-2 pick
(0.631 from a fact/memory model) resolves that night, a wrong pick one night
later; a missed window holds the fake to the horizon. A fake resolved on
night j has been held j nights. Exact fractions.
PREDICTIONS (written before running):
 P1 B holds the fake fewer nights than A
 P2 in B, the missed-window branch supplies more than half of held nights
 P3 B spends fewer pylons per disappearance than A
 P4 (break) with a 5-night horizon instead of 8, B still holds less than A
"""
from fractions import Fraction as Fr
S, W, N = Fr(45, 100), 3, 4
acc2 = Fr(1, 2) + Fr(1, 2)*Fr(3, 8)*Fr(7, 10)
def acc(n): return Fr(1, n) + Fr(1, 4)*(1 - Fr(1, n))
def A():
    held = pyl = Fr(0); p = Fr(1); n = N
    for night in range(1, N+1):
        a = acc(n) if n > 1 else Fr(1)
        pyl += p; held += p*a*night; p *= 1-a; n -= 1
    return held, pyl
def B(H):
    held = pyl = miss_part = Fr(0); p = Fr(1)
    for night in range(1, W+1):
        f = p*S
        held += f*(acc2*night + (1-acc2)*(night+1))
        pyl += f*(acc2 + 2*(1-acc2)); p *= 1-S
    miss_part = p*H; held += miss_part
    return held, pyl, miss_part
Ah, Ap = A(); Bh, Bp, Bm = B(8); Bh5, _, _ = B(5)
print(f"A held {float(Ah):.3f} pylons {float(Ap):.3f}")
print(f"B held {float(Bh):.3f} pylons {float(Bp):.3f} miss share {float(Bm/Bh):.3f} miss rate {float((1-S)**W):.3f}")
print(f"B held at horizon 5: {float(Bh5):.3f}")
checks = [Bh < Ah, Bm/Bh > Fr(1, 2), Bp < Ap, Bh5 < Ah]
held = sum(checks)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4 predictions held; A held {float(Ah):.3f} "
      f"B held {float(Bh):.3f} (h5 {float(Bh5):.3f}); miss share {float(Bm/Bh):.3f}; pylons A {float(Ap):.3f} B {float(Bp):.3f}")
