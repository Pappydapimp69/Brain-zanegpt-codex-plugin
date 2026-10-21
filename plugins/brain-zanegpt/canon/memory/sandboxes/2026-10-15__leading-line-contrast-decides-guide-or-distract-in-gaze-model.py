"""Gap pass: ideas:PHOTOGRAPHY/composition/leading-lines/leading-lines-genuinely-redirect-gaze-eye-tracking-confirms-it

HAND-WRITTEN gaze model, not eye-tracking data and not a published saliency model. It can only show what
follows from its own rules: fixations go to the best of saliency x proximity x line-continuation bias,
with inhibition of return.
Frame 48x32. Background texture saliency 0.05-0.15 (integer hash). Subject: disc radius 2 at (38, 8),
saliency s. Leading line: from (4, 30) to an endpoint, pixels of saliency l. When the current fixation is
within 1 px of the line, candidates ahead along the line direction get x(1 + 2 cos) (backwards no boost).
Next fixation = argmax of sal * exp(-d/12) * lead, pixels within 3 px of the last 4 fixations x0.1.
16 start points on a lattice, 10 fixations each. TTFF = index of first fixation within 3 px of the subject
(11 if never); dwell = share of fixations there.
Prediction (written before the first run): with a strong subject (s=0.8) a line ending at the subject
cuts mean TTFF by at least 20 percent vs no line; a line ending in an empty corner gives no cut (TTFF not
lower than no line); the line's TTFF cut is larger for a strong subject than a faint one (s=0.3), as the
kernel's qualifier says; break: a line brighter than the subject (l=1.0) raises TTFF above the l=0.4 line.
Pure stdlib, deterministic."""
import math

W, H, SUBJ, START = 48, 32, (38, 8), (4, 30)

def bg(x, y):
    return 0.05 + 0.10 * (((x * 73856093) ^ (y * 19349663)) % 101) / 100

def line_pts(end):
    (x0, y0), (x1, y1) = START, end
    n = max(abs(x1 - x0), abs(y1 - y0))
    return [(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)]

def scene(s, l, end):
    sal = {(x, y): bg(x, y) for x in range(W) for y in range(H)}
    pts = line_pts(end) if end else []
    for p in pts:
        sal[p] = max(sal[p], l)
    if s > 0:
        for x in range(W):
            for y in range(H):
                if (x - SUBJ[0]) ** 2 + (y - SUBJ[1]) ** 2 <= 4:
                    sal[(x, y)] = max(sal[(x, y)], s)
    d = None
    if end:
        dx, dy = end[0] - START[0], end[1] - START[1]; m = math.hypot(dx, dy); d = (dx / m, dy / m)
    return sal, set(pts), d

def scanpath(sal, pts, d, start, n=10, beta=2):
    fix, cur = [], start
    for _ in range(n):
        on_line = d is not None and any(abs(cur[0] - px) <= 1 and abs(cur[1] - py) <= 1 for px, py in pts)
        best, bp = -1, None
        for (x, y), v in sal.items():
            dist = math.hypot(x - cur[0], y - cur[1])
            if dist < 1: continue
            sc = v * math.exp(-dist / 12)
            if on_line:
                c = ((x - cur[0]) * d[0] + (y - cur[1]) * d[1]) / dist
                sc *= 1 + beta * max(0.0, c)
            if any(math.hypot(x - fx, y - fy) <= 3 for fx, fy in fix[-4:]):
                sc *= 0.1
            if sc > best or (sc == best and (x, y) < bp):
                best, bp = sc, (x, y)
        fix.append(bp); cur = bp
    return fix

STARTS = [(x, y) for x in (4, 16, 28, 40) for y in (4, 12, 20, 28)]

