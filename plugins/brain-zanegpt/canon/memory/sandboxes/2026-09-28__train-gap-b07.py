"""Deterministic sandbox: `brain train gap`, batch 7 (loops 31-35).

Each loop applies one ideas kernel that no memory entry had built against,
reproduces its claim, then pushes until it finds where the claim stops
holding. No real timing: every clock is a parameter. The only randomness is
a seeded splitmix64, so every run prints identical numbers.
"""
import math, hashlib, hmac
from bisect import bisect_right
from collections import deque

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


# ============================================================ LOOP 31 ====
def loop31_phase_offset():
    """Kernel VFX/weather/per-particle-phase-offset: a shared-clock wind sway
    breathes in sync; phase 2*pi*i/N decorrelates it with no RNG."""
    banner(31, "wind sway: global sync vs neighbour coherence")
    N, FREQ = 200, 1.3
    xs = [20.0 * i / N for i in range(N)]              # spawn positions, index order = x order
    r = Rng(31)
    phases = {
        "shared (0)": [0.0] * N,
        "2*pi*i/N, i in x order": [2 * math.pi * i / N for i in range(N)],
        "2*pi*i/N, shuffled i": [2 * math.pi * i / N for i in r.shuffle(list(range(N)))],
        "2*pi*i*0.618 (golden)": [2 * math.pi * ((i * 0.6180339887) % 1.0) for i in range(N)],
    }
    res = {}
    for name, ph in phases.items():
        sync = neigh = 0.0
        T = 400
        order = sorted(range(N), key=lambda i: xs[i])
        for k in range(T):
            t = k * 0.05
            off = [math.sin(t * FREQ + p) for p in ph]
            sync += abs(sum(1 if o > 0 else -1 for o in off)) / N
            a = [off[i] for i in order[:-1]]; b = [off[i] for i in order[1:]]
            ma, mb = sum(a) / len(a), sum(b) / len(b)
            cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
            va = sum((x - ma) ** 2 for x in a); vb = sum((y - mb) ** 2 for y in b)
            neigh += cov / math.sqrt(va * vb) if va > 1e-12 and vb > 1e-12 else 1.0
        res[name] = (sync / T, neigh / T)
        print(f"  {name:24s}: global sync {sync / T:.3f}; adjacent-in-x correlation {neigh / T:+.3f}")
    return res


