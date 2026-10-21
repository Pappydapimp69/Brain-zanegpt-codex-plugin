"""Sandbox: a default FOV lives in a code constant AND in markup that pre-selects a ladder button.
Prediction (written before first run): after retuning the constant 60->75, a cleared profile shows
the markup's old option (60) as selected while the camera uses 75 (mismatch on 1 of 1 empty-prefs
cases, 0 of 2 stored-prefs cases); a literal-number test passes on the stale copy; a copy-vs-copy
test fails; deriving the marked option from the constant gives 0 mismatches. A missing markup copy
(parse -> NaN) poisons a lerp-smoothed camera for every later frame; the brain/E4 extent clamp
hides a FOV drift whenever it binds."""
import math

LADDER = [45, 60, 75, 90]

def markup_static(preselected):            # the second copy of the default
    return {"selected": preselected}

def markup_derived(default):               # derived at render time
    return {"selected": default}

def render(prefs, default, markup):
    """Runtime sync: stored pref wins and toggles the active class; empty prefs leave markup as is."""
    if prefs.get("fov") is not None:
        return prefs["fov"], prefs["fov"]  # (marked option, fov the camera uses)
    return markup["selected"], default

def mismatch(prefs, default, markup):
    marked, used = render(prefs, default, markup)
    return marked != used

# Scenario 1: retune constant 60 -> 75, markup left behind
DEFAULT_OLD, DEFAULT_NEW = 60, 75
stale = markup_static(DEFAULT_OLD)
s1 = [mismatch({}, DEFAULT_NEW, stale),
      mismatch({"fov": 90}, DEFAULT_NEW, stale),
      mismatch({"fov": 75}, DEFAULT_NEW, stale)]
print("S1 stale markup: empty/stored90/stored75 mismatch =", s1)

# Scenario 2: tests. literal assertion vs copy-vs-copy on a cleared profile
literal_test_passes = (stale["selected"] == 60)                  # author edits to whichever copy they see
copy_vs_copy_passes = not mismatch({}, DEFAULT_NEW, stale)
print("S2 literal test passes:", literal_test_passes, "| copy-vs-copy passes:", copy_vs_copy_passes)

# Scenario 3: derived marker never drifts across retunes
s3 = [mismatch({}, d, markup_derived(d)) for d in LADDER]
print("S3 derived mismatches over", LADDER, "=", s3)

# Scenario 4 (BREAK, E1 NaN camera): markup copy missing -> parsed NaN feeds lerp-smoothed camera
def run_camera(first_fov, frames=100, guard=False):
    cam, bad = 60.0, 0
    for f in range(frames):
        target = first_fov if f < 10 else 75.0
        if guard and not math.isfinite(target):
            target = cam
        cam = cam + 0.2 * (target - cam)       # stateful lerp stores whatever it is fed
        bad += not math.isfinite(cam)
    return bad
parsed = float("nan")                           # int('') style failure on a deleted preselect
s4 = (run_camera(parsed), run_camera(parsed, guard=True))
print("S4 NaN frames unguarded/guarded of 100 =", s4)

# Scenario 5 (brain/E4 extent clamp): scale = min(schedule(fov), extent_fit)
def scale(fov, extent_fit):
    return min(fov / 45.0, extent_fit)
hidden = scale(DEFAULT_OLD, 1.0) == scale(DEFAULT_NEW, 1.0)     # clamp binds at 1.0
visible = scale(DEFAULT_OLD, 2.0) != scale(DEFAULT_NEW, 2.0)    # clamp loose
print("S5 drift hidden when clamp binds:", hidden, "| visible when loose:", visible)

ok = (s1 == [True, False, False] and literal_test_passes and not copy_vs_copy_passes
      and not any(s3) and s4 == (100, 0) and hidden and visible)
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      f"drift only on empty prefs {s1}; derived 0 mismatches; NaN frames {s4}; clamp hides drift={hidden}")
