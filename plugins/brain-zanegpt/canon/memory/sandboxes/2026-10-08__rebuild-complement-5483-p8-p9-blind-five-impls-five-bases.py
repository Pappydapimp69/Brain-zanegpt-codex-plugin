"""Blind rebuild: complement-set disjointness as a lag-cover test vs dict membership.

PREDICTION (written before first run, never edited):
  * Model: lags are 1..N; pair a<b<=N; shadow count summed over widths 1..P-1,
    horizons T=base+r (r=0..P-1), divided by P (Fraction).
  * With a CORRECT universe [0, T+Nmax) (Nmax = 2P+1), complement-disjoint cover ==
    dict-membership cover == frozenset-subset == bitmask == arithmetic periodic
    predicate, for every (width, horizon, b) shadow-count vector, at every offset
    I try (5483, 3571, 9001, 43, and also base 0, since equivalence is logical,
    not statistical).
  * At offset 5483: P8 avg(N=8)=8, avg(N=16)=18; P9 avg(N=9)=100/9, avg(N=18)=220/9.
    Flats defined as N in P-1..2P+1 with avg(N)==avg(N-1): predicted exactly [P, 2P].
    The five N values (P-1,P,2P-1,2P,2P+1) identical for complement and dict.
  * I expect 3571 and 9001 (and probably 43, since 43 > 2P+1) to give the same averages
    as 5483 (steady state); base-0 (horizons 0..P-1) to give DIFFERENT averages.
  * Controls expected to differ from dict: any-overlap cover, length-only cover,
    ignore-cover (cut=b always) and ignore-cover (cut=a always).
  * Too-small universes ([0,T), [0,T+a), [0,T+Nmax-1)) are expected to silently
    call uncovered pairs covered, so the shadow counts / averages should diverge
    from dict (certainly for [0,T); [0,T+a) too; the off-by-one T+Nmax-1 only
    matters if the final tick T+Nmax-2+1 is a landing of lag Nmax, so it may
    differ only slightly or not at all - uncertain).
  * Empty landing lists occur at tiny horizons (T=0, base 0); all correct
    implementations should still agree there.
"""
import time
from fractions import Fraction

TABLE = bytes.maketrans(b"\x00\x01", b"01")


def legal(P, w, L, t):
    return (t % P) >= w or ((t + L) % P) < w


def shadow(cov, a_ne, b_ne):
    cut = 'b' if not cov else ('a' if a_ne else None)
    last = 'b' if b_ne else 'a'
    return cut != last


def arith_cov(P, w, T, a, b):
    """Covered iff every landing of b is a landing of a, via periodic arithmetic only."""
    d = b - a
    head = min(max(T - d, 0), P)
    for t in range(head):
        if legal(P, w, b, t) and not legal(P, w, a, t + d):
            return False
    for t in range(max(T - d, 0), T):
        if legal(P, w, b, t):
            return False
    return True


def arith_ne(P, w, T, L):
    return any(legal(P, w, L, t) for t in range(min(T, P)))


def run(P, base, edge=False, dict_mode='loop'):
    Nmax = 2 * P + 1
    impls = ['dict', 'comp', 'fset', 'bit', 'arith', 'anyov', 'lenonly', 'ign_b', 'ign_a']
    if edge:
        impls += ['comp_T', 'comp_Ta', 'comp_off1']
    vec = {k: {} for k in impls}
    empties = 0
    first_miss = None
    for w in range(1, P):
        for r in range(P):
            T = base + r
            lst = {L: [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]
                   for L in range(1, Nmax + 1)}
            empties += sum(1 for L in lst if not lst[L])
            dd = {L: dict.fromkeys(lst[L], 1) for L in lst}
            fs = {L: frozenset(lst[L]) for L in lst}
            n = T + Nmax
            bits = {}
            for L in lst:
                arr = bytearray(n)
                for x in lst[L]:
                    arr[x] = 1
                bits[L] = int(bytes(arr[::-1]).translate(TABLE), 2) if T else 0
            full = set(range(n))
            comp = {L: full - fs[L] for L in lst}
            if edge:
                compT = {L: set(range(T)) - fs[L] for L in lst}
                compTa = {L: set(range(T + L)) - fs[L] for L in lst}
                compO = {L: set(range(n - 1)) - fs[L] for L in lst}
            acc = {k: [0] * (Nmax + 1) for k in impls}
            for b in range(2, Nmax + 1):
                db, fb = dd[b], fs[b]
                for a in range(1, b):
                    da, fa = dd[a], fs[a]
                    a_ne, b_ne = bool(da), bool(db)
                    if dict_mode == 'loop':
                        c_dict = True
                        for x in db:
                            if x not in da:
                                c_dict = False
                                break
                    else:
                        c_dict = db.keys() <= da.keys()
                    c_comp = fb.isdisjoint(comp[a])
                    covs = {
                        'dict': c_dict,
                        'comp': c_comp,
                        'fset': fb <= fa,
                        'bit': (bits[b] & ~bits[a]) == 0,
                        'arith': arith_cov(P, w, T, a, b),
                        'anyov': not fb.isdisjoint(fa),
                        'lenonly': len(lst[b]) <= len(lst[a]),
                    }
                    nes = {k: (a_ne, b_ne) for k in covs}
                    nes['arith'] = (arith_ne(P, w, T, a), arith_ne(P, w, T, b))
                    for k, c in covs.items():
                        if shadow(c, *nes[k]):
                            acc[k][b] += 1
                    # ignore-cover readings
                    if shadow(False, a_ne, b_ne):      # cut = b always
                        acc['ign_b'][b] += 1
                    cut_a_shadow = ('a' != ('b' if b_ne else 'a'))   # cut = a always
                    if cut_a_shadow:
                        acc['ign_a'][b] += 1
                    if edge:
                        for k, cm in (('comp_T', compT), ('comp_Ta', compTa), ('comp_off1', compO)):
                            ck = fb.isdisjoint(cm[a])
                            if shadow(ck, a_ne, b_ne):
                                acc[k][b] += 1
                            if k == 'comp_T' and ck and not c_dict and first_miss is None:
                                first_miss = (w, T, a, b, sorted(set(lst[b]) - fa)[:3])
            for k in impls:
                vec[k][(w, r)] = acc[k]
    return vec, empties, first_miss


