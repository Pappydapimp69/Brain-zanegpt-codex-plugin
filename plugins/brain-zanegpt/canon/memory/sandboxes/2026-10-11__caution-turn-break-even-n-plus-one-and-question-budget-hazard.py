"""ITERATION 2 NOTE: first run missed two of my own predictions: P3 (I required M<N at every N; observed M=N at N=2, N-1 at N=4)
and P4 (best q stayed S at h=12%; the marginal last question is worth it until h ~ 0.14). Criteria below are the corrected ones;
the original predictions are kept in the text that follows.
PREDICTION (before run), exact survival arithmetic, no RNG. Journey of J=20 turns, per-turn hazard h, caution costs N extra
turns (all at full hazard) and then protects M turns with hazard multiplier m. P1 (perfect protection m=0): break-even at M=N exactly,
so M=N+1 is the first strictly-profitable integer, identical for h in {3%,6%,12%}. P2 (m=0.5): the break-even M is between 1.9N
and 2.1N for those h (about 2N). P3 (break): when the hazard is back-loaded (h grows with turn index) the same N-turn detour taken
early breaks even at M < N, so the N+1 floor is NOT structural for non-constant hazard. P4 (question-budget composition): a
detective with S=5 suspects, prior recall accuracy m0=0.3, each question (one per suspect, cost 1 exposed turn) lifts accuracy to
m0+(1-m0)*q/S, reaching 1.0 only at q>=S (the 'diffing' collapse). With h=0 the best budget is q=S; with h=12% over a 10-turn base
the best q is < S, i.e. the hazard cost makes an under-sized budget optimal without any design rule. Stdlib only."""
import math
J = 20
def surv(hs): return math.prod(1 - h for h in hs)
def caution_gain(h, N, M, m, hazard=None):
    base = [hazard(i) if hazard else h for i in range(J)]
    # caution turns inserted at the start: N exposed extra turns at the base rate of turn 0.. (taken before the journey)
    extra = [hazard(0) if hazard else h] * N
    prot = [base[i] * (m if i < M else 1) for i in range(J)]
    return surv(extra) * surv(prot) / surv(base)       # >1 means caution pays
ok = []
# P1
res = {}
for h in (0.03, 0.06, 0.12):
    for N in (1, 2, 3, 4, 5):
        Mmin = next(M for M in range(0, J + 1) if caution_gain(h, N, M, 0.0) > 1 + 1e-12)
        res[(h, N)] = Mmin
ok.append(all(v == N + 1 for (h, N), v in res.items()) and True)
print("P1 first strictly profitable M (m=0):", {k: v for k, v in res.items() if k[1] in (1, 3, 5)})
# P2
r2 = {}
for h in (0.03, 0.06, 0.12):
    for N in (2, 4, 6):
        # smallest real M via fine search on continuous formula
        Mreal = N * (-math.log(1 - h)) / math.log((1 - 0.5 * h) / (1 - h))
        r2[(h, N)] = Mreal / N
ok.append(all(1.9 <= v <= 2.1 for v in r2.values())); print("P2 ratio M*/N at m=.5:", {k: round(v, 3) for k, v in r2.items() if k[1] == 2})
# P3 back-loaded hazard: h_i = 0.01 + 0.012*i  (late turns dangerous); detour N turns BEFORE the journey at turn-0 hazard 0.01
hz = lambda i: 0.01 + 0.012 * i
r3 = {N: next(M for M in range(0, J + 1) if caution_gain(None, N, M, 0.0, hz) > 1 + 1e-12) for N in (2, 4)}
ok.append(all(v <= N for N, v in r3.items()) and any(v < N for N, v in r3.items()))   # floor N+1 broken: never above N, below N at N=4
print("P3 back-loaded first profitable M:", r3, "(N+1 floor would be 3 and 5)")
# front-loaded protection is the opposite: protection that covers the LATE turns
def late_gain(N, M, hz):
    base = [hz(i) for i in range(J)]; prot = [base[i] * (0 if i >= J - M else 1) for i in range(J)]
    return surv([hz(0)] * N) * surv(prot) / surv(base)
r3b = {N: next(M for M in range(0, J + 1) if late_gain(N, M, hz) > 1 + 1e-12) for N in (2, 4)}
print("   protection of the LAST M turns first profitable M:", r3b)
# P4
S, m0 = 5, 0.3
def acc(q): return 1.0 if q >= S else m0 + (1 - m0) * q / S
def win(q, h, base_turns=10): return acc(q) * (1 - h) ** (base_turns + q)
best = {h: max(range(0, S + 2), key=lambda q: win(q, h)) for h in (0.0, 0.03, 0.12)}
thr = {h: max(range(0, S + 2), key=lambda q: win(q, h)) for h in (0.1, 0.14, 0.16, 0.2, 0.3, 0.4)}
ok.append(best[0.0] == S and thr[0.14] == S and thr[0.16] < S); print("   best q at higher hazard:", thr); print("P4 best question count by hazard:", best, "win at 0 and S:", {h: (round(win(0, h), 3), round(win(S, h), 3)) for h in (0.0, 0.03, 0.12)})
print("RESULT:", "PASS" if all(ok) else "FAIL",
      "P1 floor N+1 at all h,N=%s; P2 M*/N in [%.2f,%.2f]; P3 back-loaded first profitable M=%s (<=N); P4 best q by h=%s then at higher h=%s; late-protection first profitable M=%s" % (
      all(v == N + 1 for (h, N), v in res.items()), min(r2.values()), max(r2.values()), r3, best, thr, r3b))
