"""Deterministic sandbox: `brain train gap`, batch 8 (loops 36-40).

Each loop applies one ideas kernel that no memory entry had built against,
reproduces its claim, then pushes until it finds where the claim stops
holding. No real timing: every clock is a parameter. The only randomness is
a seeded splitmix64. Substrates vary on purpose: loops 36 and 37 run in real
Node.js (real Intl.Segmenter, real Promise scheduling), loop 40 reads real
gcc/clang -O2 assembly, loops 38 and 39 are Python models.
"""
import os, re, subprocess, tempfile, json
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


def banner(n, title):
    print("=" * 78); print(f"LOOP {n} -- {title}"); print("=" * 78)


def node(src, *args):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "m.js")
        open(p, "w").write(src)
        out = subprocess.run(["node", p, *args], capture_output=True, text=True)
        if out.returncode:
            raise RuntimeError(out.stderr)
        return json.loads(out.stdout)


# ============================================================ LOOP 36 ====
JS36 = r"""
const seg = new Intl.Segmenter("en", {granularity: "grapheme"});
const g = s => [...seg.segment(s)].map(x => x.segment);
const S = {
  ascii: "hello", composed: "café", decomposed: "café",
  flag: "\u{1F1EF}\u{1F1F5}", skin: "\u{1F44D}\u{1F3FD}",
  family: "\u{1F468}‍\u{1F469}‍\u{1F467}‍\u{1F466}",
  devanagari: "क्षि", hangulJamo: "각",
  thai: "กำ", mixed: "a\u{1F468}‍\u{1F469}‍\u{1F467}b́\u{1F1EF}\u{1F1F5}!",
};
const rows = {};
let sliceCuts = 0, sliceLone = 0, sliceTotal = 0, spreadRevBroken = 0, grRevBroken = 0;
for (const [k, s] of Object.entries(S)) {
  const graphemes = g(s);
  rows[k] = {units: s.length, codepoints: [...s].length, graphemes: graphemes.length,
             utf8: Buffer.byteLength(s, "utf8"), nfcUnits: s.normalize("NFC").length};
  const bounds = new Set([0]); let acc = 0; for (const x of graphemes) { acc += x.length; bounds.add(acc); }
  for (let n = 1; n < s.length; n++) {
    sliceTotal++;
    if (!bounds.has(n)) sliceCuts++;
    const c = s.charCodeAt(n - 1); if (c >= 0xD800 && c <= 0xDBFF) sliceLone++;
  }
  const rev1 = [...s].reverse().join(""), rev2 = graphemes.slice().reverse().join("");
  if (g(rev1).length !== graphemes.length) spreadRevBroken++;
  if (g(rev2).length !== graphemes.length) grRevBroken++;
}
console.log(JSON.stringify({icu: process.versions.icu, unicode: process.versions.unicode, rows,
  sliceCuts, sliceLone, sliceTotal, spreadRevBroken, grRevBroken, n: Object.keys(S).length}));
"""


def loop36_graphemes():
    """Kernel TEXT/unicode/grapheme-not-code-unit: the ZWJ family emoji is
    .length 11, 7 code points, 1 grapheme; segment on graphemes for anything
    a human counts."""
    banner(36, "string lengths in real Node, and what slice and reverse break")
    o = node(JS36)
    print(f"  node ICU {o['icu']}, Unicode {o['unicode']}")
    print("  string       .length codepoints graphemes utf8-bytes NFC-.length")
    for k, r in o["rows"].items():
        print(f"  {k:12s} {r['units']:7d} {r['codepoints']:10d} {r['graphemes']:9d} {r['utf8']:10d} {r['nfcUnits']:11d}")
    print(f"  .slice(0, n) at every n inside each string: {o['sliceCuts']} of {o['sliceTotal']} cut a grapheme, "
          f"{o['sliceLone']} leave a lone high surrogate")
    print(f"  reverse via [...s]: breaks the grapheme count of {o['spreadRevBroken']} of {o['n']} strings; "
          f"reverse by graphemes: {o['grRevBroken']}")
    return o


