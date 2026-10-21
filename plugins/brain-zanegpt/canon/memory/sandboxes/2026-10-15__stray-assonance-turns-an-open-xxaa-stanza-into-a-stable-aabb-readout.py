"""Train kernel (new half): path = SONGWRITING two-pass letter assignment
(resolved rhymes claim UPPERCASE letters first, assonance gets lowercase) +
SONGWRITING rhyme-scheme shape (AABB stable, ABAB flowing, XXAA open then
resolved, ABBA wistful); companion = suno-builder E7 (a structure check keyed
on the word 'Chorus' misfires; define the repeating section by role).
Composed claim: an 'emotional motion' readout per section is only right if
(1) the scheme comes from the two-pass labeller (one pass lets stray assonance
steal letters and mislabels the shape) and (2) sections are matched by
repetition, not by their label.
Own fixture, deterministic: words are (vowel, coda-class, coda) triples;
perfect = same vowel and coda; family = same vowel, same coda class;
assonance = same vowel only. 8 stanzas with known intended shapes, 3 of them
with a stray assonance pair; a song of 7 sections where the hook is labelled
'Hook' (not 'Chorus') and one unrepeated section is labelled 'Chorus'.
PREDICTION (written before running): one-pass mislabels the shape of every
stanza with stray assonance (3/8) and two-pass mislabels 0/8; a label-keyed
repeat finder misses the Hook (repeats 3 times) and wrongly treats the lone
'Chorus' as the repeating section; a content-keyed finder gets both right.
"""
import sys
print("python", sys.version.split()[0])
W = {"day": ("ei", "open", ""), "way": ("ei", "open", ""), "rain": ("ei", "nasal", "n"), "same": ("ei", "nasal", "m"),
     "night": ("ai", "stop", "t"), "light": ("ai", "stop", "t"), "side": ("ai", "stop", "d"), "time": ("ai", "nasal", "m"),
     "home": ("ou", "nasal", "m"), "stone": ("ou", "nasal", "n"), "road": ("ou", "stop", "d"), "cold": ("ou", "lat", "ld"),
     "hand": ("a", "nasal", "nd"), "stand": ("a", "nasal", "nd"), "back": ("a", "stop", "k"), "glass": ("a", "fric", "s"),
     "tree": ("i", "open", ""), "sea": ("i", "open", ""), "keep": ("i", "stop", "p"), "deep": ("i", "stop", "p")}
def kind(a, b):
    va, ca, ka = W[a]; vb, cb, kb = W[b]
    if va != vb: return None
    if ka == kb: return "perfect"
    if ca == cb: return "family"
    return "assonance"
def one_pass(ends):
    lab = [None] * len(ends); nxt = 0
    for i, w in enumerate(ends):
        for j in range(i):
            if kind(w, ends[j]): lab[i] = lab[j]; break
        if lab[i] is None: lab[i] = "ABCDEFG"[nxt]; nxt += 1
    return norm(lab)
def two_pass(ends):
    lab = [None] * len(ends); nxt = 0
    for i, w in enumerate(ends):
        for j in range(i):
            if lab[j] and lab[j].isupper() and kind(w, ends[j]) in ("perfect", "family"): lab[i] = lab[j]; break
        else:
            if any(kind(w, ends[k]) in ("perfect", "family") for k in range(i + 1, len(ends))): lab[i] = "ABCDEFG"[nxt]; nxt += 1
    for i, w in enumerate(ends):
        if lab[i] is None: lab[i] = "x"
    return norm(lab)
def norm(lab):
    m = {}; out = ""
    for l in lab:
        if l.lower() == "x" and l == "x": out += "X"; continue
        if sum(1 for q in lab if q == l) == 1: out += "X"; continue
        if l not in m: m[l] = "ABCD"[len(m)]
        out += m[l]
    return out
SHAPE = {"AABB": "stable", "ABAB": "flowing", "XXAA": "open-then-resolved", "ABBA": "wistful", "XAXA": "flowing"}
ST = [(["day", "way", "night", "light"], "AABB"), (["hand", "night", "stand", "light"], "ABAB"),
      (["road", "keep", "rain", "same"], "XXAA"),   # same/rain family -> resolved couplet; road/keep unrelated
      (["home", "tree", "sea", "stone"], "ABBA"),
      (["rain", "day", "side", "night"], "XXAA"),   # STRAY: rain/day assonance; side/night family
      (["back", "glass", "deep", "keep"], "XXAA"),  # STRAY: back/glass assonance
      (["cold", "home", "night", "light"], "XXAA"), # STRAY: cold/home assonance
      (["sea", "side", "tree", "light"], "ABAB")]
mis1 = mis2 = stray = 0
for ends, want in ST:
    s1, s2 = one_pass(ends), two_pass(ends)
    bad1, bad2 = SHAPE.get(s1) != SHAPE[want], SHAPE.get(s2) != SHAPE[want]
    mis1 += bad1; mis2 += bad2
    print(f"{' '.join(ends):24s} want {want} ({SHAPE[want]:18s}) one-pass {s1} {'MIS' if bad1 else 'ok '} two-pass {s2} {'MIS' if bad2 else 'ok'}")
SONG = [("Verse", "v1"), ("Hook", "h"), ("Verse", "v2"), ("Hook", "h"), ("Chorus", "lone"), ("Bridge", "b"), ("Hook", "h")]
label_rep = [n for n, _ in SONG if n == "Chorus"]
counts = {}
for _, body in SONG: counts[body] = counts.get(body, 0) + 1
content_rep = {n for n, b in SONG if counts[b] > 1}
print(f"label-keyed repeating section: {set(label_rep) or None} (appears {len(label_rep)}x); content-keyed: {content_rep}")
c = [mis1 == 3, mis2 == 0, label_rep == ["Chorus"] and "Hook" not in label_rep, content_rep == {"Hook"}]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/4; shape mislabels one-pass {mis1}/8, two-pass {mis2}/8; label-keyed finder picks the lone 'Chorus', content-keyed finds {content_rep}")
