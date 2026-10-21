from collections import Counter
TROPES = ["t%d" % i for i in range(6)]
ENGINES = ["e%d" % i for i in range(8)]
SKELS = 2
ALIAS = {"t5": "t5-alias"}     # the source renames one pattern: same real trope, second label
def build(R, label_of):
    """Greedy: fill engine-skeleton slots; each video takes the engine with fewest uses, the trope label with room under cap R."""
    use = Counter(); eng = Counter(); batch = []
    slots = [(e, s) for s in range(SKELS) for e in ENGINES]
    labels = sorted({label_of(t, k) for t in TROPES for k in (0, 1)})
    for (e, s) in slots:
        cand = [l for l in labels if use[l] < R]
        if not cand: break
        l = min(cand, key=lambda x: (use[x], x)); use[l] += 1; eng[e] += 1; batch.append((e, s, l))
    return batch
def real(l): return l.replace("-alias", "")
def stats(batch):
    e = Counter(b[0] for b in batch); t = Counter(real(b[2]) for b in batch)
    return len(batch), max(e.values()), max(t.values()), len(e)
def lab_plain(t, k): return t
def lab_alias(t, k): return ALIAS[t] if (t in ALIAS and k == 1) else t   # a mixed-source batch uses both labels
out = {}
for R in (1, 2, 3, 6):
    out["plain R=%d" % R] = stats(build(R, lab_plain))
    out["alias R=%d" % R] = stats(build(R, lab_alias))
for k, v in out.items(): print(k, "(size, max engine reuse, max real-trope reuse, engines used)", v)
ceil = lambda R: min(16, 6 * R)
ok = all(out["plain R=%d" % R][0] == ceil(R) for R in (1, 2, 3, 6))
ok = ok and out["plain R=1"][1] == 1 and out["plain R=2"][1] == 2 and out["plain R=3"][1] == 2
ok = ok and out["alias R=1"][2] == 2 and out["plain R=1"][2] == 1 and out["alias R=1"][0] == 7
print("RESULT: %s ceiling min(16,6R) reproduced (6/12/16/16); distinct-engine batches only up to 8 (reuse 1 at size 6, 2 at 12 and 16); a source-renamed trope label lifts the batch 6->7 at R=1 and doubles real-trope reuse 1->2, silently breaking the cap"
      % ("PASS" if ok else "FAIL"))
