# Sandbox: does a power that only changes the PARTNER's world make a gate
# structurally co-op (no solo route), where a self-targeted or shared power does not?
# Deterministic BFS over a 1-D vertical gate: stand on ground (0), the ledge (G),
# or pins. A jump reaches up to JUMP higher. A pin goes at any height up to
# caster height + REACH. Pins are usable by: 'partner' -> the non-caster only,
# 'self' -> the caster only, 'shared' -> anyone. No RNG, no timing.
from collections import deque

JUMP, REACH, PIN_MAX = 3, 3, 2

def solvable(G, target, players):
    start = (tuple([0] * players), ())
    seen, q = {start}, deque([start])
    while q:
        hs, pins = q.popleft()
        if any(h == G for h in hs):
            return True
        for i, h in enumerate(hs):
            usable = [p for (p, c) in pins if
                      (target == 'shared') or (target == 'self' and c == i) or
                      (target == 'partner' and c != i)]
            stands = {0, G, *usable}
            for s in stands:                      # move: jump up or drop down
                if s <= h + JUMP and s != h:
                    nh = list(hs); nh[i] = s
                    st = (tuple(nh), pins)
                    if st not in seen: seen.add(st); q.append(st)
            if len(pins) < PIN_MAX:               # place a pin
                for p in range(1, h + REACH + 1):
                    if p == G or any(pp == p for pp, _ in pins): continue
                    st = (hs, tuple(sorted(pins + ((p, i),))))
                    if st not in seen: seen.add(st); q.append(st)
    return False

cases = [
    ("1 partner-targeted, gate 5", 5, 'partner', False, True),
    ("2 self-targeted, gate 5",    5, 'self',    True,  True),
    ("3 shared, gate 5",           5, 'shared',  True,  True),
    ("4 BREAK partner-targeted, gate 3 (layout leak)", 3, 'partner', True, True),
    ("5 partner-targeted, gate 8 (pin budget caps duo reach)", 8, 'partner', False, False),
]
ok = True
for name, G, tgt, want_solo, want_duo in cases:
    solo, duo = solvable(G, tgt, 1), solvable(G, tgt, 2)
    good = (solo == want_solo) and (duo == want_duo)
    ok &= good
    print(f"{name}: solo={solo} duo={duo} {'ok' if good else 'MISMATCH'}")
print("RESULT: PASS partner-targeted powers block every solo route only when the gate exceeds the solo jump (gate 5: solo=False duo=True); self/shared powers and a 3-high gate leak a solo route; gate 8 is unsolvable even as a duo with PIN_MAX 2"
      if ok else "RESULT: FAIL see mismatches above")
