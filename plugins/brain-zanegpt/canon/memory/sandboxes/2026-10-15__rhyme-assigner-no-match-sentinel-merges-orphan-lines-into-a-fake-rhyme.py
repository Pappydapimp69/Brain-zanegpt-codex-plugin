"""Sandbox: dbz-combat/E3 (no-winner sentinel pollutes a tally) composed with
lyrical-composition/E7 (rhyme-scheme letter assigner) and E8 (closure distance).
Deterministic, stdlib only."""
RHYME = {"night": "ait", "light": "ait", "day": "ei", "stay": "ei",
         "fire": "air", "wire": "air"}
cls = lambda w: RHYME.get(w)  # None = no known partner class (the sentinel)

def assign_naive(words):
    letters, seen = [], {}
    for w in words:
        k = cls(w)                      # None folded in like any key
        if k not in seen: seen[k] = chr(65 + len(seen))
        letters.append(seen[k])
    return "".join(letters)

def assign_guarded(words):
    letters, seen, n = [], {}, 0
    for w in words:
        k = cls(w)
        if k is None:                   # orphan: its own letter, never shared
            letters.append(chr(65 + n)); n += 1; continue
        if k not in seen: seen[k] = chr(65 + n); n += 1
        letters.append(seen[k])
    return "".join(letters)

def rhymed_share(scheme):
    return sum(scheme.count(c) > 1 for c in scheme) / len(scheme)

def closure(scheme):  # E8: distance to most recent same-letter partner
    out, last = [], {}
    for i, c in enumerate(scheme):
        out.append(i - last[c] if c in last else None); last[c] = i
    return max([d for d in out if d is not None], default=0)

cases = {
    "1 couplets AABB": ["night", "light", "day", "stay"],
    "2 free verse (BREAK)": ["river", "orange", "month", "silver"],
    "3 mixed ABAC": ["night", "orange", "light", "month"],
    "4 orphans around a couplet": ["river", "fire", "wire", "silver"],
}
ok = True; rows = []
for name, ws in cases.items():
    n, g = assign_naive(ws), assign_guarded(ws)
    rn, rg = rhymed_share(n), rhymed_share(g)
    cn, cg = closure(n), closure(g)
    print(f"{name}: naive={n} share={rn:.2f} closure={cn} | guarded={g} share={rg:.2f} closure={cg}")
    rows.append((name, n, g, rn, rg, cn, cg))
# expectations
ok &= rows[0][1] == rows[0][2] == "AABB"
ok &= rows[1][1] == "AAAA" and rows[1][3] == 1.0 and rows[1][2] == "ABCD" and rows[1][4] == 0.0
ok &= rows[2][1] == "ABAB" and rows[2][2] == "ABAC" and rows[2][3] == 1.0 and rows[2][4] == 0.5
ok &= rows[3][1] == "ABBA" and rows[3][5] == 3 and rows[3][2] == "ABBC" and rows[3][6] == 1
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      " no-match sentinel turns free verse ABCD into AAAA (rhymed share 0.00 -> 1.00), ABAC into ABAB (0.50 -> 1.00),"
      " and an orphan-wrapped couplet ABBC into ABBA (closure 1 -> 3); fully rhymed AABB unaffected")
