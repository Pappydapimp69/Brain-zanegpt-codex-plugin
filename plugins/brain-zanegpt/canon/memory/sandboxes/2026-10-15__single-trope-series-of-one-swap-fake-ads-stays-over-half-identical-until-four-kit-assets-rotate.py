"""Sandbox: one-trope-one-swap fake-ad premises (kernel) inside a reusable kit
(template-similarity E1) with axis labels checked against the source list
(source-check E1). Pure stdlib, deterministic.

Video = 16 slots: 10 kit assets, 4 trope-unique feature slots, 1 joke, 1 script.
A swap replaces one trope feature with an absurd value from a pool of 20.
Readable = at least 2 of 4 trope features untouched (brain-creative-training E6),
so at most 2 swaps per video. Batch similarity = mean share of identical slots
over all pairs of 8 videos. Flag line 0.5 (assumption carried from E1).
"""
import random, itertools

KIT, FEAT, POOL, VARIANTS, NVID, TRIALS = 10, 4, 20, 6, 8, 3000
TROPES = ["pin-pull", "fail-player", "number-gates", "help-him", "merge-bait", "live-skit"]
KERNEL_AXES = ["gameplay disguise", "narrative pretense", "borrowed fame",
               "ruleset distortion", "incentive illusion"]
SOURCE_AXES = ["gameplay disguise", "narrative pretense", "popular externalization",
               "ruleset distortion", "incentive illusion"]  # psu.edu 2025-01-13, per source-check E1

def video(rng, trope, swaps, rotated, vid_id, axes):
    kit = [("kit", i, rng.randrange(VARIANTS) if i < rotated else 0) for i in range(KIT)]
    feats = [(trope, j) for j in range(FEAT)]
    for j in rng.sample(range(FEAT), swaps):
        feats[j] = ("absurd", rng.randrange(POOL))
    axis = rng.choice(axes)
    readable = FEAT - swaps >= 2
    return kit + feats + [("joke", vid_id), ("script", vid_id)], axis, readable

def batch_sim(rng, trope_mode, swaps, rotated, axes=KERNEL_AXES):
    vids, labels, ok = [], [], True
    start = rng.randrange(len(TROPES))
    for v in range(NVID):
        t = TROPES[start] if trope_mode == "single" else TROPES[(start + v) % len(TROPES)]
        s, a, r = video(rng, t, swaps, rotated, v, axes)
        vids.append(s); labels.append(a); ok = ok and r
    sims = [sum(x == y for x, y in zip(p, q)) / len(p) for p, q in itertools.combinations(vids, 2)]
    return sum(sims) / len(sims), labels, ok

def run(name, trope_mode, swaps, rotated, seed):
    rng = random.Random(seed)
    tot, untrace, nlab, readable = 0.0, 0, 0, True
    for _ in range(TRIALS):
        s, labels, ok = batch_sim(rng, trope_mode, swaps, rotated)
        tot += s; readable &= ok
        untrace += sum(l not in SOURCE_AXES for l in labels); nlab += len(labels)
    m = tot / TRIALS
    print(f"{name:52s} sim={m:.3f} readable={readable} untraceable_labels={untrace/nlab:.3f}")
    return m, readable, untrace / nlab

r = {}
r["S1"] = run("S1 single trope, kit fixed, 1 swap (kernel as written)", "single", 1, 0, 1)
r["S2"] = run("S2 single trope, kit fixed, 2 swaps (readable max)", "single", 2, 0, 2)
r["S3"] = run("S3 BREAK single trope, 2 swaps, 3 kit rotated (E1 fix)", "single", 2, 3, 3)
r["S4"] = run("S4 single trope, 2 swaps, 4 kit rotated", "single", 2, 4, 4)
r["S5"] = run("S5 single trope, 1 swap, 4 kit rotated", "single", 1, 4, 5)
r["S6"] = run("S6 trope rotated, 1 swap, kit fixed", "rotate", 1, 0, 6)
r["S7"] = run("S7 trope rotated, 1 swap, 3 kit rotated", "rotate", 1, 3, 7)
r["S8"] = run("S8 3 swaps (over the readable cap)", "single", 3, 0, 8)

traced = sum(a in SOURCE_AXES for a in KERNEL_AXES)
print(f"kernel axis labels found verbatim in source list: {traced}/5")

# Predictions written before the first run
checks = {
    "S1 in 0.72-0.80": 0.72 <= r["S1"][0] <= 0.80,
    "S2 in 0.65-0.72": 0.65 <= r["S2"][0] <= 0.72,
    "S3 stays over 0.5 (E1 fix insufficient for single-trope series)": r["S3"][0] > 0.5,
    "S7 under 0.5": r["S7"][0] < 0.5,
    "S8 unreadable": r["S8"][1] is False,
    "labels 4/5 traceable": traced == 4,
}
for k, v in checks.items():
    print(("ok  " if v else "MISS"), k)
n = sum(checks.values())
print(f"RESULT: {'PASS' if n == len(checks) else 'FAIL'} {n}/{len(checks)} checks; single-trope 1 swap {r['S1'][0]:.3f}, 2 swaps {r['S2'][0]:.3f}, "
      f"+3 kit rotated {r['S3'][0]:.3f}, +4 rotated {r['S4'][0]:.3f}; trope rotated+3 kit {r['S7'][0]:.3f}")
