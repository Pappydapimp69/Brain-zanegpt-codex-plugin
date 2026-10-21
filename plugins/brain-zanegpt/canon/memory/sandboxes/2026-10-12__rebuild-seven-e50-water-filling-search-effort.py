"""Blind rebuild of seven E50 (search effort spreads by water filling).
Own fixture: 20 sectors in a line (not a ring), prior = discretised Laplace
around sector 6 with scale 'noise' plus 5% uniform; sweep width w = 0.7 per
hour; detection in a sector with effort e: 1 - exp(-w e). Total hours H.
Optimal (Koopman/Stone): e_i = max(0, ln(w p_i / lam)/w) with lam found by
bisection so sum e_i = H. Compared with ALL hours on the likeliest sector, and
a fixed block of the 4 likeliest with H/4 each.
PREDICTION (before running): water filling is never beaten by 2000 random
feasible allocations or by the alternatives; number of sectors searched grows
with H and with noise; concentrating loses >= 0.15 at H=8, noise 3; with a
sharp prior (noise 0.3) and H=1 concentrating is within 0.01 of optimal; the
fixed block loses most when noise is high. Break scenario: a bimodal prior (two
equal peaks far apart) - the 4-block and concentration both fail; water filling
should split across both peaks.
"""
import math, sys
print("python", sys.version.split()[0])
N, W = 20, 0.7
def prior(noise, peaks=(6,)):
    w = [sum(math.exp(-abs(i-c)/noise) for c in peaks) for i in range(N)]
    s = sum(w); return [0.95*v/s + 0.05/N for v in w]
def pd(p, e): return sum(pi*(1-math.exp(-W*ei)) for pi, ei in zip(p, e))
def water(p, H):
    lo, hi = 1e-12, max(p)*W
    for _ in range(200):
        lam = (lo*hi)**0.5
        e = [max(0.0, math.log(W*pi/lam)/W) for pi in p]
        if sum(e) > H: lo = lam
        else: hi = lam
    e = [max(0.0, math.log(W*pi/hi)/W) for pi in p]; s = sum(e)
    return [v*H/s for v in e]
x = 2024
def u():
    global x; x = (6364136223846793005*x + 1442695040888963407) % 2**64; return (x >> 11)/2**53
ok = True; table = {}
for noise in (0.3, 1.0, 3.0):
    for H in (1, 4, 8, 16):
        p = prior(noise); e = water(p, H); opt = pd(p, e)
        best = max(range(N), key=lambda i: p[i]); conc = pd(p, [H if i == best else 0 for i in range(N)])
        top4 = sorted(range(N), key=lambda i: -p[i])[:4]; blk = pd(p, [H/4 if i in top4 else 0 for i in range(N)])
        beat = 0
        for _ in range(150):
            r = [u()**3 for _ in range(N)]; s = sum(r); beat += pd(p, [v*H/s for v in r]) > opt + 1e-9
        n = sum(v > 1e-9 for v in e); table[(noise, H)] = (opt, conc, blk, n)
        ok &= beat == 0 and opt >= conc - 1e-9 and opt >= blk - 1e-9
        print(f"noise {noise} H {H:2d}: opt {opt:.3f} ({n:2d} sectors) concentrate {conc:.3f} block4 {blk:.3f} random beat {beat}")
grow_H = all(table[(n, 1)][3] <= table[(n, 16)][3] for n in (0.3, 1.0, 3.0))
grow_noise = all(table[(0.3, H)][3] <= table[(3.0, H)][3] for H in (1, 4, 8, 16))
loss = table[(3.0, 8)][0]-table[(3.0, 8)][1]; sharp = table[(0.3, 1)][0]-table[(0.3, 1)][1]
print(f"grows with H {grow_H}, with noise {grow_noise}; concentrate loss@H8,n3 {loss:.3f}; sharp H1 gap {sharp:.4f}")
p = prior(1.0, peaks=(3, 15)); e = water(p, 8)
both = sum(e[:9]) > 1 and sum(e[9:]) > 1
print(f"break bimodal: opt {pd(p,e):.3f} split both peaks {both} | top4 block {pd(p,[2 if i in sorted(range(N),key=lambda i:-p[i])[:4] else 0 for i in range(N)]):.3f}")
ok &= grow_H and grow_noise and loss >= 0.15 and sharp <= 0.01 and both
print(f"RESULT: {'PASS' if ok else 'FAIL'} never beaten; sectors {table[(1.0,1)][3]}->{table[(1.0,16)][3]} with hours; concentrate loses {loss:.3f} at H8 noise3; sharp prior gap {sharp:.4f}")
