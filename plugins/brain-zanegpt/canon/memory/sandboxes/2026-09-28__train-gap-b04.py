"""Deterministic sandbox: `brain train gap`, batch 4 (loops 16-20).

Each loop applies one ideas kernel that no memory entry had built against,
reproduces its claim, then pushes until it finds where the claim stops
holding. No real timing: every clock is a parameter. The only randomness is
a seeded splitmix64, so every run prints identical numbers.
"""
import math
import html
from html.parser import HTMLParser
from urllib.parse import quote
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


def banner(n, title):
    print("=" * 78); print(f"LOOP {n} -- {title}"); print("=" * 78)


# ============================================================ LOOP 16 ====
def loop16_depth_buffer():
    """Kernel GEOMETRY/visibility/a-depth-buffer-is-a-correctness-choice:
    for piercing geometry no whole-face order is correct; a depth buffer is."""
    banner(16, "painter's order vs Z-buffer on piercing triangles, and Z precision")
    W = H = 64
    A = [(6, 8, 50.0), (58, 8, 50.0), (32, 58, 50.0)]          # flat
    B = [(2, 18, 86.0), (62, 18, 86.0), (32, 62, 16.0)]        # leans through A

    def raster(tri):
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = tri
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        out = {}
        for py in range(H):
            for px in range(W):
                x, y = px + 0.5, py + 0.5
                a = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / den
                b = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y2)) / den
                c = 1 - a - b
                if a >= 0 and b >= 0 and c >= 0:
                    out[(px, py)] = a * z0 + b * z1 + c * z2
        return out
    ra, rb = raster(A), raster(B)
    truth = {}
    for p in set(ra) | set(rb):
        za, zb = ra.get(p, math.inf), rb.get(p, math.inf)
        truth[p] = "A" if za < zb else "B"                 # smaller z is nearer
    covered = len(truth)

    def painter(order):
        img = {}
        for name in order:
            for p in (ra if name == "A" else rb):
                img[p] = name
        return sum(img[p] != truth[p] for p in truth)
    ab, ba = painter("AB"), painter("BA")
    cz = {n: sum(v[2] for v in t) / 3 for n, t in (("A", A), ("B", B))}
    centroid_order = "".join(sorted("AB", key=lambda n: -cz[n]))    # far to near
    split_wrong = 0
    img = {}
    for p, z in rb.items():                                 # far half of B first
        if z >= 50.0:
            img[p] = "B"
    for p in ra:
        img[p] = "A"
    for p, z in rb.items():                                 # near half of B last
        if z < 50.0:
            img[p] = "B"
    split_wrong = sum(img[p] != truth[p] for p in truth)
    print(f"  covered pixels {covered}: order A,B wrong {ab} ({ab / covered:.1%}); order B,A wrong "
          f"{ba} ({ba / covered:.1%}); centroid far-to-near picks {','.join(centroid_order)}; "
          f"split B at the intersection: {split_wrong} wrong")

    def zbuf(bits, near, far):
        levels = (1 << bits) - 1

        def q(z):
            d = (far / (far - near)) * (1 - near / z)          # standard perspective depth
            return round(d * levels)
        wrong = 0
        for p in truth:
            za, zb = ra.get(p), rb.get(p)
            if za is None or zb is None:
                continue
            win = "A" if q(za) <= q(zb) else "B"               # A drawn first, LESS test keeps it on ties
            wrong += win != truth[p]
        return wrong
    both = sum(1 for p in truth if p in ra and p in rb)
    res = {}
    for bits in (16, 24):
        row = []
        for near in (1.0, 0.1, 0.01, 0.001):
            w = zbuf(bits, near, 10000.0)
            res[(bits, near)] = w
            row.append(f"near={near}: {w}")
        print(f"  {bits}-bit perspective Z (far 10000), wrong of {both} overlapping pixels: " + ", ".join(row))
    return ab, ba, res


# ============================================================ LOOP 17 ====
class _Collect(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags, self.script_data = [], []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, attrs))

    def handle_data(self, data):
        if self.lasttag == "script":
            self.script_data.append(data)


def _scheme_ok(v):
    """Allow-list: http(s) or a scheme-less relative reference."""
    t = "".join(ch for ch in v if ch not in "\t\n\r").strip().lower()
    head = t.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    return ":" not in head or t.startswith(("http:", "https:"))


