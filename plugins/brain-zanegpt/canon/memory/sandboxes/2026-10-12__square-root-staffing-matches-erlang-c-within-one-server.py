"""Seed sandbox for a new domain, QUEUEING-THEORY.
Claim: square-root staffing s = ceil(R + beta*sqrt(R)), with beta solving the
Halfin-Whitt limit alpha = 1/(1 + beta*Phi(beta)/phi(beta)), lands within one
server of the exact Erlang C minimum for a target P(wait) <= alpha; pooling
two loads saves about beta*(2 - sqrt 2)*sqrt(R) servers.
Exact and deterministic: Erlang C (Wikipedia 'Erlang (unit)') is cross-checked
against a directly solved M/M/s birth-death chain."""
import math
def erlang_c(R, s):
    if s <= R: return 1.0
    # stable recursion: Erlang B then C
    b = 1.0
    for k in range(1, s + 1): b = R * b / (k + R * b)
    return s * b / (s - R * (1 - b))
def chain(R, s):
    p = [1.0]
    n = 1
    while True:
        p.append(p[-1] * R / min(n, s))
        if n > s and p[-1] < 1e-18 * sum(p): break
        n += 1
    return sum(p[s:]) / sum(p)
Phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
phi = lambda x: math.exp(-x * x / 2) / math.sqrt(2 * math.pi)
def beta_for(alpha):
    lo, hi = 0.0, 6.0
    for _ in range(100):
        m = (lo + hi) / 2
        if 1 / (1 + m * Phi(m) / phi(m)) > alpha: lo = m
        else: hi = m
    return (lo + hi) / 2
def exact_s(R, alpha):
    s = math.floor(R) + 1
    while erlang_c(R, s) > alpha: s += 1
    return s
# 1) formula vs chain
maxerr = 0.0
for R in (0.5, 1, 2, 5, 10, 20, 50, 100):
    for s in range(math.floor(R) + 1, math.floor(R) + 1 + 12):
        maxerr = max(maxerr, abs(erlang_c(R, s) - chain(R, s)))
print(f"1) Erlang C vs birth-death chain: max |diff| {maxerr:.2e}")
# 2) betas
alphas = (0.5, 0.2, 0.05, 0.01)
betas = {a: beta_for(a) for a in alphas}
print("2) beta for alpha:", {a: round(b, 3) for a, b in betas.items()})
# 3) rule vs exact over R
Rs_big = (5, 10, 20, 50, 100, 200, 500)
Rs_small = (0.5, 1, 2, 3)
worst_big = 0; worst_small = 0; rows = []
for a in alphas:
    for R in Rs_small + Rs_big:
        rule = math.ceil(R + betas[a] * math.sqrt(R)); ex = exact_s(R, a); d = rule - ex
        rows.append((a, R, rule, ex, d))
        if R in Rs_big: worst_big = max(worst_big, abs(d))
        else: worst_small = max(worst_small, abs(d))
for a in alphas:
    print(f"3) alpha {a}: " + " ".join(f"R{R}:{r}/{e}" for aa, R, r, e, d in rows if aa == a) + "  (rule/exact)")
# limit check: exact P(wait) at s = R + beta*sqrt(R) (non-integer avoided via large R)
lim = {a: erlang_c(10000, round(10000 + betas[a] * 100)) for a in alphas}
print("   P(wait) at R=10000, s=R+beta*sqrt(R):", {a: round(v, 4) for a, v in lim.items()})
# 5) pooling
R = 100; a = 0.2
two = 2 * exact_s(R, a); one = exact_s(2 * R, a); pred = betas[a] * (2 - math.sqrt(2)) * math.sqrt(R)
print(f"5) pooling R=100 x2 at alpha .2: separate {two}, pooled {one}, saved {two-one} vs sqrt-rule {pred:.2f}")
ok1 = maxerr < 1e-12
ok3 = worst_big <= 1
ok4 = worst_small <= 1
ok5 = abs((two - one) - pred) <= 2
short = sum(1 for r in rows if r[4] < 0); over = sum(1 for r in rows if r[4] > 0)
print(f"rule short of exact in {short}/{len(rows)} cells, over in {over}; rule+1 never short: {all(r[4] >= -1 for r in rows)}")
print(f"checks: formula==chain {ok1}; rule within 1 for R>=5 {ok3} (worst {worst_big}); within 1 for R<=3 {ok4} (worst {worst_small}); pooling {ok5}")
held = sum((ok1, ok3, ok4, ok5))
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; rule short {short}/{len(rows)} over {over}; worst rule error R>=5 {worst_big}, R<=3 {worst_small}; pooling saved {two-one} vs {pred:.1f}; betas {[round(betas[a],2) for a in alphas]}")