def avgs(vec, P):
    Nmax = 2 * P + 1
    tot = [0] * (Nmax + 1)
    for v in vec.values():
        for b in range(2, Nmax + 1):
            tot[b] += v[b]
    out, run_ = {}, 0
    for N in range(2, Nmax + 1):
        run_ += tot[N]
        out[N] = Fraction(run_, P)
    return out


def five(av, P):
    return [av[N] for N in (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)]


def flats(av, P):
    return [N for N in range(P - 1, 2 * P + 2) if av[N] == av[N - 1]]


def fmt(f):
    return str(f)


def main():
    t0 = time.time()
    ok = True
    notes = []
    claim = {8: {8: Fraction(8), 16: Fraction(18)}, 9: {9: Fraction(100, 9), 18: Fraction(220, 9)}}
    ref5483 = {}
    for P in (8, 9):
        print(f"=== P={P} ===")
        for base in (5483, 3571, 9001, 43, 0):
            edge = base in (5483, 43)
            mode = 'loop' if base in (5483, 43, 0) else 'keys'
            vec, empties, miss = run(P, base, edge=edge, dict_mode=mode)
            av = {k: avgs(v, P) for k, v in vec.items()}
            d = av['dict']
            print(f"-- base {base} (dict_mode={mode}, empty landing lists={empties}, t={time.time()-t0:.0f}s)")
            print("   dict five-N:", [fmt(x) for x in five(d, P)], "flats", flats(d, P))
            for k in ('comp', 'fset', 'bit', 'arith'):
                same_vec = vec[k] == vec['dict']
                print(f"   {k:8s} vectors==dict: {same_vec}   five-N: {[fmt(x) for x in five(av[k], P)]}")
                if not same_vec:
                    ok = False
                    notes.append(f"P{P} base{base} {k} != dict")
            for k in [x for x in vec if x not in ('dict', 'comp', 'fset', 'bit', 'arith')]:
                nd = sum(1 for key in vec[k] if vec[k][key] != vec['dict'][key])
                print(f"   control {k:9s} differing (w,r) vectors: {nd}/{len(vec[k])}  five-N: {[fmt(x) for x in five(av[k], P)]}  flats {flats(av[k], P)}")
            if edge and miss:
                print("   too-small-universe example (comp_T says covered, dict says uncovered): (w,T,a,b,uncovered ticks)=", miss)
            if base == 5483:
                ref5483[P] = d
                for N, v in claim[P].items():
                    good = d[N] == v
                    print(f"   claim avg(N={N}) = {v}: got {d[N]} -> {good}")
                    ok &= good
                fl = flats(d, P)
                good = fl == [P, 2 * P]
                print(f"   flats == [P,2P]={[P, 2*P]}: got {fl} -> {good}")
                ok &= good
                # control expectations
                for k in ('anyov', 'lenonly', 'ign_b', 'ign_a', 'comp_T', 'comp_Ta', 'comp_off1'):
                    if five(av[k], P) == five(d, P) and flats(av[k], P) == flats(d, P):
                        notes.append(f"P{P}: control {k} did NOT differ at 5483")
            else:
                same = (d == ref5483[P])
                print(f"   avg curve identical to base 5483: {same}")
                if base == 0 and same:
                    notes.append(f"P{P}: base-0 control did NOT differ")
                if base in (3571, 9001, 43) and not same:
                    notes.append(f"P{P}: base {base} averages differ from 5483 (informational)")
            if base == 0:
                print("   base0 per-N avg (N=2..):", [fmt(d[N]) for N in range(2, 2 * P + 2)])
        if P in ref5483:
            print("   base5483 avg curve N=2..2P+1:", [fmt(ref5483[P][N]) for N in range(2, 2 * P + 2)])
    print(f"runtime {time.time()-t0:.0f}s; notes: {notes}")
    ps = {P: (fmt(ref5483[P][P]), fmt(ref5483[P][2 * P])) for P in ref5483}
    print(f"RESULT: {'PASS' if ok else 'FAIL'} complement==dict==fset==bitmask==arith at bases 5483/3571/9001/43/0 (correct universe T+2P+1); "
          f"avg(P),avg(2P) per P={ps}; flats [P,2P]; notes={notes}")


if __name__ == '__main__':
    main()
