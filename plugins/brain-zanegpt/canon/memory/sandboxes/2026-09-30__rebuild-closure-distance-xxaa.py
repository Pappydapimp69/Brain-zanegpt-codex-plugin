# Rebuild of: closure distance scores XXAA like AABB (max distance 1) though XXAA stays open by delaying its first
# rhyme; pair it with the first-closing line. Own definitions: closure distance = max gap between consecutive members
# of a rhyme group (X = unrhymed, ignored); first-closing line = 1-based index of the first line completing any rhyme.
# Enumerate all 15 set partitions of 4 lines (singletons shown as X) plus some 6-line schemes.
def partitions(n):
    def rec(i, cur):
        if i == n: yield list(cur); return
        for b in range(max(cur, default=-1) + 2):
            yield from rec(i + 1, cur + [b])
    yield from rec(0, [])
def to_scheme(p):
    cnt = {b: p.count(b) for b in p}; m = {}; out = ""
    for b in p:
        if cnt[b] == 1: out += "X"
        else: out += m.setdefault(b, "ABCDEF"[len(m)])
    return out
def dist(s):
    d = 0
    for g in set(s) - {"X"}:
        idx = [i for i, c in enumerate(s) if c == g]
        d = max(d, max(b - a for a, b in zip(idx, idx[1:])))
    return d
def first_close(s):
    seen = set()
    for i, c in enumerate(s):
        if c != "X" and c in seen: return i + 1
        seen.add(c)
    return None
schemes = sorted({to_scheme(p) for p in partitions(4)})
print(len(schemes), "4-line schemes")
for s in schemes: print(f"  {s}: distance={dist(s)} first_close={first_close(s)}")
same_as_aabb = [s for s in schemes if dist(s) == dist("AABB") and first_close(s) not in (None, first_close("AABB"))]
print("distance ties AABB but first-close later:", same_as_aabb)
six = ["AABBCC", "XXXXAA", "XXAABB", "ABCABC"]
for s in six: print(f"  6-line {s}: distance={dist(s)} first_close={first_close(s)}")
ok = dist("XXAA") == dist("AABB") == 1 and dist("ABBA") == 3 and first_close("XXAA") == 4 and first_close("AABB") == 2 and dist("XXXXAA") == 1
print("RESULT: %s XXAA distance %d = AABB %d, ABBA %d; first-close separates them (4 vs 2); other distance-1 late closers: %s; 6-line XXXXAA also distance 1 first-close 6" % (
    "PASS" if ok else "FAIL", dist("XXAA"), dist("AABB"), dist("ABBA"), same_as_aabb))
