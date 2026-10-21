"""Blind rebuild: aperiodic primary B + periodic residue-subset fallback A.

PREDICTION (written before first run, never edited):
  1. Cutoff cross-check: direct simulation cutoff == largest legal lag (bitmask) in every case; 0 mismatches.
  2. Per-press loss, T>=300: the largest-configured-lag shortcut has ZERO failures for every non-empty
     R subset of Z_m (m=4,5,7,9) for every primary (squares, primes, triangular, Beatty sqrt2, Thue-Morse,
     Fibonacci word, seeded randoms, powers of two), because non-B ticks are plentiful and one residue
     r gives a press t = r-L mod m that is legal at the max lag.
  3. Empty fallback: failures > 0 overall (sparse primaries like squares/powers-of-two/primes fail;
     dense ones like Thue-Morse / random(0.8) may have zero failures since B->B pairs exist at every lag).
  4. Failures non-increasing in |R| (rate per subset), and exactly monotone under nested R subset R'.
  5. Coverage-loss reading is DIFFERENT: the largest lag's landings are often covered by shorter lags,
     so the shortcut under coverage loss fails frequently, including for non-empty R (esp. full R) -> the
     "single residue suffices" statement is about per-press loss only, not coverage.
  6. Tiny horizon T=8 breaks 'single residue suffices' (some |R|=1 failures; presses cannot reach lag-L landings).
"""
import itertools, math, random, sys, time
from collections import defaultdict

t0 = time.time()
NTICK = 2000
LAGMAX = 12
LAGS = list(range(1, LAGMAX + 1))
LAGSETS = list(itertools.combinations(LAGS, 3))

def from_pred(pred):
    return bytearray(1 if pred(t) else 0 for t in range(NTICK))

def is_square(n):
    r = math.isqrt(n); return r * r == n
def is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True
def is_tri(n):
    # n = k(k+1)/2
    d = 8 * n + 1; r = math.isqrt(d); return r * r == d
def beatty(n_max, a):
    s = set()
    k = 1
    while True:
        v = math.isqrt(k * k * 2) if a == 2 else int(k * a)
        if v >= n_max: break
        s.add(v); k += 1
    return s
phi = (1 + 5 ** 0.5) / 2
def fibword(t):
    return (math.floor((t + 2) / phi) - math.floor((t + 1) / phi)) == 1
rng1 = random.Random(20261008); rnd35 = {t for t in range(NTICK) if rng1.random() < 0.35}
rng2 = random.Random(77); rnd80 = {t for t in range(NTICK) if rng2.random() < 0.80}
bt = beatty(NTICK, 2)
PRIMARIES = {
    'squares': from_pred(is_square),
    'primes': from_pred(is_prime),
    'triangular': from_pred(is_tri),
    'beatty_sqrt2': from_pred(lambda t: t in bt),
    'thue_morse': from_pred(lambda t: bin(t).count('1') % 2 == 1),
    'fibword': from_pred(fibword),
    'rand35': from_pred(lambda t: t in rnd35),
    'rand80': from_pred(lambda t: t in rnd80),
    'pow2': from_pred(lambda t: t >= 1 and (t & (t - 1)) == 0),
}

def assert_aperiodic(name, B, T):
    for p in range(1, 61):
        if all(B[t] == B[t + p] for t in range(T - p)):
            raise AssertionError(f'{name} periodic with p={p} over T={T}')
for T in (300, 700):
    for name, B in PRIMARIES.items():
        assert_aperiodic(name, B, T)
        assert sum(B[:T]) > 3, name

def amask_bytes(m, R):
    return bytearray(1 if (t % m) in R else 0 for t in range(NTICK))

# ---------- implementation 1: direct simulation ----------
def sim_per_lag(B, A, T):
    cnt = {}; land = {}
    for L in LAGS:
        c = 0; s = set()
        for t in range(T):
            u = t + L
            if (B[u] if B[t] else A[u]):
                c += 1; s.add(u)
        cnt[L] = c; land[L] = s
    return cnt, land