def loop17_xss():
    """Kernel SECURITY/web/xss/xss-defense-is-context-matched-encoding: the
    right encoding depends on where data lands; CSP is a backstop."""
    banner(17, "encoder x output context, plus what CSP does not stop")
    PAYLOADS = [
        "<script>alert(1)</script>", "<img src=x onerror=alert(1)>",
        '" onmouseover="alert(1)', "' onmouseover='alert(1)", "x onmouseover=alert(1)",
        "';alert(1);//", "\\';alert(1);//", "</script><script>alert(1)</script>",
        "javascript:alert(1)", " JaVaScRiPt:alert(1)", "java\tscript:alert(1)",
        '<form action="https://evil.example/steal">', '<base href="https://evil.example/">',
    ]
    BENIGN = ["O'Brien & <Co>", 'say "hi"', "a/b?c=1&d=2", "https://ok.example/p?q=1"]
    ENC = {
        "none": lambda s: s,
        "html": lambda s: html.escape(s, quote=True),
        "js-naive": lambda s: s.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"'),
        "js-hex": lambda s: "".join(c if c.isalnum() else f"\\x{ord(c):02x}" for c in s),
        "url": lambda s: quote(s, safe=""),
        "html+allow": lambda s: html.escape(s if _scheme_ok(s) else "#", quote=True),
    }
    CTX = {
        "body": "<div>{}</div>",
        "attr-quoted": '<div title="{}">x</div>',
        "attr-unquoted": "<div title={}>x</div>",
        "js-string": "<script>var s='{}';</script>",
        "href": '<a href="{}">x</a>',
    }
    EXPECT = {"body": ["div"], "attr-quoted": ["div"], "attr-unquoted": ["div"],
              "js-string": ["script"], "href": ["a"]}
    SCRIPTY = ("script", "onerror", "onmouseover", "javascript:")

    def js_string_ok(src):
        """Script body must be exactly: var s='<one string literal>';"""
        pre = "var s='"
        if not src.startswith(pre):
            return False, None
        i, out = len(pre), []
        while i < len(src):
            c = src[i]
            if c == "\\" and i + 1 < len(src):
                n = src[i + 1]
                if n == "x" and i + 3 < len(src):
                    out.append(chr(int(src[i + 2:i + 4], 16))); i += 4; continue
                out.append(n); i += 2; continue
            if c == "'":
                return src[i:] == "';", "".join(out)
            if c == "\n":
                return False, None
            out.append(c); i += 1
        return False, None

    def outcome(ctx, raw):
        doc = CTX[ctx].format(raw)
        p = _Collect(); p.feed(doc); p.close()
        tags = [t for t, _a in p.tags]
        attrs = [(k, v) for _t, a in p.tags for k, v in a]
        injected = tags != EXPECT[ctx] or any(k not in ("title", "href") for k, _v in attrs)
        value = None
        if ctx == "js-string":
            ok, value = js_string_ok("".join(p.script_data))
            injected = injected or not ok
        elif ctx == "href":
            hv = dict(p.tags[0][1]).get("href", "") if p.tags else ""
            value = hv
            scheme = "".join(ch for ch in hv if ch not in "\t\n\r").strip().lower()
            injected = injected or scheme.startswith("javascript:")
        else:
            value = dict(p.tags[0][1]).get("title") if ctx.startswith("attr") and p.tags else None
        return injected, value, tags, attrs

    print(f"  injected payloads of {len(PAYLOADS)} | benign strings that survive intact of {len(BENIGN)}")
    header = "  " + "encoder".ljust(10) + "".join(c.rjust(15) for c in CTX)
    print(header)
    grid = {}
    for en, f in ENC.items():
        cells = []
        for ctx in CTX:
            inj = sum(outcome(ctx, f(pl))[0] for pl in PAYLOADS)
            ok = 0
            for b in BENIGN:
                injected, value, _t, _a = outcome(ctx, f(b))
                if ctx == "body":
                    pp = _Collect(); pp.feed(CTX[ctx].format(f(b))); pp.close()
                    txt = CTX[ctx].format(f(b))[5:-6]
                    ok += (not injected) and html.unescape(txt) == b
                elif ctx == "href":
                    ok += (not injected) and value == b
                else:
                    ok += (not injected) and value == b
            grid[(en, ctx)] = (inj, ok)
            cells.append(f"{inj:2d} inj {ok}/{len(BENIGN)} ok".rjust(15))
        print("  " + en.ljust(10) + "".join(cells))
    # CSP (script-src 'self', no unsafe-inline) as a backstop on unencoded output
    blocked = passed = 0
    for ctx in ("body",):
        for pl in PAYLOADS:
            inj, _v, tags, attrs = outcome(ctx, pl)
            if not inj:
                continue
            scripty = any(t == "script" for t in tags) or any(k.startswith("on") for k, _v in attrs) \
                or any(isinstance(v, str) and "javascript:" in v.lower() for _k, v in attrs)
            blocked += scripty; passed += not scripty
    print(f"  CSP script-src 'self' over unencoded HTML-body injections: blocks {blocked}, "
          f"lets through {passed} (markup-only: <form action>, <base href>)")
    return grid, blocked, passed


