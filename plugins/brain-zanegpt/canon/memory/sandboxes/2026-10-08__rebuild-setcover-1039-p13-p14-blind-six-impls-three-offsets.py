#!/usr/bin/env python3
"""Blind rebuild: lag-cover tests for the 2-lag age-cutoff period average.

PREDICTION (written before the first run, not edited afterwards):
  For P13 and P14, at offsets 1039, 517 and 2711 alike, every implementation
  (dict reference, frozenset subset, sorted-merge-from-the-right, prefix-count,
  arithmetic predicate with no stored landings, big-int and-not bitmask)
  gives identical exact Fraction period averages at N in {P-1,P,2P-1,2P,2P+1}.
  Concrete numbers: P13 avg(N=12)=avg(N=13)=406/13, avg(N=25)=avg(N=26)=854/13;
  P14 avg(N=13)=avg(N=14)=77/2, avg(N=27)=avg(N=28)=161/2; avg(N=2P+1) strictly
  larger than avg(2P).  Over the whole N=P-1..2P+1 the flat steps (avg(N)==avg(N-1))
  are exactly N=P and N=2P and nothing else.  The base-0 control (offset 0,
  i.e. horizons 0..P-1) differs from the dict value at N=P, and the buggy
  any-landing cover (b covered if ANY landing of b is a landing of a) differs
  from the dict value at N=P (it over-counts shadows, giving a larger average).
  Extra informational probe (not part of PASS): a tiny offset such as 20 is
  expected NOT to reproduce the claimed values for at least one modulus.

MODEL (inferred from other lessons, then calibrated against P8/P9 numbers in them):
  period P, window width w in 1..P-1, role B available at tick t iff t%P < w,
  fallback always on.  A press at tick t with lag L is legal iff t is outside B
  or t+L is in B; it lands at tick t+L.  Landing set of lag L at horizon T is
  {t+L : 0<=t<T, legal}.  For a lag pair a<b: b is covered by a iff all of b's
  landings are landings of a.  cut lag = b if b uncovered else a if a lands
  anything.  last-landing lag = b if b lands anything else a (if it lands).
  shadow iff last-landing lag != cut lag.  Count shadows over all widths and all
  pairs a<b<=N, for horizons T=base+r, r=0..P-1, and divide by P (exact Fraction).
"""
from fractions import Fraction
from itertools import accumulate

MODULI = (13, 14)
OFFSETS = (1039, 517, 2711)          # all full implementations
CLAIM = {13: (Fraction(406, 13), Fraction(854, 13)),
         14: (Fraction(77, 2), Fraction(161, 2))}


def legal(P, w, L, t):
    return (t % P) >= w or ((t + L) % P) < w


def shadow_rule(a_nonempty, b_nonempty, b_covered):
    last = 'b' if b_nonempty else ('a' if a_nonempty else None)
    cut = 'b' if not b_covered else ('a' if a_nonempty else None)
    return 1 if last != cut else 0


# ---------------------------------------------------------------- implementations
# Each impl: make(P,w,L,T) -> structure ; pair(P,w,T,a,b,sa,sb) -> 0/1 shadow.

def landing_list(P, w, L, T):
    return [t + L for t in range(T) if legal(P, w, L, t)]   # ascending


class Dict:
    name = 'dict'
    @staticmethod
    def make(P, w, L, T):
        d = {}
        for x in landing_list(P, w, L, T):
            d[x] = True
        return d
    @staticmethod
    def pair(sa, sb):
        cov = True
        for x in sb:
            if x not in sa:
                cov = False
                break
        return shadow_rule(bool(sa), bool(sb), cov)


class FSet:
    name = 'frozenset'
    @staticmethod
    def make(P, w, L, T):
        return frozenset(landing_list(P, w, L, T))
    @staticmethod
    def pair(sa, sb):
        return shadow_rule(bool(sa), bool(sb), sb <= sa)


class RightMerge:
    name = 'right-merge'
    @staticmethod
    def make(P, w, L, T):
        return landing_list(P, w, L, T)
    @staticmethod
    def pair(sa, sb):
        i, j = len(sa) - 1, len(sb) - 1
        cov = True
        while j >= 0:
            while i >= 0 and sa[i] > sb[j]:
                i -= 1
            if i < 0 or sa[i] != sb[j]:
                cov = False
                break
            j -= 1
        return shadow_rule(bool(sa), bool(sb), cov)


class PrefixCount:
    """cumulative landing counts over ticks; membership of x = pc[x+1]-pc[x]."""
    name = 'prefix-count'
    @staticmethod
    def make(P, w, L, T):
        ls = landing_list(P, w, L, T)
        size = T + 64
        ind = [0] * size
        for x in ls:
            ind[x] = 1
        pc = [0] + list(accumulate(ind))
        return (pc, ls)
    @staticmethod
    def pair(sa, sb):
        pca, la = sa
        pcb, lb = sb
        cov = True
        for x in lb:
            if pca[x + 1] - pca[x] != 1:
                cov = False
                break
        return shadow_rule(bool(la), bool(lb), cov)


