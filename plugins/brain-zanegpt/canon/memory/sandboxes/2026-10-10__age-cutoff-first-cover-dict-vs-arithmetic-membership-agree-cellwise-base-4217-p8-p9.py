"""Prediction (before run): the first-cover dictionary cover (3001 family) and the list-free arithmetic membership cover (2111 family)
give IDENTICAL one-period totals in every (P, N) cell at new base 4217 for P8 and P9, N=P-1..2P+1, and both flat exactly at N=P and N=2P.
Built to break: base 4217 is new, cells are compared one by one, not just flats. Deterministic, stdlib."""
def count_dict(P, T, N):
    sh = 0
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
                sh += (last != cut)
    return sh
def count_arith(P, T, N):
    sh = 0
    for w in range(1, P):
        ok = lambda t, L: 0 <= t < T and (not (t % P < w) or ((t + L) % P < w))
        for a in range(1, N):
            for b in range(a + 1, N + 1):
                srcs = [t for t in range(T) if ok(t, b)]
                if srcs and all(ok(t + b - a, a) for t in srcs): sh += 1
    return sh
tot = lambda f, P, base, N: sum(f(P, base + r, N) for r in range(P))
ok = True; summ = []; ncell = 0
for P in (8, 9):
    Ns = list(range(P - 1, 2 * P + 2))
    D = {N: tot(count_dict, P, 4217, N) for N in Ns}
    A = {N: tot(count_arith, P, 4217, N) for N in Ns}
    same = all(D[N] == A[N] for N in Ns); ncell += len(Ns)
    flats = [N for N in Ns[1:] if A[N] == A[N - 1]]
    print(P, [D[N] for N in Ns], [A[N] for N in Ns], same, flats, flush=True)
    ok = ok and same and flats == [P, 2 * P]
    summ.append(f"P{P} same={same} flats={flats} totN2P={A[2*P]}")
print("RESULT:", "PASS" if ok else "FAIL", f"{ncell} cells; " + "; ".join(summ))
