"""Square-wave state s(t)=(t%P)<H. Hint emitted at t is applied at t+L.
Policies: naive (hint=s(t)); frozen-stale executes it; token drops it when s(t)!=s(t+L);
compensated (hint=s(t+L-e_est_err)) with lag estimate off by e.
PREDICTION (N=600): naive mismatch == frozen stale execs == token drops for every (P,H,L);
exact compensation (e=0) gives 0 mismatch at every lag; with error e=1 mismatch == 2*N/P
(two edges per period) for P in 6,10,12 with H>=2 and P-H>=2, independent of L;
breaker: a sawtooth state s(t)=t%P changes every frame so e=1 mismatch == N (rate-bound, not period-bound)."""
N = 600
def mism(s, L, delta):
    # hint predicts state at t+L-delta (delta = compensation applied, true lag L); error = L-delta... use est
    return sum(1 for t in range(N) if s(t + delta) != s(t + L))
ok = True
for P, H in ((6, 3), (10, 4), (12, 5)):
    s = lambda t, P=P, H=H: (t % P) < H
    for L in (0, 1, 2, 4, 7, 15):
        naive = mism(s, L, 0)
        token = sum(1 for t in range(N) if s(t) != s(t + L))
        if naive != token: ok = False; print("conv broken", P, H, L)
        if mism(s, L, L) != 0: ok = False; print("exact comp nonzero", P, L)
        for e in (1,):
            for d in (L - e, L + e):
                if d < 0: continue
                m = mism(s, L, d)
                if m != 2 * N // P: ok = False; print("err budget off", P, H, L, d, m, 2 * N // P)
    print(f"P{P}H{H}: e=1 mismatch", 2 * N // P, "naive by L", [mism(s, L, 0) for L in (0, 1, 2, 4, 7, 15)])
saw = lambda t: t % 7
m = sum(1 for t in range(N) if saw(t + 4) != saw(t + 5))
print("sawtooth e=1 mismatch", m)
if m != N: ok = False
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" naive==token drops; exact comp 0 mismatch; e=1 costs 2N/P (200/120/100) any lag; sawtooth breaker {m}")
