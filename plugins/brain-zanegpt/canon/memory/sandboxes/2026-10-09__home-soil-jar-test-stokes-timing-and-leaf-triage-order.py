"""Sandbox: ideas:GARDEN/soil/cheap-home-soil-diagnostics (jar test + pH + old-vs-new leaf tell).

PREDICTION (written before the first run):
 P1 Jar test timings as the kernel states them (sand at ~1 min, silt by ~3 min, clay at 24-48 h),
    applied to a 40/40/20 loam, recover each fraction within +/-5 percentage points.
    (Checked with Stokes' law, 10 cm fill, 20 C.)
 P2 A leaf-colour-only triage sends fertilizer to >=2 of the 7 true conditions where fertilizer is
    wasted; adding a structure check and a pH-first gate cuts single-cause waste to 0.
 P3 With two simultaneous causes (low pH + N shortage), one pass of the gated triage fixes at most
    1 of 2; a retest loop fixes both within 3 passes.
 P4 Kernel-compost 4:1 browns:greens by volume lands at C:N 25-35 for leaves+grass clippings under
    my stated dry-matter-per-litre assumptions, and stays inside 20-40 across a +/-25% density sweep.
Deterministic, stdlib only, no RNG, no timing.
"""
import math

G = 9.81; RHO_P = 2650.0
def water(tc):  # density, dynamic viscosity of water (Pa s) at tc C, simple table interpolation
    tbl = {10: (999.7, 1.307e-3), 20: (998.2, 1.002e-3), 30: (995.7, 0.797e-3)}
    return tbl[tc]
def stokes_v(d_m, tc=20):
    rho_w, mu = water(tc)
    return G * d_m**2 * (RHO_P - rho_w) / (18 * mu)
def settle_s(d_um, depth_m=0.10, tc=20):
    return depth_m / stokes_v(d_um * 1e-6, tc)

# --- particle classes (USDA): sand 50-2000 um, silt 2-50, clay <2 (floor 0.2). log-uniform quantile grid.
def grid(lo, hi, n=400):
    return [math.exp(math.log(lo) + (math.log(hi) - math.log(lo)) * (i + 0.5) / n) for i in range(n)]
SAND, SILT, CLAY = grid(50, 2000), grid(2, 50), grid(0.2, 2)

def sample(fs, fi, fc):
    return [(d, fs / len(SAND), 'sand') for d in SAND] + [(d, fi / len(SILT), 'silt') for d in SILT] + [(d, fc / len(CLAY), 'clay') for d in CLAY]

def settled_pct(parts, t_s, tc=20, depth=0.10):
    return sum(m for d, m, _ in parts if settle_s(d, depth, tc) <= t_s)

MIN = 60; HR = 3600
def read_texture(parts, t_sand, t_silt, t_total, tc=20):
    a = settled_pct(parts, t_sand, tc); b = settled_pct(parts, t_silt, tc); c = settled_pct(parts, t_total, tc)
    tot = c if c > 0 else 1.0
    return (100 * a / tot, 100 * (b - a) / tot, 100 * (tot - b) / tot)

fails = []
print("== S1 jar test timings via Stokes (10 cm fill, 20 C)")
for name, d in (("0.05mm sand", 50), ("0.025mm silt", 25), ("0.010mm silt", 10), ("0.002mm silt", 2)):
    t = settle_s(d)
    print(f"  {name:14s} settles in {t:9.0f} s = {t/60:8.1f} min = {t/3600:6.2f} h")
