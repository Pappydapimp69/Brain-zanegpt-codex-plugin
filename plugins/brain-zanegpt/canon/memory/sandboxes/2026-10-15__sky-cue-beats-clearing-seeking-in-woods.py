"""Lost in woods, finding a friend by whistle. Two strategies under heading noise (no sun):
HOME: whistle, turn to the answer, walk a leg, repeat; with no answer, walk on blind for 80 m.
CLEARING: the same, but with no answer, first head for the nearest unvisited clearing, then whistle.
Sound: 100 dB at 1 m, -20log10(d), -1 dB/100 m air, -att dB/100 m inside forest; heard if above 20 dB.
Deterministic (seeded), stdlib only. Mirrors the Veer game's model."""
import math, random
SPEED, TURN, NOISE, DT = 3.6, 1.6, .22, 1 / 15
def world(kind):
    if kind == 'deep':   # dense woods; friend in a clearing 520 m away, a big clearing on the way
        return dict(size=800, att=23, clear=[(400, 430, 115), (560, 200, 70)], start=(400, 730), friend=(560, 200), limit=420)
    if kind == 'near':   # same woods, friend only 130 m away: already in earshot
        return dict(size=800, att=23, clear=[(400, 430, 115), (560, 200, 70)], start=(400, 730), friend=(470, 620), limit=420)
    if kind == 'open':   # open ground: everyone hears everyone (BREAK case: clearings cannot help)
        return dict(size=800, att=0, clear=[(400, 430, 115)], start=(400, 730), friend=(560, 200), limit=420)
def att_at(w, x, y):
    if not (0 <= x <= w['size'] and 0 <= y <= w['size']): return 30
    return 0 if any(math.hypot(x - cx, y - cy) < r for cx, cy, r in w['clear']) else w['att']
def level(w, a, b):
    d = max(1, math.dist(a, b)); n = max(1, math.ceil(d / 5)); f = 0
    for k in range(n):
        q = (k + .5) / n; f += att_at(w, a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q) * (d / n) / 100
    return 100 - 20 * math.log10(d) - d / 100 - f
def run(w, policy, seed, noise=NOISE):
    r = random.Random(seed); x, y = w['start']; th = -math.pi / 2; t = 0.0
    tried = set(); fx, fy = w['friend']
    while t < w['limit']:
        # whistle and wait for the answer (round trip plus reaction)
        L = level(w, (x, y), (fx, fy)); t += 1.5
        if L > 20:
            rel = math.atan2(fy - y, fx - x) - th; q = min(1, (L - 20) / 30); width = .18 + (1 - q) * 1.1
            target = th + rel + (r.random() - .5) * width; leg = 30 + (1 - q) * 110
        else:
            t += 5; target, leg = th, 80
            if policy == 'clearing' and att_at(w, x, y) > 0:
                opts = [(math.hypot(cx - x, cy - y), (cx, cy)) for cx, cy, cr in w['clear'] if (cx, cy) not in tried and math.hypot(cx - x, cy - y) > cr * .6]
                if opts:
                    d, c = min(opts); tried.add(c); target = th + math.atan2(c[1] - y, c[0] - x) - th; leg = d
        th = target   # turning is exact; drift only accrues while walking
        gone = 0
        while gone < leg and t < w['limit']:
            th += noise * math.sqrt(DT) * r.gauss(0, 1)
            nx, ny = x + math.cos(th) * SPEED * DT, y + math.sin(th) * SPEED * DT
            if 4 < nx < w['size'] - 4 and 4 < ny < w['size'] - 4: x, y = nx, ny
            else: th += 1.2
            gone += SPEED * DT; t += DT
            if math.hypot(fx - x, fy - y) < 9: return t
            # a call from the friend every 22 s re-aims a walker who can hear it
            if int(t / 22) != int((t - DT) / 22) and level(w, (fx, fy), (x, y)) > 20: break
    return None
N = 40
res = {}
for kind, noise in (('deep', NOISE), ('deep', 0.0), ('near', NOISE), ('open', NOISE)):
    w = world(kind); key = kind + ('-sun' if noise == 0 else ''); res[key] = {}
    for pol in ('home', 'clearing'):
        times = [run(w, pol, s, noise) for s in range(N)]; ok = [t for t in times if t is not None]
        res[key][pol] = (len(ok), sorted(ok)[len(ok) // 2] if ok else None)
        print(f"{key:9s} {pol:8s} found {len(ok):2d}/{N}  median {res[key][pol][1] and round(res[key][pol][1])} s")
fog_gain = res['deep']['clearing'][0] - res['deep']['home'][0]
sky_gain = res['deep-sun']['home'][0] - res['deep']['home'][0]
same = res['near']['clearing'] == res['near']['home'] and res['open']['clearing'] == res['open']['home']
ok = sky_gain >= 15 and fog_gain <= 5 and same
print(f"RESULT: {'PASS' if ok else 'FAIL'} out of earshot in deep woods a sky cue lifts homing from {res['deep']['home'][0]}/{N} to {res['deep-sun']['home'][0]}/{N}, while seeking a clearing first adds only {fog_gain}/{N} under drift (and none in earshot or in the open)")
