"""Toy model: rank 10 ad recuts (engine-first batch, 8 engines) on IPM x D1 vs IPM,
at two impression budgets. Does the top-3 collapse onto one comic engine, and what
does a per-engine cap of 1 cost in true value?  Deterministic (seeded)."""
import random
ENGINES = 8
N = 10
TRIALS = 2000

def run(budget, corr, seed, skew=False):
    rnd = random.Random(seed)
    rep = 0; rep_cap = 0; loss = 0.0; n = 0
    for t in range(TRIALS):
        eng_q = [rnd.random() for _ in range(ENGINES)]       # engine strength
        ideas = []
        for i in range(N):
            e = i % ENGINES if i < ENGINES else rnd.randrange(ENGINES)
            if skew and i < 4: e = 0
            q = corr * eng_q[e] + (1 - corr) * rnd.random()
            ctr = 0.02 + 0.04 * q                            # true IPM-ish rate
            d1 = 0.15 + 0.25 * (corr * eng_q[e] + (1 - corr) * rnd.random())
            ideas.append((e, ctr, d1))
        def obs(x):
            e, ctr, d1 = x
            inst = sum(rnd.random() < ctr for _ in range(budget))
            ret = sum(rnd.random() < d1 for _ in range(max(inst, 1)))
            return (inst / budget) * (ret / max(inst, 1))
        score = sorted(range(N), key=lambda i: -obs(ideas[i]))
        top = score[:3]
        engs = [ideas[i][0] for i in top]
        if len(set(engs)) < 3: rep += 1
        # cap 1 per engine
        seen = set(); capped = []
        for i in score:
            if ideas[i][0] not in seen:
                seen.add(ideas[i][0]); capped.append(i)
            if len(capped) == 3: break
        tv = lambda ids: sum(ideas[i][1] * ideas[i][2] for i in ids)
        loss += (tv(top) - tv(capped)) / tv(top)
        n += 1
    return rep / n, loss / n

res = {}
for budget in (300, 1000):
    for corr in (0.0, 0.5, 0.9):
        res[(budget, corr)] = run(budget, corr, 7)
        print(f"budget={budget} engine-corr={corr}: top3 repeats an engine in {res[(budget,corr)][0]*100:.1f}% of batches; cap-1 value loss {res[(budget,corr)][1]*100:.1f}%")
sk = run(1000, 0.9, 7, skew=True)
print(f"BREAK skewed 4 of 10 ideas on one engine, corr 0.9, budget 1000: repeat {sk[0]*100:.1f}%, cap-1 loss {sk[1]*100:.1f}%")
base = res[(1000, 0.0)][0]
hi = res[(1000, 0.9)][0]
ok = hi > base + 0.10 and res[(1000, 0.9)][1] < 0.15 and sk[1] < 0.15
print(f"RESULT: {'PASS' if ok else 'FAIL'} repeat rate {base*100:.1f}% at corr 0 vs {hi*100:.1f}% at corr 0.9 (budget 1000); cap-1 loss {res[(1000,0.9)][1]*100:.1f}%; skewed-layout loss {sk[1]*100:.1f}%")
