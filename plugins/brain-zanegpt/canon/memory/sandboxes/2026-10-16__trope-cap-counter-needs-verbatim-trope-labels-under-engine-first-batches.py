# Engine-first batch (8 engines x 2 skeletons = 16 slots) with a per-trope cap R=2 (6 tropes -> ceiling 12).
# A cap counter keyed on free-text trope labels vs a closed verbatim list. Seeded, stdlib only.
import random
TROPES = ["pin pull", "fake level", "soap drama", "makeover", "celebrity", "popular externalization"]
PARA = {"popular externalization": "borrowed fame"}  # the real paraphrase drift from the kernel check
def alt(t): return PARA.get(t, t + " (reworded)")
def run(k, R, p, verbatim, seed):
    rng = random.Random(seed); true = {}; seen = {}; made = 0; eng = {}
    for i in range(k):
        e = i % 8; t = rng.choice(TROPES)
        label = t if (verbatim or rng.random() >= p) else alt(t)
        if verbatim and label not in TROPES: continue
        # counter keyed on the label string actually written
        if seen.get(label, 0) >= R: # redraw once to a trope under cap per the counter
            ok = [x for x in TROPES if seen.get(x, 0) < R]
            if not ok: break
            t = rng.choice(ok); label = t if (verbatim or rng.random() >= p) else alt(t)
        seen[label] = seen.get(label, 0) + 1; true[t] = true.get(t, 0) + 1
        eng[e] = eng.get(e, 0) + 1; made += 1
    return made, max(true.values()) > R, max(eng.values())
N = 2000
def rate(k, R, p, v):
    r = [run(k, R, p, v, s) for s in range(N)]
    return sum(x[1] for x in r) / N, max(x[2] for x in r), sum(x[0] for x in r) / N
res = {}
for name, (k, p, v) in {"free p0.0 k12": (12, 0.0, False), "free p0.3 k12": (12, 0.3, False),
                        "free p0.6 k12": (12, 0.6, False), "verbatim p0.6 k12": (12, 0.6, True),
                        "verbatim k16 (past ceiling)": (16, 0.0, True)}.items():
    res[name] = rate(k, 2, p, v)
    print(name, "true-cap-breach=%.3f max-engine-repeat=%d made=%.2f" % res[name])
ok = (res["free p0.0 k12"][0] == 0 and res["free p0.3 k12"][0] > 0.1 and res["verbatim p0.6 k12"][0] == 0
      and res["free p0.3 k12"][1] <= 2 and res["verbatim k16 (past ceiling)"][2] < 16 + 1)
print("RESULT: %s breach free p0 %.3f p.3 %.3f p.6 %.3f verbatim %.3f; engine repeat max %d; k16 made %.2f of 16 (ceiling 12)" % (
    "PASS" if ok else "FAIL", res["free p0.0 k12"][0], res["free p0.3 k12"][0], res["free p0.6 k12"][0],
    res["verbatim p0.6 k12"][0], res["free p0.3 k12"][1], res["verbatim k16 (past ceiling)"][2]))
