import heapq, itertools
# Prediction (before run): over all 720 declaration orders of a 6-node DAG, a lexicographic-heap Kahn gives 1 distinct
# output and a (depth, name) composite sort gives 1 distinct output, but the two canonical outputs DIFFER from each other
# (a,b,c,d,e,f vs a,b,c,d,f,e). A chained stable sort written in reading order (depth, then name) is name-major: valid
# on the alphabetical labelling (0 invalid of 720) but INVALID on a relabelled graph whose names run against the edges.
EDGES = {"c": ["a"], "d": ["a", "b"], "e": ["c", "d"], "f": ["b"], "a": [], "b": []}  # node: prerequisites
def relabel(m): return {m[k]: [m[p] for p in v] for k, v in EDGES.items()}
REV = relabel(dict(zip("abcdef", "fedcba")))
def depth(g):
    memo = {}
    def d(n):
        if n not in memo: memo[n] = 0 if not g[n] else 1 + max(d(p) for p in g[n])
        return memo[n]
    return {n: d(n) for n in g}
def valid(order, g):
    pos = {n: i for i, n in enumerate(order)}
    return all(pos[p] < pos[n] for n in g for p in g[n])
def kahn_lex(order, g):
    indeg = {n: len(g[n]) for n in order}; ready = [n for n in order if indeg[n] == 0]; heapq.heapify(ready); out = []
    while ready:
        n = heapq.heappop(ready); out.append(n)
        for m in order:
            if n in g[m]:
                indeg[m] -= 1
                if indeg[m] == 0: heapq.heappush(ready, m)
    return out
def composite(order, g):
    d = depth(g); return sorted(order, key=lambda n: (d[n], n))
def chain_correct(order, g):
    d = depth(g); o = sorted(order, key=lambda n: n); return sorted(o, key=lambda n: d[n])  # least significant (name) first
def chain_reading(order, g):
    d = depth(g); o = sorted(order, key=lambda n: d[n]); return sorted(o, key=lambda n: n)  # reading order -> name-major
def sweep(fn, g):
    outs = set(); bad = 0
    for p in itertools.permutations(sorted(g)):
        o = tuple(fn(list(p), g)); outs.add(o); bad += (not valid(o, g))
    return outs, bad
res = {}
for name, fn in (("kahn_lex", kahn_lex), ("composite", composite), ("chain_ok", chain_correct), ("chain_reading", chain_reading)):
    for gname, g in (("alpha", EDGES), ("reversed", REV)):
        outs, bad = sweep(fn, g); res[(name, gname)] = (len(outs), bad); print(name, gname, "distinct", len(outs), "invalid", bad)
k = tuple(kahn_lex(list("abcdef"), EDGES)); c = tuple(composite(list("abcdef"), EDGES))
print("canonical outputs differ:", "".join(k), "vs", "".join(c))
ok = (res[("kahn_lex", "alpha")] == (1, 0) and res[("composite", "alpha")] == (1, 0) and k != c
      and res[("chain_ok", "alpha")][0] == 1 and res[("chain_ok", "reversed")][1] == 0
      and res[("chain_reading", "alpha")][1] == 0 and res[("chain_reading", "reversed")][1] == 720)
print("RESULT: %s kahn-lex 1 distinct, depth-name composite 1 distinct but %s vs %s; reading-order chain invalid 0/720 on alphabetical labels, %d/720 on reversed labels"
      % ("PASS" if ok else "FAIL", "".join(k), "".join(c), res[("chain_reading", "reversed")][1]))
