"""Deterministic sandbox: `brain train gap`, batch 10 (loops 46-50).

Each loop applies one ideas kernel that no memory entry had built against,
reproduces its claim, then pushes until it finds where the claim stops
holding. No real timing: every clock is a parameter. The only randomness is
a seeded splitmix64. Loop 49 runs in real Node.js (real JSON.stringify); the
rest are Python models.
"""
import math, os, subprocess, tempfile, json
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


def banner(n, title):
    print("=" * 78); print(f"LOOP {n} -- {title}"); print("=" * 78)


# ============================================================ LOOP 46 ====
def loop46_realtime_callback():
    """Kernel DSP/real-time-buffer/no-unbounded-work-in-the-callback: one late
    callback is one glitch whatever the average; preallocate, and talk across
    threads through a lock-free SPSC ring."""
    banner(46, "audio callback deadlines: mean latency vs glitches, three hand-off designs")
    DEADLINE = 128 / 48000 * 1e6                         # 2667 us per 128-sample block
    BLOCKS = 48000 * 600 // 128                           # 10 simulated minutes
    DSP = 900.0                                           # fixed DSP cost per block, us

    def heavy_tail(r, typical, p_tail, tail_max):
        """Mostly `typical`, occasionally a long stall (assumed shape)."""
        if r.u() < p_tail:
            return typical + r.u() * tail_max
        return typical * (0.5 + r.u())

    res = {}
    for design in ("malloc-in-callback", "mutex-with-ui", "trylock-skip", "spsc-ring"):
        r = Rng(46)
        glitches, total, worst = 0, 0.0, 0.0
        stale_blocks = 0
        ui_holds_until = -1.0
        t = 0.0
        for b in range(BLOCKS):
            t = b * DEADLINE
            work = DSP * (0.9 + 0.2 * r.u())
            # the UI thread takes the shared lock now and then; while holding it it may be preempted
            if r.u() < 0.02:
                hold = 20.0 + (r.u() * 8000.0 if r.u() < 0.01 else 0.0)
                ui_holds_until = t + r.u() * DEADLINE + hold
            if design == "malloc-in-callback":
                if r.u() < 0.3:                           # a new voice needs memory this block
                    work += heavy_tail(r, 5.0, 0.0005, 6000.0)
            elif design == "mutex-with-ui":
                if ui_holds_until > t:
                    work += ui_holds_until - t            # blocks until the UI thread releases
            elif design == "trylock-skip":
                if ui_holds_until > t:
                    stale_blocks += 1                     # parameters left as last block's
                work += 0.2
            elif design == "spsc-ring":
                work += 0.5                               # pop a few messages, bounded
            total += work; worst = max(worst, work)
            glitches += work > DEADLINE
        res[design] = (total / BLOCKS, worst, glitches, stale_blocks)
        print(f"  {design:18s}: mean {total / BLOCKS:7.1f} us, worst {worst:7.1f} us (deadline {DEADLINE:.0f}), "
              f"glitches in 10 min {glitches}" + (f", blocks with stale params {stale_blocks}" if design == "trylock-skip" else ""))
    return res


# ============================================================ LOOP 47 ====
def loop47_layer_counters():
    """Kernel testing/harness/count-the-same-event-at-every-depth: a counter
    per layer (DOM, framework input, hit decision) localises an input fault
    in one round trip."""
    banner(47, "on-screen per-layer counters: which fault can each probe localise?")
    FAULTS = {
        "overlay-swallows-dom": 0, "pointer-events-none": 0,
        "framework-input-disabled": 1, "hit-test-wrong-camera": 2,
        "hit-area-offset-30pct": 2, "handler-throws-after-hit": 3,
        "action-gated-by-state": 3, "none": None,
    }

    def run(fault, taps=20, seed=0):
        r = Rng(seed)
        c = [0, 0, 0, 0]                                  # dom, input, hit, action-done
        for _ in range(taps):
            if fault in ("overlay-swallows-dom", "pointer-events-none"):
                continue
            c[0] += 1
            if fault == "framework-input-disabled":
                continue
            c[1] += 1
            if fault == "hit-test-wrong-camera" or (fault == "hit-area-offset-30pct" and r.u() < 0.3):
                continue
            c[2] += 1
            if fault in ("handler-throws-after-hit", "action-gated-by-state"):
                continue
            c[3] += 1
        return c

    def localise(counts, probe):
        """The layers between the last counter that kept up and the first that fell behind."""
        prev = -1
        for L in probe:
            if counts[L] < 20:
                return set(range(prev + 1, L + 1))
            prev = L
        return set()                                      # every counter kept up: "input is fine"

    res = {}
    probes = {"1 counter (hit decided)": [2], "3 counters (DOM, input, hit)": [0, 1, 2],
              "4 counters (+ action done)": [0, 1, 2, 3]}
    for name, probe in probes.items():
        right, rows = 0, []
        for fault, layer in FAULTS.items():
            if fault == "none":
                continue                                  # nobody reports a working button
            ok = localise(run(fault), probe) == {layer}
            right += ok
            rows.append(f"{fault}:{'ok' if ok else 'x'}")
        res[name] = right
        print(f"  {name:28s}: localised {right}/{len(FAULTS) - 1}  (" + ", ".join(rows) + ")")
    c = run("hit-area-offset-30pct", taps=200, seed=4)
    print(f"  partial fault, 200 taps, hit area 30% off: counters {c[:3]} -> hit/input ratio {c[2] / c[1]:.2f}")
    return res


