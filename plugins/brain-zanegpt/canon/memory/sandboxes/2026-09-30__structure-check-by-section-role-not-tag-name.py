# Composes: bridge-hides-final-chorus sandbox/E1 (the bridge's job is to withhold the returning section),
# lyrics-structure/E5 (a bracket-tag parser only knows tag text), lyrics-structure/E1 (authored variants such as
# "[Chorus - Final]" differ from a repeat marker), and the standard-pop-structure kernel.
# PREDICTION (before running): over 8 forms I wrote, a check keyed on the literal tag "Chorus" gets at least 3 wrong
# (Hook/Refrain forms, AABA, a "[Chorus - Final]" variant); a role check gets at most 1 wrong; both catch the real
# defect (bridge followed by a verse).
# ITERATION 1 (kept below as role_freq): "returning section = most repeated tag" was wrong on 2/8 and MISSED the real
# defect, because verses repeat as often as choruses (3 verses vs 2 choruses -> 'verse'). ITERATION 2 (role_text):
# the returning section is the one whose LYRIC TEXT repeats; a section returns if its text overlaps it by >= 50%.
import re
from itertools import combinations
def norm(tag):
    t = re.sub(r"\b(final|last|\d+)\b", " ", tag.lower()); t = re.sub(r"[-]", " ", t); return " ".join(t.split())
def overlap(a, b): return len(a & b) / max(1, min(len(a), len(b)))
def lit(sec):
    tags = [t for t, _ in sec]; out = []
    if "Bridge" in tags:
        i = tags.index("Bridge")
        if i + 1 >= len(tags) or tags[i + 1] != "Chorus": out.append("bridge->not-return")
    elif tags.count("Chorus") >= 3: out.append("no-bridge")
    return out
def role_freq(sec):
    ns = [norm(t) for t, _ in sec]; body = [n for n in ns if n not in ("bridge",)]
    r = max(set(body), key=lambda n: (body.count(n), -body.index(n))); out = []
    if "bridge" in ns:
        i = ns.index("bridge")
        if i + 1 >= len(ns) or ns[i + 1] != r: out.append("bridge->not-return")
    elif ns.count(r) >= 3: out.append("no-bridge")
    return out
def role_text(sec):
    idx = [i for i, (t, _) in enumerate(sec) if norm(t) != "bridge"]
    best, ref = 0, None
    for i, j in combinations(idx, 2):
        o = overlap(sec[i][1], sec[j][1])
        if o > best: best, ref = o, sec[i][1]
    returns = [i for i in idx if ref is not None and best >= 0.5 and overlap(sec[i][1], ref) >= 0.5]
    tags = [norm(t) for t, _ in sec]; out = []
    if "bridge" in tags:
        b = tags.index("bridge")
        if b + 1 not in returns: out.append("bridge->not-return")
    elif len(returns) >= 3: out.append("no-bridge")
    return out
C, H, R, A = {"c1", "c2", "c3", "c4"}, {"h1", "h2", "h3"}, {"r1", "r2"}, {"a1", "a2", "title"}
CF = {"c1", "c2", "c3", "c5"}                     # evolved final chorus: 3 of 4 lines shared
v = lambda n: {f"v{n}a", f"v{n}b", f"v{n}c", f"v{n}d"}
FORMS = [
    ("pop", [("Verse", v(1)), ("Chorus", C), ("Verse", v(2)), ("Chorus", C), ("Bridge", {"b"}), ("Chorus", C)], []),
    ("pop final-variant", [("Verse", v(1)), ("Chorus", C), ("Verse", v(2)), ("Chorus", C), ("Bridge", {"b"}), ("Chorus - Final", CF)], []),
    ("hip-hop hook", [("Hook", H), ("Verse", v(1)), ("Hook", H), ("Verse", v(2)), ("Bridge", {"b"}), ("Hook", H)], []),
    ("folk refrain no bridge", [("Verse", v(1)), ("Refrain", R), ("Verse", v(2)), ("Refrain", R), ("Verse", v(3)), ("Refrain", R)], ["no-bridge"]),
    ("AABA", [("A", A | {"x1"}), ("A", A | {"x2"}), ("Bridge", {"b"}), ("A", A | {"x3"})], []),
    ("pop no bridge", [("Verse", v(1)), ("Chorus", C), ("Verse", v(2)), ("Chorus", C), ("Verse", v(3)), ("Chorus", C)], ["no-bridge"]),
    ("DEFECT bridge->verse", [("Verse", v(1)), ("Chorus", C), ("Verse", v(2)), ("Chorus", C), ("Bridge", {"b"}), ("Verse", v(3))], ["bridge->not-return"]),
    ("BREAK verse-heavy", [("Verse 1", v(1)), ("Verse 2", v(2)), ("Chorus", C), ("Verse 3", v(3)), ("Bridge", {"b"}), ("Chorus", C)], []),
]
w = {"literal": 0, "freq": 0, "text": 0}; defect_ok = True
for name, sec, want in FORMS:
    r = {"literal": lit(sec), "freq": role_freq(sec), "text": role_text(sec)}
    for k in w: w[k] += r[k] != want
    if name.startswith("DEFECT"): defect = r
    print(f"{name:24s} want {want!s:24} literal {r['literal']!s:24} freq {r['freq']!s:24} text {r['text']}")
ok = w["literal"] >= 3 and w["text"] <= 1 and defect["literal"] == defect["text"] == ["bridge->not-return"]
print("RESULT: %s wrong on 8 forms: literal tag name %d, most-repeated-tag role %d (misses the real defect=%s), repeated-text role %d; text role flags the bridge->verse defect" % (
    "PASS" if ok else "FAIL", w["literal"], w["freq"], defect["freq"] == [], w["text"]))
