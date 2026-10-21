# Rebuild of: how a labeller treats a repeated end word flips verdicts in opposite directions by section:
# post-chorus title x4 -> AAAA (pass stable) if repetition counts, XXXX (fail) if excluded; a verse with an accidental
# repeat fakes a rhyme under "counts". Rule: decide by section role. Own fixture; phonetic rhyme via hand-written rimes.
RIME = {"tonight": "AYT", "light": "AYT", "fall": "AOL", "call": "AOL", "rain": "EYN", "again": "EYN",
        "door": "AOR", "floor": "AOR", "down": "AWN", "town": "AWN", "go": "OW", "know": "OW", "stay": "EY", "away": "EY"}
def letter(words, repeat_counts):
    lab = []; groups = []
    for i, w in enumerate(words):
        g = None
        for j in range(i):
            same = words[j] == w
            if (same and repeat_counts) or (not same and RIME[words[j]] == RIME[w]): g = lab[j]; break
        if g is None: g = chr(65 + len(set(x for x in lab if x != "?"))); g = g
        lab.append(g)
    cnt = {c: lab.count(c) for c in lab}; m = {}
    return "".join("X" if cnt[c] == 1 else m.setdefault(c, "ABCD"[len(m)]) for c in lab)
def stable(s): return "X" not in s
def by_role(words, role): return letter(words, role == "post-chorus")
CASES = [("post-chorus", ["tonight"] * 4, "stable wanted"),
         ("verse", ["door", "go", "door", "know"], "only go/know rhyme"),
         ("verse", ["rain", "down", "rain", "town"], "only down/town rhyme"),
         ("verse", ["stay", "fall", "away", "call"], "true ABAB, no repeats"),
         ("verse", ["tonight", "tonight", "tonight", "tonight"], "BREAK: refrain-style verse")]
rows = []
for role, ws, note in CASES:
    a, b, r = letter(ws, True), letter(ws, False), by_role(ws, role)
    rows.append((role, a, b, r)); print(f"{role:11s} {ws} counts={a} excluded={b} by-role={r}  ({note})")
ok = rows[0][1] == "AAAA" and rows[0][2] == "XXXX" and rows[1][1] == "ABAB" and rows[1][2] == "XAXA" and rows[3][1] == rows[3][2] == "ABAB"
print("RESULT: %s post-chorus title x4: counts=%s excluded=%s; verse door/go/door/know: counts=%s (fake ABAB) excluded=%s; by-role gives %s and %s; refrain verse by-role %s" % (
    "PASS" if ok else "FAIL", rows[0][1], rows[0][2], rows[1][1], rows[1][2], rows[0][3], rows[1][3], rows[4][3]))
