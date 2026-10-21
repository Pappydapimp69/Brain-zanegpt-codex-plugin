"""Do the published non-uniform reverberation formulas (Fitzroy 1959, Arau-Puchades 1988)
settle Sabine-vs-Eyring in very dead or lumped-absorption rooms?

Self-contained: the diffuse-reflection (Lambertian) ray tracer below is copied
verbatim from the earlier sandbox 2026-10-12__eyring-and-sabine-bracket-reverberation-time.py
(stdlib only, random.Random(12345), 4000 rays, 1 ms bins, T60 from the -5..-35 dB slope).

Formulas checked first-hand in Prawda, Schlecht & Valimaki, "Evaluation of Reverberation
Time Models with Variable Acoustics", SMC 2020, pp.145-152:
  eq.(5) Fitzroy:       T60 = 0.161V/S^2 * sum_j [ -S_j / ln(1 - a_j) ],  j = x,y,z,
         S_j total area of the opposite parallel walls along the axis, a_j their mean absorption
  eq.(6) Arau-Puchades: T60 = prod_j [ 0.161V / (-S ln(1 - a_j) + 4mV) ]^(S_j/S)   (m = 0 here, no air)
  eq.(3) Millington-Sette: T60 = 0.161V / (-sum_i S_i ln(1 - a_i))   (extra column, for reference)
Run: python3 -I <this file>
"""
import math, random

C = 343.0
K = 24 * math.log(10) / C  # 0.1611

def sabine(V, S, a): return K * V / (S * a)
def eyring(V, S, a): return -K * V / (S * math.log(1 - a))

def surfaces(L):
    lx, ly, lz = L
    # (axis, side) -> area
    return {(0, 0): ly*lz, (0, 1): ly*lz, (1, 0): lx*lz, (1, 1): lx*lz, (2, 0): lx*ly, (2, 1): lx*ly}

def lambert(axis, side, rng):
    # cosine-weighted direction into the room from wall (axis, side)
    u1, u2 = rng.random(), rng.random()
    r, phi = math.sqrt(u1), 2 * math.pi * u2
    t1, t2, n = r * math.cos(phi), r * math.sin(phi), math.sqrt(1 - u1)
    d = [0.0, 0.0, 0.0]
    o = [i for i in range(3) if i != axis]
    d[o[0]], d[o[1]] = t1, t2
    d[axis] = n if side == 0 else -n
    return d

def trace(L, alpha, rays=4000, seed=12345, dt=0.001, floor_db=-45.0):
    rng = random.Random(seed)
    stop = 10 ** (floor_db / 10)
    # time horizon: generous, from the slowest plausible decay
    amin = min(alpha.values())
    V = L[0]*L[1]*L[2]; S = sum(surfaces(L).values())
    tmax = 1.6 * (-K * V / (S * math.log(1 - amin))) * (-floor_db) / 60 + 0.5
    nb = int(tmax / dt) + 2
    diff = [0.0] * (nb + 1)
    n1 = s1 = s2 = 0.0
    for _ in range(rays):
        p = [rng.random() * L[i] for i in range(3)]
        z = 2 * rng.random() - 1; ph = 2 * math.pi * rng.random(); s = math.sqrt(1 - z*z)
        d = [s * math.cos(ph), s * math.sin(ph), z]
        e, t, first = 1.0, 0.0, True
        diff[0] += 1.0
        while e > stop:
            best, ax, sd = 1e18, -1, -1
            for i in range(3):
                if d[i] > 1e-12:
                    ti, si = (L[i] - p[i]) / d[i], 1
                elif d[i] < -1e-12:
                    ti, si = -p[i] / d[i], 0
                else:
                    continue
                if ti < best: best, ax, sd = ti, i, si
            p = [p[i] + d[i] * best for i in range(3)]
            p[ax] = L[ax] if sd == 1 else 0.0
            t += best / C
            if not first: n1 += 1; s1 += best; s2 += best * best
            first = False
            k = int(t / dt)
            if k >= nb: break
            ne = e * (1 - alpha[(ax, sd)])
            diff[k] -= (e - ne)
            e = ne
            d = lambert(ax, sd, rng)
        # remaining energy is cut off at horizon (below fit range)
    E, acc = [], 0.0
    for k in range(nb):
        acc += diff[k]; E.append(acc)
    mfp = s1 / n1
    return fit_t60(E, rays, dt), mfp, (s2 / n1 - mfp * mfp) / (mfp * mfp)

def fit_t60(E, n, dt):
    xs, ys = [], []
    for k, v in enumerate(E):
        if v <= 0: break
        db = 10 * math.log10(v / n)
        if -35 <= db <= -5: xs.append(k * dt); ys.append(db)
    m = len(xs); mx = sum(xs) / m; my = sum(ys) / m
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return -60.0 / slope

def kuttruff(V, S, a, g2):
    la = math.log(1 - a)
    return -K * V / (S * la * (1 + g2 / 2 * la))


def axis_pairs(L, alpha):
    sa = surfaces(L); out = []
    for ax in range(3):
        Sj = sa[(ax, 0)] + sa[(ax, 1)]
        aj = (sa[(ax, 0)] * alpha[(ax, 0)] + sa[(ax, 1)] * alpha[(ax, 1)]) / Sj
        out.append((Sj, aj))
    return out