def sim_cutoffs(cnt, land, Ls):
    maxL = max(Ls)
    pp = None
    for c in range(0, maxL + 1):
        if sum(cnt[L] for L in Ls if L > c) == 0:
            pp = c; break
    union = set()
    for L in Ls: union |= land[L]
    cov = None
    for c in range(0, maxL + 1):
        cur = set()
        for L in Ls:
            if L <= c: cur |= land[L]
        if cur == union:
            cov = c; break
    return pp, cov

# ---------- implementation 2: bitmask set arithmetic ----------
def bits(bs):
    v = 0
    for i, x in enumerate(bs):
        if x: v |= 1 << i
    return v

def mask_per_lag(Bm, Am, T):
    full = (1 << T) - 1
    Pb = Bm & full; Pn = ~Bm & full
    return {L: ((Pb << L) & Bm) | ((Pn << L) & Am) for L in LAGS}

def mask_cutoffs(masks, Ls):
    ls = sorted(Ls)
    nz = [L for L in ls if masks[L]]
    pp = max(nz) if nz else 0
    total = 0
    for L in ls: total |= masks[L]
    cov = 0
    if total:
        cur = 0
        for L in ls:
            cur |= masks[L]
            if cur == total: cov = L; break
    return pp, cov

def subsets(m):
    for k in range(m + 1):
        for R in itertools.combinations(range(m), k):
            yield frozenset(R)

def run(T, moduli, primaries):
    """returns stats[(pname,m)][k] = [n_cfg, pp_fail, cov_fail]; mismatch counts; nested violations."""
    stats = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    mism = 0; nest_pp = 0; nest_cov = 0; ncases = 0
    firstfail = {}
    for pname in primaries:
        B = PRIMARIES[pname]; Bm = bits(B)
        for m in moduli:
            failbits_pp = {}; failbits_cov = {}
            for R in subsets(m):
                A = amask_bytes(m, R); Am = bits(A)
                cnt, land = sim_per_lag(B, A, T)
                masks = mask_per_lag(Bm, Am, T)
                for L in LAGS:  # consistency of the two legal sets
                    assert cnt[L] == bin(masks[L]).count('1')
                    assert land[L] == {i for i in range(NTICK) if masks[L] >> i & 1}
                fp = 0; fc = 0
                for idx, Ls in enumerate(LAGSETS):
                    ppS, covS = sim_cutoffs(cnt, land, Ls)
                    ppM, covM = mask_cutoffs(masks, Ls)
                    ncases += 1
                    if ppS != ppM or covS != covM: mism += 1
                    # also cutoff == largest legal lag
                    legal = [L for L in Ls if cnt[L] > 0]
                    if ppS != (max(legal) if legal else 0): mism += 1
                    st = stats[(pname, m)][len(R)]
                    st[0] += 1
                    if ppS != max(Ls):
                        st[1] += 1; fp |= 1 << idx
                        if len(R) >= 1 and (pname, m) not in firstfail:
                            firstfail[(pname, m)] = (sorted(R), Ls)
                    if covS != max(Ls):
                        st[2] += 1; fc |= 1 << idx
                failbits_pp[R] = fp; failbits_cov[R] = fc
            for R, fp in failbits_pp.items():
                for x in range(m):
                    if x not in R:
                        R2 = R | {x}
                        if failbits_pp[R2] & ~fp: nest_pp += 1
                        if failbits_cov[R2] & ~failbits_cov[R]: nest_cov += 1
    return stats, mism, nest_pp, nest_cov, ncases, firstfail

def rates_by_k(stats, keys, m):
    out = []
    for k in range(m + 1):
        n = sum(stats[key][k][0] for key in keys); f = sum(stats[key][k][1] for key in keys)
        c = sum(stats[key][k][2] for key in keys)
        out.append((k, n, f, c))
    return out

