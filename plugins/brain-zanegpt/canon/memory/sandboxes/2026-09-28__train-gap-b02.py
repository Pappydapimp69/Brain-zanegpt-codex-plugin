"""Deterministic sandbox: `brain train gap`, batch 2 (loops 6-10).

Each loop applies one ideas kernel that no memory entry had built against,
reproduces its claim, then pushes until it finds where the claim stops
holding. No real timing: every clock is a parameter. The only randomness is
a seeded splitmix64, so every run prints identical numbers.
"""
import math
from itertools import combinations

M64 = 0xFFFFFFFFFFFFFFFF


def splitmix64(x):
    x = (x + 0x9E3779B97F4A7C15) & M64
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


class Rng:
    def __init__(self, seed):
        self.s = seed & M64

    def u(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & M64
        return (splitmix64(self.s) >> 11) / float(1 << 53)

    def below(self, n):
        return int(self.u() * n)


def banner(n, title):
    print("=" * 78); print(f"LOOP {n} -- {title}"); print("=" * 78)


# ============================================================ LOOP 6 =====
def loop6_replay_oracle():
    """Kernel SYSTEM/testing/a-replay-fingerprint-only-covers-the-mechanism:
    replay parity says nothing about a precondition enforced outside the
    replayed reducer; build a ground-truth oracle computed independently of
    the mechanism's own success signal."""
    banner(6, "replay parity vs an i-frame gate living in the driver")
    W, T, SEEDS, DMG = 4, 600, 60, 7

    def raw_input(seed):
        r = Rng(seed * 7919 + 1)
        return [(r.u() < 0.03, r.u() < 0.15) for _ in range(T)]

    def driver(raw, variant):
        """Presentation layer. Spec: a dodge at tick d grants i-frames on
        ticks d..d+W-1, and an enemy attack is WITHHELD during them."""
        start, end = -1, -2
        cmds, selflog = [], []
        for t, (dodge, attack) in enumerate(raw):
            if dodge:
                cmds.append(("DODGE", t))
                if variant == "late-window":      # off-by-one: window starts a tick late
                    start, end = t + 1, t + W
                else:
                    start, end = t, t + W - 1
            if attack:
                active = start <= t <= end
                if variant == "no-gate" or not active:
                    cmds.append(("HIT", t))
                    selflog.append((t, active))
        return cmds, selflog

    def reduce(cmds):
        hp, fp = 1000, 0x1234
        for kind, t in cmds:
            if kind == "HIT":
                hp -= DMG
            fp = splitmix64(fp ^ (1 if kind == "HIT" else 2) ^ (t << 16) ^ ((hp & 0xFFFFF) << 40))
        return fp

    def truth_violations(raw, cmds):
        """Ground truth: recompute every window from RAW input, per spec."""
        protected = set()
        for d, (dodge, _a) in enumerate(raw):
            if dodge:
                protected.update(range(d, d + W))
        return sum(1 for k, t in cmds if k == "HIT" and t in protected)

    res = {}
    for variant in ("correct", "no-gate", "late-window"):
        replay_ok = golden_ok_clean = golden_ok_bug_era = 0
        self_viol = truth_viol = seeds_truth = seeds_self = 0
        for s in range(SEEDS):
            raw = raw_input(s)
            cmds, selflog = driver(raw, variant)
            live = reduce(cmds)
            replay = reduce(list(cmds))          # replay the recorded log
            replay_ok += live == replay
            golden_clean = reduce(driver(raw, "correct")[0])
            golden_ok_clean += live == golden_clean
            golden_ok_bug_era += live == reduce(driver(raw, variant)[0])
            sv = sum(1 for _t, active in selflog if active)
            tv = truth_violations(raw, cmds)
            self_viol += sv; truth_viol += tv
            seeds_self += sv > 0; seeds_truth += tv > 0
        res[variant] = (replay_ok, golden_ok_clean, golden_ok_bug_era,
                        self_viol, seeds_self, truth_viol, seeds_truth)
        print(f"  {variant:12s} replay parity {replay_ok}/{SEEDS}  "
              f"golden(clean era) match {golden_ok_clean}/{SEEDS}  "
              f"golden(recorded with bug) match {golden_ok_bug_era}/{SEEDS}")
        print(f"  {'':12s} self-oracle (driver's own flag): {self_viol} violations "
              f"in {seeds_self} seeds | ground-truth oracle: {truth_viol} in {seeds_truth} seeds")
    return res


# ============================================================ LOOP 7 =====
def loop7_bisection():
    """Kernel DEBUGGING/strategy/bisection: halve a good..bad range each test;
    git's example "675 revisions left (roughly 10 steps)"."""
    banner(7, "bisection: log2 steps, then flaky tests and non-monotone history")

    def bisect(n, is_bad):
        """good = 0, bad = n; returns (first bad, tests run)."""
        lo, hi, tests = 0, n, 0
        while hi - lo > 1:
            mid = (lo + hi) // 2
            tests += 1
            if is_bad(mid):
                hi = mid
            else:
                lo = mid
        return hi, tests

    print("  monotone history, exact test:")
    for n in (10, 100, 676, 1000, 10000, 100000):
        worst = 0
        for first in range(1, n + 1, max(1, n // 997)):
            got, t = bisect(n, lambda c, f=first: c >= f)
            assert got == first
            worst = max(worst, t)
        print(f"    n={n:6d}: bisect worst {worst} tests (ceil log2 n = "
              f"{math.ceil(math.log2(n))}); linear scan worst {n - 1}, mean {(n - 1) / 2:.0f}")

    n, TR = 676, 4000
    print(f"  flaky test (a bad commit reads 'good' with prob p), n={n}, {TR} trials:")
    flaky = {}
    for p in (0.01, 0.05, 0.10):
        for label, reps in (("single", 1), ("best-of-3", 3)):
            wrong = tests_total = 0
            for tr in range(TR):
                r = Rng(tr * 104729 + int(p * 1000) * 31 + reps)
                first = 1 + r.below(n)

                def is_bad(c, first=first, r=r, reps=reps):
                    if c < first:
                        return False
                    votes = sum(r.u() >= p for _ in range(reps))
                    return votes * 2 > reps
                got, t = bisect(n, is_bad)
                wrong += got != first
                tests_total += t * reps
            flaky[(p, label)] = wrong / TR
            print(f"    p={p:.2f} {label:9s}: wrong commit {wrong / TR:6.1%}  "
                  f"(test runs {tests_total / TR:.1f})")

    # non-monotone: introduced at a, masked at b, unmasked at c (a<b<c)
    hit_a = hit_c = other = cases = 0
    r = Rng(99)
    for _ in range(20000):
        a, b, c = sorted(r.below(n - 1) + 1 for _ in range(3))
        if not (a < b < c):
            continue
        cases += 1
        got, _t = bisect(n, lambda x: (a <= x < b) or x >= c)
        hit_a += got == a; hit_c += got == c; other += got not in (a, c)
    print(f"  non-monotone (bug at a, masked at b, back at c), {cases} histories: "
          f"bisect returns a {hit_a / cases:.1%}, c {hit_c / cases:.1%}, other {other / cases:.1%}")
    return flaky, hit_a / cases


# ============================================================ LOOP 8 =====
def loop8_race():
    """Kernel CONCURRENCY/correctness/race-conditions: the outcome depends on
    the interleaving, not the input; passing runs are weak evidence."""
    banner(8, "lost update: outcome set per input, rarity, and the observer effect")

    def run(schedule, prog):
        """schedule: sequence of thread ids; prog: per-thread op lists."""
        mem = {"x": 0}
        regs = [0, 0]; pcs = [0, 0]
        for tid in schedule:
            if pcs[tid] >= len(prog[tid]):
                continue
            op = prog[tid][pcs[tid]]; pcs[tid] += 1
            if op == "load":
                regs[tid] = mem["x"]
            elif op == "inc":
                regs[tid] += 1
            elif op == "store":
                mem["x"] = regs[tid]
        return mem["x"]

    def all_schedules(l0, l1):
        tot = l0 + l1
        for pos in combinations(range(tot), l0):
            s = [1] * tot
            for p in pos:
                s[p] = 0
            yield s

    for K in (1, 2, 3):
        prog = [["load", "inc", "store"] * K] * 2
        outcomes = {}
        for s in all_schedules(3 * K, 3 * K):
            v = run(s, prog)
            outcomes[v] = outcomes.get(v, 0) + 1
        tot = sum(outcomes.values())
        print(f"  K={K} increments each, same input, all {tot} interleavings: "
              + ", ".join(f"x={v}: {c}" for v, c in sorted(outcomes.items()))
              + f"  -> correct {outcomes.get(2 * K, 0) / tot:.1%}")

    def random_run(seed, K, work, p, log_inside=0):
        """Each thread: K x [work x 'nop', load, (log_inside x 'nop'), inc, store].
        A preemptive scheduler switches thread with prob p per step."""
        body = ["nop"] * work + ["load"] + ["nop"] * log_inside + ["inc", "store"]
        prog = [body * K, body * K]
        r = Rng(seed)
        sched, cur = [], 0
        left = [len(prog[0]), len(prog[1])]
        while left[0] or left[1]:
            if left[cur] == 0 or r.u() < p:
                cur ^= 1
                if left[cur] == 0:
                    cur ^= 1
            sched.append(cur); left[cur] -= 1
        return run(sched, prog) != 2 * K

    RUNS, K = 3000, 20
    print(f"  preemptive scheduler, K={K}, {RUNS} runs each (fraction of runs that LOSE an update):")
    rates = {}
    for work in (0, 50):
        for p in (0.2, 0.01, 0.001):
            bad = sum(random_run(i * 7 + work * 1000 + int(p * 1e6), K, work, p) for i in range(RUNS))
            rates[(work, p, 0)] = bad / RUNS
            need = ("never seen" if bad == 0 else "every run" if bad == RUNS else f"~{math.ceil(math.log(0.05) / math.log(1 - bad / RUNS))} runs for 95% odds of one failure")
            print(f"    work={work:2d} p={p:<5} fail {bad / RUNS:6.1%}   ({need})")
    print("  observer effect (work=50, p=0.01): a 5-step log call added ...")
    base = rates[(50, 0.01, 0)]
    inside = sum(random_run(i * 7 + 50 * 1000 + 10000, K, 50, 0.01, log_inside=5) for i in range(RUNS)) / RUNS

    def outside_run(seed):
        return random_run(seed, K, 55, 0.01)
    outside = sum(outside_run(i * 7 + 777) for i in range(RUNS)) / RUNS
    print(f"    none {base:6.1%} | inside load..store {inside:6.1%} | outside the critical section {outside:6.1%}")
    return rates, base, inside, outside


# ============================================================ LOOP 9 =====
def loop9_float_dt_cooldown():
    """Kernel SYSTEM/determinism/float-dt-cooldown-is-a-real-fairness-bug:
    `cd -= dt; if cd <= 0 { move; cd = STEP }` at STEP=108ms gave 515 moves at
    60fps, 540 at 144, 450 at 30 over 60 s; the gap grows with hold time."""
    banner(9, "float-dt cooldown: the reset discards overshoot")
    STEP = 108.0

    def moves(fps, seconds, mode, jitter_seed=None):
        dt0 = 1000.0 / fps
        r = Rng(jitter_seed) if jitter_seed is not None else None
        t, cd, n = 0.0, 0.0, 0
        total = seconds * 1000.0
        while t < total:
            dt = dt0 if r is None else dt0 * (0.5 + r.u())
            dt = min(dt, total - t)
            t += dt
            cd -= dt
            if mode == "reset":
                if cd <= 0:
                    n += 1; cd = STEP
            elif mode == "carry":
                if cd <= 0:
                    n += 1; cd += STEP
            elif mode == "carry-loop":
                while cd <= 0:
                    n += 1; cd += STEP
        return n

    ideal60 = math.floor(60000 / STEP) + 1
    print(f"  ideal over 60 s (a move at t=0 and every 108 ms): {ideal60}")
    for fps in (30, 60, 144):
        pred = 60000 / (math.ceil(STEP / (1000 / fps)) * (1000 / fps))
        print(f"    {fps:3d}fps reset {moves(fps, 60, 'reset'):4d} (period ceil(108/dt)*dt predicts {pred:.1f})"
              f" | carry {moves(fps, 60, 'carry'):4d} | carry-loop {moves(fps, 60, 'carry-loop'):4d}")
    print("  hold time vs gap (reset form, 144fps minus 30fps):")
    for secs in (5, 15, 60, 240):
        a, b = moves(144, secs, "reset"), moves(30, secs, "reset")
        print(f"    {secs:3d}s: {a} vs {b}  abs gap {a - b:3d}  relative {(a - b) / a:.1%}")
    worst = (0, 0)
    for fps in range(20, 241):
        d = abs(moves(fps, 60, "reset") - ideal60) / ideal60
        worst = max(worst, (d, fps))
    print(f"  sweep 20..240fps: worst reset shortfall {worst[0]:.1%} at {worst[1]}fps")
    print("  low frame rate (dt > STEP), 60 s:")
    for fps in (8, 5):
        print(f"    {fps}fps reset {moves(fps, 60, 'reset')} | carry {moves(fps, 60, 'carry')} | "
              f"carry-loop {moves(fps, 60, 'carry-loop')} (ideal {ideal60})")
    spread = {}
    for mode in ("reset", "carry-loop"):
        vals = [moves(60, 60, mode, jitter_seed=s) for s in range(10)]
        spread[mode] = (min(vals), max(vals))
        print(f"  jittered 60fps (dt x U[0.5,1.5]), 10 seeds, {mode}: {min(vals)}..{max(vals)}")
    return spread


# ============================================================ LOOP 10 ====
def loop10_aba():
    """Kernel CONCURRENCY/lock-free/definition-and-aba: lock-free is a progress
    guarantee (a suspended thread can't stall the rest); ABA lets a CAS
    succeed on a structure whose meaning changed."""
    banner(10, "Treiber stack: ABA, tag width, and suspension")

    def aba_trial(seed, tag_bits, ops):
        """Thread A reads (head, tag, next) to pop, stalls; thread B runs `ops`
        random push/pop with node recycling; A then CASes. Returns
        'corrupt' if A's CAS succeeds and the stack no longer matches a
        sequential pop, 'retry' if CAS failed, 'ok' if it succeeded safely."""
        r = Rng(seed)
        nxt = {}
        head, tag = None, 0
        free = []
        vals = {}
        mask = (1 << tag_bits) - 1 if tag_bits else 0

        def push(node, v):
            nonlocal head, tag
            nxt[node] = head; vals[node] = v; head = node; tag = (tag + 1) & mask

        def pop():
            nonlocal head, tag
            n = head
            head = nxt[n]; tag = (tag + 1) & mask
            return n
        for i in range(4):
            push(i, i)
        nodes = 4
        a_head, a_tag, a_next = head, tag, nxt[head]
        for _ in range(ops):
            if head is not None and r.u() < 0.5:
                free.append(pop())
            else:
                if free and r.u() < 0.8:
                    node = free.pop()            # recycle a freed node
                else:
                    node = nodes; nodes += 1
                push(node, r.below(1000))
        if head == a_head and tag == a_tag:
            expected_after = nxt[head]           # what a correct pop would leave
            if a_next != expected_after:
                return "corrupt"
            head = a_next
            return "ok"
        return "retry"

    TR = 4000
    res = {}
    for bits in (0, 1, 2, 4, 8):
        for ops in (2, 6, 16, 40, 256):
            c = {"corrupt": 0, "ok": 0, "retry": 0}
            for s in range(TR):
                c[aba_trial(s * 131 + ops, bits, ops)] += 1
            res[(bits, ops)] = c["corrupt"]
        print(f"  tag {bits} bits: corrupt CAS per {TR} stalls, B ran "
              + ", ".join(f"{o} ops: {res[(bits, o)]}" for o in (2, 6, 16, 40, 256)))

    # suspension: N threads, each op = acquire/CAS loop; thread 0 suspended
    # forever at its first critical step. Count ops the others finish.
    def suspend_run(kind, N=4, steps=4000):
        owner = None
        done = [0] * N
        stage = [0] * N
        for step in range(steps):
            t = step % N
            if t == 0 and stage[0] == 1:
                continue                        # suspended inside its critical step
            if kind == "mutex":
                if stage[t] == 0:
                    if owner is None:
                        owner = t; stage[t] = 1
                elif stage[t] == 1:
                    owner = None; stage[t] = 0; done[t] += 1
            else:                               # CAS: read, then CAS (never blocks others)
                if stage[t] == 0:
                    stage[t] = 1
                else:
                    stage[t] = 0; done[t] += 1
        return sum(done[1:])
    m, lf = suspend_run("mutex"), suspend_run("cas")
    print(f"  thread 0 suspended mid-operation, 4000 steps: other threads finish "
          f"mutex {m} ops, CAS {lf} ops")
    return res, m, lf


if __name__ == "__main__":
    loop6_replay_oracle()
    loop7_bisection()
    loop8_race()
    loop9_float_dt_cooldown()
    loop10_aba()