# ============================================================ LOOP 48 ====
def loop48_removed_guard():
    """Kernel SYSTEM/testing/a-fix-for-one-invariant-can-delete-the-only-check:
    trusting the agent's live position (correct) also deleted the only check
    that would catch a non-atomic save leaving the agent inside a wall."""
    banner(48, "non-atomic save: incidents, and where the deleted check can live")
    W = H = 24

    def trial(seed, churn, gap, atomic):
        r = Rng(seed)
        grid = [[r.u() < 0.2 for _ in range(W)] for _ in range(H)]
        ax, ay = r.below(W), r.below(H)
        grid[ay][ax] = False
        for _ in range(30):                               # live play: agent moves, grid churns
            nx, ny = ax + r.below(3) - 1, ay + r.below(3) - 1
            if 0 <= nx < W and 0 <= ny < H and not grid[ny][nx]:
                ax, ay = nx, ny
            for _ in range(3):
                cx, cy = r.below(W), r.below(H)
                if (cx, cy) != (ax, ay) and r.u() < churn * 10:
                    grid[cy][cx] = not grid[cy][cx]
        live_in_wall = 0
        # a door closes on the agent during live play: legitimate "inside blocked" moments
        if r.u() < 0.05:
            grid[ay][ax] = True; live_in_wall = 1
        saved_pos = (ax, ay)
        if not atomic:
            for _ in range(gap):                          # churn between the two save steps
                cx, cy = r.below(W), r.below(H)
                if r.u() < churn:
                    grid[cy][cx] = not grid[cy][cx]
        saved_grid = [row[:] for row in grid]
        if atomic:
            saved_grid = [row[:] for row in grid]
        bad = saved_grid[saved_pos[1]][saved_pos[0]]
        return bad, live_in_wall

    res = {}
    for churn, gap in ((0.02, 20), (0.05, 40)):
        for atomic in (False, True):
            N = 5000
            incidents = live = 0
            for s in range(N):
                bad, lw = trial(s, churn, gap, atomic)
                incidents += bad and not lw
                live += lw
            res[(churn, gap, atomic)] = incidents
            print(f"  churn {churn} x {gap} steps between saves, {'atomic' if atomic else 'two-step'} save: "
                  f"agent saved inside a blocked cell {incidents}/{N} ({incidents / N:.2%})")
    # detection: replanner trusts position (catches 0); a load-time validator catches every one;
    # putting the check back into the replanner would also reject legitimate live moments
    N = 5000
    inc = live_moments = 0
    for s in range(N):
        bad, lw = trial(s, 0.05, 40, False)
        inc += bad and not lw
        live_moments += lw
    print(f"  of {inc} incidents: replanner (trusts position) flags 0; a load-time position-vs-grid check flags {inc}; "
          f"re-adding the check to the live replanner would also reject {live_moments} legitimate live moments "
          f"(a door closing on the agent)")
    return res, inc, live_moments


# ============================================================ LOOP 49 ====
JS49 = r"""
function reduce(s, cmd) {
  const n = JSON.parse(JSON.stringify(s));
  if (cmd.t === "move") { n.pos[cmd.id] = [n.pos[cmd.id][0] + cmd.dx, n.pos[cmd.id][1] + cmd.dy]; }
  if (cmd.t === "hit") { n.hp[cmd.id] -= cmd.d; }
  return n;
}
function fp(s) { return JSON.stringify(s); }
function rng(seed) { let x = BigInt(seed) + 1n; return () => { x = (x * 6364136223846793005n + 1442695040888963407n) & ((1n << 64n) - 1n); return Number(x >> 33n) / 2 ** 31; }; }
const out = {};
// 1) replay parity with a view that reads vs a view that writes smoothing back into state
for (const design of ["view-reads", "view-writes-back"]) {
  let mism = 0;
  for (let seed = 0; seed < 200; seed++) {
    const r = rng(seed);
    const cmds = [];
    for (let i = 0; i < 60; i++) cmds.push(r() < 0.7 ? {t: "move", id: Math.floor(r() * 3), dx: Math.floor(r() * 3) - 1, dy: Math.floor(r() * 3) - 1} : {t: "hit", id: Math.floor(r() * 3), d: 1 + Math.floor(r() * 5)});
    let live = {pos: [[0, 0], [5, 5], [9, 1]], hp: [30, 30, 30]};
    const view = {pos: live.pos.map(p => p.slice())};
    for (const c of cmds) {
      live = reduce(live, c);
      for (let k = 0; k < 3; k++) {             // the view eases toward state each frame
        view.pos[k][0] += (live.pos[k][0] - view.pos[k][0]) * 0.5;
        view.pos[k][1] += (live.pos[k][1] - view.pos[k][1]) * 0.5;
        if (design === "view-writes-back" && r() < 0.1) live.pos[k] = view.pos[k].slice();   // "snap state to what's drawn"
      }
    }
    let rep = {pos: [[0, 0], [5, 5], [9, 1]], hp: [30, 30, 30]};
    for (const c of cmds) rep = reduce(rep, c);
    mism += fp(rep) !== fp(live);
  }
  out[design] = mism;
}
// 2) save/load as JSON.stringify(state): which value kinds survive a round trip
const kinds = {
  number: 3, float: 0.1 + 0.2, negZero: -0, nan: NaN, inf: Infinity, undef: undefined,
  nested: {a: [1, {b: 2}]}, map: new Map([["k", 1]]), set: new Set([1, 2]), date: new Date(0),
  sparse: [1, , 3],
};
const surv = {};
for (const [k, v] of Object.entries(kinds)) {
  const s = {v};
  const back = JSON.parse(JSON.stringify(s));
  const same = (a, b) => Object.is(a, b) || (typeof a === "object" && a !== null && !(a instanceof Map) && !(a instanceof Set) && !(a instanceof Date) && JSON.stringify(a) === JSON.stringify(b) && Array.isArray(a) === Array.isArray(b) && (!Array.isArray(a) || a.every((x, i) => Object.is(x, b[i])) && Object.keys(a).length === Object.keys(b).length));
  surv[k] = ("v" in back) && same(v, back.v);
}
let bigThrows = false; try { JSON.stringify({v: 10n}); } catch (e) { bigThrows = true; }
surv.bigint_throws = bigThrows;
out.roundtrip = surv;
console.log(JSON.stringify(out));
"""


