# Prediction (before run): with F=200 files, 5 trunk commits/day (3 files each) and a branch editing 3 files/day,
# 3-way conflicts per merge grow ~quadratically in branch lifetime L (0.25d -> <0.1, 20d -> >30% of pool, saturating),
# amortized conflicts per branch-day rise with L; a 100000-file pool shows ~0 at any L (mechanism needs overlap);
# rebase replays k same-file commits as up to k conflicts vs 1 for merge; a squash-landed prefix makes a plain merge
# conflict on every prefix file that trunk later edited, while patch-id-aware rebase drops them (0 phantom).
SEEDS = range(1, 21)
def lcg(seed):
    x = seed * 2654435761 % 2**32
    while True:
        x = (1103515245 * x + 12345) % 2**31
        yield x
def pick(g, F):
    # hot-skew: 50% of edits land in the hottest 10% of files
    r = next(g); r2 = next(g)
    return (r2 % max(1, F // 10)) if r % 2 == 0 else (r2 % F)
def conflicts_at_merge(L, F, seed, trunk_rate=5, files_per=3, branch_rate=3):
    g = lcg(seed)
    trunk, branch = {}, {}
    for i in range(int(round(trunk_rate * L))):
        for _ in range(files_per): trunk[pick(g, F)] = f"t{i}"
    for i in range(max(1, int(round(branch_rate * L)))):
        branch[pick(g, F)] = f"b{i}"
    return sum(1 for f in branch if f in trunk)      # base same for all: both sides changed, contents differ
def avg(L, F): return sum(conflicts_at_merge(L, F, s) for s in SEEDS) / len(SEEDS)
LS = [0.25, 1, 2, 5, 10, 20]
small = {L: avg(L, 200) for L in LS}
big = {L: avg(L, 100000) for L in LS}
for L in LS: print(f"L={L:>5}d conflicts/merge F=200: {small[L]:.2f} (per branch-day {small[L]/L:.2f})  F=100000: {big[L]:.2f}")
# merge vs rebase: one line of a file; trunk changed it to "T". Branch commits are (parent -> new) edits of that line.
def merge_conf(commits, base="v0"):
    net = commits[-1][1]
    return 1 if net != base and net != "T" else 0         # 3-way on the net result only
def rebase_conf(commits):
    tip, n = "T", 0
    for parent, new in commits:
        if tip != parent: n += 1                           # replayed commit does not apply onto trunk's version; resolve
        tip = new                                          # resolution keeps the commit's content
    return n
mono = [("v0", "b0"), ("b0", "b1"), ("b1", "b2"), ("b2", "b3")]        # keeps editing the same line
revert = [("v0", "b0"), ("b0", "v0")]                                   # edits then reverts: net change zero
print("monotone 4 commits -> merge", merge_conf(mono), "rebase", rebase_conf(mono))
print("edit-then-revert -> merge", merge_conf(revert), "rebase", rebase_conf(revert))
# phantom conflicts after a squash-landed prefix (opticon E7 shape): m of k commits already landed as one squash,
# trunk then edited those files again
def phantom(m, trunk_edits_after):
    prefix = {f"p{i}": f"b{i}" for i in range(m)}
    trunk = dict(prefix)                                      # squash lands identical content
    for i in range(trunk_edits_after): trunk[f"p{i}"] = f"t{i}"
    base = {f: "v0" for f in prefix}
    merge = sum(1 for f in prefix if prefix[f] != base[f] and trunk[f] != base[f] and prefix[f] != trunk[f])
    rebase = 0                                                # patch-id equal commits are dropped before replay
    return merge, rebase
ph = phantom(6, 4); ph0 = phantom(6, 0)
print("squash prefix 6, trunk edits 4 files after -> merge, rebase", ph, "; no later trunk edits ->", ph0)
import math
slope_dense = math.log(small[10] / small[1]) / math.log(10)
slope_sparse = math.log(big[20] / big[5]) / math.log(4)
print(f"log-log slope of conflicts vs lifetime: dense hot set {slope_dense:.2f}, sparse overlap {slope_sparse:.2f}")
ok = (small[0.25] < 0.15 and 0.9 < slope_dense < 1.3 and slope_sparse > 1.5 and big[1] < 0.05
      and small[20] > 100 * small[0.25] and merge_conf(mono) == 1 and rebase_conf(mono) == 1
      and merge_conf(revert) == 0 and rebase_conf(revert) == 1 and ph == (4, 0) and ph0 == (0, 0))
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
 f"conflicts/merge F=200 L=.25d {small[0.25]:.2f} 1d {small[1]:.2f} 10d {small[10]:.1f} 20d {small[20]:.1f} (slope {slope_dense:.2f}, linear not quadratic); F=1e5 slope {slope_sparse:.2f}, 20d {big[20]:.2f}; rebase vs merge monotone 1 vs 1, edit-revert 1 vs 0; squash-prefix phantom merge {ph[0]} vs rebase {ph[1]}")