loam = sample(0.40, 0.40, 0.20)
true = (40, 40, 20)
kern = read_texture(loam, 1 * MIN, 3 * MIN, 48 * HR)
corr = read_texture(loam, 1 * MIN, 2 * HR, 48 * HR)
print("  true loam            ", true)
print("  kernel timing 1m/3m/48h  sand/silt/clay = %.1f/%.1f/%.1f" % kern)
print("  silt@2h timing 1m/2h/48h sand/silt/clay = %.1f/%.1f/%.1f" % corr)
err_k = max(abs(a - b) for a, b in zip(kern, true)); err_c = max(abs(a - b) for a, b in zip(corr, true))
print(f"  max abs error: kernel timing {err_k:.1f} pts, 2h timing {err_c:.1f} pts")
p1 = err_k <= 5
if not p1: fails.append(f"P1 kernel jar timings off by {err_k:.1f} pts (silt read {kern[1]:.1f} vs 40, clay {kern[2]:.1f} vs 20)")
# BREAK scenarios: other textures and cold water
for lab, tex, tc in (("sandy 70/20/10", (0.70, 0.20, 0.10), 20), ("clayey 20/30/50", (0.20, 0.30, 0.50), 20), ("loam in 10 C water", (0.40, 0.40, 0.20), 10)):
    p = sample(*tex); k = read_texture(p, 60, 180, 48 * HR, tc); c = read_texture(p, 60, 2 * HR, 48 * HR, tc)
    print(f"  {lab:18s} kernel-timing {k[0]:.0f}/{k[1]:.0f}/{k[2]:.0f}  2h-timing {c[0]:.0f}/{c[1]:.0f}/{c[2]:.0f}")
sweep_ok = True
for tt in (60, 180, 600, 1800, 2 * HR):
    r = read_texture(loam, 60, tt, 48 * HR); print(f"  silt read at {tt/60:6.0f} min -> silt {r[1]:5.1f}")

print("== S2 triage: leaf-colour-only proxy vs structure+pH gated (7 conditions x 2 variants)")
# symptom table from the kernel's own statements; overlap variants model 'real symptoms overlap'
CAUSES = ["N", "P", "K", "compaction", "ph_high", "ph_low", "ok"]
def obs(cause, v):
    o = dict(old_yellow=False, old_purple=False, old_margin_burn=False, new_yellow=False, stunted=False, pooling=False, ph=6.6)
    if cause == "N": o.update(old_yellow=True, stunted=True)
    if cause == "P": o.update(old_purple=True, stunted=True)
    if cause == "K": o.update(old_margin_burn=True, old_yellow=(v == 1))
    if cause == "compaction": o.update(old_yellow=True, stunted=True, pooling=True)
    if cause == "ph_high": o.update(new_yellow=True, ph=7.9, stunted=(v == 1))
    if cause == "ph_low": o.update(old_yellow=True, stunted=True, ph=5.1 if v == 0 else 5.6)
    return o
def leaf_only(o):
    if o["old_margin_burn"]: return "K"
    if o["old_purple"]: return "P"
    if o["old_yellow"]: return "N"
    if o["new_yellow"]: return "micro"
    return "ok"
def gated(o):
    if o["ph"] < 6.0 or o["ph"] > 7.5: return "ph_low" if o["ph"] < 6.0 else "ph_high"
    if o["pooling"]: return "compaction"
    return leaf_only(o)
FIX_OK = {("N", "N"), ("P", "P"), ("K", "K"), ("compaction", "compaction"), ("ph_high", "ph_high"), ("ph_high", "micro"), ("ph_low", "ph_low"), ("ok", "ok")}
def score(policy):
    waste = 0; proj = {}; right = 0; n = 0
    for c in CAUSES:
        for v in (0, 1):
            o = obs(c, v); a = policy(o); n += 1
            right += (c, a) in FIX_OK
            if a in ("N", "P", "K", "micro") and (c, a) not in FIX_OK: waste += 1
            proj.setdefault(a, set()).add(c)
    return right, n, waste, proj
r1, n, w1, proj = score(leaf_only); r2, _, w2, _ = score(gated)
print(f"  leaf-only: correct {r1}/{n}, wasted fertilizer {w1}")
print(f"  gated    : correct {r2}/{n}, wasted fertilizer {w2}")
coll = {k: sorted(v) for k, v in proj.items() if len(v) > 1}
print("  leaf-only projection collapses:", coll)
wasted_conds = sorted({c for c in CAUSES for v in (0, 1) if leaf_only(obs(c, v)) in ("N", "P", "K", "micro") and (c, leaf_only(obs(c, v))) not in FIX_OK})
print("  conditions with wasted fertilizer under leaf-only:", wasted_conds)
p2 = len(wasted_conds) >= 2 and w2 == 0
if not p2: fails.append(f"P2 wasted conds {wasted_conds}, gated waste {w2}")

