"""Toy: 10 beats, 40% severe (0.9 harm) / 60% mild (0.3). Distance d in [0,1] per beat.
Severe beat is funny only if d >= 0.7 (needs distance): funny = 1.0 if ok else -(0.7-d)*4.
Mild beat is funny when close: funny = 1.0 - d (closeness) .
Rule card covers fraction f of severe beats (a covered severe beat is kept as written; an uncovered
severe beat is delivered safe only if a safe cue backstop exists, else it lands at -0.5 harm penalty).
Strategies: GLOBAL (one d for whole sketch, best of grid) vs PER-BEAT (severe d=0.8, mild d=0.1)."""
import itertools
N = 10; SEV = 4
def beat_score(kind, d, covered, cue):
    if kind == "severe":
        base = 1.0 if d >= 0.7 else -(0.7 - d) * 4
        if not covered and not cue: base -= 0.5
        return base
    return 1.0 - d
def total(d_sev, d_mild, f, cue, per_beat):
    cov = round(f * SEV); s = 0.0
    for i in range(N):
        if i < SEV: s += beat_score("severe", d_sev, i < cov, cue)
        else: s += beat_score("mild", d_mild, True, cue)
    return s / N
grid = [i/10 for i in range(11)]
def best_global(f, cue):
    return max(total(d, d, f, cue, False) for d in grid)
def per_beat(f, cue): return total(0.8, 0.1, f, cue, True)
ok_rows = []
for cue in (False, True):
    for f in (0.0, 0.5, 1.0):
        g, p = best_global(f, cue), per_beat(f, cue)
        print(f"cue={cue} coverage={f}: global-best {g:.2f} per-beat {p:.2f} gain {p-g:+.2f}")
        ok_rows.append((cue, f, g, p))
gain50 = [r for r in ok_rows if not r[0] and r[1]==0.5][0]
gain0c = [r for r in ok_rows if r[0] and r[1]==0.0][0]
# BREAK: if mild beats do not reward closeness (flat 0.5) per-beat shouldn't help -> checked in a variant
def total_nocloseness(f, cue, d_sev, d_mild):
    cov = round(f*SEV); s = 0
    for i in range(N):
        s += beat_score("severe", d_sev, i < cov, cue) if i < SEV else 0.5
    return s/N
g_nc = max(total_nocloseness(0.5, False, d, d) for d in grid); p_nc = total_nocloseness(0.5, False, 0.8, 0.1)
print(f"BREAK no closeness reward for mild: global-best {g_nc:.2f} per-beat {p_nc:.2f} gain {p_nc-g_nc:+.2f}")
ok = (gain50[3]-gain50[2] >= 0.3) and (gain0c[3]-gain0c[2] > 0) and abs(p_nc-g_nc) < 1e-9
print(f"RESULT: {'PASS' if ok else 'FAIL'} per-beat distance gain at 50% coverage {gain50[3]-gain50[2]:+.2f}, with cue at 0% coverage {gain0c[3]-gain0c[2]:+.2f}, no-closeness break {p_nc-g_nc:+.2f}")
