# Sandbox: 60 one-second windows of a film score. Windows 20-29 are INTENTIONAL silence (no scheduled notes).
# Fault A: scene with windows 40-49 names an unknown mode, so the live player silently drops its notes.
# Fault B: a voice cap that never releases offline drops every note after the 30th sounded note.
# Detectors: (1) build-time config-key check against the engine table; (2) naive silent-window count;
#            (3) schedule-aware scan: flag windows that have scheduled notes but rendered level below 1% of median.
# Run 1 prediction (partly missed: I left 'phrygian' in the config of every case so the key check always fired, and the median-relative
# threshold collapsed to 0 once over half the windows were silent, so fault B flagged 0 windows): key check finds fault A (1 of 2 faults, 0 of fault B windows); naive silent count
# flags 10 intentional + dropped windows = 10 false positives; schedule-aware scan flags exactly the dropped
# windows with 0 false positives: A 10 windows, B = windows after the cap. BREAK: clean score (no fault) -> all three report 0
# real problems, schedule-aware scan 0 flags (naive still counts the 10 intentional silences).
# Run 2 prediction (after run 1): config holds 'phrygian' only when fault A is on; the threshold is 1% of the level the schedule
# expects (0.3 per note, so 0.6 for 2 notes), not of the rendered median. Key check: ['phrygian'] only for A; schedule-aware scan:
# A=10, B=35 (cap hit after 15 two-note windows: windows 15-19 plus 30-59), both=35 (A's windows fall inside B's), clean=0.
# Median-relative naive scan reports 0 for B because over half the windows are then silent.
TABLE = {"ionian", "dorian", "lydian", "mixolydian", "aeolian"}
scene_modes = {range(0, 20): "dorian", range(20, 30): None, range(30, 40): "lydian", range(40, 50): "PH", range(50, 60): "aeolian"}
sched = [0 if 20 <= w < 30 else 2 for w in range(60)]            # notes scheduled per window

def render(fault_a, fault_b):
    scene_modes[range(40, 50)] = "phrygian" if fault_a else "aeolian"
    level, sounded = [], 0
    for w in range(60):
        ok = 1.0
        mode = next(m for r, m in scene_modes.items() if w in r)
        if fault_a and mode == "phrygian": ok = 0.0
        out = 0.0
        for _ in range(sched[w]):
            if ok and not (fault_b and sounded >= 30): out += 0.3; sounded += 1
        level.append(out)
    return level

def detect(level, modes):
    key = sorted({m for m in modes.values() if m and m not in TABLE})
    med = sorted(level)[len(level) // 2]
    naive = [w for w in range(60) if level[w] < 0.01 * med]
    aware = [w for w in range(60) if sched[w] and level[w] < 0.01 * 0.3 * sched[w]]
    return key, naive, aware

res = {}
for name, (a, b) in {"fault A only": (1, 0), "fault B only": (0, 1), "both": (1, 1), "clean (BREAK)": (0, 0)}.items():
    key, naive, aware = detect(render(a, b), scene_modes); res[name] = (key, len(naive), len(aware))
    print(name, "key_check=%s naive_silent=%d schedule_aware=%d" % (key, len(naive), len(aware)))
ok = (res["fault A only"] == (["phrygian"], 20, 10) and res["fault B only"][0] == [] and res["fault B only"][2] == 35
      and res["both"][2] == 35 and res["clean (BREAK)"] == ([], 10, 0))
print("RESULT: %s key check sees fault A only; schedule-aware scan finds A=%d and B=%d dropped windows with 0 false alarms; median-relative naive scan reports %d for B"
      % ("PASS" if ok else "FAIL", res["fault A only"][2], res["fault B only"][2], res["fault B only"][1]))