# ============================================================ LOOP 37 ====
JS37 = r"""
// A tiny DataLoader: collect keys until the microtask queue drains, then one batch call.
function makeDb() { const log = []; return { log, batch: async (table, keys) => { log.push([table, keys.length]); return keys.map(k => ({table, k})); } }; }
function loader(db, table, max) {
  let pending = [], scheduled = false;
  const flush = () => { const p = pending; pending = []; scheduled = false;
    for (let i = 0; i < p.length; i += max) { const chunk = p.slice(i, i + max);
      db.batch(table, chunk.map(x => x.k)).then(rows => chunk.forEach((x, j) => x.res(rows[j]))); } };
  return k => new Promise(res => { pending.push({k, res}); if (!scheduled) { scheduled = true; queueMicrotask(() => queueMicrotask(flush)); } });
}
async function run(N, B, mode, max) {
  const db = makeDb();
  const one = async (table, k) => { db.log.push([table, 1]); return {table, k}; };
  const L = mode === "naive" ? null : {addr: loader(db, "address", max), books: loader(db, "books", max), rev: loader(db, "reviews", max)};
  db.log.push(["authors", N]);
  const authors = Array.from({length: N}, (_, i) => i);
  const resolveAuthor = async a => {
    const addr = L ? L.addr(a) : one("address", a);
    const books = L ? L.books(a) : one("books", a);
    await Promise.all([addr, books]);
    const ids = Array.from({length: B}, (_, j) => a * 100 + j);
    if (mode === "sequential") { for (const b of ids) await L.rev(b); }
    else await Promise.all(ids.map(b => L ? L.rev(b) : one("reviews", b)));
  };
  if (mode === "sequential") { for (const a of authors) await resolveAuthor(a); }
  else await Promise.all(authors.map(resolveAuthor));
  return db.log.length;
}
(async () => {
  const out = {};
  for (const [N, B] of [[50, 0], [50, 3], [500, 3]]) {
    out[`${N}x${B}`] = {naive: await run(N, B, "naive", 1e9), batched: await run(N, B, "batched", 1e9),
      sequential: await run(N, B, "sequential", 1e9), capped100: await run(N, B, "batched", 100)};
  }
  console.log(JSON.stringify(out));
})();
"""


def loop37_graphql_n_plus_one():
    """Kernel API-DESIGN/graphql/n-plus-one-resolvers: per-field resolvers
    turn one query into N+1 datastore calls (50 authors' addresses: 51
    naive vs 2 batched); batching must be added deliberately."""
    banner(37, "resolver datastore calls in real Node: naive, batched, sequential awaits")
    o = node(JS37)
    for k, v in o.items():
        n, b = k.split("x")
        print(f"  {n} authors x {b} books' reviews: naive {v['naive']}, DataLoader {v['batched']}, "
              f"DataLoader with sequential awaits {v['sequential']}, DataLoader capped at 100 keys {v['capped100']}")
    return o