# ============================================================ LOOP 18 ====
def loop18_gate_params():
    """Kernel SYSTEM/architecture/gate-and-perturbation-params-must-precede-the-
    command: a gate must not read its threshold from the command crossing it."""
    banner(18, "fuzzed command streams against three gate designs")
    REQUIRED = 5

    def run(stream, design):
        st = {"stage": 0, "done": 0, "threshold": REQUIRED}
        for cmd in stream:
            kind = cmd[0]
            if kind == "TASK":
                st["done"] += 1
            elif kind == "SET_DIFFICULTY" and design == "state-writable":
                st["threshold"] = cmd[1]                    # a client command writes the pinned value
            elif kind == "ADVANCE":
                if design == "payload":
                    thr = cmd[1] if len(cmd) > 1 else 0     # omitted param defaults to 0
                else:
                    thr = st["threshold"]
                if st["done"] >= thr:
                    st["stage"] += 1; st["done"] = 0
        return st["stage"]

    def honest_stages(stream):
        st, done = 0, 0
        for cmd in stream:
            if cmd[0] == "TASK":
                done += 1
            elif cmd[0] == "ADVANCE" and done >= REQUIRED:
                st += 1; done = 0
        return st

    res = {}
    for label, maker in (("benign client (omits optional params)", "benign"),
                         ("fuzzed client (any command, any param)", "fuzz")):
        counts = {"payload": 0, "state-writable": 0, "state-pinned": 0}
        N = 5000
        for s in range(N):
            r = Rng(s * 31 + (7 if maker == "fuzz" else 3))
            stream = []
            for _ in range(12):
                k = r.below(3)
                if k == 0:
                    stream.append(("TASK",))
                elif k == 1:
                    if maker == "benign":
                        stream.append(("ADVANCE",))
                    else:
                        stream.append(("ADVANCE", r.below(8)) if r.u() < 0.5 else ("ADVANCE",))
                else:
                    if maker == "fuzz":
                        stream.append(("SET_DIFFICULTY", r.below(8)))
                    else:
                        stream.append(("TASK",))
            h = honest_stages(stream)
            for d in counts:
                counts[d] += run(stream, d) > h
        res[maker] = counts
        print(f"  {label}: streams that advance further than the real rule allows, of {N}:")
        print("    " + ", ".join(f"{d} {c}" for d, c in counts.items()))
    return res


