"""Deterministic sandbox: `brain train gap`, batch 3 (loops 11-15).

Each loop applies one ideas kernel that no memory entry had built against,
reproduces its claim, then pushes until it finds where the claim stops
holding. No real timing: every clock is a parameter. The only randomness is
a seeded splitmix64, so every run prints identical numbers.
"""
import math
from bisect import bisect_left, bisect_right
from fractions import Fraction

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

    def shuffle(self, xs):
        for i in range(len(xs) - 1, 0, -1):
            j = self.below(i + 1)
            xs[i], xs[j] = xs[j], xs[i]
        return xs


def banner(n, title):
    print("=" * 78); print(f"LOOP {n} -- {title}"); print("=" * 78)


# ============================================================ LOOP 11 ====
def loop11_safe_integer():
    """Kernel SYSTEM/determinism/float64-safe-integer-headroom: at 5.5x per
    event, 2^53 is crossed after ~21 events and Infinity after ~416; past
    2^53 arithmetic still looks right but exact-integer operations break."""
    banner(11, "float64 past 2^53: what breaks and what does not")
    SAFE = 2 ** 53
    for v0 in (1, 2, 5, 10):
        v, n, n_safe = float(v0), 0, None
        while v != math.inf:
            v *= 5.5; n += 1
            if n_safe is None and v > SAFE:
                n_safe = n
        print(f"  start {v0:2d}: crosses 2^53 after {n_safe} events, reaches Infinity after {n}")

    # integer-valued stat, floor(v * 5.5) each event: float vs exact integers
    fv, iv = 1.0, 1
    first_diff = None
    for n in range(1, 60):
        fv = math.floor(fv * 5.5); iv = (iv * 11) // 2
        if first_diff is None and int(fv) != iv:
            first_diff = (n, iv > SAFE)
    rel = abs(Fraction(int(fv)) - iv) / iv
    print(f"  floor(v*5.5) per event: float first differs from exact integers at event "
          f"{first_diff[0]} (exact value past 2^53: {first_diff[1]}); after 59 events "
          f"relative error {float(rel):.1e}")

    lost = {}
    for exp in (52, 53, 54, 56):
        base = 2 ** exp
        r = Rng(exp)
        tries = 20000
        l = 0
        for _ in range(tries):
            x = float(base + r.below(1 << 20) * (1 if exp < 53 else 2 ** (exp - 52)))
            l += (x + 1.0) == x
        lost[exp] = l / tries
        print(f"  +1 on values in [2^{exp}, 2^{exp + 1}): lost {l / tries:6.1%}")

    order = {}
    for exp in (48, 52, 53, 55, 60):
        r = Rng(1000 + exp)
        trials, diff = 4000, 0
        for _ in range(trials):
            xs = [float(r.below(1 << 20) * 2 ** max(0, exp - 52) + (2 ** exp if i == 0 else r.below(4096)))
                  for i in range(8)]
            a = sum(xs)
            ys = r.shuffle(xs[:])
            b = sum(ys)
            diff += a != b
        order[exp] = diff / trials
        print(f"  sum of 8 integer-valued stats, largest ~2^{exp}: two orders disagree {diff / trials:6.1%}")
    rerun = all(math.floor(float(v) * 5.5) == math.floor(float(v) * 5.5) for v in range(1000))
    print(f"  same op sequence re-run gives identical bits (IEEE-754 * and + are correctly rounded): {rerun}")
    return first_diff, lost, order


