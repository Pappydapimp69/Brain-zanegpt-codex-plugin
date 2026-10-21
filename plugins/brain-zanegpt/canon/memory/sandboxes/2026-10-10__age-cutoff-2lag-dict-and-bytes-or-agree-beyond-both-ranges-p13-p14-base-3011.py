"""Prediction (before run): the first-cover dict (recorded to P12) and the bytearray-OR cover (recorded to P10) still agree cell by cell
at base 3011 on P13 and P14 (outside BOTH recorded ranges), flats only at N=P and N=2P, and the any-overlap rule differs at N=P or 2P.
Extrapolated 2P totals are not predicted. Stdlib, deterministic, no RNG."""


from fractions import Fraction as F

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def cnt_dict(P, T, N):
    sh = 0
    for w in range(1, P):
        ev = {L: lands(P, T, w, L) for L in range(1, N + 1)}
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                first = {}
                for x in ev[a]: first.setdefault(x, a)
                cut = a if first else 0
                for x in ev[b]:
                    if x not in first: first[x] = b; cut = b
                last = b if ev[b] else (a if ev[a] else 0)
                sh += (last != cut)
    return sh

def cnt_bytes(P, T, N, rule="subset"):
    sh = 0; size = T + N + 2
    for w in range(1, P):
        mp = {}
        for L in range(1, N + 1):
            m = bytearray(size)
            for x in lands(P, T, w, L): m[x] = 1
            mp[L] = m
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                ma, mb = mp[a], mp[b]
                if rule == "subset":
                    covered = bytes(x | y for x, y in zip(ma, mb)) == bytes(ma)
                else:  # wrong rule: any overlap counts as covered
                    covered = any(x & y for x, y in zip(ma, mb))
                # shadow = last landing lag (b if b has events else a) != cutting lag
                # cutting lag = b iff b adds a new tick, else a (if a has events)
                adds = any(y and not x for x, y in zip(ma, mb))
                cut = b if adds else (a if any(ma) else 0)
                last = b if any(mb) else (a if any(ma) else 0)
                if rule == "subset": sh += (last != cut)
                else: sh += (last != (a if covered else cut))
    return sh

ok = True; out = []
REC = {}
for P in (13, 14):
    Ns = list(range(P - 1, 2 * P + 2))
    dsum, bsum, wrong = {}, {}, {}
    for N in Ns:
        dsum[N] = sum(cnt_dict(P, 3011 + r, N) for r in range(P))
        bsum[N] = sum(cnt_bytes(P, 3011 + r, N) for r in range(P))
    for N in (P, 2 * P):
        wrong[N] = sum(cnt_bytes(P, 3011 + r, N, "any") for r in range(P))
    same = dsum == bsum
    A = {N: F(dsum[N], P) for N in Ns}
    flats = [N for N in Ns[1:] if A[N] == A[N - 1]]
    breaks = any(wrong[N] != dsum[N] for N in wrong)
    rec = True
    if P in REC: rec = (dsum[P], dsum[2 * P]) == REC[P]
    print(P, "same", same, "flats", flats, "totP,2P", dsum[P], dsum[2 * P], "rec", rec, "wrongDiffers", breaks, flush=True)
    ok = ok and same and flats == [P, 2 * P] and breaks and rec
    out.append(f"P{P} flats={flats} tot2P={dsum[2*P]} same={same}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
