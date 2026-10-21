"""STABLE-MATCHING/deferred-acceptance kernel: the proposing side gets its best stable
partner and only the receiving side can gain by misreporting. How OFTEN can a receiver gain,
and is the proposer side really never able to? 3,000 random 4x4 instances (deterministic
LCG); for every agent on both sides, try every one of the 24 preference orders as a lie
(others truthful), run proposer-optimal deferred acceptance, compare the true-preference
rank of the partner obtained. Exhaustive per instance.
PREDICTION (written before running): no proposer ever gains (0 instances); at least one
receiver can gain in 20-50% of instances; when the instance has a single stable matching,
no one can gain. Iteration 1 found only 4.7% with reordering lies; prediction for iteration 2,
written before its run: with truncation lies a receiver can gain in exactly the instances
that have more than one stable matching."""
import itertools
class LCG:
    def __init__(self, s): self.s = s
    def r(self, m): self.s = (6364136223846793005 * self.s + 1442695040888963407) % 2 ** 64; return (self.s >> 33) % m
def shuffle(g, xs):
    xs = xs[:]
    for i in range(len(xs) - 1, 0, -1):
        j = g.r(i + 1); xs[i], xs[j] = xs[j], xs[i]
    return xs
def da_t(P, R):        # receivers may list only some proposers (truncation); unlisted = unacceptable
    n = len(P); free = list(range(n)); nxt = [0] * n; held = [None] * n
    rank = [{m: i for i, m in enumerate(R[w])} for w in range(n)]
    while free:
        m = free.pop()
        if nxt[m] >= n: continue                       # exhausted: stays single
        w = P[m][nxt[m]]; nxt[m] += 1
        if m not in rank[w]: free.append(m); continue
        if held[w] is None: held[w] = m
        elif rank[w][m] < rank[w][held[w]]: free.append(held[w]); held[w] = m
        else: free.append(m)
    return held                                        # receiver -> proposer (or None)
def da(P, R):          # P[m] = list of receivers in order; R[w] = list of proposers; returns match proposer->receiver
    n = len(P); free = list(range(n)); nxt = [0] * n; held = [None] * n
    rank = [{m: i for i, m in enumerate(R[w])} for w in range(n)]
    while free:
        m = free.pop(); w = P[m][nxt[m]]; nxt[m] += 1
        if held[w] is None: held[w] = m
        elif rank[w][m] < rank[w][held[w]]: free.append(held[w]); held[w] = m
        else: free.append(m)
    return {held[w]: w for w in range(n)}
def stable_count(P, R):
    n = len(P); c = 0
    rp = [{w: i for i, w in enumerate(P[m])} for m in range(n)]; rr = [{m: i for i, m in enumerate(R[w])} for w in range(n)]
    for perm in itertools.permutations(range(n)):
        inv = {w: m for m, w in enumerate(perm)}
        if not any(rp[m][w] < rp[m][perm[m]] and rr[w][m] < rr[w][inv[w]] for m in range(n) for w in range(n)): c += 1
    return c
g = LCG(5); n = 4; T = 3000; recv_gain = prop_gain = recv_gain_single = singles = 0
orders = list(itertools.permutations(range(n)))
for _ in range(T):
    P = [shuffle(g, list(range(n))) for _ in range(n)]; R = [shuffle(g, list(range(n))) for _ in range(n)]
    base = da(P, R); inv = {w: m for m, w in base.items()}
    rg = False; pg = False
    for w in range(n):
        tr = {m: i for i, m in enumerate(R[w])}
        for lie in orders:
            R2 = R[:]; R2[w] = list(lie); m2 = {v: k for k, v in da(P, R2).items()}
            if tr[m2[w]] < tr[inv[w]]: rg = True; break
        if rg: break
    for m in range(n):
        tp = {w: i for i, w in enumerate(P[m])}
        for lie in orders:
            P2 = P[:]; P2[m] = list(lie)
            if tp[da(P2, R)[m]] < tp[base[m]]: pg = True; break
        if pg: break
    single = stable_count(P, R) == 1; singles += single
    recv_gain += rg; prop_gain += pg; recv_gain_single += rg and single
# iteration 2: truncation lies (keep the true order, declare only the first k acceptable)
g = LCG(5); trunc_gain = multi = 0
for _ in range(T):
    P = [shuffle(g, list(range(n))) for _ in range(n)]; R = [shuffle(g, list(range(n))) for _ in range(n)]
    base = da(P, R); inv = {w: m for m, w in base.items()}
    multi += stable_count(P, R) > 1
    gained = False
    for w in range(n):
        tr = {m: i for i, m in enumerate(R[w])}
        for k in range(1, n):
            got = da_t(P, [R[x] if x != w else R[w][:k] for x in range(n)])[w]
            if got is not None and tr[got] < tr[inv[w]]: gained = True; break
        if gained: break
    trunc_gain += gained
print(f"(iteration 2) truncation lies: a receiver can gain in {trunc_gain} ({trunc_gain / T:.1%}); instances with >1 stable matching {multi}")
share = recv_gain / T
ok = prop_gain == 0 and recv_gain_single == 0 and trunc_gain == multi
print(f"instances {T}: a receiver can gain in {recv_gain} ({share:.1%}); a proposer can gain in {prop_gain}; "
      f"single-stable-matching instances {singles}, receiver gain among them {recv_gain_single}")
print(f"RESULT: {'PASS' if ok else 'FAIL'} proposers never gain ({prop_gain}); receivers can gain in {share:.1%} of instances; "
      f"never when the stable matching is unique ({recv_gain_single}/{singles}); truncation lets a receiver gain in {trunc_gain} = every multi-stable instance ({multi}): {trunc_gain == multi}")
