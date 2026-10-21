# Sandbox: ddmin over 12 config items with a failure predicate. Three failure shapes: AND of 2 items, OR of 2 independent items,
# OR of 3. Loop = ddmin, delete the found culprit(s), re-run until the failure is gone. Then a positive control: run the
# predicate on a synthetic state; a faithful state keeps all fields, a lazy one drops the field one cause reads.
# Prediction (written before run): ddmin returns both items for AND in 66/66 pairs, exactly one item for OR in 66/66 pairs,
# delete-and-rerun then finds every cause (66/66 OR pairs in 2 rounds, 220/220 OR-3 triples in 3 rounds), and a lazy control
# lacking one cause's field wrongly blames the predicate in exactly the pairs where that cause is the one under test (33 of 66 ordered... counted below).
import itertools
N = 12; ITEMS = list(range(N))
def ddmin(items, fails):
    n = 2
    while len(items) >= 2:
        sz = max(len(items) // n, 1); chunks = [items[i:i+sz] for i in range(0, len(items), sz)]; reduced = False
        for c in chunks:
            if fails(c): items, n, reduced = c, 2, True; break
        if not reduced:
            for c in chunks:
                comp = [x for x in items if x not in c]
                if comp and fails(comp): items, n, reduced = comp, max(n-1, 2), True; break
        if not reduced:
            if n >= len(items): break
            n = min(len(items), n*2)
    return items
def run(shape, causes):
    full = ITEMS[:]; found = []; rounds = 0
    f = (lambda s: all(c in s for c in causes)) if shape == 'and' else (lambda s: any(c in s for c in causes))
    while f(full):
        r = ddmin(full[:], f); found += r; full = [x for x in full if x not in r]; rounds += 1
    return found, rounds
bad = {'and_whole': 0, 'or_one': 0, 'or_all': 0, 'or3_all': 0}; tot_and = tot_or = tot_or3 = 0
for a, b in itertools.combinations(ITEMS, 2):
    tot_and += 1; f, _ = run('and', (a, b)); bad['and_whole'] += set(f) != {a, b}
    tot_or += 1
    r1 = ddmin(ITEMS[:], lambda s: a in s or b in s); bad['or_one'] += len(r1) != 1
    f, rounds = run('or', (a, b)); bad['or_all'] += set(f) != {a, b} or rounds != 2
for t in itertools.combinations(ITEMS, 3):
    tot_or3 += 1; f, rounds = run('or', t); bad['or3_all'] += set(f) != set(t) or rounds != 3
# positive control: predicate reads field per cause; lazy synthetic state lacks the field for cause b
mis = same = 0
for a, b in itertools.combinations(ITEMS, 2):
    state_faithful = {a: 1, b: 1}; state_lazy = {a: 1}
    pred = lambda st: a in st or b in st
    # control for cause b: "does the predicate fire when only b's field is present?"
    ok_f = pred({b: 1}); ok_l = pred({k: v for k, v in state_lazy.items() if k == b})
    mis += (ok_f and not ok_l); same += ok_f
print('AND', tot_and, 'OR', tot_or, 'OR3', tot_or3, bad, 'lazy control false "predicate broken" for cause b', mis, '/', same)
ok = bad['and_whole'] == 0 and bad['or_one'] == 0 and bad['or_all'] == 0 and bad['or3_all'] == 0 and mis == same == tot_or
print(('RESULT: PASS' if ok else 'RESULT: FAIL') + f" ddmin whole AND {tot_and-bad['and_whole']}/{tot_and}; OR returns one cause {tot_or-bad['or_one']}/{tot_or}; delete-and-rerun finds all {tot_or-bad['or_all']}/{tot_or} pairs and {tot_or3-bad['or3_all']}/{tot_or3} triples; lazy control misblames the predicate {mis}/{same}")
