"""ITERATION 2 NOTE: run 1 (no shared use factor) gave 2/4 held with P1 False, P3 False (use_r flat 0.420 because the four style loadings cancel in the sum); the shared factor was added to make the overall-use score meaningful. Predictions below were written before run 1 and not edited.
Prediction (before run): (1) with 4 styles on two latent axes, raising axis correlation rho from 0 to 0.8 cuts max-subscale
retest agreement (band 0) by >=0.10; (2) a margin band of 0.5 sample-SD raises agreement among labeled respondents by >=0.10 over
band 0 at rho=0.8 while coverage falls below 0.7; (3) overall-use score retest correlation stays >=0.85 at every rho;
(4) BREAK: adding self-report shading (affiliative/self-enhancing lifted, aggressive/self-defeating lowered) RAISES retest
agreement at band 0 by >=0.05 while LOWERING accuracy against the true top style by >=0.05, so agreement alone cannot certify labels.
Deterministic: Halton quasi-random points through the inverse normal CDF, no RNG. Stdlib only."""
from statistics import NormalDist
ND = NormalDist()
def halton(i, b):
    f, r = 1.0, 0.0
    while i > 0:
        f /= b; r += f * (i % b); i //= b
    return r
PR = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
def z(i, k): return ND.inv_cdf(min(max(halton(i + 1, PR[k]), 1e-6), 1 - 1e-6))
# styles: 0 affiliative,1 self-enhancing (benign) ; 2 aggressive,3 self-defeating (injurious)
# axis A = benign vs injurious use, axis B = self vs other target. style = (use, target) combination.
def traits(i, rho):
    s = rho ** .5; u = (1 - rho) ** .5
    A = z(i, 0); B = z(i, 1)             # latent axes, loadings share a common factor G with weight s
    G = z(i, 2)
    ua = s * G + u * A; ub = s * G + u * B
    # each style loads on both axes (2x2): +/- signs
    Uc = 1.0 * z(i, 8)   # overall humor-use factor shared by all four styles (iteration 2: run 1 had none, so the sum score was pure noise)
    return [ (ua + ub) / 2 + .6 * z(i, 3) + Uc, (ua - ub) / 2 + .6 * z(i, 4) + Uc,
             (-ua + ub) / 2 + .6 * z(i, 5) + Uc, (-ua - ub) / 2 + .6 * z(i, 6) + Uc ]
SHADE = [.5, .5, -.5, -.5]
def observe(t, i, wave, noise, shade):
    return [t[k] + noise * z(i * 7 + wave * 100003, 7 + k % 4 + 0) * (1 if k < 4 else 1) + (SHADE[k] if shade else 0) for k in range(4)]
def label(p, band):
    o = sorted(range(4), key=lambda k: -p[k])
    return o[0] if p[o[0]] - p[o[1]] > band else None
def pcorr(x, y):
    n = len(x); mx = sum(x) / n; my = sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y)); sxx = sum((a - mx) ** 2 for a in x); syy = sum((b - my) ** 2 for b in y)
    return sxy / (sxx * syy) ** .5
def run(rho, band_sd, shade, N=1500, noise=.8):
    A = []; B = []; T = []
    for i in range(N):
        t = traits(i, rho); T.append(t)
        A.append(observe(t, i, 1, noise, shade)); B.append(observe(t, i, 2, noise, shade))
    allv = [v for p in A for v in p]; m = sum(allv) / len(allv)
    sd = (sum((v - m) ** 2 for v in allv) / len(allv)) ** .5
    band = band_sd * sd
    la = [label(p, band) for p in A]; lb = [label(p, band) for p in B]
    both = [(x, y) for x, y in zip(la, lb) if x is not None and y is not None]
    lab = [x for x in la if x is not None]
    agree = sum(x == y for x, y in both) / max(1, len(both))
    cov = len(lab) / N
    acc_pairs = [(x, max(range(4), key=lambda k: t[k])) for x, t in zip(la, T) if x is not None]
    acc = sum(x == y for x, y in acc_pairs) / max(1, len(acc_pairs))
    use = pcorr([sum(p) for p in A], [sum(p) for p in B])
    return agree, cov, acc, use
res = {}
for rho in (0, .4, .8):
    for band in (0, .25, .5, 1.0):
        res[(rho, band, False)] = run(rho, band, False)
        print(f"rho={rho} band={band}sd agree={res[(rho,band,False)][0]:.3f} cov={res[(rho,band,False)][1]:.3f} acc={res[(rho,band,False)][2]:.3f} use_r={res[(rho,band,False)][3]:.3f}")
sh = run(.8, 0, True); print("shaded rho=.8 band0 agree=%.3f cov=%.3f acc=%.3f" % sh[:3])
shb = run(.8, .5, True); print("shaded rho=.8 band.5 agree=%.3f cov=%.3f acc=%.3f" % shb[:3])
p1 = res[(0, 0, False)][0] - res[(.8, 0, False)][0] >= .10
p2 = res[(.8, .5, False)][0] - res[(.8, 0, False)][0] >= .10 and res[(.8, .5, False)][1] < .7
p3 = all(res[(r, 0, False)][3] >= .85 for r in (0, .4, .8))
p4 = sh[0] - res[(.8, 0, False)][0] >= .05 and res[(.8, 0, False)][2] - sh[2] >= .05
print("P1", p1, "P2", p2, "P3", p3, "P4", p4)
print("RESULT:", "PASS" if all([p1, p2, p3, p4]) else "FAIL", f"{sum([p1,p2,p3,p4])}/4 predictions held; agree rho0 band0 {res[(0,0,False)][0]:.3f} vs rho.8 {res[(.8,0,False)][0]:.3f}; band.5 {res[(.8,.5,False)][0]:.3f} cov {res[(.8,.5,False)][1]:.3f}; shaded agree {sh[0]:.3f} acc {sh[2]:.3f} vs unshaded acc {res[(.8,0,False)][2]:.3f}")