def fitzroy(V, S, pairs):
    return K * V / S**2 * sum(-Sj / math.log(1 - aj) for Sj, aj in pairs)

def arau(V, S, pairs):
    return math.exp(sum(Sj / S * math.log(K * V / (-S * math.log(1 - aj))) for Sj, aj in pairs))

def millington(V, sa, alpha):
    return K * V / (-sum(sa[k] * math.log(1 - alpha[k]) for k in sa))

def run(name, L, alpha):
    sa = surfaces(L); S = sum(sa.values()); V = L[0]*L[1]*L[2]
    a = sum(sa[k] * alpha[k] for k in sa) / S
    pr = axis_pairs(L, alpha)
    T, mfp, g2 = trace(L, alpha)
    est = dict(S=sabine(V, S, a), E=eyring(V, S, a), F=fitzroy(V, S, pr), AP=arau(V, S, pr),
               MS=millington(V, sa, alpha), K=kuttruff(V, S, a, g2))
    err = {k: (v - T) / T * 100 for k, v in est.items()}
    print(f"{name:34s} a={a:.3f} T={T:6.3f}s " + " ".join(f"{k} {err[k]:+6.1f}%" for k in ('S','E','F','AP','MS','K'))
          + f"  mfp={mfp/(4*V/S):.3f} g2={g2:.2f}")
    return dict(name=name, a=a, T=T, est=est, err=err, mfp=mfp / (4 * V / S))

def uni(x): return {k: x for k in surfaces((1, 1, 1))}
def faces(base, **over):
    keys = dict(x0=(0,0), x1=(0,1), y0=(1,0), y1=(1,1), z0=(2,0), z1=(2,1))
    d = {k: base for k in keys.values()}
    for n, v in over.items(): d[keys[n]] = v
    return d

print("Prior rooms (the five dead/lumped rooms of the open tension)")
prior = [run("shoebox 10x8x4 uniform 0.8", (10, 8, 4), uni(0.8)),
         run("small 6x5x3 uniform 0.7", (6, 5, 3), uni(0.7)),
         run("corridor 2x2x20 uniform 0.8", (2, 2, 20), uni(0.8)),
         run("flat hall 20x16x3 floor+ceil 0.8", (20, 16, 3), faces(0.02, z0=0.8, z1=0.8)),
         run("cube 6^3 one face 0.9", (6, 6, 6), faces(0.03, z0=0.9))]
print("Held-out rooms (chosen before the first run)")
held = [run("BREAK corridor 2x2x20 END walls 0.9", (2, 2, 20), faces(0.05, z0=0.9, z1=0.9)),
        run("shoebox 10x8x4 one side wall 0.9", (10, 8, 4), faces(0.05, y0=0.9)),
        run("flat hall 20x16x3 floor only 0.9", (20, 16, 3), faces(0.05, z0=0.9)),
        run("corridor 2x2x20 sides+floor+ceil 0.8", (2, 2, 20), faces(0.8, z0=0.02, z1=0.02))]
ALL = prior + held
uniform = prior[:3]
ident = max(max(abs(r['est'][k] - r['est']['E']) / r['est']['E'] for k in ('F', 'AP')) for r in uniform) * 100
print(f"uniform rooms: max |Fitzroy or Arau - Eyring| = {ident:.4f}% (algebraic identity)")
def wins(k): return sum(min(r['err'].items(), key=lambda kv: abs(kv[1]) if kv[0] in ('S','E','F','AP') else 1e9)[0] == k for r in ALL)
within = {k: sum(abs(r['err'][k]) <= 15 for r in ALL) for k in ('S', 'E', 'F', 'AP', 'MS')}
worst = {k: max(abs(r['err'][k]) for r in ALL) for k in ('S', 'E', 'F', 'AP', 'MS')}
for k in ('S', 'E', 'F', 'AP', 'MS'):
    print(f"{k:2s}: within 15% in {within[k]}/{len(ALL)} rooms, worst {worst[k]:.0f}%, closest-of-four in {wins(k)}")
mfp_ok = all(abs(r['mfp'] - 1) <= 0.03 for r in ALL)
settles = [k for k in ('F', 'AP') if within[k] == len(ALL)]
key = "; ".join(f"{r['name'].split(' ')[0] if not r['name'].startswith('BREAK') else 'BREAK'}:"
                f"S{r['err']['S']:+.0f}/E{r['err']['E']:+.0f}/F{r['err']['F']:+.0f}/AP{r['err']['AP']:+.0f}" for r in ALL)
if settles and mfp_ok:
    print(f"RESULT: PASS {'+'.join(settles)} within 15% in all {len(ALL)} dead/lumped rooms; {key}")
else:
    print(f"RESULT: FAIL F {within['F']}/{len(ALL)} AP {within['AP']}/{len(ALL)} within 15% (S {within['S']}, E {within['E']}); "
          f"uniform F=AP=E to {ident:.3f}%; mfp_ok={mfp_ok}; {key}")