# ============================================================ LOOP 38 ====
def loop38_ca_caves():
    """Kernel PROCGEN/cellular-automata/convergence-is-not-connectivity: the
    4-5 rule stabilises by iteration 2-3 but can settle disconnected."""
    banner(38, "CA caves: fixed points, connectivity by density, cost of the fixes")
    W, H = 64, 40

    def gen(density, seed):
        r = Rng(seed)
        return [[1 if (x == 0 or y == 0 or x == W - 1 or y == H - 1 or r.u() < density) else 0
                 for x in range(W)] for y in range(H)]

    def step(g):
        n = [[1] * W for _ in range(H)]
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                c = sum(g[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
                n[y][x] = 1 if c > 4 else (0 if c < 4 else g[y][x])
        return n

    def regions(g):
        seen, sizes = set(), []
        for y in range(H):
            for x in range(W):
                if g[y][x] == 0 and (x, y) not in seen:
                    q, sz = deque([(x, y)]), 0
                    seen.add((x, y))
                    while q:
                        cx, cy = q.popleft(); sz += 1
                        for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                            if g[ny][nx] == 0 and (nx, ny) not in seen:
                                seen.add((nx, ny)); q.append((nx, ny))
                    sizes.append(sz)
        return sorted(sizes, reverse=True)

    res = {}
    for density in (0.40, 0.45, 0.50):
        single = fixed = osc = 0
        lost_area = []
        fixed_at, stable_at = [], []
        N = 60
        for s in range(N):
            g = gen(density, s * 7 + int(density * 100))
            hist = [g]
            counts = [len(regions(g))]
            fx = None
            for it in range(1, 31):
                g2 = step(g)
                if g2 == g:
                    fx = it; break
                if len(hist) >= 2 and g2 == hist[-2]:
                    osc += 1; fx = -1; break
                hist.append(g2); g = g2
                counts.append(len(regions(g)))
            if fx and fx > 0:
                fixed += 1; fixed_at.append(fx)
            last = max(i for i in range(len(counts)) if i == 0 or counts[i] != counts[i - 1])
            stable_at.append(last)
            rs = regions(g)
            single += len(rs) == 1
            if rs:
                lost_area.append(1 - rs[0] / sum(rs))
        fixed_at.sort()
        res[density] = (single, fixed, osc, lost_area)
        med = fixed_at[len(fixed_at) // 2] if fixed_at else None
        stable_at.sort()
        print(f"  density {density:.2f}, {N} seeds: one connected cave {single}/{N}; grid reached a fixed point "
              f"{fixed}/{N} (median iteration {med}; region count final from median iteration "
              f"{stable_at[len(stable_at) // 2]}), period-2 oscillation {osc}/{N}; 'keep largest region' "
              f"discards median {sorted(lost_area)[len(lost_area) // 2]:.1%}, worst {max(lost_area):.1%} of floor")
    return res


# ============================================================ LOOP 39 ====
def loop39_lfsr():
    """Kernel DSP/lfsr-noise/tap-polynomial-not-width-sets-period: a
    non-primitive tap set fractures the state space into several cycles and
    which one a seed lands in varies (SN76489 16-bit, taps 0 and 3: 57337)."""
    banner(39, "LFSR cycle structure: every seed of the 16-bit register")

    def stepf(width, mask):
        top = width - 1

        def f(s):
            fb = bin(s & mask).count("1") & 1
            return (s >> 1) | (fb << top)
        return f

    def cycles(width, mask):
        f = stepf(width, mask)
        n = 1 << width
        cyc_of = [-1] * n
        lens = []
        for s in range(n):
            if cyc_of[s] != -1:
                continue
            path, x = [], s
            while cyc_of[x] == -1:
                cyc_of[x] = -2; path.append(x); x = f(x)
            if cyc_of[x] == -2:                        # found a new cycle
                i = path.index(x)
                cid = len(lens); lens.append(len(path) - i)
                for y in path[i:]:
                    cyc_of[y] = cid
                for y in path[:i]:
                    cyc_of[y] = cid
            else:
                for y in path:
                    cyc_of[y] = cyc_of[x]
        return lens, cyc_of

    res = {}
    for label, width, mask in (("SN76489-style 16-bit, taps 0,3 (0x0009)", 16, 0x0009),
                               ("16-bit, taps 0,2,3,5 (0x002D)", 16, 0x002D),
                               ("15-bit, taps 0,1 (0x0003)", 15, 0x0003)):
        lens, cyc = cycles(width, mask)
        big = sorted(lens, reverse=True)
        counts = {}
        for L in lens:
            counts[L] = counts.get(L, 0) + 1
        seeds = {hex(s): lens[cyc[s]] for s in (0x8000 >> (16 - width), 0x0001, 0x4000 >> (16 - width), 0x1234 & ((1 << width) - 1))}
        res[label] = (big[:6], seeds)
        short = sum(1 for st in range(1, 1 << width) if lens[cyc[st]] < big[0])
        print(f"  {label}: {len(lens)} cycles; longest {big[:4]}; seeds -> period {seeds}; "
              f"non-zero seeds off the longest cycle {short} of {(1 << width) - 1}")
    return res


# ============================================================ LOOP 40 ====
C40 = r"""
#include <stdatomic.h>
int plain_flag; volatile int vol_flag; _Atomic int at_flag;
int plain_data; _Atomic int ready;
void spin_plain(void)    { while (!plain_flag) { } }
void spin_volatile(void) { while (!vol_flag) { } }
void spin_acquire(void)  { while (!atomic_load_explicit(&at_flag, memory_order_acquire)) { } }
int  spin_plain_count(void) { int n = 0; while (!plain_flag) n++; return n; }
"""


def loop40_happens_before():
    """Kernel CONCURRENCY/memory-model/happens-before: without a
    happens-before edge a write may never become visible; 'worked in testing'
    says nothing."""
    banner(40, "spin-wait on a flag: what -O0 and -O2 actually emit (gcc | clang)")
    FN = ["spin_plain", "spin_volatile", "spin_acquire", "spin_plain_count"]
    res = {}
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "f.c")
        open(src, "w").write(C40)
        for cc in ("gcc", "clang"):
            for opt in ("-O0", "-O2"):
                asm = subprocess.run([cc, opt, "-S", "-o", "-", src], capture_output=True, text=True).stdout
                funcs, cur = {}, None
                for line in asm.splitlines():
                    m = re.match(r"^([A-Za-z_]\w*):", line)
                    if m and m.group(1) in FN:
                        cur = m.group(1); funcs[cur] = []; continue
                    if cur and ".cfi_endproc" in line:
                        cur = None; continue
                    if cur:
                        funcs[cur].append(line.strip())
                for fn in FN:
                    body = [l for l in funcs.get(fn, []) if l and not l.startswith(".") or re.match(r"^\.L\w+:", l or "")]
                    labels = {re.match(r"^(\.L\w+):", l).group(1): i for i, l in enumerate(body) if re.match(r"^\.L\w+:", l)}
                    loop_loads, self_loop = None, False
                    for j, l in enumerate(body):
                        m = re.match(r"^j\w*\s+(\.L\w+)", l)
                        if m and m.group(1) in labels and labels[m.group(1)] <= j:
                            seg = body[labels[m.group(1)] + 1:j + 1]
                            loads = sum(1 for s in seg if re.search(r"(mov\w*|cmp\w*)\s+\w*\(?(plain|vol|at)_flag", s)
                                        or re.search(r"(plain|vol|at)_flag\(%rip\)", s))
                            loop_loads = loads if loop_loads is None else max(loop_loads, loads)
                            self_loop = self_loop or len(seg) == 1
                    res[(cc, opt, fn)] = (loop_loads, self_loop)
        ver = {cc: subprocess.run([cc, "--version"], capture_output=True, text=True).stdout.splitlines()[0] for cc in ("gcc", "clang")}
    print(f"  {ver['gcc']} | {ver['clang']}")
    for fn in FN:
        cells = []
        for cc in ("gcc", "clang"):
            for opt in ("-O0", "-O2"):
                ll, sl = res[(cc, opt, fn)]
                cells.append(f"{cc}{opt}: " + ("no loop" if ll is None else f"{ll} flag load(s) in loop" + (" (jmp to self)" if sl else "")))
        print(f"  {fn:17s} " + " | ".join(cells))
    return res


if __name__ == "__main__":
    loop36_graphemes()
    loop37_graphql_n_plus_one()
    loop38_ca_caves()
    loop39_lfsr()
    loop40_happens_before()
