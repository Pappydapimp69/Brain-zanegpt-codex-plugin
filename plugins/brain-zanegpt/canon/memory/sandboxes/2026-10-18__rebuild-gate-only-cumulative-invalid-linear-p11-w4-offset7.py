# Own fixture: P=11, W=4, phase offset 7 (legal(t) = (t+7) % 11 < 4), N = 40P = 440, lags 1..60 (=5P+5).
# Prediction (before running): cumulative one-sided invalid at cutoff kP-1 is k*(N/P)*W*(P-W) = k*40*28 = 1120k
# for k=1..5; symmetric equals twice one-sided at every lag; the lossless cutoff (largest lag with a valid hint)
# is 58, NOT the scan limit 60, because residues 4..7 have no valid hint (60%11=5, 59%11=4 invalid; 58%11=3 valid).
P, W, OFF, N, MAXL = 11, 4, 7, 440, 60
legal = lambda t: (t + OFF) % P < W
base = 5 * P
def counts(L):
    one = sum(1 for t in range(base, base + N) if legal(t - L) and not legal(t))
    sym = sum(1 for t in range(base, base + N) if legal(t - L) != legal(t))
    val = sum(1 for t in range(base, base + N) if legal(t - L) and legal(t))
    return one, sym, val
c = {L: counts(L) for L in range(1, MAXL + 1)}
cum = lambda k: sum(c[L][0] for L in range(1, k + 1))
stair = {k: (cum(k * P - 1), k * (N // P) * W * (P - W)) for k in range(1, 6)}
sym_ok = all(c[L][1] == 2 * c[L][0] for L in c)
lossless = max(L for L in c if c[L][2] > 0)
rule = max(L for L in range(1, MAXL + 1) if (L % P) < W or (L % P) > P - W)
print("staircase", stair, "sym==2*one", sym_ok, "lossless", lossless, "residue rule", rule)
ok = all(a == b for a, b in stair.values()) and sym_ok and lossless == rule == 58
print("RESULT: %s staircase exact at k=1..5 (%s), symmetric twice one-sided on all %d lags, lossless cutoff %d equals residue rule %d and not scan limit %d" % ("PASS" if ok else "FAIL", ",".join(str(a) for a, _ in stair.values()), MAXL, lossless, rule, MAXL))
