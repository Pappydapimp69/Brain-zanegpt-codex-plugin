"""Own fixture: tiny phoneme lexicon (vowel nucleus, coda). perfect = same nucleus+coda; assonance = same nucleus only.
Prediction (before run): on 6 stanzas, single-pass (any match claims a letter, first-match) mislabels the scheme of at
least 3 versus the intended truth, two-pass (uppercase perfect first, lowercase assonance after) mislabels 0 on
perfect-driven stanzas; BREAK: on an assonance-only stanza (no perfect pairs) two-pass yields all-lowercase and
equals single-pass structure; and closure distance (lines between a letter and its previous same-letter line)
is capped at 1 for AABB-like and reaches 3 for ABBA under two-pass."""
LEX = {"night": ("ai", "t"), "light": ("ai", "t"), "time": ("ai", "m"), "mine": ("ai", "n"), "line": ("ai", "n"),
       "day": ("ei", ""), "way": ("ei", ""), "name": ("ei", "m"), "stone": ("ou", "n"), "home": ("ou", "m"),
       "bone": ("ou", "n"), "road": ("ou", "d"), "tree": ("i", ""), "sea": ("i", ""), "grin": ("i", "n")}
def rel(a, b):
    if a == b: return None            # same word is repetition, not a rhyme
    (n1, c1), (n2, c2) = LEX[a], LEX[b]
    if n1 == n2 and c1 == c2: return "perfect"
    if n1 == n2: return "assonance"
    return None
def single_pass(ws):
    out = [None] * len(ws); nxt = 0
    for i in range(len(ws)):
        if out[i]: continue
        out[i] = chr(65 + nxt); nxt += 1
        for j in range(i + 1, len(ws)):
            if not out[j] and rel(ws[i], ws[j]): out[j] = out[i]
    return "".join(out)
def two_pass(ws):
    out = [None] * len(ws); up = 0; lo = 0
    for i in range(len(ws)):
        if out[i]: continue
        grp = [j for j in range(i + 1, len(ws)) if not out[j] and rel(ws[i], ws[j]) == "perfect"]
        if grp:
            for j in [i] + grp: out[j] = chr(65 + up)
            up += 1
    for i in range(len(ws)):
        if out[i]: continue
        grp = [j for j in range(i + 1, len(ws)) if not out[j] and rel(ws[i], ws[j]) == "assonance"]
        out[i] = chr(97 + lo)
        for j in grp: out[j] = out[i]
        lo += 1
    return "".join(out)
def norm(s):  # canonical relabel ignoring case
    m = {}; r = ""
    for c in s.lower():
        m.setdefault(c, chr(65 + len(m))); r += m[c]
    return r
def closure(s):
    last = {}; mx = 0
    for i, c in enumerate(s.lower()):
        if c in last: mx = max(mx, i - last[c])
        last[c] = i
    return mx
# (words, intended scheme by perfect rhyme only; truth lowercased classes: perfect pairs share, assonance stays open)
S = [(["night", "light", "day", "way"], "AABB"),
     (["night", "mine", "light", "line"], "ABAB"),       # night/light perfect, mine/line perfect, night~mine assonance
     (["time", "night", "mine", "light"], "ABCB"),       # time~night~mine assonance, night/light perfect
     (["stone", "home", "bone", "road"], "ABAC"),        # stone/bone perfect; home, road assonance only
     (["day", "tree", "way", "sea"], "ABAB"),
     (["time", "mine", "night", "line"], "ABCB")]        # mine/line perfect; time, night assonance
def perfect_groups(ws):
    g = set()
    for i in range(len(ws)):
        for j in range(i + 1, len(ws)):
            if rel(ws[i], ws[j]) == "perfect": g.add((i, j))
    return g
def same_letter_pairs(s, upper_only=False):
    return {(i, j) for i in range(len(s)) for j in range(i + 1, len(s)) if s[i] == s[j] and (not upper_only or s[i].isupper())}
bad1 = bad2 = 0   # iteration 1 metric: case-blind scheme equality (kept; it FAILED because it ignores the case channel)
conf1 = conf2 = 0  # iteration 2 metric: same-letter pairs that are NOT perfect rhymes in the resolved (uppercase) channel
for ws, truth in S:
    a, b = single_pass(ws), two_pass(ws)
    t1, t2 = norm(a) != norm(truth), norm(b) != norm(truth)
    bad1 += t1; bad2 += t2
    pg = perfect_groups(ws)
    c1 = len(same_letter_pairs(a) - pg)            # single-pass has no case channel: every shared letter claims a rhyme
    c2 = len(same_letter_pairs(b, True) - pg) + len(pg - same_letter_pairs(b, True))
    conf1 += c1; conf2 += c2
    print(f"{' '.join(ws):24s} truth={truth} single={a} two-pass={b} case-blind {'1x' if t1 else 'ok'}/{'2x' if t2 else 'ok'} falseclaims single={c1} twopass={c2}")
ao = ["time", "night", "mine", "grin"]
print("assonance-only", ao, "single", single_pass(ao), "two-pass", two_pass(ao))
brk = two_pass(["time", "tree", "night", "grin"]).islower()  # no perfect pair at all
c_aabb, c_abba = closure(two_pass(["night", "light", "day", "way"])), closure(two_pass(["night", "day", "way", "light"]))
print("case-blind mismatches single", bad1, "two-pass", bad2, "(iteration 1 metric, ignores case)")
print("closure AABB", c_aabb, "ABBA", c_abba, "assonance-only all lowercase", brk)
ok = conf1 >= 6 and conf2 == 0 and brk and c_aabb == 1 and c_abba == 3
print("RESULT:", "PASS" if ok else "FAIL", f"false rhyme claims single-pass {conf1} vs two-pass uppercase {conf2} over 6 stanzas; case-blind scheme check misfires ({bad2}/6 two-pass); closure AABB {c_aabb} ABBA {c_abba}; assonance-only all-lowercase {brk}")