MODULI = (4, 5, 7, 9)
verdicts = []
tot_mism = 0; big_nonempty_pp = 0; empty_fail_ok = True; mono_ok = True; nest_viol = 0
summary_bits = []
cov_nonempty_big = 0
for T in (300, 700):
    stats, mism, nest_pp, nest_cov, ncases, firstfail = run(T, MODULI, list(PRIMARIES))
    tot_mism += mism; nest_viol += nest_pp
    print(f'\n=== T={T}: cases={ncases} cutoff_mismatches={mism} nested_violations per-press={nest_pp} coverage={nest_cov}')
    for m in MODULI:
        keys = [(p, m) for p in PRIMARIES]
        rb = rates_by_k(stats, keys, m)
        line = ' '.join(f'|R|={k}:pp={f}/{n}({f/n:.3f}),cov={c}/{n}({c/n:.3f})' for k, n, f, c in rb)
        print(f' m={m} (all primaries) {line}')
        rates = [f / n for k, n, f, c in rb]
        if any(rates[i + 1] > rates[i] + 1e-12 for i in range(m)): mono_ok = False
        big_nonempty_pp += sum(f for k, n, f, c in rb if k >= 1)
        cov_nonempty_big += sum(c for k, n, f, c in rb if k >= 1)
        if rb[0][2] == 0: empty_fail_ok = False
    print(' per primary: empty-fallback pp failures (of 220 lag sets) | nonempty pp failures | coverage failures by |R| (m=7)')
    for p in PRIMARIES:
        e = [stats[(p, m)][0][1] for m in MODULI]
        ne = [sum(stats[(p, m)][k][1] for k in range(1, m + 1)) for m in MODULI]
        cv7 = [stats[(p, 7)][k][2] / stats[(p, 7)][k][0] for k in range(8)]
        print(f'  {p:13s} empty={e} nonempty={ne} cov_rate_m7_by_|R|=' + ','.join(f'{x:.2f}' for x in cv7))
        pe = [m for m in MODULI if stats[(p, m)][0][1] == 0]
    print(f'   [{time.time()-t0:.0f}s]')

# empty fallback per-primary summary
print('\nprimaries with ZERO empty-fallback failures are dense (B->B pair at every lag); see per-primary table above')

# ---------- tiny horizons ----------
print('\n=== tiny/short horizons (aperiodicity assertion not applicable): per-press failures at |R|>=1, all primaries')
tiny_break = {}
for T in (8, 12, 20, 40):
    stats, mism, nest_pp, nest_cov, ncases, firstfail = run(T, MODULI, list(PRIMARIES))
    tot_mism += mism; nest_viol += nest_pp
    row = []
    for m in MODULI:
        keys = [(p, m) for p in PRIMARIES]
        rb = rates_by_k(stats, keys, m)
        row.append(f'm={m}: ' + ','.join(f'k{k}={f}' for k, n, f, c in rb))
    tiny_break[T] = sum(stats[(p, m)][k][1] for p in PRIMARIES for m in MODULI for k in range(1, m + 1) if k == 1)
    print(f' T={T}: mism={mism} nested={nest_pp} |R|=1 pp failures total={tiny_break[T]}; ' + ' | '.join(row))
    if T == 8:
        ff = {k: v for k, v in firstfail.items()}
        for k, v in list(ff.items())[:6]: print('   first nonempty failure', k, 'R=', v[0], 'lags=', v[1])

ok = (tot_mism == 0 and big_nonempty_pp == 0 and empty_fail_ok and mono_ok and nest_viol == 0 and tiny_break[8] > 0)
print(f'\nruntime {time.time()-t0:.0f}s; coverage failures at T>=300 with nonempty R: {cov_nonempty_big}')
print(f"RESULT: {'PASS' if ok else 'FAIL'} cutoff_mismatches={tot_mism} nonempty_pp_failures_T>=300={big_nonempty_pp} "
      f"empty_has_failures={empty_fail_ok} rate_monotone={mono_ok} nested_violations={nest_viol} "
      f"T8_|R|=1_failures={tiny_break[8]} coverage_failures_nonempty_T>=300={cov_nonempty_big}")
