# Preemption-bounded schedule enumeration over tiny thread models. Deterministic, stdlib only.
import itertools

def run(threads_fn, k, check):
    """Enumerate all schedules with <= k preemptions (switch away from a runnable thread).
    Returns (schedules_run, first_bad_index_or_None, min_preemptions_of_bad)."""
    n_sched = 0; first_bad = None; minp = None
    def rec(state, pcs, last, pre, trace):
        nonlocal n_sched, first_bad, minp
        threads = threads_fn()
        runnable = [t for t in range(len(threads)) if pcs[t] < len(threads[t])]
        if not runnable:
            n_sched += 1
            if not check(state):
                if first_bad is None: first_bad = n_sched
                if minp is None or pre < minp: minp = pre
            return
        for t in runnable:
            p = pre + (1 if (last is not None and t != last and last in runnable) else 0)
            if p > k: continue
            s = {a: (list(b) if isinstance(b, list) else b) for a, b in state.items()}
            s['L'] = {a: dict(b) if isinstance(b, dict) else b for a, b in state.get('L', {}).items()}
            threads[t][pcs[t]](s, t)
            npcs = list(pcs); npcs[t] += 1
            rec(s, npcs, t, p, trace + [t])
    rec({'L': {}}, [0]*len(threads_fn()), None, 0, [])
    return n_sched, first_bad, minp

# Model A: lost update (2 threads: read, write+1)
def lost():
    def rd(s, t): s['L'][t] = s.get('x', 0)
    def wr(s, t): s['x'] = s['L'][t] + 1
    return [[rd, wr], [rd, wr]]
chkA = lambda s: s.get('x') == 2
# Model B: torn read of a 2-slot value; writer does W updates, reader copies slot0 then slot1.
def torn(W):
    def mk():
        def w(i):
            def f(s, t):
                s['a'] = i + 1
            return f
        def w2(i):
            def f(s, t):
                s['b'] = i + 1
            return f
        writer = []
        for i in range(W): writer += [w(i), w2(i)]
        r0 = lambda s, t: s['L'].__setitem__('r', (s.get('a', 0),))
        r1 = lambda s, t: s['L'].__setitem__('r', s['L']['r'] + (s.get('b', 0),))
        s0 = lambda s, t: s.__setitem__('res', s['L']['r'])
        return [writer, [r0, r1, s0]]
    return mk
chkB = lambda s: s['res'][0] == s['res'][1]
# Model C: bug needing 3 preemptions: reader must see state==3 mid-way through 3 separate 1-step windows
def deep():
    def A(i):
        def f(s, t): s['x'] = i + 1
        return f
    def obs(i):
        def f(s, t): s.setdefault('seen', []).append((i, s.get('x', 0)))
        return f
    # thread0: x=1; x=2; x=3. thread1 observes 3 times then asserts it saw 1,2,3 in order (interleaved)
    return [[A(0), A(1), A(2)], [obs(0), obs(1), obs(2)]]
chkC = lambda s: [v for _, v in s['seen']] != [1, 2, 3]

res = {}
for name, fn, chk, ks in [('lost', lost, chkA, (0,1,2)), ('torn-W1', torn(1), chkB, (0,1,2)),
                          ('torn-W2', torn(2), chkB, (0,1,2)), ('deep', deep, chkC, (0,1,2,3,4))]:
    for k in ks:
        n, fb, mp = run(fn, k, chk)
        res[(name, k)] = (n, fb, mp)
        print(name, 'k=%d' % k, 'schedules=%d' % n, 'first_bad=%s' % fb, 'min_preempt=%s' % mp)
ok = (res[('lost',0)][1] is None and res[('lost',1)][1] is not None and res[('lost',1)][2] == 1
      and res[('torn-W1',1)][1] is not None and res[('torn-W2',1)][1] is not None
      and True)
# claim "most bugs need <=1-2 switches" holds for lost/torn; breaks if deep needs >2
deep_min = min((k for k in (0,1,2,3,4) if res[('deep',k)][1] is not None), default=None)
print('deep needs k =', deep_min)
claim_holds_simple = res[('lost',1)][2] == 1 and res[('torn-W1',1)][2] == 1
print('RESULT: %s lost/torn bugs found at k=1 (first_bad %s/%s); deep bug needs k=%s so a fixed k<=2 cap misses it'
      % ('PASS' if claim_holds_simple and deep_min is not None and deep_min > 2 else 'FAIL',
         res[('lost',1)][1], res[('torn-W1',1)][1], deep_min))
