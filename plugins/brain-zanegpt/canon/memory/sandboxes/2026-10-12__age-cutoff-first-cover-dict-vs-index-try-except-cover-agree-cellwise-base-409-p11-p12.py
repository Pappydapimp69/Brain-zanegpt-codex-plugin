"""Prediction (before run): the first-cover dictionary cover and an index try/except cover (own build: a list of landing marks per lag,
probed by list index, IndexError counted as 'not covered', no dict/set) give IDENTICAL one-period totals in every (P, N) cell at new base 409
for P11 and P12, lags N=P-1..2P+1, and both are flat exactly at N=P and N=2P. Built to break: the index form is the one that earlier stopped at P5-P7.
Deterministic, stdlib."""
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
def count_idx(P, T, N):
    sh = 0
    size = T + N + 1
    for w in range(1, P):
        tab = {}
        for L in range(1, N + 1):
            m = [0] * (T + L)          # deliberately short: probes beyond T+L raise IndexError
            for t in range(T):
                if (t % P) >= w or ((t + L) % P) < w: m[t + L] = 1
            tab[L] = m
        for a in range(1, N + 1):
            ma = tab[a]
            for b in range(a + 1, N + 1):
                mb = tab[b]
                if not any(mb): continue          # later lag has no landings -> cutoff stays at a, last==cut
                new = False
                for x in range(size):
                    try: vb = mb[x]
                    except IndexError: break
                    if vb:
                        try: va = ma[x]
                        except IndexError: va = 0
                        if not va: new = True; break
                sh += (not new)
    return sh
tot = lambda f, P, base, N: sum(f(P, base + r, N) for r in range(P))
ok = True; summ = []; ncell = 0
for P in (11, 12):
    Ns = list(range(P - 1, 2 * P + 2))
    D = {N: tot(count_dict, P, 409, N) for N in Ns}
    A = {N: tot(count_idx, P, 409, N) for N in Ns}
    same = all(D[N] == A[N] for N in Ns); ncell += len(Ns)
    flats = [N for N in Ns[1:] if A[N] == A[N - 1]]
    print(P, [D[N] for N in Ns], [A[N] for N in Ns], same, flats, flush=True)
    ok = ok and same and flats == [P, 2 * P]
    summ.append(f"P{P} same={same} flats={flats} totN2P={A[2*P]}")
print("RESULT:", "PASS" if ok else "FAIL", f"{ncell} cells; " + "; ".join(summ))
