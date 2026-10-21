# Rebuild of: a rhyme-scheme labeller needs a phonetic judge AND two-pass (perfect-first) lettering; either alone fails.
# (first run printed BACA for ABCB: letters were not canonicalised by first appearance; fixed.)
# Own fixture: hand-written pronunciations (vowel, coda); stanzas chosen by me, not the original's.
PRON = {"home": ("OW", "M"), "phone": ("OW", "N"), "roam": ("OW", "M"), "stone": ("OW", "N"),
        "come": ("AH", "M"), "dome": ("OW", "M"), "cat": ("AE", "T"), "hat": ("AE", "T"),
        "dog": ("AO", "G"), "log": ("AO", "G"), "night": ("AY", "T"), "light": ("AY", "T"),
        "bite": ("AY", "T"), "hide": ("AY", "D")}
def ph_perfect(a, b): return PRON[a] == PRON[b]
def ph_slant(a, b): return PRON[a][0] == PRON[b][0]
def sp_perfect(a, b): return a[-3:] == b[-3:]
def sp_slant(a, b): return a[-2:] == b[-2:]
def letters(words, perfect, slant, two_pass):
    lab = [None] * len(words); nxt = iter("ABCDEFGH")
    if two_pass:
        for i, w in enumerate(words):                      # pass 1: perfect rhymes only
            for j in range(i):
                if perfect(words[j], w): lab[i] = lab[j]; break
            else:
                if any(perfect(w, words[k]) for k in range(i + 1, len(words))): lab[i] = next(nxt)
        for i, w in enumerate(words):                      # pass 2: leftover lines join by slant, else new letter
            if lab[i] is None:
                for j in range(len(words)):
                    if j != i and lab[j] and slant(words[j], w) and not perfect(words[j], w): lab[i] = lab[j]; break
                else: lab[i] = next(nxt)
    else:
        for i, w in enumerate(words):                      # single pass: first earlier match of either kind
            for j in range(i):
                if perfect(words[j], w) or slant(words[j], w): lab[i] = lab[j]; break
            else: lab[i] = next(nxt)
    m = {}                                                 # canonicalise letters by first appearance
    return "".join(m.setdefault(c, "ABCDEFGH"[len(m)]) for c in lab)
STANZAS = {"eye-rhyme+assonance trap": (["home", "phone", "roam", "stone"], "ABAB"),
           "eye-rhyme come/dome": (["come", "night", "dome", "light"], "ABCB"),
           "BREAK clean spelling rhymes": (["cat", "dog", "hat", "log"], "ABAB")}
res = {}
for name, (ws, truth) in STANZAS.items():
    row = {}
    for jn, (p, s) in {"spelling": (sp_perfect, sp_slant), "phonetic": (ph_perfect, ph_slant)}.items():
        for tp in (False, True):
            row[(jn, tp)] = letters(ws, p, s, tp)
    res[name] = (row, truth)
    print(name, ws, "truth", truth, {f"{j}/{'two' if t else 'one'}": v for (j, t), v in row.items()})
trap_ok = all(r[("phonetic", True)] == t and r[("spelling", True)] != t and r[("phonetic", False)] != t
              for n, (r, t) in res.items() if not n.startswith("BREAK") and n.startswith("eye-rhyme+"))
second_ok = res["eye-rhyme come/dome"][0][("phonetic", True)] == "ABCB"
brk_all_right = all(v == res["BREAK clean spelling rhymes"][1] for v in res["BREAK clean spelling rhymes"][0].values())
print("RESULT: %s trap stanza: only phonetic+two-pass is right (spelling+two %s, phonetic+one %s); come/dome stanza phonetic+two %s; break stanza with clean spellings: all 4 combos right=%s" % (
    "PASS" if trap_ok and second_ok else "FAIL", res["eye-rhyme+assonance trap"][0][("spelling", True)], res["eye-rhyme+assonance trap"][0][("phonetic", False)],
    res["eye-rhyme come/dome"][0][("phonetic", True)], brk_all_right))
