"""Sandbox: draft/E4 (one shared key keeps two consumers in agreement, at a cost)
composed with sandbox-lyrical-composition/E7 (section-blind rhyme assigner links
unrelated lines). Which scope should a rhyme-letter table have? Deterministic, stdlib."""
# (section instance, section type, rhyme class of the line end)
SONG = [("v1", "verse", "ay"), ("v1", "verse", "ight"), ("v1", "verse", "ay"), ("v1", "verse", "ight"),
        ("c1", "chorus", "own"), ("c1", "chorus", "own"), ("c1", "chorus", "ire"), ("c1", "chorus", "ire"),
        ("v2", "verse", "ee"), ("v2", "verse", "own"), ("v2", "verse", "ee"), ("v2", "verse", "ay"),
        ("c2", "chorus", "own"), ("c2", "chorus", "own"), ("c2", "chorus", "ire"), ("c2", "chorus", "ire")]
# intended links: same class within a section instance, or the same chorus line across chorus repeats
def intended(i, j):
    si, ti, ci = SONG[i]; sj, tj, cj = SONG[j]
    if si == sj: return ci == cj
    if ti == tj == "chorus": return ci == cj
    return False

def assign(scope_of):
    tables, out = {}, []
    for i, (inst, typ, cls) in enumerate(SONG):
        scope = scope_of(inst, typ)
        t = tables.setdefault(scope, {})
        if cls not in t: t[cls] = f"{scope}:{chr(65 + len(t))}"
        out.append(t[cls])
    return out

def printed(labels):  # what a reader sees: the letter only
    return [l.split(":")[1] for l in labels]

schemes = {
    "global": lambda inst, typ: "g",              # one table, like one shared counter
    "per-instance": lambda inst, typ: inst,       # reset every section
    "per-type": lambda inst, typ: typ if typ == "chorus" else inst,  # repeats share, verses own
}
n = len(SONG); rows = {}
for name, f in schemes.items():
    lab = assign(f); shown = printed(lab)
    false_links = sum(1 for i in range(n) for j in range(i + 1, n) if lab[i] == lab[j] and not intended(i, j))
    missed = sum(1 for i in range(n) for j in range(i + 1, n) if intended(i, j) and lab[i] != lab[j])
    look_alike = sum(1 for i in range(n) for j in range(i + 1, n)
                     if shown[i] == shown[j] and lab[i] != lab[j])  # same printed letter, not linked
    rows[name] = (false_links, missed, look_alike)
    print(f"{name:13s} {''.join(shown[:4])} {''.join(shown[4:8])} {''.join(shown[8:12])} {''.join(shown[12:])}"
          f"  false_links={false_links} missed={missed} printed_lookalikes={look_alike}")
ok = rows["global"][0] > 0 and rows["global"][1] == 0
ok &= rows["per-instance"][0] == 0 and rows["per-instance"][1] > 0 and rows["per-instance"][2] > 0
ok &= rows["per-type"][0] == 0 and rows["per-type"][1] == 0
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" global table false links {rows['global'][0]} (missed {rows['global'][1]}); per-instance reset missed {rows['per-instance'][1]} chorus links"
      f" and {rows['per-instance'][2]} printed look-alikes; per-section-type scope 0 false / 0 missed (look-alikes {rows['per-type'][2]})")
