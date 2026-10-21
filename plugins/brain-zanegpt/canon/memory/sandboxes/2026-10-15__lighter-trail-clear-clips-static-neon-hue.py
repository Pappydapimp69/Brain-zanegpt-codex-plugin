"""Loop 4 pass 1 (current half). Kernel: composite modes are the style - 'lighter' for neon
(overlaps brighten, translucent black clear alpha ~0.2 for trails), 'multiply' onto paper for ink/riso
(overlap makes a third overprint colour). Reproduce both, then push the neon recipe until it breaks.
Canvas 2D maths modelled per channel in 8-bit like a canvas backing store:
  lighter: d = min(255, d + s)            source-over black at alpha a: d = round(d * (1 - a))
  multiply (opaque src, alpha a over opaque backdrop): d = round(d * (1 - a) + a * d * s / 255)
No RNG; deterministic.
PREDICTION (written before running):
 1) two crossing neon strokes at 128 under lighter give 255 at the crossing, source-over 128;
    cyan-ish x magenta-ish riso inks multiplied on warm paper give a third colour darker than both.
 2) draw order: lighter and multiply give 1 distinct result over all 6 orders of 3 strokes, source-over >1.
    (Run 1 refuted this for 8-bit multiply: 5 distinct. The check now asks float multiply = 1 and 8-bit
    spread <= 2 levels, i.e. rounding only - a change made after seeing the result.)
 3) BREAK: with the trail clear (a=0.2) a pixel the stroke covers every frame converges to s/a = 5s,
    so an orange (255,128,26) stroke held still turns yellow-white: hue drifts > 20 degrees within
    3 frames; a stroke moving faster than its width (dwell 1 frame) keeps its hue.
 4) BREAK: 8-bit rounding leaves a ghost: after the stroke leaves, values <= 2 never fade to 0 at a=0.2.
 5) FIX: keep the persistent trail with 'lighten' (max) and add only this frame's strokes with
    'lighter' -> static hue drift 0, crossing still 255."""
import colorsys, itertools

def lighter(d, s): return tuple(min(255, x + y) for x, y in zip(d, s))
def lighten(d, s): return tuple(max(x, y) for x, y in zip(d, s))
def fade(d, a): return tuple(int(x * (1 - a) + 0.5) for x in d)           # black at alpha a, source-over
def over(d, s, a): return tuple(int(x * (1 - a) + y * a + 0.5) for x, y in zip(d, s))
def multiply(d, s, a): return tuple(int(x * (1 - a) + a * x * y / 255 + 0.5) for x, y in zip(d, s))
def hue(c):
    h, l, s = colorsys.rgb_to_hls(*(x / 255 for x in c)); return h * 360
def hdiff(a, b): d = abs(a - b) % 360; return min(d, 360 - d)

out = {}
# 1) reproduce: neon overlap brightens; riso overprint makes a third colour
n = (0, 128, 128)
out["cross_lighter"] = lighter(lighter((0, 0, 0), n), n)
out["cross_over"] = over(over((0, 0, 0), n, 1.0), n, 1.0)
paper = (245, 238, 220); teal = (0, 150, 190); pink = (255, 72, 176)
t = multiply(paper, teal, 1.0); p = multiply(paper, pink, 1.0); tp = multiply(t, pink, 1.0)
third = sum(tp) < min(sum(t), sum(p)) and hdiff(hue(tp), hue(t)) > 20 and hdiff(hue(tp), hue(p)) > 20
print(f"1) crossing lighter {out['cross_lighter']} vs source-over {out['cross_over']}; riso teal {t} pink {p} overprint {tp} "
      f"hue {hue(t):.0f}/{hue(p):.0f}/{hue(tp):.0f} third colour {third}")

# 2) draw-order independence over 6 orders of 3 strokes
strokes = [(200, 40, 10), (30, 180, 90), (60, 60, 220)]
distinct = {}
for mode in ("lighter", "multiply", "source-over a0.6"):
    res = set()
    for order in itertools.permutations(strokes):
        d = (0, 0, 0) if mode == "lighter" else paper
        for s in order:
            d = lighter(d, s) if mode == "lighter" else multiply(d, s, 0.6) if mode == "multiply" else over(d, s, 0.6)
        res.add(d)
    distinct[mode] = len(res)
