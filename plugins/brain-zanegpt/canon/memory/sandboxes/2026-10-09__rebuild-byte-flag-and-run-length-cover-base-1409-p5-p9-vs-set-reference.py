"""Rebuild of the claim (byte-flag / interval-run covers equal a membership reference; flat at N=P and 2P;
any-for-all breaks it). Own fixture: base 1409 (claim used 503), moduli P5,P6,P7,P9, N sweep P-1..2P+1,
reference = Python set subset, candidates = bytearray flag cover and run-length (start,end) interval cover.
PREDICTION (before run): P6 avg 7/2 at N=6 and 17/2 at N=12; P9 100/9 at N=9 and 220/9 at N=18; flats exactly
at N=P and N=2P for every P tested; all three implementations agree on every cell; any-for-all at N=P gives
75 for P6 and 288 for P9; base-0 control differs at N=P.
Landing model (taken from the claim family): a start t lands at t+L when (t%P)>=w or ((t+L)%P)<w;
lag pair a<b is a shadow when b lands somewhere and every b landing is already landed by a."""
from fractions import Fraction as F
from itertools import groupby

def events(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def sh_set(ea, eb):
    return bool(eb) and set(eb) <= set(ea)

def sh_flags(ea, eb, size):
    f = bytearray(size)
    for x in ea: f[x] = 1
    return bool(eb) and all(f[x] for x in eb)

def runs(ev):
    # maximal consecutive runs of the sorted unique landings as (start, end)
    out = []
    for _, g in groupby(enumerate(sorted(set(ev))), key=lambda p: p[1] - p[0]):
        g = list(g); out.append((g[0][1], g[-1][1]))
    return out

def sh_runs(ea, eb):
    ra = runs(ea)
    def covered(x):
        lo, hi = 0, len(ra)
        while lo < hi:
            m = (lo + hi) // 2
            if ra[m][1] < x: lo = m + 1
            else: hi = m
        return lo < len(ra) and ra[lo][0] <= x
    return bool(eb) and all(covered(x) for x in eb)

def sh_any(ea, eb):
    return bool(eb) and any(x in set(ea) for x in eb)

def counts(P, T, N):
    c = {"set": 0, "flags": 0, "runs": 0, "any": 0}
    for w in range(1, P):
        ev = {L: events(P, T, w, L) for L in range(1, N + 1)}
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                c["set"] += sh_set(ev[a], ev[b])
                c["flags"] += sh_flags(ev[a], ev[b], T + N + 2)
                c["runs"] += sh_runs(ev[a], ev[b])
                c["any"] += sh_any(ev[a], ev[b])
    return c

def avgs(P, base, N):
    tot = {"set": 0, "flags": 0, "runs": 0, "any": 0}
    for r in range(P):
        for k, v in counts(P, base + r, N).items(): tot[k] += v
    return {k: F(v, P) for k, v in tot.items()}

ok = True; out = []
EXP = {6: (F(7, 2), F(17, 2)), 9: (F(100, 9), F(220, 9))}
for P in (5, 6, 7, 9):
    Ns = list(range(P - 1, 2 * P + 2))
    A = {N: avgs(P, 1409, N) for N in Ns}
    agree = all(A[N]["set"] == A[N]["flags"] == A[N]["runs"] for N in Ns)
    flats = [N for N in Ns[1:] if A[N]["set"] == A[N - 1]["set"]]
    ctrl = avgs(P, 0, P)["set"] != A[P]["set"]
    anyd = A[P]["any"] != A[P]["set"]
    exp_ok = (P not in EXP) or ((A[P]["set"], A[2 * P]["set"]) == EXP[P])
    print(P, "flats", flats, "avgP", A[P]["set"], "avg2P", A[2 * P]["set"], "agree", agree, "ctrl", ctrl,
          "any_avgP", A[P]["any"], flush=True)
    ok = ok and agree and flats == [P, 2 * P] and ctrl and anyd and exp_ok
    out.append(f"P{P} flats={flats} avgP={A[P]['set']} avg2P={A[2*P]['set']} agree={agree} any_avgP={A[P]['any']}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