class Predicate:
    """No stored landings: arithmetic test of b's landing ticks against a's rule."""
    name = 'predicate'
    @staticmethod
    def make(P, w, L, T):
        return (P, w, L, T)
    @staticmethod
    def pair(sa, sb):
        P, w, a, T = sa
        _, _, b, _ = sb
        a_nonempty = any(legal(P, w, a, t) for t in range(min(T, 4 * P)))
        # every residue pattern repeats with period P, so 4P ticks decide emptiness
        b_nonempty = any(legal(P, w, b, t) for t in range(min(T, 4 * P)))
        cov = True
        for x in range(b, T + b):
            if legal(P, w, b, x - b):
                # x must be a landing of a: x-a in [0,T) and press at x-a legal
                ta = x - a
                if not (0 <= ta < T and legal(P, w, a, ta)):
                    cov = False
                    break
        return shadow_rule(a_nonempty, b_nonempty, cov)


class BigInt:
    name = 'bigint-andnot'
    @staticmethod
    def make(P, w, L, T):
        m = 0
        for x in landing_list(P, w, L, T):
            m |= 1 << x
        return m
    @staticmethod
    def pair(sa, sb):
        return shadow_rule(sa != 0, sb != 0, (sb & ~sa) == 0)


class AnyBug:
    """buggy rule: b counted covered if ANY of its landings is a landing of a."""
    name = 'any-landing-bug'
    @staticmethod
    def make(P, w, L, T):
        return frozenset(landing_list(P, w, L, T))
    @staticmethod
    def pair(sa, sb):
        return shadow_rule(bool(sa), bool(sb), (not sb) or bool(sa & sb))


IMPLS = (Dict, FSet, RightMerge, PrefixCount, Predicate, BigInt)


def averages(impl, P, base, Nmax):
    """returns {N: Fraction} for N=2..Nmax, using per-b shadow counts and prefix sums."""
    cnt = [0] * (Nmax + 1)
    for r in range(P):
        T = base + r
        for w in range(1, P):
            st = {L: impl.make(P, w, L, T) for L in range(1, Nmax + 1)}
            for b in range(2, Nmax + 1):
                sb = st[b]
                c = 0
                for a in range(1, b):
                    c += impl.pair(st[a], sb)
                cnt[b] += c
    tot = list(accumulate(cnt))
    return {N: Fraction(tot[N], P) for N in range(2, Nmax + 1)}


def main():
    ok = True
    notes = []
    for P in MODULI:
        Ns = (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)
        Nmax = 2 * P + 1
        for base in OFFSETS:
            ref = averages(Dict, P, base, Nmax)
            for impl in IMPLS[1:]:
                got = averages(impl, P, base, Nmax)
                same = all(got[N] == ref[N] for N in range(2, Nmax + 1))
                print(f'P{P} base{base} {impl.name}: equals dict at all N 2..{Nmax}: {same}', flush=True)
                if not same:
                    ok = False
            flats = [N for N in range(P, Nmax + 1) if ref[N] == ref[N - 1]]
            claim_ok = (ref[P] == CLAIM[P][0] and ref[2 * P] == CLAIM[P][1])
            strict_up = ref[2 * P + 1] > ref[2 * P]
            print(f'P{P} base{base}: flats={flats} avgP={ref[P]} avg2P={ref[2*P]} '
                  f'N-values={[(N, str(ref[N])) for N in Ns]} claim_vals={claim_ok}', flush=True)
            if flats != [P, 2 * P] or not claim_ok or not strict_up:
                ok = False
            if base == OFFSETS[0]:
                bug = averages(AnyBug, P, base, Nmax)
                ctrl = averages(Dict, P, 0, Nmax)
                bug_diff = bug[P] != ref[P]
                ctrl_diff = ctrl[P] != ref[P]
                print(f'P{P}: any-bug avgP={bug[P]} differs={bug_diff}; base-0 control avgP={ctrl[P]} differs={ctrl_diff}', flush=True)
                if not (bug_diff and ctrl_diff):
                    ok = False
                small = averages(FSet, P, 20, Nmax)
                notes.append(f'P{P}_base20_avgP={small[P]}_avg2P={small[2*P]}')
        notes.append(f'P{P}_avgP={CLAIM[P][0]}_avg2P={CLAIM[P][1]}')
    print('RESULT: %s impls=%d offsets=%s %s' % ('PASS' if ok else 'FAIL', len(IMPLS), list(OFFSETS), ' '.join(notes)))


if __name__ == '__main__':
    main()
