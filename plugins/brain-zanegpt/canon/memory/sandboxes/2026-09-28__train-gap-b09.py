"""Deterministic sandbox: `brain train gap`, batch 9 (loops 41-45).

Each loop applies one ideas kernel that no memory entry had built against,
reproduces its claim, then pushes until it finds where the claim stops
holding. No real timing: every clock is a parameter. The only randomness is
a seeded splitmix64. Substrates vary: loop 41 runs a real SQLite engine and
counts its virtual-machine instructions; loop 42 counts comparisons made by
CPython's real list.sort; loops 43-45 are Python models.
"""
import math, sqlite3, sys
from functools import cmp_to_key

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


# ============================================================ LOOP 41 ====
def loop41_index_write_cost():
    """Kernel DATABASE-DESIGN/indexing/write-cost: every index is kept in sync
    on every write, so unused indexes tax every INSERT/UPDATE/DELETE."""
    banner(41, "SQLite VM instructions per statement vs number of indexes")

    def vm_count(con, sql, params=()):
        n = [0]

        def tick():
            n[0] += 1
            return 0
        con.set_progress_handler(tick, 1)
        con.execute(sql, params)
        con.set_progress_handler(None, 1)
        return n[0]

    res = {}
    for k in (0, 1, 3, 10):
        con = sqlite3.connect(":memory:")
        cols = ", ".join(f"c{i} INTEGER" for i in range(10))
        con.execute(f"CREATE TABLE t (id INTEGER PRIMARY KEY, {cols}, note TEXT)")
        for i in range(k):
            con.execute(f"CREATE INDEX ix{i} ON t(c{i})")
        r = Rng(41)
        rows = [tuple(r.below(100000) for _ in range(10)) for _ in range(2000)]
        for row in rows[:1000]:
            con.execute(f"INSERT INTO t (c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,note) VALUES ({','.join('?' * 10)}, 'x')", row)
        ins = sum(vm_count(con, f"INSERT INTO t (c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,note) VALUES ({','.join('?' * 10)}, 'x')", row)
                  for row in rows[1000:1200]) / 200
        upd_note = sum(vm_count(con, "UPDATE t SET note = 'y' WHERE id = ?", (i,)) for i in range(1, 201)) / 200
        upd_c0 = sum(vm_count(con, "UPDATE t SET c0 = c0 + 1 WHERE id = ?", (i,)) for i in range(1, 201)) / 200
        dele = sum(vm_count(con, "DELETE FROM t WHERE id = ?", (i,)) for i in range(1001, 1101)) / 100
        sel = sum(vm_count(con, "SELECT id FROM t WHERE c0 = ?", (rows[i][0],)) for i in range(100)) / 100
        res[k] = (ins, upd_note, upd_c0, dele, sel)
        print(f"  {k:2d} indexes: INSERT {ins:6.1f}  UPDATE unindexed col {upd_note:6.1f}  UPDATE c0 {upd_c0:6.1f}  "
              f"DELETE {dele:6.1f}  SELECT WHERE c0= {sel:8.1f}")
    print(f"  (SQLite {sqlite3.sqlite_version}; VM instructions counted by a progress handler firing every opcode)")
    return res


