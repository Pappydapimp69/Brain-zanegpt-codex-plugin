"""Sandbox (train gap, SEARCH-THEORY kernel): split a fixed test-time budget over
suspect modules where one module hides a bug with prior p_i and testing for e
hours finds it with 1 - exp(-w e). Different fixture from seven/E50 (ring of
night-search sectors): a geometric prior over 12 modules, no spatial structure.
Policies: CONCENTRATE (all on module 0), UNIFORM over all 12, GREEDY marginal
(unit by unit, largest p_i*w*exp(-w e_i)). Exact, no RNG.
PREDICTION (before first run): modules receiving effort grow with the budget
(budget 1h -> 1-2 modules, 12h -> at least 4, 48h -> all 12); greedy P(find) >=
both others in every case; after greedy, p_i*exp(-w e_i) is level (spread < one
unit's step) across searched modules and the unsearched ones sit below that level
(E47: failed search lowers, not clears). BREAK: a sharp prior (r=0.3) with a tiny
budget makes CONCENTRATE equal to greedy, so 'spread' is not universal."""
import math

UNIT = 0.25
def prior(r, n=12):
    raw = [r ** i for i in range(n)]; t = sum(raw); return [x / t for x in raw]

def pfind(p, e, w): return sum(pi * (1 - math.exp(-w * ei)) for pi, ei in zip(p, e))

def greedy(p, w, budget):
    e = [0.0] * len(p)
    for _ in range(int(round(budget / UNIT))):
        i = max(range(len(p)), key=lambda k: p[k] * math.exp(-w * e[k]))
        e[i] += UNIT
    return e

def run(r, w, budget):
    p = prior(r)
    g = greedy(p, w, budget)
    c = [budget] + [0.0] * 11
    u = [budget / 12] * 12
    return p, g, pfind(p, c, w), pfind(p, u, w), pfind(p, g, w)

rows = []
for r, budget in [(0.8, 1), (0.8, 12), (0.8, 48), (0.5, 1), (0.5, 12), (0.5, 48), (0.3, 0.5)]:
    p, g, c, u, o = run(r, 0.6, budget)
    k = sum(1 for x in g if x > 0)
    rows.append((r, budget, k, c, u, o))
    print(f"prior r={r} budget {budget}h: modules searched {k}, concentrate {c:.3f} uniform {u:.3f} greedy {o:.3f}")

# leveling: posterior-unnormalised p*exp(-w e) across searched vs unsearched
p, g, *_ = run(0.8, 0.6, 12)
post = [pi * math.exp(-0.6 * ei) for pi, ei in zip(p, g)]
srch = [x for x, ei in zip(post, g) if ei > 0]; uns = [x for x, ei in zip(post, g) if ei == 0]
step = max(srch) - min(srch)
print(f"level spread among searched {step:.4f} (one-unit factor {1-math.exp(-0.6*UNIT):.3f}*max); max unsearched {max(uns) if uns else 0:.4f} <= min searched {min(srch)*math.exp(-0.6*UNIT):.4f}+")

k = {(r, b): kk for r, b, kk, *_ in rows}
grow = k[(0.8, 1)] <= 2 and k[(0.8, 12)] >= 4 and k[(0.8, 48)] == 12 and k[(0.5, 1)] <= k[(0.5, 12)] <= k[(0.5, 48)]
dominates = all(o >= c - 1e-12 and o >= u - 1e-12 for *_, c, u, o in rows)
level = step <= max(srch) * (1 - math.exp(-0.6 * UNIT)) + 1e-9 and (not uns or max(uns) <= max(srch))
brk = abs(rows[-1][3] - rows[-1][5]) < 0.02 and rows[-1][2] <= 2
print(f"RESULT: {'PASS' if grow and dominates and level and brk else 'FAIL'} searched modules grow {k[(0.8,1)]}->{k[(0.8,12)]}->{k[(0.8,48)]} (r=.8); greedy >= others in {sum(1 for *_,c,u,o in rows if o>=max(c,u)-1e-12)}/{len(rows)}; levelled; sharp prior tiny budget concentrate {rows[-1][3]:.3f} vs greedy {rows[-1][5]:.3f}")