print("== S3 compound causes (BREAK: gated single pass vs retest loop)")
def observe_set(causes):
    o = dict(old_yellow=False, old_purple=False, old_margin_burn=False, new_yellow=False, stunted=False, pooling=False, ph=6.6)
    for c in causes:
        for k, v in obs(c, 0).items():
            if k == "ph":
                if v != 6.6: o["ph"] = v
            else: o[k] = o[k] or v
    return o
def run(causes, passes):
    left = set(causes); log = []
    for _ in range(passes):
        a = gated(observe_set(left))
        if a == "ok": break
        left.discard({"micro": "ph_high"}.get(a, a)); log.append(a)
    return log, left
for combo in (("ph_low", "N"), ("compaction", "N"), ("ph_low", "compaction", "K")):
    one, l1 = run(combo, 1); loop, l2 = run(combo, 3)
    print(f"  {'+'.join(combo):22s} one pass fixes {len(combo)-len(l1)}/{len(combo)} {one}; 3-pass loop fixes {len(combo)-len(l2)}/{len(combo)} {loop}")
combo = ("ph_low", "N"); p3 = (len(combo) - len(run(combo, 1)[1]) <= 1) and not run(combo, 3)[1]
if not p3: fails.append("P3 compound loop did not behave as predicted")

print("== S4 compost-recipe sibling: does '4:1 browns:greens by volume' give C:N ~30?")
# per-kg dry matter: (pct N, C:N); dry matter per litre of loose material (assumed)
MAT = {"leaves": (0.8, 60, 0.06), "straw": (0.6, 80, 0.04), "grass": (2.5, 17, 0.06), "kitchen": (2.0, 15, 0.10), "coffee": (2.2, 20, 0.30)}
def cn(mix, scale=None):
    sn = sc = 0.0
    for m, vol in mix.items():
        pn, ratio, dm = MAT[m]
        if scale: dm *= scale.get(m, 1)
        n = vol * dm * pn / 100; sn += n; sc += n * ratio
    return sc / sn
mixes = {"leaves4:grass1": {"leaves": 4, "grass": 1}, "leaves4:kitchen1": {"leaves": 4, "kitchen": 1}, "straw4:grass1": {"straw": 4, "grass": 1}}
for k, m in mixes.items(): print(f"  {k:18s} C:N {cn(m):5.1f}")
base = cn(mixes["leaves4:grass1"]); lo = min(cn(mixes["leaves4:grass1"], {"leaves": a, "grass": b}) for a in (.75, 1.25) for b in (.75, 1.25)); hi = max(cn(mixes["leaves4:grass1"], {"leaves": a, "grass": b}) for a in (.75, 1.25) for b in (.75, 1.25))
print(f"  leaves4:grass1 base {base:.1f}, density sweep +/-25% -> {lo:.1f}..{hi:.1f}")
vols = {r: cn({"leaves": r, "grass": 1}) for r in (1, 2, 3, 4, 5, 6)}
near30 = min(vols, key=lambda r: abs(vols[r] - 30)); print("  ratio nearest C:N 30 (leaves:grass by volume):", near30, "->", round(vols[near30], 1))
p4 = 25 <= base <= 35 and 20 <= lo and hi <= 40
if not p4: fails.append(f"P4 4:1 gives C:N {base:.1f} (sweep {lo:.1f}..{hi:.1f}); nearest 30 at {near30}:1")

print("PREDICTIONS:", dict(P1=p1, P2=p2, P3=p3, P4=p4))
if fails:
    print("RESULT: FAIL " + "; ".join(fails))
else:
    print("RESULT: PASS all four predictions held")
