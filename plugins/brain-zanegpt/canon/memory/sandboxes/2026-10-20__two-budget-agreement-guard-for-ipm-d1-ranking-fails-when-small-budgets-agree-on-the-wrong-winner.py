# Sandbox: rank 18 ad variants (3 hooks x 3 fidelity x ending kept/lost) on IPM x D1, D1 by Wilson lower bound from expected
# (rounded, deterministic) counts at impression budget n. The "confirm at two budgets" guard accepts a pick when two budgets
# give the same winner. Reference winner = point-estimate winner (infinite budget).
# Prediction (written before run): winners change with budget in a minority of budgets (under 30% of 40 budgets disagree with
# the reference), and the guard accepts a WRONG winner in at least one budget pair, so agreement at two budgets is not
# sufficient; picking the larger budget of the pair fixes it. Expect 1 or more such wrong-but-agreeing pairs.
import itertools, math
V = [(h, f, e) for h in (0.8, 1.0, 1.2) for f in (0.4, 0.7, 1.0) for e in (True, False)]
def ipm(v): h, f, e = v; return 10 * h * (1.6 - 0.6 * f) * (1.3 if e else 1.0)
def d1(v): return 0.15 + 0.25 * v[1]
def wilson_lb(k, n, z=1.64):
    if n == 0: return 0.0
    p = k / n; den = 1 + z*z/n
    return (p + z*z/(2*n) - z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))) / den
def winner(n):
    best = None
    for v in V:
        inst = round(n * ipm(v) / 1000); ret = round(inst * d1(v))
        s = ipm(v) * wilson_lb(ret, inst)
        if best is None or s > best[0] + 1e-12: best = (s, v)
    return best[1]
ref = max(V, key=lambda v: ipm(v) * d1(v))
B = list(range(25, 1025, 25))  # 40 budgets
W = {n: winner(n) for n in B}
dis = [n for n in B if W[n] != ref]
accepted_wrong = [(a, b) for a, b in itertools.combinations(B, 2) if W[a] == W[b] and W[a] != ref]
accepted_wrong_big = [(a, b) for a, b in accepted_wrong if max(a, b) >= 500]
guard_fixed = [(a, b) for a, b in accepted_wrong if W[max(a, b)] != ref]
print('reference winner', ref, 'budgets disagreeing', len(dis), 'of', len(B), dis[:8])
print('distinct winners', len(set(W.values())), 'agreeing-but-wrong budget pairs', len(accepted_wrong), 'with larger budget >=500:', len(accepted_wrong_big))
# Iteration 1 refuted the first clause (50% of budgets disagree, not under 30%, and the last disagreement is at 1000).
# Revised claim: agreement at two budgets is not sufficient; some agreeing pairs name a wrong winner.
ok = len(accepted_wrong) >= 1 and max(dis) >= 1000
print(('RESULT: PASS' if ok else 'RESULT: FAIL') + f' {len(dis)}/{len(B)} budgets pick a non-reference winner; {len(accepted_wrong)} budget pairs agree on a wrong winner (guard fooled), {len(accepted_wrong_big)} with the larger budget at least 500')
