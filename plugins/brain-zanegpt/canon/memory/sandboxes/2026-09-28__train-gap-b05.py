"""Deterministic sandbox: `brain train gap`, batch 5 (loops 21-25).

Each loop applies one ideas kernel that no memory entry had built against,
reproduces its claim, then pushes until it finds where the claim stops
holding. No real timing: every clock is a parameter. The only randomness is
a seeded splitmix64, so every run prints identical numbers. Loop 21 reads
real compiler output (gcc and clang at -O2) and loop 23 runs real Node.js;
both are deterministic for a given toolchain version, which is printed.
"""
import math, os, re, subprocess, tempfile, json

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


# ============================================================ LOOP 21 ====
C_SRC = r"""
#include <stdint.h>
static inline uint64_t mix(uint64_t v) {
    v ^= v >> 33; v *= 0xff51afd7ed558ccdULL;
    v ^= v >> 33; v *= 0xc4ceb9fe1a85ec53ULL;
    v ^= v >> 33; return v;
}
#define KEEP(v) __asm__ volatile("" : : "r"(v) : "memory")
#define OPAQUE(v) __asm__ volatile("" : "+r"(v))
uint64_t unused_result(uint64_t n, uint64_t x) {
    for (uint64_t i = 0; i < n; i++) { uint64_t r = mix(x + i); (void)r; } return 0; }
uint64_t sum_const_input(uint64_t n, uint64_t x) {
    uint64_t s = 0; for (uint64_t i = 0; i < n; i++) s += mix(42); return s; }
uint64_t keep_const_input(uint64_t n, uint64_t x) {
    for (uint64_t i = 0; i < n; i++) { uint64_t r = mix(42); KEEP(r); } return 0; }
uint64_t keep_opaque_input(uint64_t n, uint64_t x) {
    for (uint64_t i = 0; i < n; i++) { uint64_t in = 42; OPAQUE(in); uint64_t r = mix(in); KEEP(r); } return 0; }
uint64_t sum_varying_input(uint64_t n, uint64_t x) {
    uint64_t s = 0; for (uint64_t i = 0; i < n; i++) s += mix(x + i); return s; }
uint64_t sum_linear(uint64_t n, uint64_t x) {
    uint64_t s = 0; for (uint64_t i = 0; i < n; i++) s += i * x; return s; }
uint64_t keep_linear(uint64_t n, uint64_t x) {
    uint64_t s = 0; for (uint64_t i = 0; i < n; i++) { s += i * x; KEEP(s); } return s; }
"""
FUNCS = ["unused_result", "sum_const_input", "keep_const_input", "keep_opaque_input",
         "sum_varying_input", "sum_linear", "keep_linear"]


def _asm_functions(asm):
    out, cur = {}, None
    for line in asm.splitlines():
        m = re.match(r"^([A-Za-z_][\w.]*):", line)
        if m and m.group(1) in FUNCS:
            cur = m.group(1); out[cur] = []
            continue
        if cur and re.match(r"^\s*\.cfi_endproc", line):
            cur = None
            continue
        if cur:
            out[cur].append(line)
    return out


def _loop_stats(lines):
    """Instructions between a label and a later jump back to it = loop body."""
    labels = {}
    body = [l.strip() for l in lines if l.strip() and not l.strip().startswith(".") or re.match(r"^\.L\w+:", l.strip())]
    for i, l in enumerate(body):
        m = re.match(r"^(\.L\w+):", l)
        if m:
            labels[m.group(1)] = i
    loop_mul, has_loop = 0, False
    for j, l in enumerate(body):
        m = re.match(r"^j\w+\s+(\.L\w+)", l)
        if m and m.group(1) in labels and labels[m.group(1)] < j:
            has_loop = True
            seg = body[labels[m.group(1)]:j + 1]
            loop_mul = max(loop_mul, sum(1 for s in seg if re.match(r"^(imul|mul)", s)))
    return has_loop, loop_mul