# ============================================================ LOOP 32 ====
def loop32_pure_tracks():
    """Kernel SYSTEM/cutscene/cosmetic-tracks-as-pure-functions: state(t) is
    evaluable at any t with no replay; a naive stomp seek is wrong; lookup is
    O(log N) with sorted boundaries, not free."""
    banner(32, "cosmetic tracks: stomp vs replay vs direct eval, and relative beats")

    def make(nbeats, seed, relative):
        r = Rng(seed)
        beats, t = [], 0.0
        for i in range(nbeats):
            d = 0.5 + r.u() * 2.0
            target = r.u() * 100.0
            beats.append({"t0": t, "t1": t + d, "to": target, "relative": relative and r.u() < 0.5})
            t += d
        return beats

    def ease(a, b, u):
        u = min(1.0, max(0.0, u))
        return a + (b - a) * (u * u * (3 - 2 * u))

    class Runner:                                    # sequential, mutable
        def __init__(self, beats):
            self.b, self.i, self.x, self.start = beats, 0, 0.0, 0.0

        def advance(self, t):
            steps = 0
            while self.i < len(self.b) and t >= self.b[self.i]["t1"]:
                self.x = self.b[self.i]["to"]; self.start = self.x; self.i += 1; steps += 1
            if self.i < len(self.b):
                bt = self.b[self.i]
                self.x = ease(self.start, bt["to"], (t - bt["t0"]) / (bt["t1"] - bt["t0"]))
            return steps

    def pure_eval(beats, t, bounds, starts):
        lo, hi, probes = 0, len(bounds), 0              # counted binary search = bisect_right
        while lo < hi:
            mid = (lo + hi) // 2; probes += 1
            if t < bounds[mid]:
                hi = mid
            else:
                lo = mid + 1
        k = max(0, lo - 1)
        if k >= len(beats):
            return beats[-1]["to"], probes
        bt = beats[k]
        return ease(starts[k], bt["to"], (t - bt["t0"]) / (bt["t1"] - bt["t0"])), probes

    def truth(beats, t):
        run = Runner(beats); run.advance(t); return run.x

    res = {}
    for nb in (3, 30, 300):
        beats = make(nb, nb, False)
        bounds = [b["t0"] for b in beats]
        starts = [0.0] + [b["to"] for b in beats[:-1]]
        r = Rng(nb + 7)
        stomp_wrong = pure_wrong = 0
        replay_steps = pure_probes = 0
        cur = Runner(beats)
        for _ in range(200):
            t = r.u() * beats[-1]["t1"]
            tr = truth(beats, t)
            # naive stomp: keep the runner's beat index, just overwrite elapsed
            if cur.i < len(beats):
                bt = cur.b[cur.i]
                sx = ease(cur.start, bt["to"], (t - bt["t0"]) / (bt["t1"] - bt["t0"]))
            else:
                sx = cur.x
            stomp_wrong += abs(sx - tr) > 1e-9
            rr = Runner(beats); replay_steps += rr.advance(t)
            px, pr = pure_eval(beats, t, bounds, starts); pure_probes += pr
            pure_wrong += abs(px - tr) > 1e-9
            cur.advance(min(beats[-1]["t1"] * 0.3, t))       # the live runner sits early in the scene
        res[nb] = (stomp_wrong, pure_wrong, replay_steps / 200, pure_probes / 200)
        print(f"  {nb:3d} beats, 200 seeks: stomp wrong {stomp_wrong}, direct eval wrong {pure_wrong}; "
              f"replay crosses {replay_steps / 200:.1f} beats per seek, binary search {pure_probes / 200:.1f} probes")
    # relative beats: "move from wherever the previous beat left the camera, by +to"
    beats = make(30, 99, True)
    for b in beats:
        if b["relative"]:
            b["delta"] = b["to"] - 50.0

    def rel_truth(t):
        x = 0.0
        for b in beats:
            end = x + b["delta"] if b["relative"] else b["to"]
            if t < b["t1"]:
                return ease(x, end, (t - b["t0"]) / (b["t1"] - b["t0"]))
            x = end
        return x
    bounds = [b["t0"] for b in beats]
    naive_starts = [0.0] + [(b["delta"] if b["relative"] else b["to"]) for b in beats[:-1]]
    baked, x = [], 0.0
    for b in beats:
        baked.append(x)
        x = x + b["delta"] if b["relative"] else b["to"]
    r = Rng(5)
    wrong_naive = wrong_baked = 0
    for _ in range(200):
        t = r.u() * beats[-1]["t1"]
        k = max(0, bisect_right(bounds, t) - 1)
        b = beats[k]
        end_naive = naive_starts[k] + b["delta"] if b["relative"] else b["to"]
        end_baked = baked[k] + b["delta"] if b["relative"] else b["to"]
        u = (t - b["t0"]) / (b["t1"] - b["t0"])
        wrong_naive += abs(ease(naive_starts[k], end_naive, u) - rel_truth(t)) > 1e-9
        wrong_baked += abs(ease(baked[k], end_baked, u) - rel_truth(t)) > 1e-9
    rel = sum(b["relative"] for b in beats)
    print(f"  30 beats, {rel} of them relative ('from wherever the last beat ended'): direct eval with each "
          f"beat's own target as the next start wrong {wrong_naive}/200; with start values baked at load {wrong_baked}/200")
    return res, wrong_naive, wrong_baked


# ============================================================ LOOP 33 ====
def loop33_watch_skip_parity():
    """Kernel SYSTEM/cutscene/cmd-marker-timeline/watch-skip-provable-parity:
    markers dispatch real commands; skip fires the rest in order; watch and
    skip end on byte-identical state, proven by hashing both."""
    banner(33, "watch vs skip end-state hash under four timeline designs")

    def reduce(state, cmd):
        kind, arg = cmd
        s = dict(state)
        if kind == "give":
            s["items"] = s.get("items", ()) + (arg,)
        elif kind == "flag":
            s[arg] = s.get(arg, 0) + 1
        elif kind == "stamp":
            s["stamp"] = arg
        return s

    def h(state):
        return hashlib.sha256(repr(sorted(state.items())).encode()).hexdigest()[:12]

    def scene(seed):
        r = Rng(seed)
        markers = []
        for i in range(8):
            markers.append((10 * (1 + r.below(300)), ("give" if r.u() < 0.5 else "flag", f"m{i}")))
        markers.sort(key=lambda m: m[0])
        return markers

    def play(markers, design, skip_at, seed):
        r = Rng(seed * 3 + 1)
        state, t, ptr, fired_at = {}, 0, 0, {}
        cosmetic_hit = False
        while ptr < len(markers):
            dt = 10 * (1 + r.below(4))                    # frame deltas on the 10 ms grid
            if skip_at is not None and t >= skip_at:
                if design == "skip-by-time>=":
                    for at, cmd in markers:
                        if at >= t:
                            state = reduce(state, cmd)
                else:
                    for at, cmd in markers[ptr:]:
                        state = reduce(state, cmd if design != "wallclock-payload" else ("stamp", t))
                return state
            t += dt
            while ptr < len(markers) and markers[ptr][0] <= t:
                at, cmd = markers[ptr]
                state = reduce(state, cmd if design != "wallclock-payload" else ("stamp", t))
                ptr += 1
            if design == "cosmetic-dispatch" and not cosmetic_hit and t >= 1500:
                state = reduce(state, ("flag", "camera-reached-gate")); cosmetic_hit = True
        return state

    res = {}
    for design in ("pointer", "skip-by-time>=", "wallclock-payload", "cosmetic-dispatch"):
        mism = 0
        for s in range(500):
            markers = scene(s)
            watched = play(markers, design, None, s)
            skip_at = 10 * (1 + Rng(s + 77).below(300))
            skipped = play(markers, design, skip_at, s)
            mism += h(watched) != h(skipped)
        res[design] = mism
        print(f"  {design:18s}: watch and skip hashes differ in {mism} of 500 scenes")
    return res


