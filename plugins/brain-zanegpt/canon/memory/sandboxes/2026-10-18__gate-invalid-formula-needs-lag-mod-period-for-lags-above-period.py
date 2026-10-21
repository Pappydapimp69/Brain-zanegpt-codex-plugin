# Sandbox: gate-only invalid count for lags ABOVE the period, and the lossless cutoff of the validity design.
# Prediction (written before first run): with P=12 W=4 N=600, the formula
# (N/P)*min(L',W,P-L',P-W) with L' = L mod P is exact for every lag 1..47; the unreduced
# formula (L raw) is wrong for every L>=P-... (negative/ wrong) in at least 30 lags; lags that are
# multiples of P give 0 invalid; and gate-only invalid at the validity-lossless cutoff
# for S1 {1,3,7,20} is 600 (50+150+200+200), for S3 {5,12,24} is 200 (5->4*50=200, 12->0, 24->0).
P, W, N = 12, 4, 600
def legal(t): return t % P < W
def inval(L, P=P, W=W, N=N):
    # hint issued at t-L names B iff legal then; invalid at use t iff now illegal
    return sum(1 for t in range(3*P, 3*P+N) if legal(t-L) and not legal(t))
def fm(L, mod=True):
    l = L % P if mod else L
    return (N//P) * min(l, W, P-l, P-W)
bad_mod = [L for L in range(1, 48) if inval(L) != fm(L)]
bad_raw = [L for L in range(1, 48) if inval(L) != fm(L, mod=False)]
mult = [inval(L) for L in (12, 24, 36)]
def lossless(lags):  # validity+cutoff loses valid presses with L>cutoff; valid = legal(t-L)&legal(t) exists
    # established model: a hint is A (always legal) when B was unavailable at issue, so every lag has valid presses
    valid = [L for L in lags if any((not legal(t-L)) or legal(t) for t in range(3*P, 3*P+P))]
    return max(valid)
S1, S3 = [1,3,7,20], [5,12,24]
tot = {}
for name, S in (("S1", S1), ("S3", S3)):
    c = lossless(S)
    tot[name] = (c, sum(inval(L) for L in S if L <= c))
# second shape to avoid single-point claim
P2, W2 = 10, 3
def inval2(L): return sum(1 for t in range(30, 30+600) if (t-L)%P2 < W2 and not t%P2 < W2)
def fm2(L): l=L%P2; return 60*min(l,W2,P2-l,P2-W2)
bad2 = [L for L in range(1, 40) if inval2(L) != fm2(L)]
print("mod-formula mismatches P12W4:", bad_mod)
print("raw-formula mismatches P12W4:", len(bad_raw))
print("multiples of P invalid:", mult)
print("lossless cutoff, gate-only invalid:", tot)
print("mod-formula mismatches P10W3:", bad2)
ok = not bad_mod and len(bad_raw) >= 30 and mult == [0,0,0] and tot["S1"] == (20,600) and tot["S3"] == (24,200) and not bad2
print("RESULT: %s mod-reduced formula exact on 47 lags P12W4 and 39 lags P10W3; raw formula wrong on %d lags; S1 cutoff %s invalid %d; S3 cutoff %s invalid %d" % ("PASS" if ok else "FAIL", len(bad_raw), tot["S1"][0], tot["S1"][1], tot["S3"][0], tot["S3"][1]))
