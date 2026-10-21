# My own reading of the claim: world flag f(t)=1 iff t mod P < w (one contiguous window per period).
# A press at time t reading a stale flag with lag L "lands valid" if f(t-L)==1 for some press time t inside the open window (f(t)==1).
# Prediction (before run): brute force == closed form (circular distance of L from a multiple of P <= w-1) for all P in 3..14, w in 1..P-1, L in 1..3P;
# dropping lag P (lags 1..P) leaves max valid lag P-1 when w>=2 and 0 when w==1. BREAK: a two-window flag (non-contiguous) violates the closed form.
def brute(P, w, L, windows=None):
    inw = (lambda x: (x % P) < w) if windows is None else (lambda x: (x % P) in windows)
    return any(inw(t - L) for t in range(3 * P) if inw(t))
def closed(P, w, L):
    d = min(L % P, P - (L % P)) if L % P else 0
    return d <= w - 1
ok = True; n = 0; drop_bad = []
for P in range(3, 15):
    for w in range(1, P):
        for L in range(1, 3 * P + 1):
            n += 1
            if brute(P, w, L) != closed(P, w, L): ok = False; print("MISMATCH", P, w, L)
        valid = [L for L in range(1, P + 1) if brute(P, w, L) and L != P]  # drop the period lag
        cutoff = max(valid) if valid else 0
        want = P - 1 if w >= 2 else 0
        if cutoff != want: drop_bad.append((P, w, cutoff, want))
print("cells", n, "closed-form mismatches 0" if ok else "MISMATCH", "drop-lag cutoff violations", drop_bad[:5])
ok &= not drop_bad
# BREAK: two windows per period (non-contiguous): {0,1} and {4,5} for P=8
P = 8; wins = {0, 1, 4, 5}
mis = [L for L in range(1, 3 * P + 1) if brute(P, 2, L, wins) != closed(P, 2, L)]
valid = [L for L in range(1, P + 1) if brute(P, 2, L, wins) and L != P]
print("two-window P=8: closed form wrong at lags", mis[:8], "cutoff after drop", max(valid) if valid else 0, "(contiguous prediction P-1=7)")
ok &= len(mis) > 0
print("RESULT:", "PASS" if ok else "FAIL", "%d (P,w,L) cells brute==closed; drop-P cutoff P-1 (w>=2) / 0 (w==1) for P=3..14; non-contiguous window breaks closed form at %d lags" % (n, len(mis)))
