"""Blind rebuild: emptiness-only guard for the largest configured lag: exact under per-press loss, fails under landing-coverage loss, moduli 4/6/12.
MY MODEL (own fixture): press tick t in [0,T), lag L in set S, landing x=t+L. Hint: role B if t in P (aperiodic primary) else role A.
Legal iff hinted role is available at landing: B available iff x in P; A available iff x mod m in F (fallback residues).
Per-press loss: cutoff = largest L in S with some legal press; coverage loss: cutoff = smallest c such that lags <= c serve every landing tick that S serves.
Prediction (before run): per-press failures of 'cutoff == max S' = 0 for every non-empty fallback; coverage failures > 0 for non-empty fallbacks,
between 5% and 40% of non-empty cases; some empty-fallback per-press failures > 0 on at least one primary; coverage rule (largest lag adding an unserved landing) == brute-force smallest c in all cases."""
import itertools
T, LAGS, K = 240, range(1, 11), 4
def fam():
    N = T + 20
    primes = {n for n in range(2, N) if all(n % d for d in range(2, int(n ** .5) + 1))}
    tri = {k * (k + 1) // 2 for k in range(1, 40)}
    fib = {1, 2}; a, b = 1, 2
    while b < N: a, b = b, a + b; fib.add(b)
    tm = {n for n in range(N) if bin(n).count("1") % 2 == 1}
    return {"primes": primes, "triangular": tri, "fibonacci": fib, "thue-morse": tm}
def served(S, P, m, F):
    """landing tick -> served by lags, per lag"""
    by_lag = {}
    for L in S:
        xs = set()
        for t in range(T):
            x = t + L
            legal = (x in P) if t in P else ((x % m) in F)
            if legal: xs.add(x)
        by_lag[L] = xs
    return by_lag
def residue_fallbacks(m):
    yield ()
    for r in range(m): yield (r,)
    for p in itertools.combinations(range(m), 2): yield p
stats = {"ne": 0, "pp_ne": 0, "cov_ne": 0, "emp": 0, "pp_emp": 0, "cov_emp": 0, "rule_mism": 0}
for pname, P in fam().items():
    for m in (4, 6, 12):
        for F in residue_fallbacks(m):
            Fs = set(F)
            for S in itertools.combinations(LAGS, K):
                S = sorted(S); mx = S[-1]
                by = served(S, P, m, Fs)
                largest_legal = max([L for L in S if by[L]], default=0)
                union = set().union(*by.values())
                c_brute = next((c for c in S if set().union(*[by[L] for L in S if L <= c]) == union), 0) if union else 0
                seen, c_rule = set(), 0
                for L in S:
                    if not by[L] <= seen: c_rule = L
                    seen |= by[L]
                stats["rule_mism"] += c_rule != c_brute
                pp_fail = largest_legal != mx; cov_fail = c_brute != mx
                key = "ne" if F else "emp"
                stats[key] += 1; stats["pp_" + key] += pp_fail; stats["cov_" + key] += cov_fail
print(stats)
share = stats["cov_ne"] / stats["ne"]
print("coverage failure share among non-empty fallbacks: %.3f" % share)
ok = stats["pp_ne"] == 0 and stats["cov_ne"] > 0 and 0.05 <= share <= 0.40 and stats["pp_emp"] > 0 and stats["rule_mism"] == 0
print("RESULT: %s per_press_fail_nonempty=%d/%d coverage_fail_nonempty=%d/%d (%.3f) per_press_fail_empty=%d/%d coverage_fail_empty=%d rule_mism=%d" % (
    "PASS" if ok else "FAIL", stats["pp_ne"], stats["ne"], stats["cov_ne"], stats["ne"], share, stats["pp_emp"], stats["emp"], stats["cov_emp"], stats["rule_mism"]))
