"""Daedalus and Icarus: a safe band between two opposite failures.

Altitude h each step. Below LOW the sea spray soaks the feathers (wet meter +1),
above HIGH the sun softens the wax (heat meter +1); inside the band both meters
recover by 0.5. A meter reaching 3 is a fall, on that side.
Motion per step:
  h += drift + gust(t) + k * (setpoint - h_seen)
drift = steady upward pull ("drawn by desire for the heavens"), gust = deterministic
sine wobble, k = how hard the guide corrects, h_seen = altitude the guide reacts to
(possibly a few steps old). Deterministic, stdlib only.
"""
import math

STEPS = 60
FAIL_AT = 3.0


def fly(low=20.0, high=80.0, drift=2.0, k=0.5, amp=6.0, period=12, setpoint=None,
        abandon_at=None, delay=0, h0=None):
    center = (low + high) / 2
    sp = center if setpoint is None else setpoint
    h = center if h0 is None else h0
    hist = [h]
    wet = heat = 0.0
    lo_seen, hi_seen = h, h
    sea_steps = 0
    for t in range(STEPS):
        gain = 0.0 if (abandon_at is not None and t >= abandon_at) else k
        seen = hist[max(0, len(hist) - 1 - delay)]
        # gust is a velocity wobble; integrate its change so altitude wobbles by about amp
        gust_step = amp * (math.sin(2 * math.pi * (t + 1) / period) - math.sin(2 * math.pi * t / period))
        h = h + drift + gust_step + gain * (sp - seen)
        hist.append(h)
        if t >= 12:  # ignore the settling-in from the start
            lo_seen, hi_seen = min(lo_seen, h), max(hi_seen, h)
        if h < low:
            sea_steps += 1
            wet += 1
        else:
            wet = max(0.0, wet - 0.5)
        if h > high:
            heat += 1
        else:
            heat = max(0.0, heat - 0.5)
        if wet >= FAIL_AT:
            return ("SEA", t, lo_seen, hi_seen, sea_steps, min(hist))
        if heat >= FAIL_AT:
            return ("SUN", t, lo_seen, hi_seen, sea_steps, min(hist))
    return ("SAFE", None, lo_seen, hi_seen, sea_steps, min(hist))


def min_width(**kw):
    """Narrow a band centered on 50 until the flyer first fails; return smallest safe width."""
    best = None
    for w in range(60, 0, -1):
        r = fly(low=50 - w / 2, high=50 + w / 2, **kw)
        if r[0] == "SAFE":
            best = w
        else:
            break
    return best


ok = True

r1 = fly()
print(f"S1 guided, centered: {r1[0]}, altitude range after settling {r1[2]:.1f}-{r1[3]:.1f} "
      f"(drift/k offset = {2.0/0.5:.0f})")
ok &= r1[0] == "SAFE"

r2 = fly(abandon_at=20)
print(f"S2 guide abandoned at step 20: {r2[0]} at step {r2[1]}")
ok &= r2[0] == "SUN"

w3 = min_width()
print(f"S3 narrowing band, centered setpoint: smallest safe width {w3}")
w4 = min_width(setpoint=50 - 2.0 / 0.5)
print(f"S4 narrowing band, setpoint biased toward the sea by drift/k: smallest safe width {w4}")
ok &= w3 is not None and w4 is not None and w4 < w3

print("S5 drift tolerance vs band width (centered setpoint, k=0.5): largest safe drift")
tol = []
for w in (60, 40, 30, 20, 16):
    best = 0.0
    d = 0.0
    while d <= 20:
        if fly(low=50 - w / 2, high=50 + w / 2, drift=d)[0] == "SAFE":
            best = d
        else:
            break
        d = round(d + 0.25, 2)
    tol.append((w, best))
    print(f"   width {w:2d}: drift up to {best:.2f}")
ok &= all(tol[i][1] >= tol[i + 1][1] for i in range(len(tol) - 1))

# BREAK: the claim "more correction is always safer". Guide reacts to altitude
# 2 steps old with gain 1.5 against an UPWARD drift.
rb = fly(k=1.5, delay=2)
print(f"BREAK over-correcting guide (gain 1.5, 2-step delay), upward drift: falls to the {rb[0]} at step {rb[1]}; "
      f"lowest altitude {rb[5]:.1f} with {rb[4]} steps in the spray zone before that")
