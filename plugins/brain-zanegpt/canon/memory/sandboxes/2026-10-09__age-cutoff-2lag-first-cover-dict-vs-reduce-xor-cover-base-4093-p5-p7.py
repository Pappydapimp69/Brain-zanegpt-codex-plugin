"""Edge: first-cover dict (base-3001 entry) x set symmetric-difference / reduce cover (base-307 entry).
PREDICTION (before run): at new base 4093 for P5, P6, P7 both implementations give identical period averages for N=P-1..2P+1
(P6: 7/2 at N=6 and 17/2 at N=12; P7: 38/7 and 88/7; P5: 2 and 26/5), flats only at N=P and 2P. BREAK: a wrong cover rule
'identical landing sets' (xor empty) must DISAGREE with the true rule at N=P (strictly fewer shadows)."""
from fractions import Fraction as F
from functools import reduce

def ev(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def sh_dict(ea, eb):
    first = {}
    for x in ea: first.setdefault(x, "a")
    cut = "a" if first else None
    for x in eb:
        if x not in first: first[x] = "b"; cut = "b"
    last = "b" if eb else ("a" if ea else None)
    return last != cut

def sh_xor(ea, eb):
    # b adds nothing new iff (A xor B) is contained in A, i.e. B - A empty; computed by reduce over symmetric differences
    A, B = frozenset(ea), frozenset(eb)
    x = reduce(lambda acc, s: acc ^ s, [A, B], frozenset())
    return bool(eb) and not (x - A)

def sh_identical(ea, eb):
    return bool(eb) and not (frozenset(ea) ^ frozenset(eb))

def avg(P, base, N, fn):
    tot = 0
    for r in range(P):
        T = base + r
        for w in range(1, P):
            e = {L: ev(P, T, w, L) for L in range(1, N + 1)}
            tot += sum(fn(e[a], e[b]) for a in range(1, N + 1) for b in range(a + 1, N + 1))
    return F(tot, P)

ok = True; out = []
for P in (5, 6, 7):
    Ns = range(P - 1, 2 * P + 2)
    A = {N: avg(P, 4093, N, sh_dict) for N in Ns}
    X = {N: avg(P, 4093, N, sh_xor) for N in Ns}
    I = avg(P, 4093, P, sh_identical)
    flats = [N for N in list(Ns)[1:] if A[N] == A[N - 1]]
    agree = A == X
    ok = ok and agree and flats == [P, 2 * P] and I < A[P]
    print(P, flats, A[P], A[2 * P], agree, "identical-rule avgP", I, flush=True)
    out.append(f"P{P} flats={flats} avgP={A[P]} avg2P={A[2*P]} agree={agree} identical_avgP={I}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
