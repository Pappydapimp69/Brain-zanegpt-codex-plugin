# Deterministic funnel: friction vs merit, felt-wound motivation, correlated vs independent step gates.
N = 1000
tol = [(k + 0.5) / N for k in range(N)]                 # tolerance for effort, uniform
need = [((k * 37) % N + 0.5) / N for k in range(N)]     # value needed to keep using, uniform, decorrelated from tol

def adopt(cost, value, bonus=0.0):
    return sum(1 for k in range(N) if tol[k] + bonus >= cost and need[k] <= value)

# 1) merit tool: value .9 but 5-step setup (total cost .6); simple tool: value .6, one command (cost .1)
A = adopt(0.6, 0.9); B = adopt(0.1, 0.6)
# 2) BREAK: reader felt the wound first -> +0.4 tolerance
Aw = adopt(0.6, 0.9, 0.4); Bw = adopt(0.1, 0.6, 0.4)
# 3) tool needs value exactly 1.0 never matters: zero-friction tool with value 0.05 -> friction is not the whole story
C = adopt(0.0, 0.05)
# 4) five gates each passed at tolerance >= .2 : same-tolerance (correlated) vs shifted orderings (independent)
corr = sum(1 for k in range(N) if tol[k] >= 0.2)
def ind_pass(k):
    return all(((k * m) % N + 0.5) / N >= 0.2 for m in (1, 37, 101, 211, 307))
indep = sum(1 for k in range(N) if ind_pass(k))
prod = N * (0.8 ** 5)
print(f"friction: merit-tool {A} vs simple-tool {B}")
print(f"after felt wound (+0.4 tolerance): merit-tool {Aw} vs simple-tool {Bw}")
print(f"zero-friction junk tool: {C}")
print(f"five-gate funnel: correlated {corr}, independent {indep}, product-rule {prod:.0f}")
ok = A < B and Aw > Bw and C < B and corr > 2 * indep and abs(indep - prod) < 60
print(f"RESULT: {'PASS' if ok else 'FAIL'} merit {A} < simple {B}; wound flips {Aw} > {Bw}; junk {C}; gates corr {corr} vs indep {indep} vs product {prod:.0f}")