rb0 = fly(k=0.9, delay=2, drift=0.0)
print(f"      gain 0.9, 2-step delay, no drift: falls to the {rb0[0]} at step {rb0[1]}")
for kk in (0.5, 0.9, 1.5):
    r = fly(k=kk, delay=2)
    print(f"      gain {kk}, 2-step delay, drift 2: {r[0]} at step {r[1]}, steps in spray zone {r[4]}")
# more correction is worse than none: over-corrected flyer falls before the abandoned one,
# and it is pushed into the spray zone although the drift is upward
ok &= rb[0] != "SAFE" and rb[1] < r2[1] and rb[4] > 0


# S7/S8: sweep gain x reaction delay, with the drift upward and then flipped downward.
gains = (0.3, 0.5, 0.7, 0.9, 1.2, 1.5, 2.0)
limits = {}
side_counts = {}
for dr in (2.0, -2.0):
    print(f"S{7 if dr > 0 else 8} gain x delay, drift {dr:+.0f}: fall side@step (sea-zone steps)")
    for dl in (0, 1, 2, 3, 4):
        row = []
        for g in gains:
            r = fly(k=g, delay=dl, drift=dr)
            row.append(f"{r[0][:3]}@{r[1] if r[1] is not None else '-'}({r[4]})")
            if dr > 0 and r[0] == "SAFE":
                limits[dl] = g
            if r[0] != "SAFE":
                side_counts[(dr, r[0])] = side_counts.get((dr, r[0]), 0) + 1
        print(f"   delay {dl}: " + "  ".join(f"g{g}:{c}" for g, c in zip(gains, row)))
print("   largest safe gain by delay (drift +2):", {d: limits.get(d) for d in (0, 1, 2, 3, 4)})
print("   falls by side:", dict(sorted(side_counts.items())))
up_sun = side_counts.get((2.0, "SUN"), 0); up_sea = side_counts.get((2.0, "SEA"), 0)
dn_sea = side_counts.get((-2.0, "SEA"), 0); dn_sun = side_counts.get((-2.0, "SUN"), 0)
# Round-2 prediction was that drift would still pick the side for unstable guides; it did not
# (same split either way). Narrowed claim: drift picks the side only for a stable or absent guide.
ra_dn = fly(abandon_at=20, drift=-2.0)
rs_dn = min_width(drift=-2.0)
print(f"   drift -2, guide abandoned at 20: {ra_dn[0]} at step {ra_dn[1]}; stable guide smallest safe width {rs_dn}")
narrow_dn = fly(low=50 - (rs_dn - 1) / 2, high=50 + (rs_dn - 1) / 2, drift=-2.0) if rs_dn else None
print(f"   drift -2, stable guide, band one narrower than safe: {narrow_dn[0] if narrow_dn else None}")
ok &= ra_dn[0] == "SEA" and (narrow_dn is not None and narrow_dn[0] == "SEA")
safe_limits_fall = all((limits.get(a) or 0) >= (limits.get(b) or 0) for a, b in ((0, 1), (1, 2), (2, 3), (3, 4)))
ok &= safe_limits_fall

print(("RESULT: PASS " if ok else "RESULT: FAIL ") +
      f"guided flyer safe in [20,80]; abandoned guide falls to the {r2[0]} at step {r2[1]}; "
      f"smallest safe band {w3} centered vs {w4} biased against drift; tolerated drift shrinks as the band narrows "
      f"({tol[0][1]:.2f} at width {tol[0][0]} to {tol[-1][1]:.2f} at {tol[-1][0]}); "
      f"BREAK: over-correction (gain 1.5, 2-step delay) falls at step {rb[1]}, sooner than no guide, "
      f"after dipping to {rb[5]:.0f} in the spray zone against an upward drift (final fall: {rb[0]}); "
      f"largest safe gain falls with reaction delay {[limits.get(d) for d in (0,1,2,3,4)]}; abandoned or stable guides fall on the drift side "
      f"(drift down: {ra_dn[0]}), but unstable guides split by oscillation phase, not drift "
      f"({up_sun} sun / {up_sea} sea with drift up, {dn_sun} sun / {dn_sea} sea with drift down)")
