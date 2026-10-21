"""Rebuild (blind to the target's sandbox) of: bisect cover test at offset 307
reproduces 2-lag period-average flats at N=P and N=2P for P11, P12 with
N=P averages 215/11 and 25, N=2P averages 460/11 and 53.
NOTE: the claim text does not define the model. I took its definition from the
sibling stream-cover sandbox I audited earlier in this run (landing lists
t+L for t where t%P >= w or (t+L)%P < w; shadow count compares last landing
with the cutoff chosen by the cover test), so the MODEL is shared; the cover
method, loops and data layout below are my own (bisect, per-w precompute, cached).
PREDICTION (written before first run): flats exactly [P, 2P] for P11 and P12; averages
at N=P: P11 215/11, P12 25; at N=2P: P11 460/11, P12 53; a base-0 offset gives
different averages; a cover that ignores the lists (always 'covered') cannot
reproduce them; and bisect equals a set-membership cover on every (a,b)."""
from bisect import bisect_left
from fractions import Fraction as F

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cover_bisect(B, A):
    for x in B:
        i = bisect_left(A, x)
        if i == len(A) or A[i] != x: return False
    return True
def cover_set(B, A):
    S = set(A); return all(x in S for x in B)
def cover_ignore(B, A): return True

def avg(P, base, N, cover):
    tot = 0
    for r in range(P):
        T = base + r
        for w in range(1, P):
            V = {L: lands(P, T, w, L) for L in range(1, N + 1)}
            for a in range(1, N + 1):
                for b in range(a + 1, N + 1):
                    last = b if V[b] else (a if V[a] else 0)
                    cut = b if not cover(V[b], V[a]) else (a if V[a] else 0)
                    tot += last != cut
    return F(tot, P)

res = {}
for P in (11, 12):
    Ns = list(range(P - 1, 2 * P + 2))
    av = {N: avg(P, 307, N, cover_bisect) for N in Ns}
    flats = [N for i, N in enumerate(Ns) if i and av[N] == av[Ns[i - 1]]]
    res[P] = (flats, av[P], av[2 * P])
    same = all(avg(P, 307, N, cover_set) == av[N] for N in (P, 2 * P))
    ctl0 = avg(P, 0, P, cover_bisect)
    ign = avg(P, 307, P, cover_ignore)
    print(f"P{P}: flats {flats}  N=P {av[P]}  N=2P {av[2*P]}  set-cover equal {same}  base0 N=P {ctl0}  ignore-cover N=P {ign}")
    res[P] += (same, ctl0 != av[P], ign != av[P])

exp = {11: ([11, 22], F(215, 11), F(460, 11)), 12: ([12, 24], F(25), F(53))}
ok = all(res[P][:3] == exp[P] and res[P][3] and res[P][4] and res[P][5] for P in (11, 12))
print(f"RESULT: {'PASS' if ok else 'FAIL'} flats P11 {res[11][0]} P12 {res[12][0]}; N=P {res[11][1]},{res[12][1]}; N=2P {res[11][2]},{res[12][2]}")
