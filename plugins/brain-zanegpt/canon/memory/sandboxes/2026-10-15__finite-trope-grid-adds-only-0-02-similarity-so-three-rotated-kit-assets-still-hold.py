# Sandbox: kit rotation (pass-2 model) with the trope and axis slots drawn from the
# FINITE 6x5 grid (slot-machine cell budget) instead of fresh values.
# Slots: 10 kit + game_name, joke, script, voiceover, layout (fresh) + trope(6) + axis(5) = 17.
# PREDICTION (before run): the pass-2 result (3 rotated kit assets -> 0.475 < 0.5)
# does NOT survive a finite trope/axis grid in a 30-video batch: mean similarity
# rises above 0.5; rotating 4 kit assets restores it below 0.5. Hidden assumption:
# trope and axis repeats count as identical slots.
import random, itertools
KIT = 10; FRESH = 5; SLOTS = KIT + FRESH + 2; POOL = 6
def batch(n, rot, seed, grid=True):
    r = random.Random(seed); cells = r.sample(range(30), 30); out = []
    for i in range(n):
        v = [r.randrange(POOL) if k < rot else 0 for k in range(KIT)]
        v += [r.randrange(10**6) for _ in range(FRESH)]
        c = cells[i % 30] if grid else r.randrange(10**6)
        v += [c // 5, c % 5] if grid else [c, c + 1]
        out.append(v)
    return out
def sim(vs):
    s = [sum(x == y for x, y in zip(a, b)) / SLOTS for a, b in itertools.combinations(vs, 2)]
    return sum(s) / len(s)
rows = {}
for label, n, rot, grid in [("A 8 videos, 3 rotated, fresh trope/axis", 8, 3, False),
                            ("B 8 videos, 3 rotated, finite grid", 8, 3, True),
                            ("C BREAK 30 videos, 3 rotated, finite grid", 30, 3, True),
                            ("D 30 videos, 4 rotated, finite grid", 30, 4, True),
                            ("E 30 videos, 6 rotated, finite grid", 30, 6, True)]:
    rows[label[0]] = sum(sim(batch(n, rot, s, grid)) for s in range(20)) / 20   # mean over 20 seeds
    print(f"{label}: {rows[label[0]]:.3f}")
ok = rows["C"] > 0.5 and rows["D"] < 0.5 and rows["E"] < rows["D"]
print(f"RESULT: {'PASS' if ok else 'FAIL'} 30-video batch with 3 rotated kit assets {rows['C']:.3f} (>0.5), 4 rotated {rows['D']:.3f}, 6 rotated {rows['E']:.3f}; fresh-trope 8-video {rows['A']:.3f}, grid 8-video {rows['B']:.3f}")
