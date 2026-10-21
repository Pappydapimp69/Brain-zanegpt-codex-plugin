"""Sandbox: kernel 'rhyme-scheme-shape sets emotional motion' (AABB stops, ABBA open) measured as closure on the output of
the two-pass letter assignment kernel, vs one-pass lettering that lets assonance steal letters.
Prediction (before run): with two-pass lettering, max closure distance AABB=1, ABAB=2, ABBA=3, XXAA: letters XXAA with 2 unresolved lines and max closure 1;
a stanza whose lines 1-2 share only a vowel (assonance) and lines 3-4 rhyme perfectly is lettered XXAA by two-pass (uppercase only on 3-4) but
AAAA-like (3 equal letters) by one-pass, which changes max closure from 1 to 1 but the 'open lines' count from 2 to 0 -> one-pass hides the open start;
rhyme_kind(night,knight) is 'rich' and the letter pass must not treat identical words as a rhyme."""
VOW = set("aeiou")
# toy phonetic lexicon: word -> (nucleus, coda)  (hand-written, no external data)
LEX = {"hill": ("I", "l"), "fill": ("I", "l"), "still": ("I", "l"), "will": ("I", "l"), "night": ("Y", "t"), "light": ("Y", "t"), "knight": ("Y", "t"),
       "sea": ("E", ""), "free": ("E", ""), "tree": ("E", ""), "stone": ("O", "n"), "home": ("O", "m"), "road": ("O", "d"),
       "rain": ("A", "n"), "tame": ("A", "m"), "bird": ("U", "d"), "sky": ("Y", ""), "go": ("O", ""), "shine": ("Y", "n"), "mile": ("Y", "l")}
def kind(a, b):
    if a == b: return "same"
    (n1, c1), (n2, c2) = LEX[a], LEX[b]
    if n1 == n2 and c1 == c2: return "perfect"
    if n1 == n2: return "assonance"
    return None
def one_pass(words):
    letters, nxt = [], 0
    for i, w in enumerate(words):
        for j in range(i):
            if kind(words[j], w) in ("perfect", "assonance"):
                letters.append(letters[j]); break
        else:
            letters.append(chr(65 + nxt)); nxt += 1
    return letters
def two_pass(words):
    n = len(words); letters = [None] * n; nxt = 0
    for i in range(n):
        if letters[i]: continue
        for j in range(i + 1, n):
            if letters[j] is None and kind(words[i], words[j]) == "perfect":
                if letters[i] is None: letters[i] = chr(65 + nxt); nxt += 1
                letters[j] = letters[i]
    low = 0
    for i in range(n):
        if letters[i]: continue
        for j in range(i + 1, n):
            if letters[j] is None and kind(words[i], words[j]) == "assonance":
                if letters[i] is None: letters[i] = chr(97 + low); low += 1
                letters[j] = letters[i]
    return [l or "X" for l in letters]
def closure(letters):
    """max distance from a repeated letter to its most recent same-letter partner; unresolved = X or singleton lowercase counts as open"""
    last, dists = {}, []
    for i, l in enumerate(letters):
        if l != "X" and l in last: dists.append(i - last[l])
        last[l] = i
    open_lines = sum(1 for l in letters if l == "X" or l.islower())
    return (max(dists) if dists else 0), open_lines
cases = {
 "AABB": ["hill", "still", "night", "light"],
 "ABAB": ["hill", "night", "still", "light"],
 "ABBA": ["hill", "night", "light", "still"],
 "XXAA": ["bird", "tame", "night", "light"],
 "AAAA": ["hill", "still", "will", "fill"],
 "AAAA-repeat": ["hill", "still", "will", "hill"],
}
ok = True
exp = {"AABB": (1, 0), "ABAB": (2, 0), "ABBA": (3, 0), "XXAA": (1, 2)}
for name, ws in cases.items():
    l = two_pass(ws); c = closure(l)
    print(name, "".join(l), "closure/open", c)
    if name in exp: ok &= c == exp[name]
    if name == "AAAA": ok &= l == list("AAAA") and c == (1, 0)
    if name == "AAAA-repeat": ok &= l[3] == "X"
# assonance-steals-letter case: sky/mile? 'stone','go' share vowel O with 'road' -> one-pass collapses
ws = ["stone", "road", "night", "light"]   # stone/road assonance only
op, tp = one_pass(ws), two_pass(ws)
print("assonance start: one-pass", "".join(op), closure(op), "| two-pass", "".join(tp), closure(tp))
ok &= closure(tp)[1] == 2 and closure(op)[1] == 0   # one-pass hides the open start
# one-pass over-collapse across a rhyme and a different assonance word (XAAA failure from the kernel)
ws2 = ["bird", "night", "sky", "light"]    # night/sky share nucleus Y (assonance), night/light perfect
op2, tp2 = one_pass(ws2), two_pass(ws2)
print("stolen letter: one-pass", "".join(op2), "| two-pass", "".join(tp2))
ok &= op2[2] == op2[1] and tp2[2] != tp2[1]
# BREAK: same word repeated is not a rhyme (night/night) - letter pass must keep them apart
ws3 = ["night", "hill", "night", "still"]
tp3 = two_pass(ws3)
print("repeat word:", "".join(tp3), "kind(night,night)=", kind("night", "night"), "kind(night,knight)=", kind("night", "knight"))
ok &= tp3[0] == "X" and tp3[2] == "X" and kind("night", "knight") == "perfect"
print("RESULT: %s two-pass closure AABB 1, ABAB 2, ABBA 3, XXAA 1 with 2 open; one-pass reports 0 open lines for an assonance-start stanza (two-pass 2) and steals a letter in %s; repeated word stays unresolved (X) and a repeated-word AAAA reads AAAX" % ("PASS" if ok else "FAIL", "".join(op2)))
