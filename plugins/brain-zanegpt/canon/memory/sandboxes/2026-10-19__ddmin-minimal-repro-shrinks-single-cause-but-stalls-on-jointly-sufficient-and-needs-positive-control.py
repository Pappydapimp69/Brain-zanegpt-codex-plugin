"""Deterministic sandbox: does stripping input toward a minimal repro find the cause?
Prediction (written before run): ddmin on a single-cause failure over 32 items returns exactly
the 1 culprit; on a 2-cause (jointly necessary) failure returns a 2-item set (both causes, not
either alone); on a failure with two independent minimal causes it returns ONE of them (a
1-minimal set, hiding the other); a five-whys walk on the single-cause chain finds the culprit
but on the joint failure its single chain names only one factor. A non-reproducing 'reduced'
case is caught only by re-running the positive control."""
def ddmin(items, fails):
    n = 2
    while len(items) >= 2:
        chunk = max(1, len(items) // n)
        subs = [items[i:i+chunk] for i in range(0, len(items), chunk)]
        done = False
        for s in subs:
            if fails(s):
                items, n, done = s, 2, True; break
        if not done:
            for i in range(len(subs)):
                c = [x for j, s in enumerate(subs) if j != i for x in s]
                if c and fails(c):
                    items, n, done = c, max(n-1, 2), True; break
        if not done:
            if n >= len(items): break
            n = min(len(items), n*2)
    return items

def five_whys(causes_of, symptom, depth=5):
    chain, cur = [symptom], symptom
    for _ in range(depth):
        nxt = causes_of.get(cur, [])
        if not nxt: break
        cur = nxt[0]; chain.append(cur)      # linear: takes first answer only
    return chain

data = list(range(32))
res = {}
# S1 single cause
f1 = lambda s: 17 in s
r1 = ddmin(data, f1); res['single'] = r1
# S2 jointly necessary pair
f2 = lambda s: 5 in s and 21 in s
r2 = ddmin(data, f2); res['joint'] = sorted(r2)
# S3 BREAK: two independent sufficient causes
f3 = lambda s: 3 in s or 28 in s
r3 = ddmin(data, f3); res['either'] = r3
# five whys
g1 = {'crash': ['bad17'], 'bad17': ['root17']}
g2 = {'crash': ['bad5', 'bad21'], 'bad5': ['root5'], 'bad21': ['root21']}
w1 = five_whys(g1, 'crash'); w2 = five_whys(g2, 'crash')
named2 = {x for x in w2 if x in ('bad5', 'bad21')}
# S4 positive control: a 'reduced' repro that silently dropped a precondition does not reproduce
def fails_env(s, env_ok=True): return env_ok and 17 in s
reduced_ok = fails_env(r1)                       # control on real env
reduced_stale = fails_env(r1, env_ok=False)      # repro built without precondition
print(res, w1, w2, reduced_ok, reduced_stale)
ok = (r1 == [17] and res['joint'] == [5, 21] and len(r3) == 1 and r3[0] in (3, 28)
      and len(named2) == 1 and w1[-1] == 'root17' and reduced_ok and not reduced_stale
      and f3([3]) and f3([28]))
print(("RESULT: PASS " if ok else "RESULT: FAIL ") +
      f"single->{r1}; joint->{res['joint']}; either->{r3} (other cause 28/3 hidden); "
      f"fivewhys names {len(named2)} of 2 joint factors; control repro={reduced_ok}/stale={reduced_stale}")
