"""A print that takes its own lock inside a race window does not hide the race.

Prediction (written before the first run):
  P1 reachable final values for K=2 stay {2,3,4} with no probe, a plain probe and a
     lock-taking probe inside load..store; a lock spanning load..store gives {4}.
  P2 under a uniform-random scheduler (exact, no RNG) the lock probe's lost-update
     probability is within 10 percentage points of the plain probe's.
  P3 under a sticky scheduler (switch with q=0.01 per step) the lock probe's
     lost-update probability is >= the plain probe's.
Stdlib only, deterministic: probabilities are computed exactly by memoised DP over
the state space, every interleaving counted, no threads, no timing.
"""
from functools import lru_cache
from fractions import Fraction

K = 2

def program(kind):
    """One increment as a list of ops. kind: none | plain | lockprobe | span."""
    if kind == "none":
        inc = ["load", "store"]
    elif kind == "plain":
        inc = ["load", "work", "work", "work", "store"]
    elif kind == "lockprobe":
        inc = ["load", "acq", "work", "work", "work", "rel", "store"]
    elif kind == "span":
        inc = ["acq", "load", "work", "work", "work", "store", "rel"]
    return tuple(inc * K)

def runnable(prog, pc, lock, t):
    if pc >= len(prog):
        return False
    if prog[pc] == "acq" and lock is not None:
        return False
    return True

def step(prog, state, t):
    pcs, regs, ctr, lock = state
    op = prog[pcs[t]]
    pcs = list(pcs); regs = list(regs)
    if op == "load":
        regs[t] = ctr
    elif op == "store":
        ctr = regs[t] + 1
    elif op == "acq":
        lock = t
    elif op == "rel":
        lock = None
    pcs[t] += 1
    return (tuple(pcs), tuple(regs), ctr, lock)

def analyse(kind, q=None):
    """Returns (reachable final set, #schedules, #bad schedules, P(bad) uniform, P(bad) sticky q)."""
    prog = program(kind)
    start = ((0, 0), (0, 0), 0, None)

    @lru_cache(maxsize=None)
    def count(state):
        # -> dict final -> number of schedules
        run = [t for t in (0, 1) if runnable(prog, state[0][t], state[3], t)]
        if not run:
            assert all(pc == len(prog) for pc in state[0]), "deadlock"
            return {state[2]: 1}
        out = {}
        for t in run:
            for v, n in count(step(prog, state, t)).items():
                out[v] = out.get(v, 0) + n
        return out

    @lru_cache(maxsize=None)
    def puni(state):
        run = [t for t in (0, 1) if runnable(prog, state[0][t], state[3], t)]
        if not run:
            return Fraction(int(state[2] != 2 * K))
        return sum(puni(step(prog, state, t)) for t in run) / len(run)

    @lru_cache(maxsize=None)
    def psticky(state, cur):
        run = [t for t in (0, 1) if runnable(prog, state[0][t], state[3], t)]
        if not run:
            return Fraction(int(state[2] != 2 * K))
        if len(run) == 1:
            t = run[0]
            return psticky(step(prog, state, t), t)
        other = 1 - cur
        return (1 - q) * psticky(step(prog, state, cur), cur) + q * psticky(step(prog, state, other), other)

    c = count(start)
    total = sum(c.values()); bad = sum(n for v, n in c.items() if v != 2 * K)
    pu = puni(start)
    ps = (psticky(start, 0) + psticky(start, 1)) / 2 if q is not None else None
    return set(c), total, bad, pu, ps

q = Fraction(1, 100)
res = {k: analyse(k, q) for k in ("none", "plain", "lockprobe", "span")}
for k, (vals, tot, bad, pu, ps) in res.items():
    print(f"{k:9s} finals={sorted(vals)} schedules={tot} bad={bad} ({bad/tot:.1%}) "
          f"P_uniform={float(pu):.4f} P_sticky(q=0.01)={float(ps):.5f}")

ok = True
# Scenario 1: reachable sets
for k in ("none", "plain", "lockprobe"):
    if res[k][0] != {2, 3, 4}:
        ok = False; print("P1 miss:", k, res[k][0])
# Scenario 4 (built to BREAK the claim): a lock spanning the window does hide it
if res["span"][0] != {4} or res["span"][3] != 0:
    ok = False; print("P1 span miss")
diff = float(res["plain"][3] - res["lockprobe"][3])
print(f"P2 uniform: plain - lockprobe = {diff*100:.1f} pp")
if abs(diff) >= 0.10:
    ok = False; print("P2 miss")
print(f"P3 sticky: lockprobe {float(res['lockprobe'][4]):.5f} vs plain {float(res['plain'][4]):.5f}")
if res["lockprobe"][4] < res["plain"][4]:
    ok = False; print("P3 miss")

summ = (f"lockprobe finals={sorted(res['lockprobe'][0])} P_uni={float(res['lockprobe'][3]):.3f} vs plain "
        f"{float(res['plain'][3]):.3f}; sticky {float(res['lockprobe'][4]):.4f} vs {float(res['plain'][4]):.4f}; "
        f"span finals={sorted(res['span'][0])} P=0")
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + summ)
