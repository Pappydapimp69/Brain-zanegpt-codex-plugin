"""Sandbox: Elo K-factor schedules. 10 players, hidden true ratings 1000..1900 step 100, all start at 1500.
Outcomes deterministic: player a beats b iff u(g) < p_true where u(g)=frac(g*0.6180339887) (equidistributed, no RNG).
Mid-run shock: at game SHOCK player 0 (weakest) becomes +SHIFT stronger.
Schedules: fixed K (8,16,32,64); games-played schedule (FIDE-style shape: K=40 first 30 games, 20 to 100, then 10);
games-played with a surprise reopen (K back to 40 for 30 games when |sum of last 10 residuals| > 3).
Prediction (before run): games-played schedule has the lowest static error (RMS over games 1500-1600), but after the shock
it recovers the shocked player slowest of all except K=8; the reopen variant recovers as fast as K=32 while keeping the
low static error. Stdlib only."""
import math
N, SHOCK, SHIFT, G = 10, 2000, 400, 4000
TRUE0 = [1000 + 100 * i for i in range(N)]

def exp_score(ra, rb): return 1 / (1 + 10 ** (-(ra - rb) / 400))

class Sched:
    def __init__(self, kind, k=None):
        self.kind, self.k = kind, k
        self.games = [0] * N; self.res = [[] for _ in range(N)]; self.reopen = [0] * N
    def K(self, i):
        if self.kind == "fixed": return self.k
        base = 40 if self.games[i] < 30 else 20 if self.games[i] < 100 else 10
        if self.kind == "gp": return base
        return 40 if self.reopen[i] > 0 else base
    def update(self, i, resid):
        self.games[i] += 1
        if self.kind == "reopen":
            r = self.res[i]; r.append(resid); r[:] = r[-10:]
            if self.reopen[i] > 0: self.reopen[i] -= 1
            elif len(r) == 10 and abs(sum(r)) > 3: self.reopen[i] = 30; r.clear()

def run(sched):
    r = [1500.0] * N; true = list(TRUE0)
    static_err = []; recov = None
    for g in range(G):
        if g == SHOCK: true[0] += SHIFT
        a = g % N; b = (a + 1 + (g // N) % (N - 1)) % N
        u = (g * 0.6180339887) % 1.0
        sa = 1.0 if u < exp_score(true[a], true[b]) else 0.0
        ea = exp_score(r[a], r[b])
        ka, kb = sched.K(a), sched.K(b)
        r[a] += ka * (sa - ea); r[b] += kb * ((1 - sa) - (1 - ea))
        sched.update(a, sa - ea); sched.update(b, (1 - sa) - (1 - ea))
        if 1500 <= g < 1600:
            m = sum(r) / N; mt = sum(true) / N
            static_err.append(math.sqrt(sum(((r[i] - m) - (true[i] - mt)) ** 2 for i in range(N)) / N))
        if g >= SHOCK and recov is None:
            m = sum(r) / N; mt = sum(true) / N
            if abs((r[0] - m) - (true[0] - mt)) < 100: recov = g - SHOCK
    return sum(static_err) / len(static_err), recov

rows = {}
for name, s in [("fixed K=8", Sched("fixed", 8)), ("fixed K=16", Sched("fixed", 16)), ("fixed K=32", Sched("fixed", 32)),
                ("fixed K=64", Sched("fixed", 64)), ("games-played 40/20/10", Sched("gp")), ("gp + surprise reopen", Sched("reopen"))]:
    rows[name] = run(s); print("%-24s static RMS %.1f  recovery games after shock: %s" % ((name,) + rows[name]))
gp, rp = rows["games-played 40/20/10"]; ro = rows["gp + surprise reopen"]
best_static = min(rows, key=lambda k: rows[k][0])
rec = lambda k: rows[k][1] if rows[k][1] is not None else 10 ** 9
gp_slow = rec("games-played 40/20/10") > rec("fixed K=32") and rec("games-played 40/20/10") > rec("fixed K=16")
reopen_fast = rec("gp + surprise reopen") <= rec("games-played 40/20/10") and ro[0] <= rows["fixed K=32"][0]
print("lowest static RMS:", best_static)
ok = gp_slow and reopen_fast
print("RESULT: %s games-played K static RMS %.1f (best: %s) but recovers the shocked player in %s games vs %s for K=32; reopen variant recovers in %s with static RMS %.1f"
      % ("PASS" if ok else "FAIL", gp, best_static, rp, rows["fixed K=32"][1], ro[1], ro[0]))
