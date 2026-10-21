# Sandbox: a cosmetic sin() branch that never feeds a state VALUE still forks a seeded run
# across runtimes when (a) its argument sits on a designer angle where sin hits the
# threshold exactly (sin 30 deg = 0.5) and (b) the branch consumes a draw from the shared
# seeded stream. Composes: seeded-rng kernel (one stream, state words in the save),
# sandbox-seeded-rng-state-words/E1 (state-word reload exact, shared-stream insertion
# shifts later rolls) and transcendental-drift-forks-only-when-it-feeds-state/E1
# (branch-only sim never forked in 100k steps). Stdlib, deterministic.
import math, hashlib

M = 0xFFFFFFFF
class SFC32:
    def __init__(self, seed):
        self.s = [seed & M, (seed * 0x9E3779B9) & M, (seed ^ 0xDEADBEEF) & M, 1]
        for _ in range(12):
            self.next()
    def next(self):
        a, b, c, d = self.s
        t = (a + b + d) & M
        d = (d + 1) & M
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & M
        c = ((c << 21) | (c >> 11)) & M
        c = (c + t) & M
        self.s = [a, b, c, d]
        return t
    def words(self):
        return list(self.s)
    @classmethod
    def from_words(cls, w):
        r = cls.__new__(cls); r.s = list(w); return r

def sin_libm(x):
    return math.sin(x)

def sin_taylor(x):  # a second engine's sin: fmod range reduction + Taylor series
    x = math.fmod(x, 2 * math.pi)
    if x > math.pi:
        x -= 2 * math.pi
    s, term, n = 0.0, x, 1
    for _ in range(12):
        s += term
        term *= -x * x / ((n + 1) * (n + 2))
        n += 2
    return s

T = 3600
SEEDS = [11, 23, 37, 41, 59, 61, 73, 89]

def angle_designer(t):
    return math.radians(30 * t)          # spinner advances 30 degrees per tick

def angle_continuous(t):
    return t * 1.2345678901              # generic angle, no exact special values

def run(seed, sin_fn, angle_fn, split, start=None, t0=0, t1=T, trace=False):
    if start is None:
        game = SFC32(seed); cos_rng = SFC32(seed ^ 0x5151) if split else game
        hp, kills = 50, 0
    else:
        gw, cw, hp, kills = start
        game = SFC32.from_words(gw); cos_rng = SFC32.from_words(cw) if split else game
    fps, sparkle_ticks = [], []
    for t in range(t0, t1):
        # presentation: sparkle when the spinner points high enough; jitter is a draw
        if sin_fn(angle_fn(t)) >= 0.5:
            cos_rng.next(); sparkle_ticks.append(t)
        # authoritative: one combat roll per tick
        roll = game.next() % 20 + 1
        if roll >= 15:
            hp -= roll
            if hp <= 0:
                kills += 1; hp = 50
        if trace:
            fps.append((hp, kills, tuple(game.words())))
    snap = (game.words(), cos_rng.words(), hp, kills)
    return hp, kills, sparkle_ticks, fps, snap

