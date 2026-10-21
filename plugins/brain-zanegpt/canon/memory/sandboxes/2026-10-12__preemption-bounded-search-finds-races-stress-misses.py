"""Edge pass: ideas CONCURRENCY/race-conditions (a race is a timing-dependent outcome) with
sandbox-kernel-concurrency E1 (2 threads x 3 unprotected load-inc-store increments: 5 results over 48620
interleavings; rare preemption p = 0.001 needs ~68 runs for 95% odds) and E5 (probes shift the rate).
New angle: systematic schedule search with a PREEMPTION BOUND (all schedules with at most k involuntary
switches, run in order k = 0, 1, 2, ...), deterministic, against E1's stress numbers. (iteration 2: bound raised to 5 for 2x3 after value 2 was not reached by bound 3.) Own fixture adds a
3-thread x 2-increment case. A preemption = switching away from a thread that could still run.
Predictions written before running:
 P1 2x3: every lost-update result (final < 6) needs at most 2 preemptions; the first lost update is found within 20 schedules.
 P2 2x3: the full set of 5 results is reached by bound 2, in fewer schedules than the ~68 stress runs E1 needs
    for ONE failure... (expected: hundreds? predict <= 200 schedules).
 P3 3x2: the minimum final value (2) needs at most 2 preemptions too.
"""
from functools import lru_cache

def explore(T, N, maxb=3):
    steps = 3 * N   # load, inc, store per increment
    results = {}    # final value -> min preemptions
    order = []      # (preemptions, final) for every complete schedule, in bound order
    def rec(pcs, regs, mem, cur, pre, bound, out):
        if pre > bound: return
        live = [t for t in range(T) if pcs[t] < steps]
        if not live:
            out.append((pre, mem)); return
        for t in live:
            p = pre + (1 if (cur is not None and t != cur and pcs[cur] < steps) else 0)
            if p > bound: continue
            pc = list(pcs); rg = list(regs); m = mem
            k = pc[t] % 3
            if k == 0: rg[t] = m
            elif k == 1: rg[t] += 1
            else: m = rg[t]
            pc[t] += 1
            rec(tuple(pc), tuple(rg), m, t, p, bound, out)
    seen_by_bound = {}
    for bound in range(0, maxb + 1):
        out = []
        rec(tuple([0] * T), tuple([0] * T), 0, None, 0, bound, out)
        fresh = [(p, v) for p, v in out if p == bound]
        seen_by_bound[bound] = (len(fresh), sorted({v for _, v in out}))
        for p, v in fresh:
            order.append((p, v))
            results.setdefault(v, p)
    return results, order, seen_by_bound

for T, N in ((2, 3), (3, 2)):
    res, order, sb = explore(T, N, 5 if (T, N) == (2, 3) else 3)
    first_lost = next(i + 1 for i, (_, v) in enumerate(order) if v < T * N)
    cum, found, need_all = 0, set(), None
    for i, (p, v) in enumerate(order):
        found.add(v)
        if need_all is None and len(found) == len(res): need_all = i + 1
    print(f"{T} threads x {N} incs: results reached {sorted(res)}; min preemptions per result {dict(sorted(res.items()))}; "
          f"schedules per bound {[sb[b][0] for b in sb]}; first lost update at schedule {first_lost}; all results by schedule {need_all}")
    if (T, N) == (2, 3): r23 = (res, first_lost, need_all)
    else: r32 = res
p1 = all(p <= 2 for v, p in r23[0].items() if v < 6) and r23[1] <= 20
p2 = r23[2] is not None and r23[2] <= 200 and len(r23[0]) == 5
p3 = r32.get(2, 99) <= 2
checks = [("P1 lost updates need <= 2 preemptions, first within 20", p1), ("P2 all 5 results within 200 schedules", p2), ("P3 3x2 minimum value 2 within 2 preemptions", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; 2x3 first lost update at schedule {r23[1]}, all {len(r23[0])} results by schedule {r23[2]}, "
      f"min preemptions {dict(sorted(r23[0].items()))}; 3x2 min preemptions {dict(sorted(r32.items()))}")