# ============================================================ LOOP 12 ====
def loop12_symmetric_control():
    """Kernel SYSTEM/testing/symmetric-control-catches-turn-order-bias: two
    identical rosters showed 25/15 over 40 trials, traced to a stable sort
    preserving concatenation order on speed ties."""
    banner(12, "symmetric control: the skew, and whether 40 trials can see it")
    roster = [(12, 30, 7), (9, 26, 9)]          # (speed, hp, attack)

    def fight(seed, order_mode):
        r = Rng(seed)
        teams = [[list(f) + [t, i] for i, f in enumerate(roster)] for t in (0, 1)]
        for rnd in range(200):
            alive = [f for t in teams for f in t if f[1] > 0]
            if order_mode == "stable-A-first":
                seq = sorted(alive, key=lambda f: -f[0])
            elif order_mode == "stable-B-first":
                seq = sorted(sorted(alive, key=lambda f: -f[3]), key=lambda f: -f[0])
            elif order_mode == "shuffled-ties":
                seq = sorted(r.shuffle(alive[:]), key=lambda f: -f[0])
            elif order_mode == "alternate":
                seq = sorted(sorted(alive, key=lambda f: f[3] != rnd % 2), key=lambda f: -f[0])
            for f in seq:
                if f[1] <= 0:
                    continue
                foes = [g for g in teams[1 - f[3]] if g[1] > 0]
                if not foes:
                    return f[3]
                g = foes[r.below(len(foes))]
                g[1] -= f[2] + r.below(5)
            for t in (0, 1):
                if all(f[1] <= 0 for f in teams[t]):
                    return 1 - t
        return -1

    N = 4000
    rates = {}
    for mode in ("stable-A-first", "stable-B-first", "shuffled-ties", "alternate"):
        w = sum(fight(s * 17 + 3, mode) == 0 for s in range(N))
        rates[mode] = w / N
        print(f"  {mode:15s}: team A wins {w / N:6.1%} of {N}")

    def binom_two_sided_p(k, n):
        pmf = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
        return min(1.0, sum(p for p in pmf if p <= pmf[k] + 1e-15))

    p25 = binom_two_sided_p(25, 40)
    q = rates["stable-A-first"]

    def power(q, n):
        crit = [k for k in range(n + 1) if binom_two_sided_p(k, n) < 0.05]
        return sum(math.comb(n, k) * q ** k * (1 - q) ** (n - k) for k in crit)
    print(f"  25/40 against 50/50: two-sided exact p = {p25:.3f}")
    for n in (40, 100, 400):
        print(f"  a {n}-trial control detects a true {q:.1%} skew at p<0.05 with probability "
              f"{power(q, n):.1%} (a 62.5% skew: {power(0.625, n):.1%})")
    return rates, p25