def first_diff(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None

res = {}
# S1 designer angles, shared stream, libm vs taylor
forks = 0; flip_counts = []; first_flips = []
for s in SEEDS:
    ha, ka, spa, _, _ = run(s, sin_libm, angle_designer, split=False)
    hb, kb, spb, _, _ = run(s, sin_taylor, angle_designer, split=False)
    flips = len(set(spa) ^ set(spb)); flip_counts.append(flips)
    first_flips.append(min(set(spa) ^ set(spb)) if flips else None)
    forks += (ha, ka) != (hb, kb)
res["S1"] = forks
print("S1 designer angles, shared stream: gameplay forked %d/%d seeds; sparkle decisions differing %s of %d ticks; first flip tick %s"
      % (forks, len(SEEDS), flip_counts[0], T, first_flips[0]))

# S2 designer angles, cosmetic draws on their own stream
forks2 = 0
for s in SEEDS:
    ha, ka, *_ = run(s, sin_libm, angle_designer, split=True)
    hb, kb, *_ = run(s, sin_taylor, angle_designer, split=True)
    forks2 += (ha, ka) != (hb, kb)
res["S2"] = forks2
print("S2 designer angles, split cosmetic stream: gameplay forked %d/%d" % (forks2, len(SEEDS)))

# S3 generic continuous angles, shared stream (the transcendental entry's branch-only case)
forks3 = 0; flips3 = 0
for s in SEEDS:
    ha, ka, spa, _, _ = run(s, sin_libm, angle_continuous, split=False)
    hb, kb, spb, _, _ = run(s, sin_taylor, angle_continuous, split=False)
    flips3 += len(set(spa) ^ set(spb)); forks3 += (ha, ka) != (hb, kb)
res["S3"] = forks3
print("S3 generic angles, shared stream: gameplay forked %d/%d, sparkle flips total %d over %d ticks"
      % (forks3, len(SEEDS), flips3, T * len(SEEDS)))

# S4 one runtime only: libm alone sparkles at 390 deg but not at 30 deg (period broken)
same_runtime_period = [(d, sin_libm(math.radians(d)) >= 0.5) for d in (30, 390, 750, 870, 1110)]
print("S4 libm alone, threshold at 30/390/750/870/1110 deg:", same_runtime_period)

# S5 BREAK attempt on the state-words save: save at tick 1000 on libm, load on taylor.
s = SEEDS[0]
_, _, _, fa, snap = run(s, sin_libm, angle_designer, split=False, t1=1000)
_, _, _, fa_rest, _ = run(s, sin_libm, angle_designer, split=False, start=snap[0:1] + snap[0:1] + snap[2:], t0=1000, trace=True)
_, _, spb_rest, fb_rest, _ = run(s, sin_taylor, angle_designer, split=False, start=snap[0:1] + snap[0:1] + snap[2:], t0=1000, trace=True)
_, _, spa_rest, _, _ = run(s, sin_libm, angle_designer, split=False, start=snap[0:1] + snap[0:1] + snap[2:], t0=1000)
_, _, _, fa_same, _ = run(s, sin_libm, angle_designer, split=False, start=snap[0:1] + snap[0:1] + snap[2:], t0=1000, trace=True)
reload_exact = fa_same == fa_rest
flip_after = min(set(spa_rest) ^ set(spb_rest)) if set(spa_rest) ^ set(spb_rest) else None
d_full = first_diff([f for f in fa_rest], [f for f in fb_rest])
d_game = first_diff([f[:2] for f in fa_rest], [f[:2] for f in fb_rest])
print("S5 save at 1000 on libm: same-runtime reload exact %s; cross-runtime first sparkle flip tick %s; full fingerprint (with state words) differs at tick %s; hp/kills-only fingerprint differs at tick %s"
      % (reload_exact, flip_after, None if d_full is None else 1000 + d_full, None if d_game is None else 1000 + d_game))

lags = []
for sd in SEEDS:
    _, _, _, _, sn = run(sd, sin_libm, angle_designer, split=False, t1=1000)
    st = sn[0:1] + sn[0:1] + sn[2:]
    _, _, _, xa, _ = run(sd, sin_libm, angle_designer, split=False, start=st, t0=1000, trace=True)
    _, _, _, xb, _ = run(sd, sin_taylor, angle_designer, split=False, start=st, t0=1000, trace=True)
    lf = first_diff(xa, xb); lg = first_diff([f[:2] for f in xa], [f[:2] for f in xb])
    lags.append((lg - lf) if lf is not None and lg is not None else None)
print("S5b hp/kills-only detection lag behind state-word fingerprint, per seed (ticks):", lags)
ok = (res["S1"] >= 7 and res["S2"] == 0 and res["S3"] == 0 and reload_exact
      and d_full is not None and d_game is not None and d_full <= d_game)
print("RESULT: %s designer-angle cosmetic branch forked gameplay %d/8 via shared stream (split 0/8, generic angles %d/8); state-word reload exact %s, cross-runtime fork seen by state-word fingerprint at tick %s vs hp-only at %s"
      % ("PASS" if ok else "FAIL", res["S1"], res["S3"], reload_exact,
         None if d_full is None else 1000 + d_full, None if d_game is None else 1000 + d_game))
