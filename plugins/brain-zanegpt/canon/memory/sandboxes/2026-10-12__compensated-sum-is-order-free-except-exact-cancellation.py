"""Gap from the review of seven E90: Python 3.12+ sum() of floats is compensated
(Neumaier) - is it therefore ORDER-FREE? Own fixture: 40 lists of 8 floats from
a seeded LCG, magnitudes spread over 1e-3..1e16 with random signs; every list
summed in 200 seeded orderings by (a) sum(), (b) a plain += loop, (c) math.fsum.
PREDICTION (written before running): fsum gives exactly 1 distinct value for
every list; the plain loop gives > 1 distinct value for most lists (>= 30/40);
sum() gives > 1 distinct value for at least 5/40 lists (compensated, not
exact) but fewer distinct values than the loop overall. Break scenario: 40
lists of 8 floats of similar magnitude (1..2) - all three nearly order-free?
I expect the loop still varies in the last bit on some lists.
ITERATION 1 refuted the sum() part: 0/40 wide and 0/40 narrow lists were
order-dependent with sum(). ITERATION 2 PREDICTION (written before running
it): order dependence in sum() needs a huge term that EXACTLY cancels (x and
-x, x ~ 1e16) beside small terms; with such a pair in each list sum() is
order-dependent in >= 10/40 lists, still fewer distinct values than the loop.
"""
import math, random, sys
print("python", sys.version.split()[0])
if sys.version_info < (3, 12): print("NOTE: pre-3.12 sum() is a plain loop; this fixture assumes 3.12+")
rng = random.Random(20261012)
def loop(xs):
    acc = 0.0
    for x in xs: acc += x
    return acc
def study(make):
    multi = {"sum": 0, "loop": 0, "fsum": 0}; distinct = {"sum": 0, "loop": 0, "fsum": 0}
    for _ in range(40):
        xs = make(); seen = {"sum": set(), "loop": set(), "fsum": set()}
        for _ in range(200):
            p = xs[:]; rng.shuffle(p)
            seen["sum"].add(sum(p)); seen["loop"].add(loop(p)); seen["fsum"].add(math.fsum(p))
        for k in seen:
            distinct[k] += len(seen[k]); multi[k] += len(seen[k]) > 1
    return multi, distinct
wide = lambda: [rng.choice((-1, 1))*10**rng.uniform(-3, 16) for _ in range(8)]
narrow = lambda: [rng.uniform(1, 2) for _ in range(8)]
cancel = lambda: (lambda x: [x, -x] + [rng.uniform(0.1, 9) for _ in range(6)])(10**rng.uniform(15, 17))
mw, dw = study(wide); mn, dn = study(narrow); mc, dc = study(cancel)
print("wide magnitudes : lists with >1 value", mw, "total distinct", dw)
print("narrow (1..2)   : lists with >1 value", mn, "total distinct", dn)
print("cancelling pair : lists with >1 value", mc, "total distinct", dc)
it1 = mw["fsum"] == 0 and mw["loop"] >= 30 and mw["sum"] >= 5
it2 = mc["sum"] >= 10 and dc["sum"] < dc["loop"] and mc["fsum"] == 0
print("iteration 1 prediction held:", it1, "| iteration 2 held:", it2)
print(f"RESULT: {'PASS' if it2 else 'FAIL'} sum() order-dependent in wide {mw['sum']}/40, narrow {mn['sum']}/40, cancelling-pair {mc['sum']}/40 lists (loop {mw['loop']}/{mn['loop']}/{mc['loop']}, fsum {mw['fsum']}/{mn['fsum']}/{mc['fsum']})")
