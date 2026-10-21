"""Exact (Fraction) model of a group verdict on a binary question. Truth = A. Each member has an
independent signal that is right with prob q. Sequential public voting uses the cascade rule:
if the running lead is >= 2 vote with the lead, else vote own signal.
Compares Janis countermeasures: leader first vs leader last (withhold opinion), independent
simultaneous voting, k parallel independent groups, and a devil's advocate. Plus a Bezos-door cost check."""
from fractions import Fraction as F
from itertools import product

def sequential(qs):
    """qs: accuracy of each speaker in order. returns P(final majority == A) with ties counted half."""
    dist = {0: F(1)}   # lead = votesA - votesB
    for q in qs:
        nd = {}
        for lead, p in dist.items():
            if abs(lead) >= 2:
                nd[lead + (1 if lead > 0 else -1)] = nd.get(lead + (1 if lead > 0 else -1), 0) + p
            else:
                nd[lead + 1] = nd.get(lead + 1, 0) + p * q
                nd[lead - 1] = nd.get(lead - 1, 0) + p * (1 - q)
        dist = nd
    return sum(p if l > 0 else p / 2 if l == 0 else 0 for l, p in dist.items())

def simultaneous(qs):
    dist = {0: F(1)}
    for q in qs:
        nd = {}
        for lead, p in dist.items():
            nd[lead + 1] = nd.get(lead + 1, 0) + p * q
            nd[lead - 1] = nd.get(lead - 1, 0) + p * (1 - q)
        dist = nd
    return sum(p if l > 0 else p / 2 if l == 0 else 0 for l, p in dist.items())

def parallel_groups(qs_groups, sequential_inside=True):
    accs = [(sequential if sequential_inside else simultaneous)(g) for g in qs_groups]
    tot = F(0)
    for combo in product([0, 1], repeat=len(accs)):  # 1 = group says A
        p = F(1)
        for a, c in zip(accs, combo): p *= a if c else 1 - a
        s = sum(combo); n = len(accs)
        tot += p if 2 * s > n else p / 2 if 2 * s == n else 0
    return tot

q = F(7, 10); N = 7
res = []
members = [q] * (N - 1)
# S1 leader of ordinary accuracy
first = sequential([q] + members); last = sequential(members + [q]); sim = simultaneous([q] * N)
print(f"S1 equal accuracy q=.7 N=7: leader first {float(first):.4f}, leader last {float(last):.4f}, simultaneous {float(sim):.4f}")
res.append(sim > last and sim > first)
# S2 leader worse than members (q_L=.55): first hurts most, last is harmless-ish
ql = F(55, 100)
f2 = sequential([ql] + members); l2 = sequential(members + [ql])
print(f"S2 weak leader .55: first {float(f2):.4f}, last {float(l2):.4f}, simultaneous-with-leader {float(simultaneous([ql]+members)):.4f}")
res.append(l2 > f2)
# S3 BREAK: leader much better than members (.95 vs .6): leader first helps vs members only
qm = F(6, 10); qL = F(95, 100)
f3 = sequential([qL] + [qm] * 6); s3 = simultaneous([qL] + [qm] * 6)
print(f"S3 strong leader .95 vs members .6: leader first {float(f3):.4f}, simultaneous {float(s3):.4f}")
res.append(f3 > s3)   # countermeasure (withhold) HURTS here
# S4 parallel groups: 3 groups of 3 sequential vs 1 group of 9 sequential
pg = parallel_groups([[q] * 3] * 3); one = sequential([q] * 9)
print(f"S4 q=.7: 3 independent groups of 3: {float(pg):.4f}; one sequential group of 9: {float(one):.4f}; simultaneous 9: {float(simultaneous([q]*9)):.4f}")
res.append(pg > one)
# S5 Bezos door: process cost. Slow = simultaneous with N=7 plus cost c; fast = leader decides alone at q_L.
for loss, label in ((1, "two-way door (loss 1)"), (100, "one-way door (loss 100)")):
    cost = F(2, 10)   # cost of the heavy process in same units as loss=1
    fast = (1 - F(8, 10)) * loss     # lone high-judgment decider q=.8
    slow = (1 - simultaneous([q] * 7)) * loss + cost
    print(f"S5 {label}: fast expected loss {float(fast):.3f}, deliberation expected loss {float(slow):.3f} -> {'fast' if fast < slow else 'deliberate'}")
    res.append((fast < slow) == (loss == 1))
ok = all(res)
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" checks={res}")