# ============================================================ LOOP 42 ====
def loop42_timsort():
    """Kernel PERFORMANCE/algorithms/asymptotic-complexity/timsort: below a
    threshold CPython sorts with O(n^2) binary insertion sort on purpose,
    because comparisons, not moves, dominate."""
    banner(42, "comparisons and moves: CPython sort vs binary insertion vs merge sort")

    def count_sorted(xs):
        c = [0]

        def cmp(a, b):
            c[0] += 1
            return (a > b) - (a < b)
        sorted(xs, key=cmp_to_key(cmp))
        return c[0]

    def binary_insertion(xs):
        a, comps, moves = [], 0, 0
        for x in xs:
            lo, hi = 0, len(a)
            while lo < hi:
                mid = (lo + hi) // 2; comps += 1
                if x < a[mid]:
                    hi = mid
                else:
                    lo = mid + 1
            moves += len(a) - lo
            a.insert(lo, x)
        return comps, moves

    def merge_sort(xs):
        comps = [0]; moves = [0]

        def ms(a):
            if len(a) <= 1:
                return a
            m = len(a) // 2
            l, r = ms(a[:m]), ms(a[m:])
            out, i, j = [], 0, 0
            while i < len(l) and j < len(r):
                comps[0] += 1
                if r[j] < l[i]:
                    out.append(r[j]); j += 1
                else:
                    out.append(l[i]); i += 1
            out += l[i:] + r[j:]
            moves[0] += len(out)
            return out
        ms(xs)
        return comps[0], moves[0]

    def linear_insertion(xs):
        a, comps = [], 0
        for x in xs:
            i = len(a)
            while i > 0:
                comps += 1
                if a[i - 1] <= x:
                    break
                i -= 1
            a.insert(i, x)
        return comps

    print(f"  Python {sys.version.split()[0]}; means over 200 random permutations")
    print("      n   CPython  bin-ins  (moves)   merge  (moves)  lin-ins")
    res = {}
    for n in (8, 16, 32, 48, 63, 64, 65, 128, 256, 1024):
        cp = bi = bm = mc = mm = li = 0
        T = 200 if n <= 256 else 40
        for s in range(T):
            r = Rng(n * 1000 + s)
            xs = list(range(n))
            for i in range(n - 1, 0, -1):
                j = r.below(i + 1); xs[i], xs[j] = xs[j], xs[i]
            cp += count_sorted(xs)
            a, b = binary_insertion(xs); bi += a; bm += b
            a, b = merge_sort(xs); mc += a; mm += b
            li += linear_insertion(xs)
        res[n] = (cp / T, bi / T, bm / T, mc / T, mm / T, li / T)
        print(f"  {n:5d} {cp / T:9.1f} {bi / T:8.1f} {bm / T:8.1f} {mc / T:7.1f} {mm / T:8.1f} {li / T:8.1f}")
    # does CPython's count equal a plain binary insertion count below the threshold?
    same = {}
    for n in (10, 30, 63, 64, 65, 100):
        eq = 0
        for s in range(100):
            r = Rng(n * 77 + s)
            xs = [r.below(10 ** 9) for _ in range(n)]
            # timsort: count_run on the leading run, then binary insertion of the rest
            c = [0]

            def cmp(a, b):
                c[0] += 1
                return (a > b) - (a < b)
            sorted(xs, key=cmp_to_key(cmp))
            run = 1
            if n > 1:
                desc = xs[1] < xs[0]
                run = 2
                while run < n and ((xs[run] < xs[run - 1]) == desc) and (desc or not xs[run] < xs[run - 1]):
                    run += 1
            head = sorted(xs[:run])
            a = head[:]
            comps = (run - 1 + (1 if run < n else 0)) if n > 1 else 0
            for x in xs[run:]:
                lo, hi = 0, len(a)
                while lo < hi:
                    mid = (lo + hi) // 2; comps += 1
                    if x < a[mid]:
                        hi = mid
                    else:
                        lo = mid + 1
                a.insert(lo, x)
            eq += comps == c[0]
        same[n] = eq
    print("  runs where CPython's comparison count equals count_run + binary insertion of the rest: "
          + ", ".join(f"n={n}: {v}/100" for n, v in same.items()))
    return res, same


# ============================================================ LOOP 43 ====
def bessel_j(n, x, steps=2000):
    h = math.pi / steps
    s = 0.0
    for i in range(steps + 1):
        t = i * h
        w = 1 if i in (0, steps) else (4 if i % 2 else 2)
        s += w * math.cos(n * t - x * math.sin(t))
    return s * h / 3 / math.pi


