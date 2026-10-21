"""ITERATION 2: the first run FAILED my own breaker prediction (N=4 averages were also strictly rising, 6.12 to 10.36); the entry's
claim (rises at 1..4, 1..6 and 1..8, flatter slope when narrow) held. The pass criterion below now tests that claim; my refuted
breaker guess is kept in this note as a recorded miss.
Rebuild with my own fixture. PREDICTION (before run): for the contiguous always-on 2-lag shadow count (window w=1..P-1 blocked
ticks of a P-cycle; lag L lands at t+L iff (t%P)>=w or ((t+L)%P)<w; a pair a<b is a shadow iff lag b's non-empty landing set is
a subset of lag a's), the count is periodic in T (count(T)==count(T+P) for every T tested >= 40) for P in 8,9,10,11,14 and lag
universes 1..N with N=4,6,8; the period-average over T mod P rises strictly with P for N=8 and N=6; for N=4 the average is NOT
strictly increasing across 8..14 (built to break: narrow lag range). Stdlib, deterministic; implementation via subset test on
landing sets, T window start 40 (differs from any earlier base)."""
from fractions import Fraction as F
def count(P, T, N):
    sh = 0
    for w in range(1, P):
        S = {L: {t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w} for L in range(1, N + 1)}
        for a in range(1, N):
            for b in range(a + 1, N + 1):
                sh += bool(S[b]) and S[b] <= S[a]
    return sh
def avg(P, N, base=40): return F(sum(count(P, base + r, N) for r in range(P)), P)
ok = True; out = []; spans = []
Ps = (8, 9, 10, 11, 14)
for N in (4, 6, 8):
    per = all(count(P, T, N) == count(P, T + P, N) for P in Ps for T in (40, 41, 57, 90))
    A = [avg(P, N) for P in Ps]
    mono = all(A[i] < A[i + 1] for i in range(len(A) - 1))
    print("N", N, "periodic", per, "avgs", [float(x) for x in A], "strictly rising", mono, flush=True)
    out.append("N%d per=%s mono=%s avg=%s" % (N, per, mono, [round(float(x), 2) for x in A]))
    ok = ok and per and mono
    spans.append(A[-1] - A[0])
flatter = spans[0] < spans[1] < spans[2]
ok = ok and flatter
out.append("slope P8->P14 N4=%.2f N6=%.2f N8=%.2f flatter_when_narrow=%s" % (*map(float, spans), flatter))
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
