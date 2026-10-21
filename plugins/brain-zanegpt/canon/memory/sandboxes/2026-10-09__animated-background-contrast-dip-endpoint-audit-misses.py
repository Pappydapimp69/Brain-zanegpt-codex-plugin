#!/usr/bin/env python3
"""Sandbox: do dog#E104 (role-against-background tokens, measured pairs) and
sandbox-cvd-transition-audit#E1 (sample the TRAJECTORY, not the endpoints) compose
when a background ANIMATES (dog#E10 1-pow follow, a day/night sky ease)?

PREDICTION (written before the first run):
  P1. Day->night sky ease with a role-token swap at the half-way point: both endpoint
      pairs measure >= 7:1, but the dense-trajectory minimum contrast is < 3.0:1.
  P2. Choosing the better of the two role tokens PER FRAME (luminance-based) does NOT
      rescue it: the dense minimum lands between 3.5 and 4.5 (below WCAG AA 4.5)
      with near-white #f5f5f5 / near-black #141414 tokens.
  P3. A fixed scrim behind the text keeps contrast equal to its endpoint value
      (>= 7:1) for every point of the trajectory.
  P4. The 1-pow follow moves every channel by the same scalar, so the colour PATH is
      identical at any frame rate; frame-sampled minima are a subset of it. At 144 fps
      the frame-sampled minimum is within 0.05 of the dense minimum, while at a fast
      ease (base 1e-6/s) at 15 fps it overstates the minimum by more than 0.3.
  P5. CVD: on a day/dusk/night sky vs three third-entity colours, at least one
      transition is flagged (trajectory deutan-distance < 25% of the nearer
      endpoint distance and < 0.05 absolute, at luminance ratio < 1.5).
  BREAK scenario: S4 (scrim) and S6 (control pair with no hazard) are built to break
  the claim that every animated background is hazardous.
Deterministic, stdlib only, no RNG, no real timing.
"""
import math

# ---------- colour maths ----------
def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def lum(rgb):
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

# Vienot-Brettel-Mollon 1999 deuteranope matrix (linear RGB; rows sum to 1)
DEUTAN = ((0.29275, 0.70725, 0.0), (0.29275, 0.70725, 0.0), (-0.02234, 0.02234, 1.0))

def deutan(rgb):
    l = [lin(c) for c in rgb]
    return tuple(sum(DEUTAN[i][j] * l[j] for j in range(3)) for i in range(3))

def ddist(a, b):
    da, db = deutan(a), deutan(b)
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(da, db)))

def mix(a, b, s):  # lerp in sRGB gamma space (how a canvas/CSS/three colour lerp behaves)
    return tuple(x + (y - x) * s for x, y in zip(a, b))

def smooth(t):
    return t * t * (3 - 2 * t)

DENSE = [i / 4000.0 for i in range(4001)]

NIGHT = hex2rgb('#0c1428')
DAY = hex2rgb('#9ccbf0')
LIGHT_TXT = hex2rgb('#f5f5f5')   # role: text on dark glass (dog#E104)
DARK_TXT = hex2rgb('#141414')    # role: text on cream/light surface

def swap_token(s, bg_is_day_side_after):
    return DARK_TXT if s >= 0.5 else LIGHT_TXT

results = {}

# ---------- S1: endpoint-safe role tokens, time-based swap at s=0.5 ----------
end_night = contrast(LIGHT_TXT, NIGHT)
end_day = contrast(DARK_TXT, DAY)
c1 = [contrast(LIGHT_TXT if s < 0.5 else DARK_TXT, mix(NIGHT, DAY, smooth(s))) for s in DENSE]
s1_min = min(c1)
print(f"S1 endpoints: night {end_night:.2f}:1, day {end_day:.2f}:1; dense trajectory min with half-way swap {s1_min:.2f}:1")
results['P1'] = end_night >= 7 and end_day >= 7 and s1_min < 3.0

# ---------- S2: per-frame best-of-two token ----------
c2 = [max(contrast(LIGHT_TXT, mix(NIGHT, DAY, smooth(s))), contrast(DARK_TXT, mix(NIGHT, DAY, smooth(s)))) for s in DENSE]
s2_min = min(c2)
print(f"S2 per-frame best-of-two token: dense min {s2_min:.2f}:1 (AA body text needs 4.5)")
results['P2'] = 3.5 <= s2_min < 4.5

# ---------- S3: pure black/white tokens, theoretical best-of-two ceiling ----------
c3 = [max(contrast((1, 1, 1), mix(NIGHT, DAY, smooth(s))), contrast((0, 0, 0), mix(NIGHT, DAY, smooth(s)))) for s in DENSE]
print(f"S3 pure black/white best-of-two on same ease (ceiling for any pair): dense min {min(c3):.2f}:1")

# ---------- S4 (BREAK): fixed scrim behind text ----------
SCRIM = hex2rgb('#101820')
c4 = [contrast(LIGHT_TXT, SCRIM) for s in DENSE]  # scrim is not animated -> text/scrim pair constant
s4_min = min(c4)
print(f"S4 scrim (background of the TEXT does not animate): min {s4_min:.2f}:1 over the same sky ease")
results['P3'] = s4_min >= 7 and abs(max(c4) - min(c4)) < 1e-9

