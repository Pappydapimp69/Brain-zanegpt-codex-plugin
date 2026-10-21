import random
# Composition: vary-the-comic-engine (engine rotation), fake-ad-kernel-source-check (label audit),
# batch-ceiling-trope-cap (batch <= min(16 skeletons, 6*cap)).
TROPES = ["pin-pull","soap","makeover","celebrity","number-gate","fail"]
ENGINES = ["deadpan","escalation","misdirect","callback","anticlimax","literalism","understatement","non-sequitur"]
SKELETONS = [(e, i) for e in ENGINES for i in range(2)]  # 16 engine-skeleton slots
SOURCE = ["popular externalization","social proof","false urgency","fake gameplay","bait-and-switch"]
KERNEL = ["borrowed fame","social proof","false urgency","fake gameplay","bait-and-switch"]  # 1/5 renamed

def build(cap, rotate, seed=1):
    rng = random.Random(seed)
    used = {t:0 for t in TROPES}; out = []; last = None
    slots = SKELETONS[:]; rng.shuffle(slots)
    for _ in range(40):  # request more than possible
        cands = [t for t in TROPES if used[t] < cap]
        if not cands or not slots: break
        t = cands[len(out) % len(cands)]
        if rotate:
            s = next((x for x in slots if x[0] != last), slots[0])
        else:
            s = next((x for x in slots if x[0] == (last or x[0])), slots[0])
        slots.remove(s); last = s[0]; used[t] += 1; out.append((t, s[0]))
    return out

def max_run(b):
    best = run = 0; prev = None
    for _, e in b:
        run = run + 1 if e == prev else 1; prev = e; best = max(best, run)
    return best

res = {}
for cap in (1, 2, 3):
    b = build(cap, True); res[cap] = len(b)
    print("cap", cap, "batch", len(b), "expected", min(16, 6*cap), "max engine run", max_run(b))
exp = {1:6, 2:12, 3:16}
ok_ceiling = res == exp
# Scenario 4: no rotation -> same engine streaks (the formula the user spotted)
nr = max_run(build(2, False)); wr = max_run(build(2, True))
print("cap2 max run no-rotate", nr, "rotate", wr)
# Scenario 5 (break attempt): label audit - numbers match but labels must be checked
bad = [(k, s) for k, s in zip(KERNEL, SOURCE) if k != s]
print("label mismatches", len(bad), bad)
ok = ok_ceiling and wr == 1 and nr > 1 and len(bad) == 1
print(("RESULT: PASS" if ok else "RESULT: FAIL"), "ceilings", res, "engine run rotate/no-rotate", wr, nr, "label mismatches", len(bad))
