"""Sandbox: do stand-up callbacks survive being cut into short social clips?

A callback is a later line that pays off an earlier joke (the antecedent). Live, the whole
room heard the antecedent. Cut into a short clip, the callback only lands if the antecedent
(or a reminder of it) is inside the same clip. Model: a 600 s set; callbacks at fixed gaps;
clips of length L at every integer start second (uniform clipping) or chosen to end 3 s after
the callback (the creator clips the biggest laugh as the closer). A callback "lands" in a clip
iff the clip contains the callback instant and at least one reference instant before it
(antecedent, an earlier runner mention, or a premise reminder line).
Analytic expectation for uniform clips away from the set edges: land fraction = max(0, L-g)/L.
Pure stdlib, deterministic, exhaustive over start seconds.
"""
SET = 1200  # first run used 600 with the callback at 590: clips were pinned by the set end (edge artifact)
GAPS = [30, 60, 120, 240, 360, 480]
CALLBACK_AT = 600  # mid-set so no clip touches a set edge; antecedent at 600 - gap

def land_fraction_uniform(refs, c, L):
    """Fraction of clips containing the callback c that also contain a ref < c."""
    starts = [s for s in range(0, SET - L + 1) if s <= c <= s + L]
    if not starts:
        return None
    hit = sum(1 for s in starts if any(s <= r <= s + L for r in refs if r < c))
    return hit / len(starts)

def lands_closer(refs, c, L, tail=3):
    s = c + tail - L
    return any(s <= r <= c + tail for r in refs if r < c)

out = {}
print("S1 uniform clips, single antecedent (land fraction vs analytic (L-g)/L):")
for L in (30, 60, 90):
    fr = []
    for g in GAPS:
        f = land_fraction_uniform([CALLBACK_AT - g], CALLBACK_AT, L)
        fr.append(f)
    ana = [max(0, L - g) / L for g in GAPS]
    out[("u", L)] = fr
    print(f"  L={L:3d}s  sim {[round(x, 3) for x in fr]}  analytic {[round(x, 3) for x in ana]}  "
          f"mean {sum(fr)/len(fr):.3f}")

print("S2 creator clips ending 3 s after the callback:")
for L in (30, 60, 90):
    n = sum(lands_closer([CALLBACK_AT - g], CALLBACK_AT, L) for g in GAPS)
    out[("c", L)] = n
    print(f"  L={L:3d}s  callbacks landing {n}/{len(GAPS)}")

# S3 runner: the same 240 s span covered by mentions every 60 s (antecedent + 3 mentions + final)
runner_refs = [CALLBACK_AT - 240, CALLBACK_AT - 180, CALLBACK_AT - 120, CALLBACK_AT - 60]
run_u60 = land_fraction_uniform(runner_refs, CALLBACK_AT, 60)
run_u90 = land_fraction_uniform(runner_refs, CALLBACK_AT, 90)
run_c90 = lands_closer(runner_refs, CALLBACK_AT, 90)
run_c60 = lands_closer(runner_refs, CALLBACK_AT, 60)
single240_c90 = lands_closer([CALLBACK_AT - 240], CALLBACK_AT, 90)
print(f"S3 runner every 60 s over 240 s: uniform L=60 {run_u60:.3f}, L=90 {run_u90:.3f}; closer L=90 {run_c90}, "
      f"L=60 {run_c60}; single 240 s callback closer L=90 {single240_c90}")

# S4 premise reminder line 5 s before each callback (long-gap callbacks keep the antecedent too)
rem = [land_fraction_uniform([CALLBACK_AT - g, CALLBACK_AT - 5], CALLBACK_AT, 60) for g in GAPS]
rem_c = sum(lands_closer([CALLBACK_AT - g, CALLBACK_AT - 5], CALLBACK_AT, 60) for g in GAPS)
print(f"S4 reminder 5 s before, uniform L=60: {[round(x, 3) for x in rem]} mean {sum(rem)/len(rem):.3f}; closer L=60 {rem_c}/6")

# S5 BREAK: the full set is the clip (or a live room): every callback lands
full = sum(lands_closer([CALLBACK_AT - g], CALLBACK_AT, SET, tail=0) for g in GAPS)
print(f"S5 BREAK full-set clip: {full}/6 land")

u60 = out[("u", 60)]
checks = {
    "P1 uniform L=60: g=30 lands 0.5, g>=60 lands 0": abs(u60[0] - 0.5) < 0.02 and all(x < 0.02 for x in u60[1:]),
    "P1 uniform L=60 mean ~0.083": abs(sum(u60) / 6 - 1 / 12) < 0.01,
    "P2 closer L=60 1/6, L=90 2/6": out[("c", 60)] == 1 and out[("c", 90)] == 2,
    "P3 runner closer L=90 lands, single 240 s does not": run_c90 and not single240_c90,
    "P4 reminder uniform L=60 mean >= 0.90": sum(rem) / len(rem) >= 0.90,
    "P5 full-set 6/6": full == 6,
}
for k, v in checks.items():
    print(f"  {'ok ' if v else 'MISS'} {k}")
print(f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} 60 s clips: callback gap 30 s lands {u60[0]:.2f}, "
      f">=60 s lands 0 (mean {sum(u60)/6:.3f}); closer clips land {out[('c',60)]}/6 at 60 s, {out[('c',90)]}/6 at 90 s; "
      f"runner every 60 s lands in 90 s closer, single 240 s gap does not; 5 s reminder lifts mean to {sum(rem)/len(rem):.3f}; full set 6/6")