def run(s, l, end, beta=2):
    sal, pts, d = scene(s, l, end)
    tt, dw, endhits = [], [], []
    for st in STARTS:
        f = scanpath(sal, pts, d, st, beta=beta)
        near = [math.hypot(x - SUBJ[0], y - SUBJ[1]) <= 3 for x, y in f]
        tt.append(near.index(True) + 1 if True in near else 11)
        dw.append(sum(near) / len(f))
        if end: endhits.append(sum(math.hypot(x - end[0], y - end[1]) <= 3 for x, y in f) / len(f))
    return sum(tt) / len(tt), sum(dw) / len(dw), (sum(endhits) / len(endhits) if endhits else 0.0)

EMPTY = (44, 30)  # a line running along the bottom into an empty corner
R = {}
for name, s, l, end in [("strong none", 0.8, 0, None), ("strong ->subj", 0.8, 0.4, SUBJ), ("strong ->empty", 0.8, 0.4, EMPTY),
                        ("faint none", 0.3, 0, None), ("faint ->subj", 0.3, 0.4, SUBJ),
                        ("absent ->spot", 0.0, 0.4, SUBJ), ("absent none", 0.0, 0, None),
                        ("strong bright->subj", 0.8, 1.0, SUBJ), ("faint bright->subj", 0.3, 1.0, SUBJ)]:
    R[name] = run(s, l, end)
    print(f"{name:20s} TTFF {R[name][0]:5.2f}  subject dwell {R[name][1]:.3f}  line-end dwell {R[name][2]:.3f}")

cut_strong = 1 - R["strong ->subj"][0] / R["strong none"][0]
cut_faint = 1 - R["faint ->subj"][0] / R["faint none"][0]
print(f"line TTFF cut: strong subject {cut_strong:.0%}, faint subject {cut_faint:.0%}")
k_ok = cut_strong >= 0.20 and R["strong ->empty"][0] >= R["strong none"][0]
qual = cut_strong > cut_faint
brk = R["strong bright->subj"][0] > R["strong ->subj"][0]
print(f"kernel core holds: {k_ok}; kernel qualifier (bigger effect with prominent subject) holds: {qual}; bright line slows TTFF: {brk}")
# Added after run 1 printed FAIL at l=0.4, beta=2: sweep line saliency and continuation boost to see what
# the base-case result depends on. The pass criterion above is unchanged; the sweep is reported, not gated.
sweep = {}
for beta in (1, 2, 8):
    for l in (0.2, 0.4, 0.6):
        sn, ss = run(0.8, 0, None, beta)[0], run(0.8, l, SUBJ, beta)[0]
        fn, fs = run(0.3, 0, None, beta)[0], run(0.3, l, SUBJ, beta)[0]
        sweep[(beta, l)] = (1 - ss / sn, 1 - fs / fn)
        print(f"sweep beta {beta} line saliency {l}: TTFF cut strong {1 - ss / sn:+.0%} faint {1 - fs / fn:+.0%}")
qual_n = sum(1 for v in sweep.values() if v[0] > v[1])
ok = k_ok and qual and brk
print("RESULT:", "PASS" if ok else "FAIL",
      f"base l=0.4: TTFF strong none {R['strong none'][0]:.2f} ->subj {R['strong ->subj'][0]:.2f} ->empty {R['strong ->empty'][0]:.2f}; "
      f"faint none {R['faint none'][0]:.2f} ->subj {R['faint ->subj'][0]:.2f}; cut strong {cut_strong:+.0%} faint {cut_faint:+.0%}; "
      f"bright line strong {R['strong bright->subj'][0]:.2f}; sweep: strong cut l0.2 {sweep[(2,0.2)][0]:+.0%} l0.4 {sweep[(2,0.4)][0]:+.0%} l0.6 {sweep[(2,0.6)][0]:+.0%}, "
      f"faint cut {sweep[(2,0.2)][1]:+.0%}/{sweep[(2,0.4)][1]:+.0%}/{sweep[(2,0.6)][1]:+.0%}; qualifier holds in {qual_n}/9 settings; beta 1 vs 8 at l0.4 strong {sweep[(1,0.4)][0]:+.0%} vs {sweep[(8,0.4)][0]:+.0%}")