# ============================================================ LOOP 19 ====
def loop19_pinned_order():
    """Kernel SYSTEM/determinism/a-privileged-gates-pinned-value-needs-one-
    canonical-computation-order: accumulation orders differ from event 2 and
    flip the gate near the safe-integer crossover (~21-29 events)."""
    banner(19, "compounding gate value: order divergence and which gates flip")
    SEEDS, EVENTS = 200, 40

    def mults(seed):
        r = Rng(seed + 500)
        return [5.0 + r.u() for _ in range(EVENTS)]         # ~5.5x per event

    first_bits = []
    flips_float = [0] * (EVENTS + 1)
    flips_floor = [0] * (EVENTS + 1)
    flips_floor_band = [0] * (EVENTS + 1)
    for s in range(SEEDS):
        ms = mults(s)
        seen_diff = None
        for n in range(1, EVENTS + 1):
            left = 1.0
            for m in ms[:n]:
                left *= m
            right = 1.0
            for m in reversed(ms[:n]):
                right = m * right
            h = n // 2
            a = 1.0
            for m in ms[:h]:
                a *= m
            b = 1.0
            for m in ms[h:n]:
                b *= m
            split = a * b
            logv = math.exp(sum(math.log(m) for m in ms[:n]))
            vals = (left, right, split, logv)
            if seen_diff is None and len(set(vals)) > 1:
                seen_diff = n
            # the gate compares a recomputed value against the value pinned by live play
            flips_float[n] += any(v < left for v in vals)
            flips_floor[n] += any(math.floor(v) < math.floor(left) for v in vals)
            r = Rng(s * 1000 + n)
            Tb = math.floor(left * (0.9 + 0.2 * r.u()))            # an authored threshold near the value
            flips_floor_band[n] += len({v >= Tb for v in vals}) > 1
        first_bits.append(seen_diff)
    fb = sorted(x for x in first_bits if x is not None)
    print(f"  first event where the 4 orders give different bits: median {fb[len(fb) // 2]}, "
          f"min {fb[0]}, max {fb[-1]} (of {SEEDS} seeds)")
    mag = {n: sorted(math.log10(math.prod(mults(s)[:n])) for s in range(SEEDS))[SEEDS // 2]
           for n in (5, 10, 15, 18, 19, 20, 21, 22, 24, 28, 40)}
    print(f"  (2^53 = 10^{math.log10(2 ** 53):.2f}) median log10(value): "
          + " ".join(f"{mag[n]:.1f}" for n in mag))
    print("  seeds (of 200) where some order flips the gate, by event count:")
    print("    events:                           " + " ".join(f"{n:>4d}" for n in (5, 10, 15, 18, 19, 20, 21, 22, 24, 28, 40)))
    print("    recomputed >= pinned (float):     " + " ".join(f"{flips_float[n]:>4d}" for n in (5, 10, 15, 18, 19, 20, 21, 22, 24, 28, 40)))
    print("    floor(recomputed) >= floor(pinned): " + " ".join(f"{flips_floor[n]:>4d}" for n in (5, 10, 15, 18, 19, 20, 21, 22, 24, 28, 40)))
    print("    value >= authored threshold (+-10%): " + " ".join(f"{flips_floor_band[n]:>4d}" for n in (5, 10, 15, 18, 19, 20, 21, 22, 24, 28, 40)))
    # canonical order: everyone folds left-to-right from the saved multiplier list
    same = all(len({math.prod(mults(s)[:n]) for _ in range(3)}) == 1 for s in range(20) for n in (10, 30))
    exact = Fraction(1)
    for m in mults(0):
        exact *= Fraction(m)
    left = 1.0
    for m in mults(0):
        left *= m
    print(f"  one canonical left fold on every path: identical bits {same}; its relative error vs exact "
          f"rational after 40 events {float(abs(Fraction(left) - exact) / exact):.1e}")
    return fb, flips_float, flips_floor, flips_floor_band


# ============================================================ LOOP 20 ====
def loop20_percent_cap():
    """Kernel RPG/combat/percent-max-hp-damage-cap: every damage curve one-shots
    past ~5-10x; only min(raw, 0.2 x defender max HP) keeps 5 turns flat."""
    banner(20, "percent-max-HP cap: flat length, and who wins")
    RATIOS = (1, 1.1, 1.2, 1.3, 1.5, 2, 5, 10, 100, 1000, 100000)

    def fight(ratio, formula, first, seed):
        pw = [float(ratio), 1.0]
        mx = [10.0 * ratio, 10.0]
        hp = mx[:]
        hits = [0, 0]
        r = Rng(seed)
        turn = first
        while True:
            a, d = turn, 1 - turn
            q = pw[a] / pw[d]
            j = 0.9 + 0.2 * r.u()
            base = 3.0 * pw[d]                          # 30% of the defender's HP at 1x
            if formula == "ratio":
                dmg = base * q * j
            elif formula == "capped5x":
                dmg = base * min(q, 5.0) * j
            elif formula == "log":
                dmg = base * (q if q < 1 else 1 + math.log(q)) * j
            elif formula == "sqrt":
                dmg = base * math.sqrt(q) * j
            elif formula == "cap20":
                dmg = min(base * q * j, 0.2 * mx[d])
            elif formula == "soft":
                dmg = 0.2 * mx[d] * q / (1 + q) * j
            hp[d] -= dmg
            hits[a] += 1
            if hp[d] <= 0:
                return a, hits[a]
            turn = d

    res = {}
    for formula in ("ratio", "capped5x", "log", "sqrt", "cap20", "soft"):
        row, wins = [], []
        for ratio in RATIOS:
            N = 400
            lens, strong = [], 0
            for s in range(N):
                first = s % 2                                   # alternate who opens
                w, ln = fight(ratio, formula, first, s * 13 + int(ratio * 7))
                strong += w == 0
                if w == 0:
                    lens.append(ln)
            row.append(f"{(sum(lens) / len(lens)) if lens else float('nan'):5.1f}")
            wins.append(f"{strong / N:5.0%}")
            res[(formula, ratio)] = ((sum(lens) / len(lens)) if lens else None, strong / N)
        print(f"  {formula:6s} strong side's hits to win by ratio {RATIOS}:")
        print("         " + " ".join(row))
        print(f"         stronger side wins: " + " ".join(wins))
    return res


if __name__ == "__main__":
    loop16_depth_buffer()
    loop17_xss()
    loop18_gate_params()
    loop19_pinned_order()
    loop20_percent_cap()
