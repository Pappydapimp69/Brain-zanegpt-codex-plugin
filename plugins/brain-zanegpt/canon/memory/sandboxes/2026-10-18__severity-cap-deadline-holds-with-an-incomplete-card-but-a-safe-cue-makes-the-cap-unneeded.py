# Composes escalation-needs-matching-distance (gate exp(-((d-I/C)/0.25)^2), habituation exp(-0.2X), six beats, C 10),
# incomplete-rule-card-keeps-go-big-only-with-a-safe-cue-backstop (card covers each beat with prob p; uncovered beats
# fall back to grounded d 0.3; a safe cue c lifts g to g+c(1-g)) and late-severity-cap-deadline-is-the-schedule-midpoint
# (a severity cap on a ramp must land by about the schedule midpoint). Added: the cap clamps severity at level*C from
# beat L (1-based) onward on a linear 2->10 ramp. Exact expectation over all 2^6 coverage patterns, no RNG.
# PREDICTION (before run): with p=0.5 and no cue, capping at 0.5*C helps (gain over uncapped > 0.3) when it lands by
# beat 3 (midpoint) and gains under 0.1 once L >= 5; with the permanent cue 0.7 the best cap gain at any L is under 0.3
# (cue makes the cap unneeded). BREAK: at p=1.0 (full card) a cap never helps (gain <= 0 at every L).
import itertools, math
C, N = 10.0, 6
RAMP = [2 + 8 * k / 5 for k in range(N)]
def score(seq, covered, cue):
    X = tot = 0.0
    for I, cov in zip(seq, covered):
        d = I / C if cov else 0.3
        g = math.exp(-((d - I / C) / 0.25) ** 2)
        if not cov: g = g + cue * (1 - g)
        tot += math.exp(-0.2 * X) * (I / C) * g; X += 1 / (1 + I / 5)
    return tot
def capped(L, level):
    return [min(s, level * C) if i + 1 >= L else s for i, s in enumerate(RAMP)]
def expected(seq, p, cue):
    e = 0.0
    for cov in itertools.product((0, 1), repeat=N):
        w = 1.0
        for c in cov: w *= p if c else 1 - p
        e += w * score(seq, cov, cue)
    return e
def gains(p, cue, level=0.5):
    base = expected(RAMP, p, cue)
    return {L: expected(capped(L, level), p, cue) - base for L in range(1, N + 1)}
out = {}
for p, cue in ((0.0, 0.0), (0.5, 0.0), (0.5, 0.7), (1.0, 0.0), (1.0, 0.7)):
    out[(p, cue)] = gains(p, cue)
    print(f"p {p} cue {cue}: gain by cap-start beat " + " ".join(f"L{L} {v:+.2f}" for L, v in out[(p, cue)].items()))
g = out[(0.5, 0.0)]
ok = (g[3] > 0.3 and g[5] < 0.1 and max(out[(0.5, 0.7)].values()) < 0.3 and max(out[(1.0, 0.0)].values()) <= 0)
print(f"RESULT: {'PASS' if ok else 'FAIL'} p.5 no cue gain L3 {g[3]:+.2f} L5 {g[5]:+.2f}; p.5 cue best {max(out[(0.5,0.7)].values()):+.2f}; full card best {max(out[(1.0,0.0)].values()):+.2f}")
