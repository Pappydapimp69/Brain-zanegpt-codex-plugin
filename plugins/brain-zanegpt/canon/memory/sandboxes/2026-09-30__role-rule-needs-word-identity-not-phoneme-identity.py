# Composes: lyrical-composition/E9 (a phoneme-only detector says MATCH for night/knight AND night/night; telling them
# apart needs a word-identity check), identity-rhyme-by-section-role sandbox/E1 (exclude repeated end words in a verse,
# count them in a post-chorus), and the rhyme-type kernel (perfect/rich rhyme resolves).
# PREDICTION (before running): if "same end word" is detected by phoneme identity, the verse rule wrongly excludes rich
# rhymes: night/knight, right/write, see/sea verses letter XAXA instead of ABAB (3 of 3 wrong); detecting by word
# identity gets all 3 right; a true repetition verse (home/home) is excluded correctly by both; post-chorus unaffected.
PH = {"night": "N AY T", "knight": "N AY T", "go": "G OW", "know": "N OW", "right": "R AY T", "write": "R AY T",
      "stay": "S T EY", "day": "D EY", "see": "S IY", "sea": "S IY", "run": "R AH N", "sun": "S AH N",
      "home": "H OW M", "tonight": "T AH N AY T", "fall": "F AO L", "call": "K AO L"}
def rime(w): p = PH[w].split(); v = max(i for i, x in enumerate(p) if x[0] in "AEIOU"); return " ".join(p[v:])
def letter(ws, role, identity):
    def same(a, b): return a == b if identity == "word" else PH[a] == PH[b]
    lab = []
    for i, w in enumerate(ws):
        g = None
        for j in range(i):
            if same(ws[j], w):
                if role == "post-chorus": g = lab[j]; break
                continue                                   # verse: repetition is not a rhyme
            if rime(ws[j]) == rime(w): g = lab[j]; break
        lab.append(g if g is not None else i)
    cnt = {c: lab.count(c) for c in lab}; m = {}
    return "".join("X" if cnt[c] == 1 else m.setdefault(c, "ABCD"[len(m)]) for c in lab)
CASES = [("verse", ["night", "go", "knight", "know"], "ABAB"), ("verse", ["right", "stay", "write", "day"], "ABAB"),
         ("verse", ["see", "run", "sea", "sun"], "ABAB"), ("verse", ["home", "fall", "home", "call"], "XAXA"),
         ("post-chorus", ["tonight"] * 4, "AAAA")]
wrong = {"phoneme": 0, "word": 0}
for role, ws, want in CASES:
    p, w = letter(ws, role, "phoneme"), letter(ws, role, "word")
    wrong["phoneme"] += p != want; wrong["word"] += w != want
    print(f"{role:11s} {ws}: want {want} phoneme-identity {p} word-identity {w}")
ok = wrong["word"] == 0 and wrong["phoneme"] == 3
print("RESULT: %s phoneme-identity role rule wrong on %d/5 sections (all rich-rhyme verses), word-identity wrong on %d/5; repetition verse and post-chorus correct under both" % ("PASS" if ok else "FAIL", wrong["phoneme"], wrong["word"]))
