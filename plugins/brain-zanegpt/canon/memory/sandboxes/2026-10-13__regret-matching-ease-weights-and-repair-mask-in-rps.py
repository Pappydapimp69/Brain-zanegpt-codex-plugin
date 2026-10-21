"""Regret matching in rock-paper-scissors with ease-of-imagining weights w_a on the
regret of each action (strategy ~ w_a * R_a^+) and a repair mask (actions with no repair path
accrue no regret). Deterministic expected-value self-play, no RNG."""
A = [[0, -1, 1], [1, 0, -1], [-1, 1, 0]]  # row payoff: R,P,S ; R<P, P<S, S<R

def run(w, mask, T=20000, init=(1.0, 0.0, 0.0)):
    reg = [[0.0] * 3 for _ in range(2)]
    cum = [[0.0] * 3 for _ in range(2)]
    strat = [list(init), [0.0, 1.0, 0.0]]
    for t in range(T):
        for p in range(2):
            for a in range(3): cum[p][a] += strat[p][a]
        u0 = [sum(A[a][b] * strat[1][b] for b in range(3)) for a in range(3)]
        u1 = [sum(A[a][b] * strat[0][b] for b in range(3)) for a in range(3)]  # symmetric game
        for p, u in ((0, u0), (1, u1)):
            ev = sum(strat[p][a] * u[a] for a in range(3))
            for a in range(3):
                if mask[a]: reg[p][a] += u[a] - ev
        for p in range(2):
            pos = [w[a] * max(reg[p][a], 0.0) for a in range(3)]
            s = sum(pos)
            strat[p] = [x / s for x in pos] if s > 0 else [1 / 3] * 3
    avg = [[c / T for c in cum[p]] for p in range(2)]
    return avg

def dist(avg):  # distance from uniform, worst player
    return max(max(abs(x - 1 / 3) for x in avg[p]) for p in range(2))

def exploit(avg):  # best-response gain of opponent against player-0 average
    return max(sum(A[a][b] * avg[0][b] for b in range(3)) for a in range(3))

res = []
base = run([1, 1, 1], [1, 1, 1])
print(f"S1 plain regret matching: max dev from uniform {dist(base):.4f}, exploitability {exploit(base):.4f}")
res.append(dist(base) < 0.02)
for wv in ([1, 3, 1], [1, 10, 1], [5, 5, 5]):
    r = run(wv, [1, 1, 1])
    print(f"S2 ease weights {wv}: dev {dist(r):.4f}, exploitability {exploit(r):.4f}, avg {[round(x,3) for x in r[0]]}")
r_eq = run([5, 5, 5], [1, 1, 1])
res.append(abs(dist(r_eq) - dist(base)) < 1e-6)  # uniform scale is a no-op
r3 = run([1, 3, 1], [1, 1, 1]); r10 = run([1, 10, 1], [1, 1, 1])
res.append(dist(r3) < 0.05 and dist(r10) < 0.05)   # predicted: still converges, since only the relative size matters
m = run([1, 1, 1], [1, 0, 1])   # BREAK: action 1 (paper) has no repair path -> never regretted
print(f"S3 repair mask kills regret of Paper: dev {dist(m):.4f}, exploitability {exploit(m):.4f}, avg {[round(x,3) for x in m[0]]}")
res.append(dist(m) > 0.1)
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" checks={res}")
