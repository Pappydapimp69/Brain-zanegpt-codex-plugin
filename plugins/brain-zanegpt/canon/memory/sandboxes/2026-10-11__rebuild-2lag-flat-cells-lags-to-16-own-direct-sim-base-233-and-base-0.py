"""Rebuild of: flat cells of the 2-lag period-average total over N=4..16, P=8..14.
Prediction (before run): flats exactly (P,P) for P=8..14 plus (16,8); totals
non-decreasing in N; a base-0 start (horizon T = r, no warm-up) gives a DIFFERENT
flat set. Own fixture: pure-Python direct sim with per-window frozen lists
(not the original's set/bitmask code), base 233, horizon T=233+r per residue
offset r, base-0 control T=r. Resolver reading carried over from the lesson family:
for block width w, slot t blocked iff t%P<w; lag L from t lands at t+L if t is
free or t+L is blocked; for lag pair (a<b) walk a then b, cut = last lag adding a
new landing; count the pair when the largest lag with any landing != cut."""
def pair_total(P, T, N):
    n = 0
    for w in range(1, P):
        blk = [(t % P) < w for t in range(T + N + 2)]
        land = [frozenset(t + L for t in range(T) if (not blk[t]) or blk[t + L]) for L in range(1, N + 1)]
        for i in range(N):
            for j in range(i + 1, N):
                cut = i + 1 if land[i] else 0
                if land[j] - land[i]: cut = j + 1
                big = j + 1 if land[j] else (i + 1 if land[i] else 0)
                n += big != cut
    return n
def table(P, base):
    return {N: sum(pair_total(P, base + r, N) for r in range(P)) for N in range(4, 17)}
def flats(tab): return [N for N in range(5, 17) if tab[N] == tab[N - 1]]
good = True; zero_differs = False; seen = []
for P in range(8, 15):
    t233 = table(P, 233); t0 = table(P, 0)
    f = flats(t233); f0 = flats(t0)
    nd = all(t233[N] >= t233[N - 1] for N in range(5, 17))
    want = [P] + ([16] if P == 8 else [])
    seen.append((P, f, f0))
    print(f"P{P} base233 flats={f} nondecreasing={nd} base0 flats={f0}")
    good &= nd and f == want
    zero_differs |= f0 != f
print("RESULT:", "PASS" if good and zero_differs else "FAIL",
      "flat cells (P,P) P8-P14 plus (16,8) at base 233; base-0 control differs" if good and zero_differs
      else "flat set or base-0 control did not match prediction: " + str(seen))
