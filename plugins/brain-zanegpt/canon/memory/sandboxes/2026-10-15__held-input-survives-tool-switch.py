"""A brush tool applied every tick while 'down'. An autopilot (or a player holding a finger) switches the tool
from a long guard to a short one. If 'down' and the pointer position survive the switch for one tick,
the new tool is applied at the old position. Deterministic, stdlib only."""
R = 3
def run(release_on_switch, ticks_before_move=1):
    zone_a = {(x, y): 19 for x in range(0, 6) for y in range(0, 6)}      # cut with the long guard, wants 19
    ptr, down, guard = (2, 2), True, 19
    def apply():
        n = 0
        for (x, y), v in zone_a.items():
            if (x - ptr[0]) ** 2 + (y - ptr[1]) ** 2 <= R * R and v > guard: zone_a[(x, y)] = guard; n += 1
        return n
    apply()                                   # last stroke in zone A with the long guard
    guard = 3                                 # switch to the short guard
    if release_on_switch: down = False
    wrong = 0
    for _ in range(ticks_before_move):        # the tick(s) before the pointer moves to zone B
        if down: wrong += apply()
    return wrong
ok = True
for rel, ticks, note in [(False, 1, 'down survives switch, 1 tick'), (False, 3, 'down survives switch, 3 ticks'), (True, 1, 'release on switch'), (True, 3, 'release on switch, 3 ticks')]:
    w = run(rel, ticks); print(f"{note:32s} strands wrongly cut short: {w}")
    ok &= (w > 0) if not rel else (w == 0)
print("RESULT: PASS a held 'down' that survives a tool switch applies the new tool at the old spot (27 strands); releasing on switch cuts 0" if ok else "RESULT: FAIL")
