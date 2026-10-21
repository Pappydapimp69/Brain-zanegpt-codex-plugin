"""Sandbox for the PITCH kernel 'two-futures-timelapse-same-start-diverging-end', exercised with
brain/E34 (fit projection to min(W,H)) and sandbox-combined-brain-viz-growth/E2 (per-mark filter vs one composited pass).
PREDICTION (before run):
 1. Both panels show the same counter at t0 (1) and diverge: take-only ends at 1, contribute ends at 1+N (N=400); two replays are byte-identical.
 2. Fitting the golden-angle spiral with an H-only scale clips most nodes on a portrait side-by-side layout (207x896 panels, >50%)
    and some on landscape (640x720, >0%), while min(W,H) clips 0 in every layout.
 3. Per-mark glow (cost 1+11 per node) exceeds a 600-unit frame budget once nodes > 50, so the contribute panel overruns late in the movie;
    one composited filter pass (n + 11) stays under budget at N=400; the take-only panel is under budget either way.
 4. BREAK: at N=1000 even the composited pass overruns (n + 11 > 600), so compositing is not a cure for unbounded growth.
Deterministic: golden angle, no RNG, no timing."""
import math, hashlib
GOLD = math.pi * (3 - math.sqrt(5))
def nodes(n, c=1.0):
    return [(c * math.sqrt(i) * math.cos(i * GOLD), c * math.sqrt(i) * math.sin(i * GOLD)) for i in range(n)]
def panel_counts(frames, n_end, contribute):
    return [1 + (round(n_end * f / (frames - 1)) if contribute else 0) for f in range(frames)]
def clipped(n, W, H, axis):
    pts = nodes(n)
    rmax = math.sqrt(n - 1)
    side = H if axis == "H" else min(W, H)
    scale = 0.5 * side * 0.9 / math.sqrt(400 - 1)   # tuned so N=400 just fits a square of that side
    return sum(1 for x, y in pts if abs(x * scale) > W / 2 or abs(y * scale) > H / 2)
N, FR = 400, 101
take, give = panel_counts(FR, N, False), panel_counts(FR, N, True)
s1 = take[0] == give[0] == 1 and take[-1] == 1 and give[-1] == 1 + N
h1 = hashlib.md5(repr((take, give)).encode()).hexdigest()
h2 = hashlib.md5(repr((panel_counts(FR, N, False), panel_counts(FR, N, True))).encode()).hexdigest()
s1 = s1 and h1 == h2
print(f"S1 counters t0 {take[0]}/{give[0]} end {take[-1]}/{give[-1]} replay_identical={h1==h2}")
layouts = {"portrait side-by-side 207x896": (207, 896), "landscape side-by-side 640x720": (640, 720), "portrait stacked 414x448": (414, 448)}
clipH, clipM = {}, {}
for k, (W, H) in layouts.items():
    clipH[k] = clipped(N, W, H, "H") / N
    clipM[k] = clipped(N, W, H, "min") / N
    print(f"S2 {k}: H-only clipped {clipH[k]:.2f} min-axis clipped {clipM[k]:.2f}")
s2 = clipH["portrait side-by-side 207x896"] > 0.5 and clipH["landscape side-by-side 640x720"] > 0 and all(v == 0 for v in clipM.values())
BUD, BASE, FILT = 600, 1, 11
def cost(n, mode): return n * (BASE + FILT) if mode == "per-mark" else n * BASE + FILT
over = {m: sum(cost(c, m) > BUD for c in give) for m in ("per-mark", "composite")}
over_take = {m: sum(cost(c, m) > BUD for c in take) for m in ("per-mark", "composite")}
first_over = next(f for f, c in enumerate(give) if cost(c, "per-mark") > BUD)
print(f"S3 frames over budget (of {FR}): contribute {over} take-only {over_take}; per-mark first overruns at frame {first_over} (nodes {give[first_over]})")
s3 = over["per-mark"] > 0 and over["composite"] == 0 and over_take == {"per-mark": 0, "composite": 0}
brk = cost(1 + 1000, "composite") > BUD
print(f"S4 BREAK composite at N=1000 cost {cost(1001, 'composite')} > {BUD}: {brk}")
ok = s1 and s2 and s3 and brk
print(f"RESULT: {'PASS' if ok else 'FAIL'} counters equal at t0 and diverge ({take[-1]} vs {give[-1]}); "
      f"H-only clips {clipH['portrait side-by-side 207x896']:.0%} on portrait, min-axis 0; per-mark overruns {over['per-mark']} frames, composite {over['composite']}; composite fails at N=1000")
