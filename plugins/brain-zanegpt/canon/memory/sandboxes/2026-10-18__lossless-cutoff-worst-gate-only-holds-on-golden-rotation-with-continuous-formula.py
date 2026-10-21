import math
PHI = (math.sqrt(5) - 1) / 2
def mk(alpha, w, off=0.13):
    return lambda t: ((off + t * alpha) % 1.0) < w
def inval(S, L, N):
    # hint issued at t names B if S(t) legal; invalid at use iff illegal at t+L
    return sum(1 for t in range(N) if S(t) and not S(t + L))
def valid(S, L, N):
    return sum(1 for t in range(N) if S(t) and S(t + L))
def circ(x):
    x %= 1.0
    return min(x, 1 - x)
def formula(alpha, w, L, N):
    return N * min(w, circ(L * alpha), 1 - w)
def run(alpha, w, N, LMAX, name):
    S = mk(alpha, w)
    inv = [inval(S, L, N) for L in range(1, LMAX + 1)]
    val = [valid(S, L, N) for L in range(1, LMAX + 1)]
    lossless = max([L for L, v in zip(range(1, LMAX + 1), val) if v > 0], default=0)
    cum = [sum(inv[:c]) for c in range(LMAX + 1)]
    mono = all(cum[i] <= cum[i + 1] for i in range(LMAX))
    err = [abs(inv[L - 1] - formula(alpha, w, L, N)) / N for L in range(1, LMAX + 1)]
    print(name, "lossless", lossless, "cum_at_lossless", cum[lossless], "max_cum", max(cum),
          "mono", mono, "maxerr%.4f" % max(err), "inv55", inv[54], "inv89", inv[88],
          "median40-70", sorted(inv[39:70])[15])
    return lossless, cum, mono, max(err), inv
N, LMAX = 1000, 144
a = run(PHI, 0.3, N, LMAX, "golden_w.3")
b = run(PHI, 0.5, N, LMAX, "golden_w.5")
c = run(math.sqrt(2) - 1, 0.3, N, LMAX, "silver_w.3_BREAK")
ok = (a[0] == LMAX and a[1][a[0]] == max(a[1]) and a[2] and a[3] < 0.02
      and a[4][54] <= 10 and a[4][88] <= 10
      and b[0] == LMAX and b[3] < 0.02 and c[2] and c[3] < 0.02)
print("RESULT: %s lossless=%d/%d on rotations, gate-only cum max at lossless, monotone, continuous formula N*min(w,|La|,1-w) err<2%% (golden %.4f, w.5 %.4f, silver %.4f), golden inv55=%d inv89=%d"
      % ("PASS" if ok else "FAIL", a[0], LMAX, a[3], b[3], c[3], a[4][54], a[4][88]))
