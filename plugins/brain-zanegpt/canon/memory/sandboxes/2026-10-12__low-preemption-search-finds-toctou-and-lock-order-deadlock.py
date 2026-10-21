"""New-idea loop 2 (CONCURRENCY): test concurrent code by enumerating schedules in order of preemption count
(bound 0, 1, 2 ...), not by random stress. New fixtures beyond the lost-update counter:
 F1 check-then-act withdraw: two threads each 'if bal >= 60: bal -= 60' on bal = 100 (overdraft bug).
 F2 lock-order deadlock: T1 locks A then B, T2 locks B then A (Coffman: circular wait).
 F3 F1 with a mutex around check-and-act (the fix): no bad outcome at any bound.
Exhaustive per bound; a preemption = switching away from a thread that could still run (blocked on a lock
does not count). Deterministic.
Predictions written before running:
 P1 the overdraft (bal < 0) appears at bound 1, within the first 5 schedules explored.
 P2 the deadlock appears at bound 1.
 P3 the mutex version shows 0 bad outcomes up to bound 3.
 P4 bound 0 (no preemption) shows neither bug: plain sequential testing passes.
"""
def explore(progs, init, bad, maxb):
    first = {}
    count = [0]
    def rec(pcs, st, locks, cur, pre, bound):
        if pre > bound: return
        live = [t for t in range(len(progs)) if pcs[t] < len(progs[t])]
        if not live:
            count[0] += 1
            if bad(st) and "bad" not in first: first["bad"] = (bound, count[0])
            return
        runnable = []
        for t in live:
            op = progs[t][pcs[t]]
            if op[0] == "lock" and locks.get(op[1]) not in (None, t): continue
            runnable.append(t)
        if not runnable:
            count[0] += 1
            if "deadlock" not in first: first["deadlock"] = (bound, count[0])
            return
        for t in runnable:
            p = pre + (1 if cur is not None and t != cur and cur in runnable else 0)
            if p > bound: continue
            op = progs[t][pcs[t]]; s = dict(st); lk = dict(locks)
            if op[0] == "lock": lk[op[1]] = t
            elif op[0] == "unlock": lk[op[1]] = None
            else: op[1](s, t)
            pc = list(pcs); pc[t] += 1
            rec(tuple(pc), s, lk, t, p, bound)
    for b in range(maxb + 1):
        count[0] = 0
        rec(tuple([0] * len(progs)), dict(init), {}, None, 0, b)
        if first: return first, b
    return first, None

def check(s, t): s[f"ok{t}"] = s["bal"] >= 60
def act(s, t):
    if s[f"ok{t}"]: s["bal"] -= 60
withdraw = [("op", check), ("op", act)]
F1 = explore([withdraw, withdraw], {"bal": 100}, lambda s: s["bal"] < 0, 3)
F2 = explore([[("lock", "A"), ("lock", "B"), ("unlock", "B"), ("unlock", "A")],
              [("lock", "B"), ("lock", "A"), ("unlock", "A"), ("unlock", "B")]], {}, lambda s: False, 3)
locked = [("lock", "M"), ("op", check), ("op", act), ("unlock", "M")]
F3 = explore([locked, locked], {"bal": 100}, lambda s: s["bal"] < 0, 3)
F0a = explore([withdraw, withdraw], {"bal": 100}, lambda s: s["bal"] < 0, 0)
F0b = explore([[("lock", "A"), ("lock", "B"), ("unlock", "B"), ("unlock", "A")],
               [("lock", "B"), ("lock", "A"), ("unlock", "A"), ("unlock", "B")]], {}, lambda s: False, 0)
print(f"F1 overdraft: first found {F1[0]} (bound, schedule #)")
print(f"F2 deadlock: first found {F2[0]}")
print(f"F3 mutex: found {F3[0] or 'nothing'} up to bound 3")
print(f"bound 0 only: overdraft {F0a[0] or 'none'}, deadlock {F0b[0] or 'none'}")
p1 = F1[0].get("bad", (9, 99))[0] == 1 and F1[0]["bad"][1] <= 5
p2 = F2[0].get("deadlock", (9,))[0] == 1
p3 = not F3[0]
p4 = not F0a[0] and not F0b[0]
checks = [("P1 overdraft at bound 1 within 5 schedules", p1), ("P2 deadlock at bound 1", p2), ("P3 mutex clean to bound 3", p3), ("P4 bound 0 finds neither", p4)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; overdraft {F1[0]}; deadlock {F2[0]}; mutex {F3[0] or 'clean'}; bound0 {F0a[0] or 'clean'}/{F0b[0] or 'clean'}")
