"""Sandbox: slot-machine cells (trope x axis) rotated without replacement; two cells on the SAME trope share a
5-beat skeleton and differ only by the beat their axis swaps. Entries: ideas:COMEDY/fake-mobile-ad/premise-slot-machine-
from-the-five-misleading-ad-patterns (pick a trope, swap one thing), fake-ad-kernel-source-check/E1 (axis labels verbatim),
engine-repeat-above-eight-needs-new-skeleton-not-new-topic/E1 (one-beat variant scored 0.60, right at the flag line).
Similarity = Jaccard of beat bigrams + voice + layout + endpoint + length, flag at 0.6 (same assumed model as that entry).
PREDICTION (before first run): the one-beat-variant 0.60 depends on WHICH beat the axis swaps: a swap at beat 0 or 4
(edge) breaks one bigram and scores about 0.78 (flagged), a swap at beats 1-3 (middle) breaks two and scores 0.60 (on the
line); if the swap also changes the endpoint (beat 4) the score drops to 0.60 or below. Assumption: the swap beat is a
free choice; it is wrong if edge and middle swaps score the same. BREAK: an axis label that is not verbatim ('borrowed
fame') cannot be mapped to a swap beat, so 1 of 5 axes would be unresolved. Scenario also: batch of 7 distinct cells,
the pigeonhole point where a trope must repeat, scored with the real axis->beat map."""
import itertools
AXES = ["gameplay disguise", "narrative pretense", "popular externalization", "ruleset distortion", "incentive illusion"]
BEAT = {"gameplay disguise": 0, "narrative pretense": 1, "popular externalization": 2, "ruleset distortion": 3, "incentive illusion": 4}
TROPES = ["pull-the-pin", "incompetent-player", "number-gates", "save-the-sad-man", "merge-bait", "stilted-skit"]
def feats(trope, swap=None, axis=None):
    b = [f"{trope}_{i}" for i in range(5)]
    end = "end_" + trope
    if swap is not None:
        b[swap] = f"{trope}_{axis}_{swap}"
        if swap == 4: end = f"end_{trope}_{axis}"
    return {("bg", x, y) for x, y in zip(b, b[1:])} | {("v", "vo_" + trope), ("l", "L_" + trope), ("e", end), ("n", 5)}
def sim(a, b): return len(a & b) / len(a | b)
base = feats("pull-the-pin")
by_pos = {p: round(sim(feats("pull-the-pin", p, "x"), base), 3) for p in range(5)}
print("one-beat variant vs base, by swapped beat:", by_pos)
pair = {}
for a, b in itertools.combinations(AXES, 2):
    pair[(a, b)] = sim(feats("pull-the-pin", BEAT[a], a), feats("pull-the-pin", BEAT[b], b))
print("same-trope distinct-axis pairs: min %.3f max %.3f mean %.3f flagged(>=0.6) %d/10" %
      (min(pair.values()), max(pair.values()), sum(pair.values()) / 10, sum(v >= 0.6 for v in pair.values())))
# batch of 7 distinct cells: first 6 one per trope, the 7th repeats trope 0 with a new axis
cells = [(TROPES[i], AXES[i % 5]) for i in range(6)] + [(TROPES[0], AXES[3])]
fs = [feats(t, BEAT[a], a) for t, a in cells]
mx = max(sim(x, y) for x, y in itertools.combinations(fs, 2))
mx6 = max(sim(x, y) for x, y in itertools.combinations(fs[:6], 2))
print("k=6 one per trope max %.3f; k=7 (trope repeat, distinct cell) max %.3f" % (mx6, mx))
unresolved = sum(1 for a in ["gameplay disguise", "narrative pretense", "borrowed fame", "ruleset distortion", "incentive illusion"] if a not in BEAT)
print("kernel-as-written axis labels unresolved:", unresolved)
edge = (by_pos[0] + by_pos[4]) / 2; mid = sum(by_pos[p] for p in (1, 2, 3)) / 3
ok = edge > mid + 0.05 and by_pos[4] <= by_pos[0] and mx6 < 0.3 and mx >= 0.5 and unresolved == 1
print("RESULT: %s edge-swap mean %.3f vs middle-swap %.3f; k=6 max %.3f, k=7 max %.3f; unresolved kernel labels %d"
      % ("PASS" if ok else "FAIL", edge, mid, mx6, mx, unresolved))
