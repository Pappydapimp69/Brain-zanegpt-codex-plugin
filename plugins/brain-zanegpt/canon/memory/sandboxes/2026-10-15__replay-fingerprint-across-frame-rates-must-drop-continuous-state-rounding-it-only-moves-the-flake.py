# Sandbox: replay-fingerprint kernel + split-state kernel + seeded-rng kernel together.
# A fixed-tick sim (20 Hz, integer scheduler) owns discrete facts and the sfc32 state
# words; a presentation layer runs per frame at 30/50/60/144 fps with a frame-rate-
# dependent camera follow. Question: what should the golden fingerprint hash so it is
# stable across frame rates yet still catches a real determinism leak?
# Stdlib, deterministic.
import hashlib, json

M = 0xFFFFFFFF
class SFC32:
    def __init__(self, seed):
        self.s = [seed & M, (seed * 0x9E3779B9) & M, (seed ^ 0xA5A5A5A5) & M, 1]
        for _ in range(12):
            self.next()
    def next(self):
        a, b, c, d = self.s
        t = (a + b + d) & M
        d = (d + 1) & M
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & M
        c = ((c << 21) | (c >> 11)) & M
        c = (c + t) & M
        self.s = [a, b, c, d]
        return t

TICK_US = 50_000           # 20 Hz sim
DUR_US = 10_000_000        # 10 s
FPS = [30, 50, 60, 144]

def canon(d):
    return hashlib.sha256(json.dumps(d, sort_keys=True, allow_nan=False).encode()).hexdigest()[:16]

def play(seed, fps, leak=False, zone_from_float=False):
    rng = SFC32(seed)
    pos, hp, kills, zone, zone_entries = 0, 40, 0, 0, 0     # discrete authoritative
    cam = 0.0                                               # continuous presentation
    frame_us = 1_000_000 // fps
    acc, t = 0, 0
    while t < DUR_US:
        t += frame_us; acc += frame_us
        while acc >= TICK_US:                               # fixed-step sim ticks
            acc -= TICK_US
            pos += 1 if rng.next() % 3 else -1              # scripted walk on the lattice
            roll = rng.next() % 20 + 1
            if roll >= 16:
                hp -= roll
                if hp <= 0:
                    kills += 1; hp = 40
            src = cam if zone_from_float else pos
            z = int(src // 5)
            if z != zone:
                zone, zone_entries = z, zone_entries + 1
                rng.next()                                   # zone entry spawns: one roll
        cam += (pos - cam) * 0.15                            # per-frame follow (fps dependent)
        if leak and abs(pos - cam) > 0.5:
            rng.next()                                       # particle jitter on the SIM stream
    words = list(rng.s)
    disc = {"pos": pos, "hp": hp, "kills": kills, "zone": zone, "entries": zone_entries}
    return {
        "raw": canon({**disc, "words": words, "cam": cam}),
        "r3": canon({**disc, "words": words, "cam": round(cam, 3)}),
        "r1": canon({**disc, "words": words, "cam": round(cam, 1)}),
        "r0": canon({**disc, "words": words, "cam": round(cam)}),
        "disc_words": canon({**disc, "words": words}),
        "disc_only": canon(disc),
        "cam": cam,
    }

SEEDS = list(range(1, 41))
SCOPES = ["raw", "r3", "r1", "r0", "disc_words", "disc_only"]

def cross_fps_mismatch(scope, **kw):
    bad = 0
    for s in SEEDS:
        hs = {play(s, f, **kw)[scope] for f in FPS}
        bad += len(hs) > 1
    return bad

# S1 clean build: which scopes are stable across frame rates? (false alarms)
clean = {sc: cross_fps_mismatch(sc) for sc in SCOPES}
spread = max(max(play(s, f)["cam"] for f in FPS) - min(play(s, f)["cam"] for f in FPS) for s in SEEDS)
print("S1 clean build, seeds whose fingerprint differs across fps (of %d):" % len(SEEDS), clean,
      "| max cam spread %.4f" % spread)

# S2 the kernel's run-twice test at ONE frame rate, with a frame-count-dependent leak
twice_same_fps = sum(play(s, 60, leak=True)["disc_words"] != play(s, 60, leak=True)["disc_words"] for s in SEEDS)
print("S2 leak, run twice at 60 fps: mismatches %d/%d" % (twice_same_fps, len(SEEDS)))

# S3 the same leak, fingerprints compared across frame rates
leak = {sc: cross_fps_mismatch(sc, leak=True) for sc in ["disc_words", "disc_only"]}
print("S3 leak across fps:", leak)

# S4 BREAK: a discrete fact (zone) derived from the continuous camera position
zf = {sc: cross_fps_mismatch(sc, zone_from_float=True) for sc in ["disc_words", "disc_only"]}
print("S4 zone from float across fps:", zf)

ok = (clean["raw"] >= 36 and clean["disc_words"] == 0 and clean["r1"] > 0
      and twice_same_fps == 0 and leak["disc_words"] >= 36 and zf["disc_words"] >= 20)
print("RESULT: %s across 4 fps x %d seeds false alarms raw %d, round3 %d, round1 %d, round0 %d, discrete+words %d; leak missed by run-twice-at-60 (%d) but caught across fps %d/%d (discrete only %d); zone-from-float caught %d"
      % ("PASS" if ok else "FAIL", len(SEEDS), clean["raw"], clean["r3"], clean["r1"], clean["r0"],
         clean["disc_words"], twice_same_fps, leak["disc_words"], len(SEEDS), leak["disc_only"], zf["disc_words"]))