def loop49_reducer_seam():
    """Kernel SYSTEM/architecture/authoritative-reducer/command-event-seam: one
    reduce() mutates state, the view never writes it, save/load is
    stringify(state)."""
    banner(49, "reducer seam in real Node: a writing view, and what stringify(state) keeps")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "r.js")
        open(p, "w").write(JS49)
        ver = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
        o = json.loads(subprocess.run(["node", p], capture_output=True, text=True).stdout)
    print(f"  node {ver}; replay of the command log vs live state, 200 seeds: "
          f"view reads only -> {o['view-reads']} mismatches; view writes eased positions back -> {o['view-writes-back']}")
    rt = o["roundtrip"]
    kept = [k for k, v in rt.items() if v is True and k != "bigint_throws"]
    lost = [k for k, v in rt.items() if v is False and k != "bigint_throws"]
    print(f"  JSON round trip keeps: {', '.join(kept)}")
    print(f"  JSON round trip changes or drops: {', '.join(lost)}; BigInt throws: {rt['bigint_throws']}")
    return o


# ============================================================ LOOP 50 ====
def loop50_trust_by_source():
    """Kernel SYSTEM/architecture/trust-by-source-not-by-value-type: trust
    values state maintains; never trust values the current command supplies;
    a position from a payload allows a wall clip."""
    banner(50, "position trust by provenance, including provenance laundered through state")
    W = H = 16

    def world(seed):
        r = Rng(seed)
        walls = {(x, y) for x in range(W) for y in range(H) if r.u() < 0.25}
        start = (0, 0)
        walls.discard(start)
        return walls, start, r

    def reachable(walls, a, b):
        q, seen = deque([a]), {a}
        while q:
            x, y = q.popleft()
            if (x, y) == b:
                return True
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= n[0] < W and 0 <= n[1] < H and n not in walls and n not in seen:
                    seen.add(n); q.append(n)
        return False

    res = {}
    for design in ("trust-payload-position", "store-payload-then-trust-state", "validate-at-write", "state-only"):
        exploits = 0
        N = 2000
        for s in range(N):
            walls, pos, r = world(s)
            breached = False
            for _ in range(15):
                kind = r.below(3)
                claim = (r.below(W), r.below(H))
                if kind == 0:                                 # move by one step (sim computes it)
                    dx, dy = ((1, 0), (-1, 0), (0, 1), (0, -1))[r.below(4)]
                    n = (pos[0] + dx, pos[1] + dy)
                    if 0 <= n[0] < W and 0 <= n[1] < H and n not in walls:
                        pos = n
                elif kind == 1:                               # replan: from where?
                    start = claim if design == "trust-payload-position" else pos
                    breached = breached or start in walls or not reachable(walls, (0, 0), start)
                else:                                         # a "sync position" command from the client
                    if design == "store-payload-then-trust-state":
                        pos = claim                           # written into state unchecked
                    elif design == "validate-at-write":
                        if claim not in walls and abs(claim[0] - pos[0]) + abs(claim[1] - pos[1]) <= 1:
                            pos = claim
                breached = breached or pos in walls
            exploits += breached
        res[design] = exploits
        print(f"  {design:31s}: fuzzed sessions (of 2000) where the agent ended up in a wall or an unreachable cell: {exploits}")
    return res


if __name__ == "__main__":
    loop46_realtime_callback()
    loop47_layer_counters()
    loop48_removed_guard()
    loop49_reducer_seam()
    loop50_trust_by_source()