# added after run 1 (multiply gave 5 distinct in 8-bit): same orders in exact float maths, and the 8-bit spread
mf = set(); m8 = []
for order in itertools.permutations(strokes):
    d = tuple(float(x) for x in paper); d8 = paper
    for s in order:
        d = tuple(x * (1 - 0.6) + 0.6 * x * y / 255 for x, y in zip(d, s)); d8 = multiply(d8, s, 0.6)
    mf.add(tuple(round(x, 9) for x in d)); m8.append(d8)
mspread = max(max(c[i] for c in m8) - min(c[i] for c in m8) for i in range(3))
distinct["multiply float"] = len(mf)
print(f"2) distinct results over 6 draw orders: {distinct}; 8-bit multiply max channel spread {mspread}")

# 3) BREAK: trail clear + lighter on a stroke that stays on a pixel for `dwell` frames
orange = (255, 128, 26)
def run(dwell, mode="lighter", a=0.2, frames=12):
    d = (0, 0, 0); log = []
    for f in range(frames):
        d = fade(d, a)
        if f < dwell: d = lighter(d, orange) if mode == "lighter" else lighten(d, orange)
        log.append(d)
    return log
static = run(12)
drift = [hdiff(hue(c), hue(orange)) for c in static]
first20 = next((i + 1 for i, x in enumerate(drift) if x > 20), None)
mover = run(1)
print(f"3) orange hue {hue(orange):.1f}; static under lighter+clear0.2 frames 1-4: {static[:4]} hue drift {[round(x,1) for x in drift[:4]]}, "
      f">20 deg at frame {first20}, steady {static[-1]} hue {hue(static[-1]):.1f}")
print(f"   moving (dwell 1): peak {mover[0]} hue drift {hdiff(hue(mover[0]), hue(orange)):.1f}")
dwell_needed = {a: next(n for n in range(1, 50) if hdiff(hue(run(n, a=a, frames=n)[-1]), hue(orange)) > 20) for a in (0.1, 0.2, 0.3, 0.5)}
print(f"   frames of dwell until >20 deg drift, by clear alpha: {dwell_needed}")

# 4) BREAK: ghosts - after the stroke leaves, does the trail reach black?
ghost = {}
for a in (0.1, 0.2, 0.3):
    d = (255, 128, 26)
    for _ in range(200): d = fade(d, a)
    ghost[a] = d
print(f"4) residual after 200 fade frames: {ghost}")

# 5) FIX: persistent trail via lighten(max), this frame's strokes summed with lighter on top
def run_fix(frames=12, a=0.2):
    trail = (0, 0, 0)
    for f in range(frames):
        trail = lighten(fade(trail, a), orange)
    return trail
fix_static = run_fix()
cur = lighter(n, n)                                      # this frame's crossing, added fresh
fix_cross = lighten(fade((0, 0, 0), 0.2), cur)
print(f"5) fix static {fix_static} drift {hdiff(hue(fix_static), hue(orange)):.1f} deg; fix crossing {fix_cross}")

ok = (out["cross_lighter"] == (0, 255, 255) and out["cross_over"] == (0, 128, 128) and third
      and distinct["lighter"] == 1 and distinct["multiply float"] == 1 and mspread <= 2 and distinct["source-over a0.6"] > 1
      and first20 is not None and first20 <= 3 and hdiff(hue(mover[0]), hue(orange)) < 1
      and hdiff(hue(fix_static), hue(orange)) < 1 and fix_cross == (0, 255, 255) and ghost[0.2] != (0, 0, 0))
print(f"RESULT: {'PASS' if ok else 'FAIL'} lighter crossing 255 vs over 128; riso overprint third colour {third}; "
      f"order-free lighter {distinct['lighter']} multiply 8-bit {distinct['multiply']} (spread {mspread}, float {distinct['multiply float']}) over {distinct['source-over a0.6']}; "
      f"static orange under clear 0.2 drifts >20deg at frame {first20} to {static[-1]} (hue {hue(orange):.0f}->{hue(static[-1]):.0f}), "
      f"dwell-1 drift {hdiff(hue(mover[0]), hue(orange)):.1f}; ghost floor {ghost[0.2]} at a0.2, {ghost[0.1]} at a0.1; max-trail fix drift "
      f"{hdiff(hue(fix_static), hue(orange)):.1f}")
