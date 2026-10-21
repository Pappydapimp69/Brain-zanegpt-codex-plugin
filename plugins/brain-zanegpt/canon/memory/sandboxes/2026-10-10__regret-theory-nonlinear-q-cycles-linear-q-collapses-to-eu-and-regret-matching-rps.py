"""Prediction (before run), 3 states, acts = payoff vectors, C = identity, A>=B iff sum_s p_s*Q(A_s-B_s) >= 0.
1) Q linear: over ALL triples of acts with payoffs in {0..4}^3 (125 acts, 1,953,125 triples) and uniform p, ZERO strict
   preference cycles, and the pairwise ranking equals expected-value ranking for every pair.
2) Q(x)=x^3: the cyclic-permutation triple (1,2,3),(2,3,1),(3,1,2) forms a strict cycle A>B>C>A; the count of cyclic
   triples over the grid is > 0 (my guess: a few thousand to tens of thousands). Q(x)=sign(x)sqrt|x| (concave in
   magnitude) also cycles, in the REVERSE direction on the same triple.
3) BREAKER: non-uniform p=(0.5,0.3,0.2) with cubic Q - the (1,2,3) triple cycle is NOT guaranteed; report whether it
   survives. Also with only two acts no cycle is possible for any Q (pairwise antisymmetric).
4) Sibling kernel (regret minimisation self-play): regret matching in rock-paper-scissors (two-player zero-sum),
   a game whose pairwise 'beats' relation is itself cyclic, has average strategies within 0.02 of (1/3,1/3,1/3)
   after 20000 deterministic iterations, i.e. cyclic structure does not stop regret minimisation converging.
Stdlib, deterministic, no RNG."""
import itertools, math
ok = True
def chk(n, c, d=""):
    global ok; ok &= bool(c); print(("PASS " if c else "FAIL ") + n, d)

def pref(A, B, Q, p):
    v = sum(ps * Q(a - b) for ps, a, b in zip(p, A, B))
    return 0 if abs(v) < 1e-12 else (1 if v > 0 else -1)
lin = lambda x: x
cub = lambda x: x ** 3
sq = lambda x: math.copysign(math.sqrt(abs(x)), x)
U = (1/3, 1/3, 1/3)
acts = list(itertools.product(range(5), repeat=3))
def table(Q, p):
    return {(i, j): pref(acts[i], acts[j], Q, p) for i in range(len(acts)) for j in range(len(acts))}
def cycles(T):
    n = len(acts); c = 0
    beats = [[j for j in range(n) if T[(i, j)] > 0] for i in range(n)]
    bset = [set(b) for b in beats]
    for a in range(n):
        for b in beats[a]:
            for cc in beats[b]:
                if a in bset[cc]: c += 1
    return c // 3
TL = table(lin, U)
ev = lambda A: sum(A) / 3
chk("S1 linear Q: ranking equals expected-value ranking on all pairs", all(TL[(i, j)] == (ev(acts[i]) > ev(acts[j])) - (ev(acts[i]) < ev(acts[j])) for i in range(len(acts)) for j in range(len(acts))))
c_lin = cycles(TL); chk("S1 linear Q: zero strict cycles", c_lin == 0, f"cycles={c_lin}")
TC = table(cub, U); c_cub = cycles(TC)
i1, i2, i3 = acts.index((1,2,3)), acts.index((2,3,1)), acts.index((3,1,2))
chk("S2 cubic Q: (1,2,3)>(2,3,1)>(3,1,2)>(1,2,3)", TC[(i1,i2)] > 0 and TC[(i2,i3)] > 0 and TC[(i3,i1)] > 0)
chk("S2 cubic Q: cycles exist over grid", c_cub > 0, f"cycles={c_cub}")
TS = table(sq, U); c_sq = cycles(TS)
chk("S2 concave-magnitude Q: reverse cycle on same triple", TS[(i1,i2)] < 0 and TS[(i2,i3)] < 0 and TS[(i3,i1)] < 0, f"cycles over grid={c_sq}")
P2 = (0.5, 0.3, 0.2)
TP = table(cub, P2); c_p = cycles(TP)
surv = TP[(i1,i2)] > 0 and TP[(i2,i3)] > 0 and TP[(i3,i1)] > 0
print(f"  breaker non-uniform p, cubic: triple cycle survives={surv}, grid cycles={c_p}")
chk("S3 non-uniform p: cycles still present on grid (not tied to uniform p)", c_p > 0, f"{c_p}")
two = all(not (TC[(i,j)] > 0 and TC[(j,i)] > 0) for i in range(len(acts)) for j in range(len(acts)))
chk("S3 two-act comparison is antisymmetric for nonlinear Q", two)
# S4 regret matching RPS
pay = [[0,-1,1],[1,0,-1],[-1,1,0]]   # row player payoff
def rm_avg(T=20000):
    reg = [[0.0]*3, [0.0]*3]; tot = [[0.0]*3, [0.0]*3]
    # deterministic asymmetric start to avoid trivial fixed point
    strat = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    for _ in range(T):
        for k in range(2): 
            for a in range(3): tot[k][a] += strat[k][a]
        u0 = [sum(pay[a][b]*strat[1][b] for b in range(3)) for a in range(3)]
        u1 = [sum(-pay[a][b]*strat[0][a] for a in range(3)) for b in range(3)]
        for k, u, s in ((0,u0,strat[0]),(1,u1,strat[1])):
            ev_ = sum(x*y for x,y in zip(u,s))
            for a in range(3): reg[k][a] += u[a]-ev_
        for k in range(2):
            pos = [max(r,0.0) for r in reg[k]]; z = sum(pos)
            strat[k] = [x/z for x in pos] if z > 0 else [1/3]*3
    return [[x/T for x in t] for t in tot]
avg = rm_avg()
dev = max(abs(x-1/3) for t in avg for x in t)
chk("S4 regret matching on cyclic RPS: average strategy within 0.02 of uniform", dev < 0.02, f"max dev={dev:.4f}")
print(f"RESULT: {'PASS' if ok else 'FAIL'} linear Q cycles={c_lin}; cubic Q cycles={c_cub} of {len(acts)} acts; sqrt Q reverses; skewed p cycles={c_p}; regret matching RPS dev={dev:.4f}")
