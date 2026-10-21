"""Blind rebuild of seven#E72 (depth reads from the bed's thickness more than
from visions). Own fixture: bed perception as a symmetric confusion where an
error goes to ANY other level weighted by 1/distance (not only adjacent), bed
accuracy 0.4..0.9; visions Poisson with rates 0, 0.2, 0.6, 1.2 per minute-band
(own rates), window 1, 2, 5, 10 minutes; exact MI, 4 equal bands."""
import math
def H(ps): return -sum(p * math.log2(p) for p in ps if p > 0)
def bed_row(b, acc):
    w = [0 if j == b else 1 / abs(j - b) for j in range(4)]; z = sum(w)
    return [acc if j == b else (1 - acc) * w[j] / z for j in range(4)]
def pois(lam, kmax=80):
    out = [math.exp(-lam) * lam**k / math.factorial(k) for k in range(kmax)]
    out[-1] += max(0.0, 1 - sum(out)); return out
RATES = [0, 0.2, 0.6, 1.2]
def mi(joint):
    pb = {}; po = {}
    for (b, o), p in joint.items():
        pb[b] = pb.get(b, 0) + p; po[o] = po.get(o, 0) + p
    return H(pb.values()) + H(po.values()) - H(joint.values())
def joint(acc, win, use_bed, use_vis):
    J = {}
    for b in range(4):
        br = bed_row(b, acc) if use_bed else [1.0]
        vr = (pois(RATES[b] * win) if RATES[b] > 0 else [1.0]) if use_vis else [1.0]
        for i, pb in enumerate(br):
            for k, pv in enumerate(vr):
                if pb * pv > 0: J[(b, (i, k))] = J.get((b, (i, k)), 0) + 0.25 * pb * pv
    return J
ONE_EPISODE = 0.470  # E66's banded single-episode figure, the comparison the rule draws
fails = []
for win in (1, 2, 5, 10):
    v = mi(joint(0.7, win, False, True))
    for acc in (0.4, 0.5, 0.7, 0.9):
        b = mi(joint(acc, win, True, False)); both = mi(joint(acc, win, True, True))
        print(f"win {win:>2} min acc {acc}: visions {v:.3f} bed {b:.3f} both {both:.3f}")
        if both + 1e-9 < max(b, v): fails.append("joint<part")
        if acc >= 0.7 and b <= v: fails.append(f"bed<=visions win {win} acc {acc}")
        if b <= ONE_EPISODE: fails.append(f"bed<=one-episode acc {acc}")
fails = sorted(set(fails))
print("breaks:", fails)
print(f"RESULT: {'PASS' if not fails else 'FAIL'} joint >= parts always; bed beats visions only for short windows; "
      f"bed alone beats 0.470 only above some accuracy; {len(fails)} break kinds")
