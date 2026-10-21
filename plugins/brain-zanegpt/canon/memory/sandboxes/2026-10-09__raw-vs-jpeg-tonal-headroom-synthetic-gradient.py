#!/usr/bin/env python3
"""Sandbox: does RAW keep tonal data that JPEG throws away? (synthetic model)

Stdlib only, no RNG, no timing. Everything is a closed-form ramp.

MODEL (assumptions, all parameterised below):
  scene   : linear-light radiance ramp, sampled densely (N samples).
  sensor  : linear, clips at 1.0, quantised to B bits (12 or 14) -> "raw".
  jpeg    : camera applies the sRGB tone curve then quantises to 8 bits.
            Optional `jw` = scene level that the camera maps to 255
            (jw<1 models in-camera highlight roll-off/clip with raw headroom).
            DCT lossy compression is NOT modelled (it only hurts JPEG more).
  edit    : decode to scene-linear, multiply by 2**EV, clamp, sRGB-encode,
            round to an 8-bit display value.
  metrics : distinct output codes, coverage = distinct / output codes the
            ideal (infinite-precision) edit would use, max adjacent gap in
            output codes (banding), histogram bin-255 pile-up (clipping).

PREDICTION (written before the first run):
  P1 +4EV push of a ramp from 2^-9..2^-5: raw14 coverage>=0.95 and max gap<=1;
     jpeg8 coverage<=0.40 and max gap>=4; raw12 max gap between 2 and 4.
  P2 at 0 EV all three paths agree within 1 output code (no edit = no difference).
  P3 BREAK: deep shadows 2^-12..2^-8, +6EV: raw12 has less than 2x the
     distinct input levels of jpeg8 (12-bit linear is NOT dramatically better
     than an 8-bit gamma-encoded file in the deepest shadows).
  P4 highlight pull -1EV on 0.72..1.0 with jw=0.7: jpeg8 keeps 0 distinct
     detail levels (all clipped, piled in bin 255); raw14 keeps >=100.
     Control jw=1.0: jpeg8 keeps >0 levels. Control: data above sensor clip
     (scene 1.0..2.0) is gone in raw too (<=1 level).
  P5 same bit depth, no tone curve: raw8-linear has LOWER shadow coverage than
     jpeg8 (curve placement, not file name, drives the result).
  P6 tungsten-cast gray ramp, blue gain x4 in post: raw14 blue max gap<=1,
     jpeg8 blue max gap>=3.
"""
import math

def enc(l):  # sRGB OETF
    l = min(1.0, max(0.0, l))
    return 12.92 * l if l <= 0.0031308 else 1.055 * l ** (1 / 2.4) - 0.055