def loop43_fm_aliasing():
    """Kernel DSP/fm-synthesis/peak-meter-blind-to-aliasing: high-index FM
    aliases while peak/RMS stay normal; check spectrally or with THD+N."""
    banner(43, "FM aliasing: peak meter, alias energy, THD+N")
    FS, FC, FMOD, N = 48000.0, 3000.0, 4200.0, 4800          # 0.1 s; 3000 and 4200 Hz complete whole cycles

    def naive(I):
        return [math.sin(2 * math.pi * FC * i / FS + I * math.sin(2 * math.pi * FMOD * i / FS)) for i in range(N)]

    def bandlimited(I):
        """Sum only the sidebands below Nyquist: sin(wc t + I sin wm t) = sum_k J_k(I) sin((wc + k wm) t)."""
        terms = []
        for k in range(-80, 81):
            f = FC + k * FMOD
            if 0 < abs(f) < FS / 2:
                terms.append((bessel_j(k, I), f))
        return [sum(a * math.sin(2 * math.pi * f * i / FS) for a, f in terms) for i in range(N)], terms

    def energy(x):
        return sum(v * v for v in x) / len(x)

    def thdn(x, f0):
        """Residual after removing the least-squares sinusoid at f0 (N holds whole cycles of f0)."""
        cs = sum(v * math.cos(2 * math.pi * f0 * i / FS) for i, v in enumerate(x)) * 2 / len(x)
        sn = sum(v * math.sin(2 * math.pi * f0 * i / FS) for i, v in enumerate(x)) * 2 / len(x)
        res = [v - cs * math.cos(2 * math.pi * f0 * i / FS) - sn * math.sin(2 * math.pi * f0 * i / FS) for i, v in enumerate(x)]
        return math.sqrt(energy(res) / energy(x))

    res = {}
    for I in (0.5, 2.0, 5.0, 10.0, 20.0):
        x = naive(I)
        bl, terms = bandlimited(I)
        alias = [a - b for a, b in zip(x, bl)]
        pk = max(abs(v) for v in x)
        rms = math.sqrt(energy(x))
        af = energy(alias) / energy(x)
        res[I] = (pk, rms, af, thdn(x, FC), thdn(bl, FC))
        print(f"  index {I:4.1f}: peak {pk:.3f} rms {rms:.3f} | aliased energy {100 * af:6.2f}% "
              f"({10 * math.log10(af) if af > 0 else -999:6.1f} dB) | THD+N naive {100 * res[I][3]:5.1f}% "
              f"band-limited {100 * res[I][4]:5.1f}%")
    return res