# ============================================================ LOOP 34 ====
def loop34_webhooks():
    """Kernel API-DESIGN/webhooks/delivery-guarantees: at-least-once delivery,
    so log processed event ids and skip repeats, and verify signatures."""
    banner(34, "webhook handler: duplicates, crash windows, races, order, replays")
    KEY = b"whsec_test"

    def sign(body, ts):
        return hmac.new(KEY, f"{ts}.{body}".encode(), hashlib.sha256).hexdigest()

    def deliveries(seed, n=200, ack_loss=0.1):
        r = Rng(seed)
        out = []
        for i in range(n):
            out.append(i)
            while r.u() < ack_loss:                      # ack lost -> sender retries
                out.append(i)
        return out

    def run(mode, seed, crash_p=0.0):
        """A crashed handler returns no 2xx, so the sender retries it."""
        r = Rng(seed + 1000)
        seen, effects = set(), []
        q = deque(deliveries(seed))
        while q:
            ev = q.popleft()
            if mode == "no-dedupe":
                effects.append(ev); continue
            if ev in seen:
                continue
            crash = r.u() < crash_p
            if mode == "record-after":
                effects.append(ev)
                if not crash:
                    seen.add(ev)
            elif mode == "record-before":
                seen.add(ev)
                if not crash:
                    effects.append(ev)
            elif mode == "atomic":
                if not crash:
                    effects.append(ev); seen.add(ev)
            if crash:
                q.append(ev)                             # retried later
        dup = len(effects) - len(set(effects))
        lost = 200 - len(set(effects))
        return dup, lost

    for mode in ("no-dedupe", "record-after", "record-before", "atomic"):
        d = l = 0
        for s in range(50):
            dd, ll = run(mode, s, crash_p=0.02)
            d += dd; l += ll
        print(f"  {mode:13s} (10% ack loss, 2% handler crash), 50 x 200 events: duplicated effects {d}, lost events {l}")

    # concurrent duplicate deliveries: check-then-insert vs insert-if-absent
    def race(atomic):
        dup = 0
        steps = ["check", "effect", "record"] if not atomic else ["claim", "effect"]
        L = len(steps)
        total = 0
        from itertools import combinations
        for pos in combinations(range(2 * L), L):
            order = [1] * (2 * L)
            for p in pos:
                order[p] = 0
            seen, effects, pcs, ok = set(), 0, [0, 0], [True, True]
            for tid in order:
                st = steps[pcs[tid]]; pcs[tid] += 1
                if st == "check":
                    ok[tid] = 7 not in seen
                elif st == "claim":
                    ok[tid] = 7 not in seen
                    seen.add(7)
                elif st == "effect" and ok[tid]:
                    effects += 1
                elif st == "record" and ok[tid]:
                    seen.add(7)
            dup += effects > 1; total += 1
        return dup, total
    d1, t1 = race(False); d2, t2 = race(True)
    print(f"  two concurrent deliveries of one event, all interleavings: check-then-record double-applies "
          f"{d1}/{t1}; atomic insert-if-absent {d2}/{t2}")

    # out-of-order status updates: retries land after newer events
    regress = regress_v = 0
    for s in range(200):
        r = Rng(s + 5000)
        events = [(i, ("active", "past_due", "canceled")[min(2, i // 3)]) for i in range(8)]
        arrivals = []
        for ev in events:
            arrivals.append(ev)
            if r.u() < 0.2:
                arrivals.append(ev)                      # a retry, delivered late
        late = [a for a in arrivals]
        tail = late[-4:]; r.shuffle(tail); late[-4:] = tail
        state, seen = None, set()
        state_v, ver = None, -1
        for i, st in late:
            if i not in seen:
                seen.add(i); state = st
            if i > ver:
                ver = i; state_v = st
        regress += state != events[-1][1]
        regress_v += state_v != events[-1][1]
    print(f"  idempotent handler, 200 subscriptions with late retries: final status wrong {regress}; "
          f"with an event-version check {regress_v}")

    # signed replays: an old, validly signed event re-sent later
    accepted_no_ts = accepted_ts = 0
    for s in range(200):
        r = Rng(s + 9000)
        ts = 1_000_000 + r.below(10_000)
        body = f'{{"id":"evt_{s}","type":"invoice.paid"}}'
        sig = sign(body, ts)
        now = ts + 600 + r.below(86_400)                 # replayed 10 min to a day later
        valid = hmac.compare_digest(sig, sign(body, ts))
        accepted_no_ts += valid
        accepted_ts += valid and abs(now - ts) <= 300
    print(f"  200 captured signed events replayed 10 min to 1 day later: accepted with signature check only "
          f"{accepted_no_ts}; with a 5-minute timestamp tolerance {accepted_ts}")
    return d1, d2, regress, regress_v


# ============================================================ LOOP 35 ====
def loop35_softlock():
    """Kernel LEVEL-DESIGN/metroidvania/bfs-softlock-audit-assumes-zero-
    abilities: BFS from spawn with zero abilities; flag one-way drops whose
    landing has no ability-free way out."""
    banner(35, "zero-ability drop audit vs exact (room, abilities) state search")
    ABIL = ("a", "b", "c")

    def gen(seed):
        r = Rng(seed)
        n = 10
        edges = []                                       # (u, v, gate or None, oneway)
        for v in range(1, n):
            u = r.below(v)
            g = ABIL[r.below(3)] if r.u() < 0.4 else None
            edges.append((u, v, g, False))
        for _ in range(3):
            u, v = r.below(n), r.below(n)
            if u != v:
                edges.append((u, v, ABIL[r.below(3)] if r.u() < 0.4 else None, False))
        for _ in range(2):
            u, v = r.below(n), r.below(n)
            if u != v:
                edges.append((u, v, ABIL[r.below(3)] if r.u() < 0.3 else None, True))
        rooms = r.shuffle(list(range(1, n)))
        item = {rooms[0]: "a", rooms[1]: "b", rooms[2]: "c"}
        goal = rooms[3]
        return n, edges, item, goal

    def moves(edges, room, have):
        for u, v, g, one in edges:
            if g is not None and g not in have:
                continue
            if u == room:
                yield v
            if not one and v == room:
                yield u

    def reach_states(n, edges, item, start, have0):
        start_have = frozenset(have0 | ({item[start]} if start in item else set()))
        seen = {(start, start_have)}
        q = deque(seen)
        while q:
            room, have = q.popleft()
            for v in moves(edges, room, have):
                nh = frozenset(have | ({item[v]} if v in item else set()))
                if (v, nh) not in seen:
                    seen.add((v, nh)); q.append((v, nh))
        return seen

    def can_finish(n, edges, item, goal, room, have):
        return any(r_ == goal for r_, _h in reach_states(n, edges, item, room, set(have)))

    tp = fp = fn = tn = 0
    levels = 0
    for seed in range(3000):
        n, edges, item, goal = gen(seed)
        states = reach_states(n, edges, item, 0, set())
        if not any(r_ == goal for r_, _ in states):
            continue                                     # not completable at all; skip
        levels += 1
        truth = any(not can_finish(n, edges, item, goal, r_, h) for r_, h in states)
        # kernel audit: every one-way drop whose origin is reachable at all; land there with ZERO
        # abilities and ask whether the goal is still reachable (pickups allowed)
        reachable_rooms = {r_ for r_, _ in states}
        flagged = False
        for u, v, g, one in edges:
            if one and u in reachable_rooms:
                if not can_finish(n, edges, item, goal, v, set()):
                    flagged = True
        tp += flagged and truth; fp += flagged and not truth
        fn += (not flagged) and truth; tn += (not flagged) and not truth
    print(f"  {levels} completable random levels (10 rooms, 3 abilities, 2 one-way drops):")
    print(f"    zero-ability drop audit vs exact state search: caught {tp}, false alarms {fp}, "
          f"missed {fn}, clean {tn}")
    return tp, fp, fn, tn


if __name__ == "__main__":
    loop31_phase_offset()
    loop32_pure_tracks()
    loop33_watch_skip_parity()
    loop34_webhooks()
    loop35_softlock()