# ============================================================ LOOP 13 ====
def loop13_pagination():
    """Kernel API-DESIGN/pagination/offset-vs-cursor: offset cost grows with
    depth and it duplicates rows under inserts; keyset/cursor does neither."""
    banner(13, "offset vs cursor under inserts, and a non-unique cursor key")
    N, L, P = 20000, 25, 60

    def session(mode, inserts_per_page, ts_burst=1, seed=5):
        r = Rng(seed)
        # rows: (ts, id); newest first; ts shared by bursts of ts_burst rows
        rows = [((i // ts_burst), i) for i in range(N)]
        next_id = N
        order = sorted(rows, reverse=True)
        seen, scanned = [], 0
        cursor = None
        start_set = set(order)
        for page in range(P):
            if mode == "offset":
                got = order[page * L:(page + 1) * L]
                scanned += page * L + L
            else:
                if cursor is None:
                    idx = 0
                elif mode == "cursor-ts<":
                    idx = next(i for i, x in enumerate(order) if x[0] < cursor[0])
                elif mode == "cursor-ts<=":
                    idx = next(i for i, x in enumerate(order) if x[0] <= cursor[0])
                else:                               # (ts, id) tuple cursor
                    idx = bisect_left([(-a, -b) for a, b in order], (-cursor[0], -cursor[1]) ) + 1
                got = order[idx:idx + L]
                scanned += L
            seen.extend(got)
            if got:
                cursor = got[-1]
            for _ in range(inserts_per_page):
                ts_new = order[0][0] + 1
                order.insert(0, (ts_new, next_id)); next_id += 1
        span_low = seen[-1] if seen else None
        dup = len(seen) - len(set(seen))
        expected = [x for x in sorted(start_set, reverse=True) if x >= span_low]
        missed = sum(1 for x in expected if x not in set(seen))
        return dup, missed, scanned

    for ins in (0, 3):
        for mode in ("offset", "cursor-tuple"):
            dup, missed, scanned = session(mode, ins)
            print(f"  {ins} inserts/page, {mode:12s}: duplicates {dup:3d}, missed {missed:3d}, "
                  f"rows scanned {scanned} (last page alone: {(P - 1) * L + L if mode == 'offset' else L})")
    print("  cursor on a non-unique timestamp (rows written in bursts of 10 per ts), no inserts:")
    res = {}
    for mode in ("cursor-ts<", "cursor-ts<=", "cursor-tuple"):
        dup, missed, _s = session(mode, 0, ts_burst=10)
        res[mode] = (dup, missed)
        print(f"    {mode:12s}: duplicates {dup:4d}, missed {missed:4d} of {P * L} rows paged")
    return res


# ============================================================ LOOP 14 ====
def loop14_salience():
    """Kernel SYSTEM/narrative/salience-selector-as-staged-filtering: stage the
    criteria as a hard filter so most-specific-wins is an invariant; a blended
    score can be reordered by a weight tweak; an LRU pass stops loops."""
    banner(14, "salience: blended score vs staged filter, and where LRU sits")
    FACTS = [f"f{i}" for i in range(8)]
    r = Rng(14)
    beats = []
    for b in range(80):
        k = r.below(4)
        crit = {}
        for _ in range(k):
            crit[FACTS[r.below(8)]] = r.u() < 0.5
        beats.append((f"b{b:02d}", crit, r.u()))

    def satisfied(beat, facts):
        return all(facts[k] == v for k, v in beat[1].items())

    def staged(facts, tension, recent=(), lru_first=False):
        pool = [b for b in beats if satisfied(b, facts)]
        if lru_first is True:
            fresh = [b for b in pool if b[0] not in recent]
            pool = fresh or pool
        top = max(len(b[1]) for b in pool)
        pool = [b for b in pool if len(b[1]) == top]
        if lru_first == "mid":
            fresh = [b for b in pool if b[0] not in recent]
            pool = fresh or pool
        best = min(abs(b[2] - tension) for b in pool)
        pool = [b for b in pool if abs(b[2] - tension) == best]
        if lru_first is False:
            fresh = [b for b in pool if b[0] not in recent]
            pool = fresh or pool
        return min(pool, key=lambda b: b[0])

    def blended(facts, tension, big, w):
        pool = [b for b in beats if satisfied(b, facts)]
        return max(pool, key=lambda b: (len(b[1]) * big - abs(b[2] - tension) * w, [-ord(c) for c in b[0]]))

    states = []
    for s in range(3000):
        rr = Rng(s + 99)
        states.append(({f: rr.u() < 0.5 for f in FACTS}, rr.u()))
    dis = {}
    for big, w in ((100, 10), (100, 100), (100, 150), (100, 300)):
        d = sum(len(blended(f, t, big, w)[1]) < len(staged(f, t)[1]) for f, t in states)
        dis[(big, w)] = d
        print(f"  blended BIG={big} tension weight={w:3d}: picks a less specific beat in {d:4d} of {len(states)} states")

    single = sum(1 for f, t in states
                 if sum(1 for b in beats if satisfied(b, f) and len(b[1]) == max(len(c[1]) for c in beats if satisfied(c, f))) == 1)
    print(f"  states whose most-specific tier has exactly one beat: {single} of {len(states)} "
          f"(an LRU pass placed after that stage has nothing to rotate to)")

    def run(lru_first, steps=300):
        rr = Rng(7)
        facts = {f: rr.u() < 0.5 for f in FACTS}
        tension, recent, picks, less_specific = 0.5, [], [], []
        for step in range(steps):
            if step % 25 == 0:
                facts[FACTS[rr.below(8)]] ^= True
            tension = min(1.0, max(0.0, tension + (rr.u() - 0.5) * 0.02))
            b = staged(facts, tension, recent[-3:], lru_first)
            top = max(len(c[1]) for c in beats if satisfied(c, facts))
            less_specific.append(len(b[1]) < top)
            picks.append(b)
            recent.append(b[0])
        repeats = sum(1 for a, b in zip(picks, picks[1:]) if a[0] == b[0])
        return repeats, picks, sum(less_specific)
    rep_after, picks_after, ls_after = run(False)
    rep_first, picks_first, ls_first = run(True)
    rep_mid, picks_mid, ls_mid = run("mid")
    distinct_after = len({b[0] for b in picks_after}); distinct_first = len({b[0] for b in picks_first})
    print(f"  300 selections, facts drifting: LRU after specificity -> {rep_after} back-to-back repeats, "
          f"{distinct_after} distinct beats, {ls_after} less-specific picks; LRU before specificity -> "
          f"{rep_first} repeats, {distinct_first} distinct, {ls_first} less-specific picks")
    print(f"  LRU between specificity and tension-fit -> {rep_mid} repeats, "
          f"{len({b[0] for b in picks_mid})} distinct, {ls_mid} less-specific picks")
    return dis, single, rep_after, rep_first


# ============================================================ LOOP 15 ====
def loop15_seek():
    """Kernel SYSTEM/cutscene/seek-resolves-position-never-executes-transit:
    seek relocates the pointer and fires nothing; playback advance fires what
    it crosses."""
    banner(15, "seek as lookup vs fast-forward, persistent state, exact-marker lands")
    r = Rng(15)
    markers = sorted((round(r.u() * 30.0, 3), "state" if r.u() < 0.5 else "effect", r.below(5))
                     for _ in range(14))
    times = [m[0] for m in markers]

    def truth_state(t):
        st = 0
        for mt, kind, val in markers:
            if kind == "state" and mt <= t:
                st = val
        return st

    class Player:
        def __init__(self, seek_mode, land="right"):
            self.t, self.ptr, self.state, self.fired = 0.0, 0, 0, []
            self.seek_mode, self.land = seek_mode, land

        def advance(self, t1, log=True):
            while self.ptr < len(markers) and markers[self.ptr][0] <= t1:
                mt, kind, val = markers[self.ptr]
                if kind == "state":
                    self.state = val
                if log:
                    self.fired.append((mt, kind))
                self.ptr += 1
            self.t = t1

        def seek(self, t):
            if self.seek_mode == "fast-forward":
                if t < self.t:
                    self.t, self.ptr, self.state = 0.0, 0, 0
                self.advance(t)
            else:
                self.ptr = (bisect_right if self.land == "right" else bisect_left)(times, t)
                self.t = t
                if self.seek_mode == "lookup+fold":
                    self.state = truth_state(t) if self.land == "right" else \
                        truth_state(t - 1e-9) if t in times else truth_state(t)

    targets = [round(r.u() * 30.0, 3) for _ in range(60)]
    res = {}
    for mode in ("fast-forward", "lookup", "lookup+fold"):
        p = Player(mode)
        fired_in_seek = stale = 0
        for tg in targets:
            before = len(p.fired)
            p.seek(tg)
            fired_in_seek += len(p.fired) - before
            stale += p.state != truth_state(tg)
        res[mode] = (fired_in_seek, stale)
        print(f"  {mode:12s}: markers fired during 60 scrubs {fired_in_seek:4d}; "
              f"state wrong after {stale:2d} of 60 seeks")
    # chapter select lands EXACTLY on marker times
    effects = [m for m in markers if m[1] == "effect"]
    for land in ("right", "left"):
        cue = 0
        for mt, _k, _v in effects:
            p = Player("lookup+fold", land)
            p.seek(mt)
            p.advance(mt + 0.5)
            cue += any(f == (mt, "effect") for f in p.fired)
        print(f"  chapter jump to an effect marker's exact time, bisect_{land}: its cue plays on resume "
              f"{cue} of {len(effects)}")
        res[land] = cue
    return res


if __name__ == "__main__":
    loop11_safe_integer()
    loop12_symmetric_control()
    loop13_pagination()
    loop14_salience()
    loop15_seek()