# ---------- S5: dog#E10 1-pow follow at several frame rates ----------
def follow_frames(fps, base, seconds=6.0):
    """Return list of scalar s per frame for x += (1-x)*(1-base**dt), starting at 0 (dog#E10 form)."""
    dt = 1.0 / fps
    x, out = 0.0, []
    for _ in range(int(seconds * fps)):
        x += (1.0 - x) * (1.0 - base ** dt)
        out.append(x)
    return out

def frame_min(fps, base):
    vals = []
    for s in follow_frames(fps, base):
        # same time-based swap rule as S1 (swap when the eased scalar passes 0.5), NO extra smoothstep
        bg = mix(NIGHT, DAY, s)
        vals.append(contrast(LIGHT_TXT if s < 0.5 else DARK_TXT, bg))
    return min(vals)

# dense path minimum for the same (no smoothstep) rule
dense_vals = [contrast(LIGHT_TXT if s < 0.5 else DARK_TXT, mix(NIGHT, DAY, s)) for s in DENSE]
dense_min = min(dense_vals)
print(f"S5 dense path min (follow path is dt-independent): {dense_min:.2f}:1")
rows = {}
for base in (0.05, 1e-6):
    for fps in (15, 30, 60, 144):
        rows[(base, fps)] = frame_min(fps, base)
        print(f"   base {base:g}/s  fps {fps:>3}: frame-sampled min {rows[(base, fps)]:.2f}:1  (overstates dense by {rows[(base, fps)] - dense_min:+.2f})")
# S5 also: the path itself is identical across fps (all samples lie on the same line)
results['P4a'] = abs(rows[(0.05, 144)] - dense_min) <= 0.05
results['P4b'] = (rows[(1e-6, 15)] - dense_min) > 0.3

# ---------- S6: CVD trajectory vs third entity (sandbox-cvd-transition-audit#E1 method) ----------
sky = {'day': hex2rgb('#8fc1e8'), 'dusk': hex2rgb('#d9774a'), 'night': hex2rgb('#0b1230')}
third = {'dog-fur': hex2rgb('#8a6a4a'), 'grass': hex2rgb('#5c8a52'), 'vent-glow': hex2rgb('#e8a04a')}
flags = []
for a in sky:
    for b in sky:
        if a == b:
            continue
        for tn, tc in third.items():
            d_end = min(ddist(sky[a], tc), ddist(sky[b], tc))
            best = (9.0, None, None)
            for s in DENSE[::20]:
                col = mix(sky[a], sky[b], smooth(s))
                d = ddist(col, tc)
                if d < best[0]:
                    best = (d, s, col)
            lr = (max(lum(best[2]), lum(tc)) + 0.05) / (min(lum(best[2]), lum(tc)) + 0.05)
            hazard = best[0] < 0.25 * d_end and best[0] < 0.05 and lr < 1.5
            if hazard:
                flags.append((a, b, tn, d_end, best[0], best[1], lr))
for f in flags:
    print(f"S6 FLAG {f[0]}->{f[1]} vs {f[2]}: endpoint min deutan-dist {f[3]:.3f}, trajectory min {f[4]:.4f} at s={f[5]:.2f}, lum ratio {f[6]:.2f}")
print(f"S6 flagged transitions: {len(flags)} of {len(sky) * (len(sky) - 1) * len(third)}")
results['P5'] = len(flags) >= 1

# ---------- S7 (BREAK / control): a transition with no hazard ----------
ctrl = []
for tn, tc in third.items():
    d_end = min(ddist(sky['night'], tc), ddist(sky['day'], tc))
    m = min(ddist(mix(sky['night'], sky['day'], smooth(s)), tc) for s in DENSE[::20])
    ctrl.append((tn, d_end, m))
print("S7 control night->day: " + "; ".join(f"{t}: end {e:.3f} traj {m:.3f}" for t, e, m in ctrl))
ctrl_clear = all(m >= 0.25 * e or m >= 0.05 for _, e, m in ctrl)

print("predictions:", {k: bool(v) for k, v in results.items()}, "control_clear:", ctrl_clear)
ok = all(results.values())
if ok:
    print(f"RESULT: PASS endpoints {end_night:.1f}/{end_day:.1f}:1 but trajectory min {s1_min:.2f}:1 (swap), {s2_min:.2f}:1 (best-of-two), scrim {s4_min:.1f}:1; {len(flags)} CVD flag(s)")
else:
    bad = [k for k, v in results.items() if not v]
    print(f"RESULT: FAIL predictions refuted: {bad}; s1 {s1_min:.2f}, s2 {s2_min:.2f}, scrim {s4_min:.1f}, flags {len(flags)}, 144fps/15fps rows {rows[(0.05,144)]:.2f}/{rows[(1e-6,15)]:.2f} vs dense {dense_min:.2f}")