def dec(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

def q(x, bits):
    m = (1 << bits) - 1
    return round(min(1.0, max(0.0, x)) * m)

def ramp(lo, hi, n):
    # log-uniform samples so every stop is sampled equally densely
    a, b = math.log2(lo), math.log2(hi)
    return [2 ** (a + (b - a) * i / (n - 1)) for i in range(n)]

def raw_edit(l, bits, ev):
    r = q(l, bits) / ((1 << bits) - 1)
    return round(255 * enc(r * 2 ** ev))

def raw_lin8_edit(l, ev):
    return raw_edit(l, 8, ev)

def jpeg_store(l, jw=1.0):
    return q(enc(min(l, jw) / jw), 8)

def jpeg_edit(l, ev, jw=1.0):
    v = jpeg_store(l, jw)
    return round(255 * enc(dec(v / 255) * jw * 2 ** ev))

def ideal(l, ev):
    return round(255 * enc(l * 2 ** ev))

def stats(outs, ideal_outs):
    d = sorted(set(outs))
    gaps = [b - a for a, b in zip(d, d[1:])]
    ideal_n = len(set(ideal_outs))
    return dict(distinct=len(d), coverage=len(d) / ideal_n,
                maxgap=max(gaps) if gaps else 0,
                bin255=sum(1 for o in outs if o == 255) / len(outs))

CHECKS = []
def check(name, cond, detail):
    CHECKS.append(cond)
    print(f"  [{'ok' if cond else 'XX'}] {name}: {detail}")

N = 20000

# ---------------- S1: +4EV shadow push -------------------
print("S1 shadow push +4EV, ramp 2^-9..2^-5")
xs = ramp(2 ** -9, 2 ** -5, N); EV = 4
idl = [ideal(l, EV) for l in xs]
r14 = stats([raw_edit(l, 14, EV) for l in xs], idl)
r12 = stats([raw_edit(l, 12, EV) for l in xs], idl)
j8 = stats([jpeg_edit(l, EV) for l in xs], idl)
for n, s in (("raw14", r14), ("raw12", r12), ("jpeg8", j8)):
    print(f"    {n}: distinct={s['distinct']} cov={s['coverage']:.2f} maxgap={s['maxgap']}")
check("P1 raw14", r14['coverage'] >= .95 and r14['maxgap'] <= 1, f"cov={r14['coverage']:.2f} gap={r14['maxgap']}")
check("P1 jpeg8", j8['coverage'] <= .40 and j8['maxgap'] >= 4, f"cov={j8['coverage']:.2f} gap={j8['maxgap']}")
check("P1 raw12 mid", 2 <= r12['maxgap'] <= 4, f"gap={r12['maxgap']}")

# ---------------- S2: no edit control -------------------
print("S2 negative control: 0 EV, same ramp")
xs0 = ramp(2 ** -9, 1.0, N)
worst = 0
for l in xs0:
    i = ideal(l, 0)
    worst = max(worst, abs(raw_edit(l, 14, 0) - i), abs(raw_edit(l, 12, 0) - i), abs(jpeg_edit(l, 0) - i))
check("P2 no-edit agreement", worst <= 1, f"worst output error vs ideal = {worst} code(s)")

# ---------------- S3: BREAK deep shadows -------------------
print("S3 BREAK: deep shadows 2^-12..2^-8 +6EV, distinct INPUT levels stored")
xd = ramp(2 ** -12, 2 ** -8, N)
in12 = len({q(l, 12) for l in xd}); in14 = len({q(l, 14) for l in xd})
inj = len({jpeg_store(l) for l in xd})
print(f"    stored levels: raw14={in14} raw12={in12} jpeg8={inj}")
check("P3 raw12 < 2x jpeg8 in deepest shadows", in12 < 2 * inj, f"{in12} vs {inj} ratio {in12/inj:.2f}")
print(f"    (info) raw14/jpeg8 in same band = {in14/inj:.2f}x")

# ---------------- S4: highlight pull + controls -------------------
print("S4 highlight pull -1EV, ramp 0.72..1.0")
xh = ramp(0.72, 1.0, N); EVh = -1
idh = [ideal(l, EVh) for l in xh]
rh = stats([raw_edit(l, 14, EVh) for l in xh], idh)
jh = stats([jpeg_edit(l, EVh, 0.7) for l in xh], idh)
jc = stats([jpeg_edit(l, EVh, 1.0) for l in xh], idh)
print(f"    raw14 distinct={rh['distinct']}  jpeg(jw=.7) distinct={jh['distinct']} bin255(stored)="
      f"{sum(1 for l in xh if jpeg_store(l,0.7)==255)/len(xh):.2f}  jpeg(jw=1) distinct={jc['distinct']}")
print(f"    (info) ideal output codes in this pull = {len(set(idh))}; raw14 coverage={rh['coverage']:.2f}")
check("P4 jpeg w/ headroom clipped", jh['distinct'] <= 1, f"distinct={jh['distinct']}")
check("P4 raw14 keeps detail", rh['distinct'] >= 100, f"distinct={rh['distinct']}")
check("P4 control jw=1 keeps data", jc['distinct'] > 1, f"distinct={jc['distinct']}")
xo = ramp(1.0, 2.0, N)  # beyond sensor clip: never recorded
ro = stats([raw_edit(l, 14, -1) for l in xo], [ideal(l, -1) for l in xo])
check("P4 control: data beyond sensor clip gone in raw too", ro['distinct'] <= 1, f"distinct={ro['distinct']}")

# ---------------- S5: same bits, no curve -------------------
print("S5 control: 8-bit linear raw vs 8-bit sRGB jpeg, +4EV ramp 2^-9..2^-5")
l8 = stats([raw_lin8_edit(l, EV) for l in xs], idl)
print(f"    raw8-linear cov={l8['coverage']:.2f} gap={l8['maxgap']}   jpeg8 cov={j8['coverage']:.2f} gap={j8['maxgap']}")
check("P5 raw8-linear worse than jpeg8", l8['coverage'] < j8['coverage'], f"{l8['coverage']:.2f} < {j8['coverage']:.2f}")

# ---------------- S6: WB fix in post -------------------
print("S6 tungsten-cast gray ramp (B channel = 0.25 of G), blue gain x4 in post")
GAIN = 4.0
xg = ramp(2 ** -6, 0.25, N)
blue = [l * 0.25 for l in xg]   # recorded blue radiance
idb = [round(255 * enc(b * GAIN)) for b in blue]
rb = stats([round(255 * enc(q(b, 14) / 16383 * GAIN)) for b in blue], idb)
def jb(b):
    v = q(enc(b), 8); return round(255 * enc(dec(v / 255) * GAIN))
jbs = stats([jb(b) for b in blue], idb)
print(f"    blue raw14 distinct={rb['distinct']} gap={rb['maxgap']}   jpeg8 distinct={jbs['distinct']} gap={jbs['maxgap']}")
print(f"    (info) blue coverage raw14={rb['coverage']:.2f} jpeg8={jbs['coverage']:.2f}")
check("P6 raw14 blue smooth", rb['maxgap'] <= 1, f"gap={rb['maxgap']}")
check("P6 jpeg8 blue banded", jbs['maxgap'] >= 3, f"gap={jbs['maxgap']}")

ok = all(CHECKS)
print(f"RESULT: {'PASS' if ok else 'FAIL'} {sum(CHECKS)}/{len(CHECKS)} predictions held "
      f"(S1 cov raw14/raw12/jpeg8={r14['coverage']:.2f}/{r12['coverage']:.2f}/{j8['coverage']:.2f}, "
      f"gap {r14['maxgap']}/{r12['maxgap']}/{j8['maxgap']}; deep-shadow raw12:jpeg8 levels={in12}:{inj})")
