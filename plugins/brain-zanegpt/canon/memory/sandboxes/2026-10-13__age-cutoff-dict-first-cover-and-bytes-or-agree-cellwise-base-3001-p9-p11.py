"""Prediction (before run): at base 3001 the dict first-cover test and the bytes-OR test (as big-int OR of the
lag byte maps) agree on EVERY (P,r,w,a,b) cell for P9..P11, lags 1..2P (disagreements = 0); the offset-averaged shortfall
totals give P11 215/11 at N=P and 460/11 at N=2P (the recorded dict values), with flats exactly at N=P and N=2P;
a base-0 control differs at N=P. Built to break: P11 (outside the P5-P8 range of the 4421 bytes run) and cell
comparison, not only totals. Stdlib, deterministic."""
from fractions import Fraction as F
def dict_cells(P, T, N):
    out = {}
    for w in range(1, P):
        ev = {L: [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w] for L in range(1, N + 1)}
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                first = {}
                for x in ev[a]: first.setdefault(x, a)
                cut = a if first else 0
                for x in ev[b]:
                    if x not in first: first[x] = b; cut = b
                last = b if ev[b] else (a if ev[a] else 0)
                out[(w, a, b)] = int(last != cut)
    return out
def bytes_cells(P, T, N):
    out = {}
    for w in range(1, P):
        maps = {}
        for L in range(1, N + 1):
            m = bytearray(T + N + 1)
            for t in range(T):
                if (t % P) >= w or ((t + L) % P) < w: m[t + L] = 1
            maps[L] = (m, int.from_bytes(m, "big"), any(m))
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                _, ia, _ = maps[a]; _, ib, nz = maps[b]
                out[(w, a, b)] = int(nz and (ia | ib) == ia)
    return out
def totals(P, base, N, fn):
    cells = [fn(P, base + r, N) for r in range(P)]
    return {n: F(sum(v for c in cells for (w, a, b), v in c.items() if b <= n), P) for n in range(P - 1, N + 1)}, cells
ok = True; summ = []
for P in (9, 10, 11):
    N = 2 * P
    A, cd = totals(P, 3001, N, dict_cells)
    bad = 0
    for r in range(P):
        cb = bytes_cells(P, 3001 + r, N)
        bad += sum(cd[r][k] != cb[k] for k in cd[r])
    Z, _ = totals(P, 0, P, dict_cells)
    flats = [n for n in range(P, N + 1) if A[n] == A[n - 1]]
    rec = (A[P], A[2 * P]) == (F(215, 11), F(460, 11)) if P == 11 else True
    ctrl = Z[P] != A[P]
    print(P, "disagree", bad, "flats", flats, "rec", rec, "ctrl", ctrl, A[P], A[2 * P], flush=True)
    ok = ok and bad == 0 and flats == [P, 2 * P] and rec and ctrl
    summ.append(f"P{P} disagree={bad} flats={flats} N=P:{A[P]} N=2P:{A[2*P]}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(summ))
