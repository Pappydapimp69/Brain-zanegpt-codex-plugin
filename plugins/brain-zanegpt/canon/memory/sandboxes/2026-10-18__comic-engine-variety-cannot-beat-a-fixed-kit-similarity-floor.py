# 16 slots/video: 10 kit assets, 2 topic slots (name, trope: always fresh), 4 engine-tied slots (joke, script, voiceover, layout).
# Engine-tied slots all take the video's comic-engine id. 8 videos; engines assigned round-robin over E engines.
# Kit: k of 10 assets rotate through a pool of 6 variants by video index (k=0 fixed kit).
from itertools import combinations
def video(i, E, k):
    kit = [(j if j < k else 0) * 0 + ((i % 6) if j < k else 0) for j in range(10)]
    topic = [("name", i), ("trope", i)]
    eng = [i % E] * 4
    return kit + [x[1] for x in topic] + eng
def batch_sim(E, k, n=8):
    vs = [video(i, E, k) for i in range(n)]
    sims = [sum(a == b for a, b in zip(u, v)) / 16 for u, v in combinations(vs, 2)]
    # topic slots are unique per video by construction (i differs) -> they never match
    return sum(sims) / len(sims)
print("engines E | kit rotated k=0 | k=3 | k=6")
tab = {}
for E in (1, 2, 4, 8):
    row = [batch_sim(E, k) for k in (0, 3, 6)]; tab[E] = row
    print(f"E={E}: " + " ".join(f"{x:.3f}" for x in row))
floor = 10/16
ok = all(tab[E][0] >= floor - 1e-9 for E in tab) and tab[8][0] < tab[1][0] and tab[8][1] < 0.5 and tab[1][1] >= 0.5 - 1e-9 + 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} fixed kit floor {floor:.3f}: E=1 {tab[1][0]:.3f} -> E=8 {tab[8][0]:.3f} (engine variety alone); with 3 kit rotated E=1 {tab[1][1]:.3f}, E=8 {tab[8][1]:.3f}")
