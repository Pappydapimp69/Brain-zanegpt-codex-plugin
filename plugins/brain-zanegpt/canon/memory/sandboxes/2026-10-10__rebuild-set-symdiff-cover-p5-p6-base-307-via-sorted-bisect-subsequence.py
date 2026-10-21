# PREDICTION (written before first run): with the family model (landing times of lag L = {t+L : t<T, t%P>=w or (t+L)%P<w},
# w in 1..P-1; shadow = lag pair a<b whose landing set b is a subset of a's), my independent sorted-list+bisect cover test
# at a DIFFERENT offset (T0=419, not 307) gives P5 avg 2 at N=5 and 26/5 at N=10, P6 avg 7/2 at N=6 and 17/2 at N=12,
# flats exactly at N=P and N=2P, and an any-overlap rule differs at N=P.
from fractions import Fraction
from bisect import bisect_left
def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]   # ascending, distinct
def covered(sa, sb):                      # every element of sb found in sa by binary search
    for x in sb:
        i = bisect_left(sa, x)
        if i == len(sa) or sa[i] != x: return False
    return True
def any_overlap(sa, sb):
    return bool(set(sa) & set(sb))
def count(P, T, N, rule):
    sh = 0
    for w in range(1, P):
        ls = {L: lands(P, T, w, L) for L in range(1, N + 1)}
        for a in range(1, N):
            for b in range(a + 1, N + 1):
                if rule(ls[a], ls[b]): sh += 1
    return sh
def avg(P, base, N, rule=covered):
    return Fraction(sum(count(P, base + r, N, rule) for r in range(P)), P)
base = 419
out = []; ok = True
for P in (5, 6):
    Ns = list(range(P - 1, 2 * P + 3))
    A = {N: avg(P, base, N) for N in Ns}
    flats = [N for N in Ns[1:] if A[N] == A[N - 1]]
    ctrl = avg(P, base, P, any_overlap)
    exp = {5: (Fraction(2), Fraction(26, 5)), 6: (Fraction(7, 2), Fraction(17, 2))}[P]
    good = A[P] == exp[0] and A[2 * P] == exp[1] and flats == [P, 2 * P] and ctrl != A[P]
    ok &= good
    out.append(f"P{P} avgP={A[P]} avg2P={A[2*P]} flats={flats} any_ctrl={ctrl}")
print("; ".join(out))
print(f"RESULT: {'PASS' if ok else 'FAIL'} " + "; ".join(out))
