"""Deterministic sandbox: `brain train gap`, batch 1 (loops 1-5).

Each loop applies one ideas kernel that no memory entry had built against,
reproduces its claim, then pushes until it finds where the claim stops
holding. No real timing: every clock is a parameter. The only randomness is
a seeded splitmix64, so every run prints identical numbers.
"""
import math, struct


def splitmix64(x):
    x = (x + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return z ^ (z >> 31)


def u01(h):
    return (h >> 11) / float(1 << 53)


def f32(x):
    return struct.unpack("f", struct.pack("f", x))[0]


def banner(n, title):
    print("=" * 78); print(f"LOOP {n} -- {title}"); print("=" * 78)


# ============================================================ LOOP 1 =====
def loop1_raf_vs_settimeout():
    """Kernel MOTION/animation-loop/requestanimationframe-over-settimeout:
    a timer loop never aligns with repaint and drifts; rAF syncs to it and
    stops when hidden; use rAF's own timestamp as the elapsed-time source."""
    banner(1, "rAF vs setTimeout, and the clock-mixing boundary")

    def present(update_times, hz, seconds):
        period = 1000.0 / hz
        frames = int(seconds * hz)
        per = [0] * frames
        for t in update_times:
            k = int(math.floor(t / period))        # shown at the next vsync
            if 0 <= k < frames:
                per[k] += 1
        return per.count(0), sum(1 for c in per if c >= 2), frames

    for hz in (60, 120, 144):
        for delay in (16, 17):
            ups = [i * delay for i in range(int(10_000 / delay))]
            zero, dbl, n = present(ups, hz, 10)
            print(f"  setTimeout({delay}ms) on {hz:3}Hz: {zero:4} of {n} frames repeat "
                  f"(no update), {dbl:3} frames waste an update")
        zero, dbl, n = present([(k + 0.5) * 1000 / hz for k in range(10 * hz)], hz, 10)
        print(f"  rAF               on {hz:3}Hz: {zero:4} of {n} frames repeat, "
              f"{dbl:3} wasted")
    # hidden tab for 5s: rAF delivers nothing; timers are throttled to ~1Hz,
    # not stopped (the kernel's "keeps ticking regardless" is only half true)

    # boundary: the rAF timestamp is the FRAME's start time. A start captured
    # with performance.now() in an input handler that runs later in the same
    # frame is on a different clock and lands AFTER the first timestamp.
    frame_start, handler_now, duration = 1000.0, 1002.4, 300.0
    start = handler_now                      # performance.now() in the click
    elapsed = frame_start - start            # first rAF(ts) of that frame
    p = elapsed / duration
    try:
        eased = p ** 0.5                     # sqrt ease of a negative number
    except Exception as e:
        eased = f"{type(e).__name__}"
    js_eased = float("nan") if p < 0 else p ** 0.5   # Math.pow(-x, 0.5) is NaN in JS
    print(f"  clock mixing: elapsed on first frame = {elapsed:+.1f}ms, p = {p:+.4f}, "
          f"Math.pow(p, 0.5) = {js_eased}")
    start2 = frame_start                     # start taken from the first rAF ts
    print(f"  same-clock fix: elapsed on first frame = {frame_start - start2:+.1f}ms "
          "(start from the first rAF timestamp, not performance.now())")
    return {"t60_16_waste": present([i * 16 for i in range(625)], 60, 10)[1],
            "t60_17_repeat": present([i * 17 for i in range(588)], 60, 10)[0],
            "nan_first_frame": math.isnan(js_eased)}


# ============================================================ LOOP 2 =====
def loop2_camera_clamp():
    """Kernel MOTION/camera/clamp-to-live-content-not-a-progress-schedule:
    a schedule-only zoom clips early far-radius items; hard-clamp scale to
    fit every visible item, with no smoothing lag on the clamp."""
    banner(2, "schedule-only camera vs live-content clamp (and which axis)")
    T, fps = 12.0, 60
    items = []                                # (spawn_time, radius, angle)
    for i in range(24):
        h = splitmix64(1000 + i)
        spawn = (i / 24) * T * 0.8
        radius = 0.3 + 0.05 * i if i % 5 else 1.9       # every 5th: outer ring, early
        angle = u01(h) * 2 * math.pi
        items.append((spawn, radius, angle))

    def run(aspect, clamp, smoothing=0.0, axis="min"):
        halfw, halfh = (aspect, 1.0) if aspect >= 1 else (1.0, 1.0 / aspect)
        halfw, halfh = halfw / max(halfw, halfh), halfh / max(halfw, halfh)
        s_eff, clipped = 2.2, 0
        for f in range(int(T * fps)):
            t = f / fps
            ease = 0.5 - 0.5 * math.cos(math.pi * min(t / T, 1))
            sched = 2.2 + (0.45 - 2.2) * ease            # zoom in -> out
            vis = [(r * math.cos(a), r * math.sin(a)) for st, r, a in items if st <= t]
            target = sched
            if clamp and vis:
                if axis == "min":
                    fit = min(min(halfw / max(abs(x), 1e-9), halfh / max(abs(y), 1e-9))
                              for x, y in vis)
                else:                                     # height only
                    fit = min(halfh / max(math.hypot(x, y), 1e-9) for x, y in vis)
                target = min(sched, fit)
            if smoothing:
                s_eff += (target - s_eff) * smoothing
            else:
                s_eff = target
            clipped += sum(1 for x, y in vis if abs(x * s_eff) > halfw + 1e-9
                           or abs(y * s_eff) > halfh + 1e-9)
        return clipped

    res = {}
    for label, asp in (("16:9 landscape", 16 / 9), ("9:16 portrait", 9 / 16)):
        a = run(asp, False); b = run(asp, True); c = run(asp, True, 0.12)
        d = run(asp, True, axis="h")
        res[label] = (a, b, c, d)
        print(f"  {label:15}: schedule-only {a:5} clipped item-frames · clamp {b:3} · "
              f"clamp smoothed(0.12/frame) {c:4} · clamp on height only {d:5}")
    return res


# ============================================================ LOOP 3 =====
def loop3_transcendental_truncation():
    """Kernel SYSTEM/determinism/transcendentals-arent-bit-identical: libms
    differ in low bits; truncating to float32 after the call discards it."""
    banner(3, "does float32 truncation make two libms agree?")

    def ulp_nudge(y, h):
        # implementation B: identical except 1 ulp off on ~1/3 of inputs
        if h % 3:
            return y
        i = struct.unpack("<q", struct.pack("<d", y))[0]
        return struct.unpack("<d", struct.pack("<q", i + (1 if y >= 0 else -1)))[0]

    def sim(x0, ticks, libm, trunc, absorbed=False):
        x = x0
        for n in range(ticks):
            s = math.sin(2.9 * x + 0.3)
            if libm == "B":
                s = ulp_nudge(s, splitmix64(n))
            if trunc:
                s = f32(s)
            # absorbed: the sine is a small term added to a large state, so
            # its low bits are rounded away by the addition itself
            x = (x + 0.25 * s - 0.01 * x) if absorbed else s
        return struct.pack("<d", x)

    raw = sum(sim(0.1 + i * 0.0037, 2000, "A", False) != sim(0.1 + i * 0.0037, 2000, "B", False)
              for i in range(200))
    tr = sum(sim(0.1 + i * 0.0037, 2000, "A", True) != sim(0.1 + i * 0.0037, 2000, "B", True)
             for i in range(200))
    ab = sum(sim(0.1 + i * 0.37, 2000, "A", False, True) != sim(0.1 + i * 0.37, 2000, "B", False, True)
             for i in range(200))
    print(f"  state = sin(): fingerprints differ raw {raw}/200 · float32-truncated {tr}/200")
    print(f"  sin() as a small term added to a large state: raw differ {ab}/200 "
          "(the addition rounds the libm noise away on its own)")

    # boundary: a double within 1 ulp of a float32 rounding midpoint rounds
    # differently in the two libms. Build such inputs deliberately.
    flips = checked = 0
    for k in range(1, 4001):
        lo = f32(0.3 + k * 1e-4)
        i32 = struct.unpack("<i", struct.pack("<f", lo))[0]
        hi = struct.unpack("<f", struct.pack("<i", i32 + 1))[0]
        mid = (lo + hi) / 2                     # exactly representable in double
        for y in (mid, math.nextafter(mid, 0), math.nextafter(mid, 1)):
            checked += 1
            if f32(y) != f32(ulp_nudge(y, 0)):  # force the 1-ulp variant
                flips += 1
    sweep = 0
    for n in range(200_000):
        y = math.sin(n * 0.001237 + 0.5)
        if f32(y) != f32(ulp_nudge(y, 0)):
            sweep += 1
    print(f"  ordinary sweep, 200000 sin() results: float32 disagrees {sweep} times")
    print(f"  results placed at float32 rounding midpoints: disagrees {flips} of {checked}")
    return {"raw": raw, "trunc": tr, "absorbed": ab, "sweep": sweep, "mid_flips": flips,
            "mid_checked": checked}


# ============================================================ LOOP 4 =====
def loop4_shared_rng_stream():
    """Kernel SYSTEM/determinism/a-shared-rng-stream-is-an-ordinal-space:
    removing one consumer shifts every later draw; address draws by a
    stable symbolic key instead."""
    banner(4, "shared stream vs symbolic keys, and which key")
    N, TICKS, SEED = 20, 50, 42
    PURPOSES = ("move", "attack", "loot")

    def draw(mode, state, eid, slot, t, d, purpose):
        if mode == "shared":
            state = splitmix64(state); return state, u01(state)
        key = {"id+purpose": (eid, t, PURPOSES.index(purpose) if purpose in PURPOSES else 9),
               "id+index":   (eid, t, d),
               "slot":       (slot, t, d)}[mode]
        return state, u01(splitmix64(SEED * 1_000_003 + key[0] * 10_007 + key[1] * 101 + key[2]))

    def outcomes(ids, mode, crit=None):
        out, state = {}, SEED
        for t in range(TICKS):
            for slot, eid in enumerate(ids):
                seq = list(PURPOSES)
                if crit == (eid, t):
                    seq.insert(1, "crit")             # a new check before attack
                for d, purpose in enumerate(seq):
                    state, r = draw(mode, state, eid, slot, t, d, purpose)
                    if purpose != "crit":
                        out[(eid, t, purpose)] = r < 0.3
        return out

    full = list(range(N)); minus3 = [e for e in full if e != 3]
    for mode in ("shared", "slot", "id+index", "id+purpose"):
        a, b = outcomes(full, mode), outcomes(minus3, mode)
        diff = sum(1 for k in b if a[k] != b[k])
        print(f"  remove entity 3 · {mode:10}: {diff:4} of {len(b)} OTHER decisions flip")
    for mode in ("shared", "id+index", "id+purpose"):
        a, b = outcomes(full, mode), outcomes(full, mode, crit=(5, 10))
        flips = [k for k in a if a[k] != b[k]]
        ents = {k[0] for k in flips}
        print(f"  entity 5 adds a crit check at tick 10 · {mode:10}: {len(flips):4} decisions "
              f"flip across {len(ents)} entit{'y' if len(ents) == 1 else 'ies'}")
    return {}


# ============================================================ LOOP 5 =====
def loop5_decay_never_reaches_zero():
    """Kernel SYSTEM/determinism/clamp-incrementally-derived-values: a
    per-frame decay can be locally right and never reach the true target
    (exact zero in floating point); clamp against the real target."""
    banner(5, "does value *= k ever reach exactly zero?")
    tiny = 5e-324
    for k in (0.3, 0.5, 0.5000001, 0.9, 0.99):
        v, n = 1.0, 0
        while v != 0.0 and n < 2_000_000:
            v *= k; n += 1
        stuck = v != 0.0
        print(f"  k={k:<9}: {'STUCK at ' + repr(v) if stuck else 'reaches 0.0'} "
              f"after {n} frames")
    print(f"  smallest subnormal {tiny!r} * 0.9 -> {tiny * 0.9!r} (rounds back up); "
          f"* 0.5 -> {tiny * 0.5!r} (tie to even)")
    # a fade 'done when alpha == 0' at k=0.9, 60fps: visually done at 1/255
    v, n, seen = 1.0, 0, None
    while n < 20_000:
        v *= 0.9; n += 1
        if seen is None and v < 1 / 255:
            seen = n
    print(f"  fade k=0.9: below 1/255 (invisible) at frame {seen}; `alpha == 0` "
          f"never fires (still {v!r} at frame {n})")
    # the kernel's fix: derive from the independent truth (elapsed frames)
    print(f"  from elapsed time instead: 0.9 ** 20000 = {0.9 ** 20000!r} · "
          f"math.pow = {math.pow(0.9, 20000)!r}")
    for k in (0.9, 0.99, 0.999):
        units = round(struct.unpack('<d', struct.pack('<d', 1.0))[0])
        v = 1.0
        for _ in range(3_000_000):
            nv = v * k
            if nv == v:
                break
            v = nv
        print(f"  k={k}: sticks at {v / 5e-324:.0f} x the smallest subnormal "
              f"(0.5/(1-k) = {0.5 / (1 - k):.1f})")
    return {"stuck_09": True}


if __name__ == "__main__":
    loop1_raf_vs_settimeout()
    loop2_camera_clamp()
    loop3_transcendental_truncation()
    loop4_shared_rng_stream()
    loop5_decay_never_reaches_zero()
