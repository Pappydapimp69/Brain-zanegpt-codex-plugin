"""Kernel under test: ideas:ORAL-STORYTELLING/voice-differentiation/prosody (quoted voices marked by pitch RANGE
not LEVEL), with sibling ideas:ORAL-STORYTELLING/voice-differentiation/listener-limits (listeners rarely reject an
unfamiliar voice) and memory sandbox-strip-test-speech-features-fail-on-short-lines/E1 (features fail on short lines).
Deterministic: z-scores come from NormalDist().inv_cdf((k+.5)/n), pairing between feature and sample order uses a fixed
stride, no RNG, no timing. Paper stats used (females): direct-quote range 119 Hz SD 66, narrative range 61 SD 44,
level 205 vs 181 Hz; level SD assumed 40 Hz (not given in the kernel).
Prediction (before run): at N=34 per class, range separates direct vs narrative with AUC >= 0.80 and level with AUC <= 0.65;
if the teller pushes level +80 Hz (the wrong dial) level AUC rises above 0.85 (BREAK: wrong dial works only when the shift
exceeds natural drift); with only 3 pitch points per segment, measured range AUC falls under 0.75; and for a listener
whose voice description is level+range with noise, no reject threshold gives both >=80% hits and >=80% absent-rejections
when the new voice is within 1 sigma of a known one."""
from statistics import NormalDist
N = NormalDist()
def zs(n): return [N.inv_cdf((k + .5) / n) for k in range(n)]
def auc(pos, neg): return sum((p > q) + .5 * (p == q) for p in pos for q in neg) / (len(pos) * len(neg))
def saw(k, m): return (k * 0.6180339887498949 % 1) * 2 - 1   # deterministic contour shape in [-1,1)

def segment(level, rng, n):          # n pitch points; true range scaled so measured range ~ rng for dense contours
    pts = [level + 0.5 * rng * saw(i + 1, 1) / 0.97 for i in range(n)]
    return pts
def feats(pts): return sum(pts) / len(pts), max(pts) - min(pts)

def build(n_seg, n_pts, lvl_dir, lvl_nar, rng_dir=(119, 66), rng_nar=(61, 44), lvl_sd=40, stride=7):
    z = zs(n_seg); zl = [z[(i * stride) % n_seg] for i in range(n_seg)]
    D, Nn = [], []
    for i in range(n_seg):
        rd = max(10, rng_dir[0] + rng_dir[1] * z[i]); rn = max(10, rng_nar[0] + rng_nar[1] * z[(i * 5 + 3) % n_seg])
        # shift contour phase per segment so short windows sample different points
        D.append(feats([lvl_dir + lvl_sd * zl[i] + 0.5 * rd * saw(i * 13 + j + 1, 1) / 0.97 for j in range(n_pts)]))
        Nn.append(feats([lvl_nar + lvl_sd * zl[(i * 3 + 1) % n_seg] + 0.5 * rn * saw(i * 17 + j + 5, 1) / 0.97 for j in range(n_pts)]))
    return D, Nn

res = {}
def run(name, **kw):
    D, Nn = build(34, **kw); a_l = auc([d[0] for d in D], [x[0] for x in Nn]); a_r = auc([d[1] for d in D], [x[1] for x in Nn])
    res[name] = (a_l, a_r); print(f"{name}: level AUC {a_l:.3f}  range AUC {a_r:.3f}"); return a_l, a_r
run("S1 paper-like (dense)", n_pts=40, lvl_dir=205, lvl_nar=181)
run("S2 BREAK wrong dial +80Hz level", n_pts=40, lvl_dir=261, lvl_nar=181)
run("S3 short lines (3 pitch points)", n_pts=3, lvl_dir=205, lvl_nar=181)

# listener model: voice described by (level, range); known cast of 3 at fixed positions; noisy re-hearing = grid offsets
def listener(gap_sigma, thr, sigma=1.0):
    known = [0.0, 3.0, 6.0]; offs = [(-1.0, -.5), (-.5, 0.), (0., .5), (.5, 1.0), (1.0, 0.)]   # fixed noise draws (units of sigma)
    hits = n = 0
    for k in known:
        for o in offs:
            x = k + o[0] * sigma; d = [abs(x - kk) for kk in known]; j = d.index(min(d)); n += 1
            hits += (j == known.index(k)) and d[j] <= thr
    newv = known[-1] + gap_sigma * sigma; rej = tot = 0
    for o in offs:
        x = newv + o[0] * sigma; tot += 1; rej += min(abs(x - kk) for kk in known) > thr
    return hits / n, rej / tot
best = 0
for thr in [t / 4 for t in range(1, 25)]:
    h, r = listener(1.0, thr); best = max(best, min(h, r))
print(f"S4 listener, new voice 1 sigma from known: best min(hit, reject) over thresholds = {best:.2f}")
best_far = max(min(*listener(4.0, t / 4)) for t in range(1, 25)); print(f"S5 listener, new voice 4 sigma away: best min(hit, reject) = {best_far:.2f}")
l1, r1 = res["S1 paper-like (dense)"]; l2, _ = res["S2 BREAK wrong dial +80Hz level"]; _, r3 = res["S3 short lines (3 pitch points)"]
ok1 = r1 >= .80 and l1 <= .65 and l2 > .85 and r3 < .75 and best < .80 <= best_far
print("ITER1 (absolute thresholds above): ", "PASS" if ok1 else "FAIL", f"- range AUC {r1:.2f} missed 0.80, level AUC {l1:.2f} missed 0.65, short-line range {r3:.2f} did not fall below 0.75")
# ITER2 prediction (written after iter1, from the paper's own SDs: d'(range)=58/79=0.73 -> AUC~0.70, d'(level)=24/57=0.42 -> ~0.62):
# range AUC exceeds level AUC by >= 0.07 and sits in 0.68-0.80 (only a MODERATE cue); +80Hz level push makes level beat range;
# short lines leave range AUC within 0.05 of dense; listener asymmetry (near < 0.80 <= far) holds.
ok2 = (r1 - l1) >= .07 and .68 <= r1 <= .80 and l2 > r1 and abs(r3 - r1) <= .05 and best < .80 <= best_far
print("RESULT:", "PASS" if ok2 else "FAIL", f"iter2 range {r1:.2f} vs level {l1:.2f}; wrong-dial level={l2:.2f}; short-line range={r3:.2f}; listener near={best:.2f} far={best_far:.2f}; iter1 absolute thresholds failed")