# ============================================================ LOOP 44 ====
def loop44_bit_exact():
    """Kernel DSP/chip-emulation/bit-exact-precision-is-the-target: a float
    'cleanup' of a fixed-point chip pipeline measurably diverges."""
    banner(44, "fixed-point oscillator vs float cleanup: samples, spurs, golden tests")
    FS, N = 53267.0, 4096
    PHASE_BITS, TABLE_BITS, AMP_BITS = 20, 10, 12
    table = [round(math.sin(2 * math.pi * (i + 0.5) / (1 << TABLE_BITS)) * ((1 << (AMP_BITS - 1)) - 1))
             for i in range(1 << TABLE_BITS)]

    def fixed(inc):
        ph, out = 0, []
        for _ in range(N):
            out.append(table[ph >> (PHASE_BITS - TABLE_BITS)])
            ph = (ph + inc) & ((1 << PHASE_BITS) - 1)
        return out

    def floaty(inc):
        return [math.sin(2 * math.pi * (i * inc / (1 << PHASE_BITS))) * ((1 << (AMP_BITS - 1)) - 1) for i in range(N)]

    def fft_mag(x):
        n = len(x)
        a = [complex(v, 0) for v in x]
        j = 0
        for i in range(1, n):                              # bit reversal
            bit = n >> 1
            while j & bit:
                j ^= bit; bit >>= 1
            j |= bit
            if i < j:
                a[i], a[j] = a[j], a[i]
        size = 2
        while size <= n:
            w = complex(math.cos(2 * math.pi / size), -math.sin(2 * math.pi / size))
            for st in range(0, n, size):
                wk = 1 + 0j
                for k in range(size // 2):
                    u, v = a[st + k], a[st + k + size // 2] * wk
                    a[st + k], a[st + k + size // 2] = u + v, u - v
                    wk *= w
            size <<= 1
        return [abs(c) for c in a[: n // 2]]

    res = {}
    for inc in (1 << 10, 256 * 13, 256 * 37):         # whole-bin frequencies: no leakage in either version
        f, g = fixed(inc), floaty(inc)
        mism = sum(a != round(b) for a, b in zip(f, g))
        maxdiff = max(abs(a - b) for a, b in zip(f, g))
        k0 = round(inc / (1 << PHASE_BITS) * N)
        F, G = fft_mag(f), fft_mag(g)
        f0, g0 = F[k0], G[k0]
        fsp = max(v for k, v in enumerate(F) if k != k0) or 1e-300
        gsp = max(v for k, v in enumerate(G) if k != k0) or 1e-300
        res[inc] = (mism, maxdiff, 20 * math.log10(fsp / f0), 20 * math.log10(gsp / g0))
        print(f"  phase inc {inc:5d} ({inc / (1 << PHASE_BITS) * FS:7.1f} Hz): samples differing after rounding "
              f"{mism}/{N} (max {maxdiff:.1f} LSB); largest spur fixed {res[inc][2]:6.1f} dBc, float {res[inc][3]:6.1f} dBc")
    return res


# ============================================================ LOOP 45 ====
def loop45_pinned_invalidation():
    """Kernel SYSTEM/architecture/pinned-privileged-values-need-invalidation:
    pin-once goes stale when the formula's inputs change (48/48); an eager
    hook on the input-changing command fixes it (0/48)."""
    banner(45, "pinned derived values: pin-once, one hook, all hooks, versioned read")

    def world(seed):
        r = Rng(seed)
        return {"base": 50 + r.below(100), "mult": 1 + r.below(4), "bonus": r.below(20)}

    def formula_gate(w):
        return w["base"] * w["mult"] + w["bonus"]

    def formula_cap(w, gate):
        return gate * 2 + w["bonus"]                     # derived from the derived gate

    res = {}
    designs = ("pin-once", "hook-on-mult-only", "hooks-all-wrong-order", "hooks-all-topological", "versioned-lazy")
    for design in designs:
        stale_runs = 0
        for s in range(500):
            r = Rng(s + 45000)
            w = world(s)
            ver = {"base": 0, "mult": 0, "bonus": 0}
            pinned = {"gate": formula_gate(w)}
            pinned["cap"] = formula_cap(w, pinned["gate"])
            pinned["_ver"] = dict(ver)
            stale = False
            for _ in range(20):
                k = ("base", "mult", "bonus")[r.below(3)]
                w[k] += 1 + r.below(3); ver[k] += 1
                if design == "hook-on-mult-only" and k == "mult":
                    pinned["gate"] = formula_gate(w); pinned["cap"] = formula_cap(w, pinned["gate"])
                elif design == "hooks-all-wrong-order":
                    pinned["cap"] = formula_cap(w, pinned["gate"])      # cap first, from the old gate
                    pinned["gate"] = formula_gate(w)
                elif design == "hooks-all-topological":
                    pinned["gate"] = formula_gate(w)
                    pinned["cap"] = formula_cap(w, pinned["gate"])
                # read the gate (and cap)
                if design == "versioned-lazy" and pinned["_ver"] != ver:
                    pinned["gate"] = formula_gate(w)
                    pinned["cap"] = formula_cap(w, pinned["gate"])
                    pinned["_ver"] = dict(ver)
                tg = formula_gate(w)
                stale = stale or pinned["gate"] != tg or pinned["cap"] != formula_cap(w, tg)
            stale_runs += stale
        res[design] = stale_runs
        print(f"  {design:22s}: runs (of 500, 20 input changes each) that ever read a stale gate or cap: {stale_runs}")
    return res


if __name__ == "__main__":
    loop41_index_write_cost()
    loop42_timsort()
    loop43_fm_aliasing()
    loop44_bit_exact()
    loop45_pinned_invalidation()
