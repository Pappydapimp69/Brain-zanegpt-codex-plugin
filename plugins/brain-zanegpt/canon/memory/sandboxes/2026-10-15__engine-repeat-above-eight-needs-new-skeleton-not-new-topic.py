"""Sandbox: engine-first batches repeat an engine once k > 8 (pigeonhole). Does the repeat read as a template?
Entries: ideas:AI-VIDEO/.../every-video-gets-its-own-joke-and-script (new game name in the same template = mass-produced),
fake-ad-kernel-source-check/E1 (use verbatim labels), engine-first-idea-batches/E1 (cap repeats at ceil(k/8)).
Similarity = Jaccard of beat bigrams + voice + layout + endpoint + length (game name excluded), flag at 0.6 (assumed).
PREDICTION (before run): k<=8 max similarity < 0.3; at k=9..16 with ONE skeleton per engine the max pair
similarity is >= 0.9 (same engine = same beats) and the repeat is flagged from k=9; with TWO fully distinct skeletons per
engine the max stays < 0.3 up to k=16 and the repeat reappears (3 per engine, flagged) at k=17; BREAK: a 'variant'
skeleton that changes only ONE beat of five gets similarity >= 0.6 (still flagged) so a nearly-same skeleton does not
cure the repeat. Assumption: repeated engine implies shared skeleton. Wrong if one-beat-variant sim < 0.6."""
import itertools
ENG = ["escalation", "literalism", "role_reversal", "anticlimax", "callback", "genre_switch", "misdirection", "deadpan_restraint"]
def skel(e, v):   # variant 0 / 1 = fully distinct beats; 'near' = variant 0 with ONE beat swapped
    base = [f"{e}_{i}" for i in range(5)]
    if v == 0: return base, "vo_" + e, "L_" + e, "end_" + e
    if v == "near": return base[:2] + ["alt"] + base[3:], "vo_" + e, "L_" + e, "end_" + e
    return [f"{e}_v{v}_{i}" for i in range(5)], f"vo_{e}_v{v}", f"L_{e}_v{v}", f"end_{e}_v{v}"
def feats(b, vo, lay, end):
    return {("bg", x, y) for x, y in zip(b, b[1:])} | {("v", vo), ("l", lay), ("e", end), ("n", len(b))}
def sim(a, b): return len(a & b) / len(a | b)
def batch(k, variants):
    out = []
    for i in range(k):
        e = ENG[i % 8]; rep = i // 8
        v = variants[rep % len(variants)] if rep else 0
        out.append((e, feats(*skel(e, v))))
    return out
def stats(bt):
    mx = max(sim(a[1], b[1]) for a, b in itertools.combinations(bt, 2)) if len(bt) > 1 else 0
    same = [sim(a[1], b[1]) for a, b in itertools.combinations(bt, 2) if a[0] == b[0]]
    return mx, (max(same) if same else 0)
rows = {}
for name, vs in (("one skeleton", [0]), ("two distinct", [0, 1]), ("near-variant", [0, "near"])):
    for k in (8, 9, 16, 17):
        # for two distinct skeletons, 3rd repeat (k=17) has to reuse variant 0 or 1: variants cycle by repetition index
        bt = batch(k, vs if name != "two distinct" else [0, 1, 0]) if name == "two distinct" else batch(k, vs)
        if name == "two distinct": bt = [(e, feats(*skel(e, (i // 8) % 2))) for i, (e, _) in enumerate(bt)]
        if name == "near-variant": bt = [(e, feats(*skel(e, "near" if i // 8 == 1 else 0))) for i, (e, _) in enumerate(bt)]
        rows[(name, k)] = stats(bt)
        print("%-13s k=%2d max-sim %.2f  max same-engine sim %.2f  flagged %s" % (name, k, rows[(name, k)][0], rows[(name, k)][1], rows[(name, k)][0] >= 0.6))
ok = (rows[("one skeleton", 8)][0] < 0.3 and rows[("one skeleton", 9)][0] >= 0.9 and rows[("two distinct", 16)][0] < 0.3
      and rows[("two distinct", 17)][0] >= 0.9 and rows[("near-variant", 16)][0] >= 0.6)
print("RESULT: %s k=8 %.2f; one skeleton k=9 %.2f; two distinct k=16 %.2f, k=17 %.2f; one-beat variant k=16 %.2f"
      % ("PASS" if ok else "FAIL", rows[("one skeleton", 8)][0], rows[("one skeleton", 9)][0], rows[("two distinct", 16)][0], rows[("two distinct", 17)][0], rows[("near-variant", 16)][0]))