def loop21_microbenchmark():
    """Kernel PERFORMANCE/measurement/microbenchmarking: a benchmark can time
    nothing (dead-code elimination, constant folding); consume the output and
    read inputs from mutable state."""
    banner(21, "what survives -O2: loop present? multiplies per iteration (gcc | clang)")
    res = {}
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "b.c")
        open(src, "w").write(C_SRC)
        for cc in ("gcc", "clang"):
            ver = subprocess.run([cc, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
            asm = subprocess.run([cc, "-O2", "-S", "-o", "-", src], capture_output=True, text=True).stdout
            fns = _asm_functions(asm)
            res[cc] = {f: _loop_stats(fns.get(f, [])) for f in FUNCS}
            print(f"  {cc}: {ver}")
    for f in FUNCS:
        g, c = res["gcc"][f], res["clang"][f]
        fmt = lambda t: f"{'loop' if t[0] else 'no loop'}, {t[1]} mul"
        print(f"  {f:18s} gcc: {fmt(g):16s} clang: {fmt(c)}")
    return res


# ============================================================ LOOP 22 ====
def loop22_snapshot_scope():
    """Kernel SYSTEM/architecture/a-scope-local-snapshot-technique-silently-
    inherits-staleness: snapshot content into a save and a content patch never
    reaches it; the only remedy is a wholesale wipe."""
    banner(22, "save snapshots vs live references across content patches")
    r = Rng(22)
    QUESTS = 30
    content = {q: {"rev": 0, "steps": [f"q{q}s{i}" for i in range(3 + r.below(4))],
                   "reward": 100 + r.below(50), "text": f"t{q}"} for q in range(QUESTS)}
    history = {q: [json.loads(json.dumps(content[q]))] for q in range(QUESTS)}
    saves = []
    for s in range(400):
        q = r.below(QUESTS)
        snap = json.loads(json.dumps(content[q]))
        saves.append({"q": q, "snap": snap, "rev": 0, "progress": r.below(len(snap["steps"])),
                      "step_id": None})
        saves[-1]["step_id"] = snap["steps"][saves[-1]["progress"]]
    kinds = {"text": 0, "reward": 0, "insert-step": 0, "remove-step": 0}
    for p in range(40):                                     # 40 content patches
        q = r.below(QUESTS)
        c = content[q]
        k = ("text", "reward", "insert-step", "remove-step")[r.below(4)]
        if k == "remove-step" and len(c["steps"]) <= 2:
            k = "text"
        kinds[k] += 1
        if k == "text":
            c["text"] += "'"
        elif k == "reward":
            c["reward"] += 10
        elif k == "insert-step":
            c["steps"].insert(r.below(len(c["steps"]) + 1), f"q{q}n{p}")
        else:
            c["steps"].pop(r.below(len(c["steps"])))
        c["rev"] += 1
        history[q].append(json.loads(json.dumps(c)))
    touched = [s for s in saves if content[s["q"]]["rev"] > 0]
    stale_snap = sum(s["snap"] != content[s["q"]] for s in saves)
    # live reference by index: progress index read against HEAD content
    broken_idx = 0
    for s in saves:
        steps = content[s["q"]]["steps"]
        broken_idx += s["progress"] >= len(steps) or steps[s["progress"]] != s["step_id"]
    # live reference with a stable step id: resolve by id, fall back if removed
    lost_id = sum(s["step_id"] not in content[s["q"]]["steps"] for s in saves)
    print(f"  {len(saves)} saves over {QUESTS} quests, 40 patches {kinds}; {len(touched)} saves hit a patched quest")
    print(f"  snapshot in save: stale on load {stale_snap}; wholesale version wipe: {len(saves)} saves' progress lost")
    print(f"  live reference, progress as a step INDEX: pointing at the wrong or no step {broken_idx}")
    print(f"  live reference, progress as a stable step ID: only saves whose current step was removed need handling "
          f"{lost_id}")
    return stale_snap, broken_idx, lost_id, len(touched)


# ============================================================ LOOP 23 ====
JS_SRC = r"""
const N = +process.argv[2], B = +process.argv[3], out = [];
function h(k) { let x = k | 0; x = Math.imul(x ^ (x >>> 16), 0x45d9f3b); x = Math.imul(x ^ (x >>> 16), 0x45d9f3b); x = x ^ (x >>> 16); return x | 0; }
for (let set = 0; set < 10; set++) {
  let neg = 0, maxLoad = 0; const buckets = new Array(B).fill(0);
  for (let i = 0; i < N; i++) { const b = h(set * 1000003 + i) % B; if (b < 0 || b >= B) neg++; else { buckets[b]++; } }
  for (const c of buckets) maxLoad = Math.max(maxLoad, c);
  out.push([neg, maxLoad]);
}
console.log(JSON.stringify(out));
"""


def loop23_vary_substrate():
    """Kernel VERIFICATION/method/vary-the-substrate: ten checks on one
    substrate are one experiment; a `|0` vs `>>>0` defect is 32-bit JS
    semantics that a Python model cannot see."""
    banner(23, "ten Python checks of a JS bucket hash vs the same ten in real Node")
    N, B = 5000, 64

    def imul(a, b):
        return (a * b) & 0xFFFFFFFF

    def h_py(k):
        x = k & 0xFFFFFFFF
        x = imul(x ^ (x >> 16), 0x45d9f3b)
        x = imul(x ^ (x >> 16), 0x45d9f3b)
        return x ^ (x >> 16)

    py = []
    for st in range(10):
        bad, buckets = 0, [0] * B
        for i in range(N):
            b = h_py(st * 1000003 + i) % B
            if 0 <= b < B:
                buckets[b] += 1
            else:
                bad += 1
        py.append((bad, max(buckets)))
    with tempfile.TemporaryDirectory() as d:
        js = os.path.join(d, "h.js")
        open(js, "w").write(JS_SRC)
        ver = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
        out = json.loads(subprocess.run(["node", js, str(N), str(B)], capture_output=True, text=True).stdout)
    py_pass = sum(1 for bad, _m in py if bad == 0)
    js_pass = sum(1 for bad, _m in out if bad == 0)
    print(f"  node {ver}; {N} keys into {B} buckets, 10 key sets")
    print(f"  Python model: index out of range in {[b for b, _ in py]} -> {py_pass}/10 checks pass")
    print(f"  real Node:    index out of range in {[b for b, _ in out]} -> {js_pass}/10 checks pass")
    fixed = JS_SRC.replace("return x | 0;", "return x >>> 0;")
    with tempfile.TemporaryDirectory() as d:
        js = os.path.join(d, "h.js")
        open(js, "w").write(fixed)
        out2 = json.loads(subprocess.run(["node", js, str(N), str(B)], capture_output=True, text=True).stdout)
    print(f"  real Node with `>>> 0`: out of range in {[b for b, _ in out2]}; max bucket load matches Python "
          f"in {sum(a[1] == b[1] for a, b in zip(out2, py))}/10 sets")
    return py_pass, js_pass, [b for b, _ in out]


# ============================================================ LOOP 24 ====
def loop24_sprite_frames():
    """Kernel SYSTEM/determinism/sprite-frame-index-as-time-accumulator: a
    per-render-tick increment plays at render rate (7-frame sheet, 10fps, at
    1 s: 2 at 30Hz, 4 at 60Hz, correct 3); frame = floor(t/dur) % n is right."""
    banner(24, "sprite frame index: tick increment vs time, and two accumulator traps")
    FR, NF = 10.0, 7
    for hz in (30, 60):
        naive = (hz * 1) % NF
        exact = math.floor((hz / hz) * FR) % NF
        acc = 0.0
        for _ in range(hz):
            acc += 1.0 / hz
        accf = math.floor(acc * FR) % NF
        print(f"  {hz}Hz render at 1 s: naive tick {naive}, exact time {exact}, float-accumulated time {accf} "
              f"(acc = {acc!r})")
    res = {}
    for hz in (30, 60, 120, 144):
        acc, wrong, frames = 0.0, 0, hz * 60
        for i in range(1, frames + 1):
            acc += 1.0 / hz
            wrong += (math.floor(acc * FR) % NF) != (math.floor(i * FR / hz) % NF)
        res[hz] = wrong
        print(f"  {hz:3d}Hz for 60 s: float accumulator shows a different frame than exact time on {wrong} "
              f"of {frames} renders")
    # speed change mid-run: derive from total time vs accumulate phase
    jumps = {}
    for mode in ("derive-from-total", "accumulate-phase"):
        t, phase, prev, maxjump = 0, 0.0, 0, 0
        for i in range(1, 60 * 30 + 1):                     # integer ms, 30 Hz
            ms = i * 100 // 3
            rate = FR if i < 900 else FR * 1.5               # 1.5x speed buff at 30 s
            if mode == "derive-from-total":
                f = math.floor(ms / 1000 * rate)
            else:
                phase += (ms - t) / 1000 * rate
                f = math.floor(phase)
            t = ms
            maxjump = max(maxjump, f - prev)
            prev = f
        jumps[mode] = maxjump
    print(f"  1.5x playback speed change at 30 s (30Hz): largest single-render frame advance "
          f"derive-from-total {jumps['derive-from-total']}, accumulate-phase {jumps['accumulate-phase']}")
    return res, jumps


# ============================================================ LOOP 25 ====
def loop25_camera_pullin():
    """Kernel MOTION/camera/obstacle-pull-in-asymmetric-damping: raw recompute
    flickers at an edge, a fast lerp pull-in clips for several frames, snap in
    and ease out is safe."""
    banner(25, "camera pull-in: flicker, clip frames, and update order")
    FAR, NEAR = 5.0, 2.0

    def required(x):
        return NEAR if x < 0.0 else FAR                 # pillar edge at x = 0

    def run(mode, path, order="camera-after-player", rate_in=0.6, rate_out=0.08):
        d, prev_x, deltas, clips = FAR, path[0], [], 0
        for x in path:
            seen = x if order == "camera-after-player" else prev_x
            req = required(seen)
            if mode == "raw":
                nd = req
            elif mode == "lerp-both":
                nd = d + (req - d) * (rate_in if req < d else rate_out)
            else:                                        # snap in, ease out
                nd = req if req < d else d + (req - d) * rate_out
            deltas.append(abs(nd - d)); d = nd
            clips += d > required(x) + 1e-9
            prev_x = x
        return sum(deltas) / len(deltas), clips

    r = Rng(25)
    hover = [(r.u() - 0.5) * 0.1 for _ in range(600)]    # standing still at the edge
    sweep = [-3 + 6 * i / 599 for i in range(600)]         # walking cleanly past it
    walk = []
    for k in range(6):                                     # repeated walks into cover
        walk += [1.0 - 0.05 * i for i in range(40)] + [-1.0] * 20 + [-1.0 + 0.05 * i for i in range(40)]
    res = {}
    for name, path in (("hover", hover), ("sweep", sweep), ("walk-in", walk)):
        row = []
        for mode in ("raw", "lerp-both", "snap-in"):
            dm, clips = run(mode, path)
            res[(name, mode)] = (dm, clips)
            row.append(f"{mode} |dd| {dm:.3f} clips {clips}")
        print(f"  {name:8s}: " + "; ".join(row))
    for order in ("camera-after-player", "camera-before-player"):
        dm, clips = run("snap-in", walk, order=order)
        res[("order", order)] = clips
        print(f"  snap-in, walk-in, {order}: clip frames {clips}")
    return res


if __name__ == "__main__":
    loop21_microbenchmark()
    loop22_snapshot_scope()
    loop23_vary_substrate()
    loop24_sprite_frames()
    loop25_camera_pullin()
