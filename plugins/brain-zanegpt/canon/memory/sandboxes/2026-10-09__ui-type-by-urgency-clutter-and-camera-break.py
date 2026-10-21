"""Prediction (before run): with a 3-tick deadline for four urgent health events, the non-diegetic readout is
on time 4/4 at every camera script when clutter is 0; the diegetic readout misses whenever the camera looks away;
meta is always on time but resolves only 3 bins so it misreads the 35 event (heal needed); the urgency rule breaks
for non-diegetic once always-on clutter reaches ~14 elements (unless contextual fade hides irrelevant ones);
a hue-only meta cue gives a colour-blind viewer 0 correct decisions, a hue+vignette-width cue restores them.
Deterministic: scripted yaw, no RNG, no real time. Stdlib only."""
EVENTS = [(5, 70), (15, 50), (25, 35), (35, 20)]   # (tick, health after hit); correct heal iff health < 40
DEADLINE = 3.0
NEED = [h < 40 for _, h in EVENTS]

def yaw_script(kind, t):
    return {"facing": 0, "away": 120, "sweep": (t * 37) % 360 - 180, "away_then_back": 120 if t % 10 < 6 else 0}[kind]

def meta_bin(h): return "ok" if h >= 60 else "hurt" if h >= 30 else "crit"

def read_time(kind, ev_t, yaw, clutter):
    """first fractional time at which the player has the value, or None if never within horizon."""
    for t in range(ev_t, ev_t + 20):
        y = abs(yaw(t))
        if kind == "nondiegetic":   return t + 1 + 0.2 * clutter
        if kind == "meta":          return t + 0
        if kind == "diegetic" and y <= 45:   return t + 1
        if kind == "spatial" and y <= 90:    return t + 1 + 0.2 * clutter
    return None

def run(kind, cam, clutter=0, cb=False, shape_cue=False):
    ontime = right = 0
    for (ev_t, h), need in zip(EVENTS, NEED):
        rt = read_time(kind, ev_t, lambda t: yaw_script(cam, t), clutter)
        ok = rt is not None and rt - ev_t <= DEADLINE
        ontime += ok
        if not ok: continue
        if kind == "meta":
            if cb and not shape_cue: continue                  # hue-only cue unreadable to this viewer
            heal = meta_bin(h) == "crit"
        else: heal = h < 40
        right += heal == need
    return ontime, right

res = {}
print("S1 type x camera (on-time/4, right-decision/4), clutter 0")
for kind in ("nondiegetic", "diegetic", "spatial", "meta"):
    row = {cam: run(kind, cam) for cam in ("facing", "away", "sweep", "away_then_back")}
    res[kind] = row; print(f"  {kind:12s}", row)
nd_all = all(v == (4, 4) for v in res["nondiegetic"].values())
dg_miss = res["diegetic"]["away"][0] < 4 and res["diegetic"]["facing"][0] == 4
meta_bin_err = all(v[0] == 4 and v[1] == 3 for v in res["meta"].values())
print("S2 BREAK clutter on the non-diegetic readout (facing camera)")
cl = {c: run("nondiegetic", "facing", clutter=c) for c in (0, 6, 10, 14)}
faded = run("nondiegetic", "facing", clutter=1)
print("  always-on clutter ->", cl, "| contextual fade (1 shown) ->", faded)
break_at = [c for c, v in cl.items() if v[0] < 4]
print("S3 colour-blind viewer on meta: hue-only", run("meta", "facing", cb=True), "| hue+vignette width", run("meta", "facing", cb=True, shape_cue=True))
cb_zero = run("meta", "facing", cb=True)[1] == 0 and run("meta", "facing", cb=True, shape_cue=True)[1] == 3
ok = nd_all and dg_miss and meta_bin_err and break_at == [14] and faded == (4, 4) and cb_zero
print("RESULT:", "PASS" if ok else "FAIL",
      f"non-diegetic 4/4 at all cameras; diegetic away {res['diegetic']['away']}; meta right 3/4 (35-bin); clutter breaks non-diegetic at {break_at}; fade restores {faded}; hue-only cb right {run('meta','facing',cb=True)[1]}/4")
