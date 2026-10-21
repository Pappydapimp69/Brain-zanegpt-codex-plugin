# Rebuild of: one stray merge (unrhymed line joins a group, or two groups merge) flips the open/stable verdict in a large
# share of single collapses, incl. XXAA->XAAA (open->stable) and ABBA->AAAA, while max closure distance barely moves.
# Own verdict rule (written before running): stable iff at most 1 unrhymed line AND every rhyme group is contiguous
# (no group encloses or interleaves another); otherwise open. Own enumeration: every merge of two blocks of every one
# of the 15 set partitions of 4 lines, deduplicated by (before, after) scheme pair.
from itertools import combinations
def partitions(n):
    def rec(i, cur):
        if i == n: yield list(cur); return
        for b in range(max(cur, default=-1) + 2): yield from rec(i + 1, cur + [b])
    yield from rec(0, [])
def scheme(p):
    cnt = {b: p.count(b) for b in p}; m = {}
    return "".join("X" if cnt[b] == 1 else m.setdefault(b, "ABCD"[len(m)]) for b in p)
def dist(s):
    d = 0
    for g in set(s) - {"X"}:
        idx = [i for i, c in enumerate(s) if c == g]; d = max(d, max(b - a for a, b in zip(idx, idx[1:])))
    return d
def verdict(s):
    contiguous = all(max(i for i, c in enumerate(s) if c == g) - min(i for i, c in enumerate(s) if c == g) + 1 == s.count(g) for g in set(s) - {"X"})
    return "stable" if s.count("X") <= 1 and contiguous else "open"
pairs = set()
for p in partitions(4):
    for a, b in combinations(sorted(set(p)), 2):
        q = [a if x == b else x for x in p]
        pairs.add((scheme(p), scheme(q)))
pairs = sorted(pairs)
flips = [(a, b) for a, b in pairs if verdict(a) != verdict(b)]
dchg = [(a, b) for a, b in pairs if dist(a) != dist(b)]
for a, b in pairs: print(f"{a}->{b}: {verdict(a)}->{verdict(b)} dist {dist(a)}->{dist(b)}")
named = {("XXAA", "XAAA"): None, ("ABBA", "AAAA"): None}
for k in named: named[k] = (verdict(k[0]), verdict(k[1]), k in set(pairs))
print("named cases:", named)
ok = len(flips) / len(pairs) >= 0.25 and all(v[0] != v[1] and v[2] for v in named.values())
print("RESULT: %s %d of %d distinct single collapses flip the verdict; closure distance changes in %d; XXAA->XAAA %s->%s, ABBA->AAAA %s->%s" % (
    "PASS" if ok else "FAIL", len(flips), len(pairs), len(dchg), *named[("XXAA", "XAAA")][:2], *named[("ABBA", "AAAA")][:2]))
