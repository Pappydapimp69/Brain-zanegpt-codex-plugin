"""Rebuild. Prediction (written before running): at offset 401, P7 avg shadow = 38/7 at N=P and 88/7 at N=2P,
P8 = 8 and 18; every container-wrapper cover equals the dict reference at N in {P-1,P,2P-1,2P,2P+1}; flats
exactly at N=P and 2P; any-for-all gives a different value at N=P. Extra fixtures I chose: offsets 401 and 733,
and a length-only cover as a second wrong rule."""
from fractions import Fraction
from collections import ChainMap, OrderedDict

def landing_ticks(P, horizon, w, lag):
    out = []
    for t in range(horizon):
        if t % P >= w or (t + lag) % P < w:
            out.append(t + lag)
    return out

# cover predicates: is every landing of `late` also a landing of `early`?
def c_dict(late, early):
    d = {x: 1 for x in early}
    return all(x in d for x in late)
def c_issuperset(late, early):
    return set(early).issuperset(iter(late))
def c_mapcontains(late, early):
    d = dict.fromkeys(early)
    return all(map(d.__contains__, late))
def c_chainmap(late, early):
    cm = ChainMap({}, dict.fromkeys(early))
    return all(x in cm for x in late)
def c_ordered_get(late, early):
    od = OrderedDict((x, True) for x in early)
    return all(od.get(x) is not None for x in late)
def c_any(late, early):
    d = dict.fromkeys(early)
    return any(x in d for x in late)
def c_len(late, early):
    return len(late) <= len(early)

def shadow_total(P, horizon, N, cover):
    total = 0
    for w in range(1, P):
        V = {L: landing_ticks(P, horizon, w, L) for L in range(1, N + 1)}
        for a in range(1, N):
            for b in range(a + 1, N + 1):
                last = b if V[b] else (a if V[a] else 0)
                cut = b if not cover(V[b], V[a]) else (a if V[a] else 0)
                total += (last != cut)
    return total

def period_avg(P, base, N, cover):
    return Fraction(sum(shadow_total(P, base + r, N, cover) for r in range(P)), P)

ok = True; notes = []
expect = {(7, 401): (Fraction(38, 7), Fraction(88, 7)), (8, 401): (Fraction(8), Fraction(18))}
impls = [c_issuperset, c_mapcontains, c_chainmap, c_ordered_get]
for base in (401, 733):
    for P in (7, 8):
        Ns = (P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1)
        ref = {N: period_avg(P, base, N, c_dict) for N in Ns}
        same = all({N: period_avg(P, base, N, f) for N in Ns} == ref for f in impls)
        flats = [N for N in (P, 2 * P) if ref[N] == ref[N - 1]]
        anyv = period_avg(P, base, P, c_any); lenv = period_avg(P, base, P, c_len)
        ctrl0 = period_avg(P, 0, P, c_dict)
        exp_ok = True
        if (P, base) in expect:
            exp_ok = (ref[P], ref[2 * P]) == expect[(P, base)]
        line = f"base{base} P{P} avgP={ref[P]} avg2P={ref[2*P]} impls_same={same} flats={flats} any={anyv} len={lenv} base0={ctrl0} expected_match={exp_ok}"
        print(line); notes.append(line)
        ok = ok and same and flats == [P, 2 * P] and anyv != ref[P] and exp_ok
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(n.split(" expected")[0] for n in notes))
