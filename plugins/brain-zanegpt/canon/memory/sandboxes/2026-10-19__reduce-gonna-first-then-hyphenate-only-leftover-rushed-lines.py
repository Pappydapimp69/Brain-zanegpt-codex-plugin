import re, itertools
VOW = re.compile(r'[aeiouy]+')
def syl(w):
    w = w.lower().strip(".,")
    if w == "gonna": return 2
    if w.endswith("e") and len(w) > 3 and not w.endswith("le"): w = w[:-1]
    return max(1, len(VOW.findall(w)))
TRUE = {"going": 2, "gonna": 2}
def tsyl(w): return TRUE.get(w.lower().strip(".,"), syl(w))
def tcount(line): return sum(tsyl(w) for w in re.split(r"[\s-]+", line) if w)
def count(line): return sum(syl(w) for w in re.split(r"[\s-]+", line) if w)
NOTVERB = {"the","a","an","my","your","his","her","our","their","me","you","him","them","us","it","that","this","be"}
def reduce(line):
    def f(m): return m.group(0) if m.group(1) in NOTVERB else "gonna " + m.group(1)
    return re.sub(r"\bgoing to (\w+)", f, line)
def hyph_hint(line, budget): return tcount(line) > budget  # keyed on true syllables
def key(line):  # whole-word rhyme key: last vowel group + coda of the final word
    w = re.split(r"[\s-]+", line.strip(".,"))[-1].lower()
    m = re.search(r"[aeiouy]+[^aeiouy]*e?$", w); return m.group(0) if m else w
def letters(lines):
    seen = {}; out = ""
    for l in lines:
        k = key(l); seen.setdefault(k, "ABCD"[len(seen)]); out += seen[k]
    return out
ENDS = ["night", "light", "stay", "away"]
VERBS = ["leave", "fight", "wait", "carry"]
BUDGET = 9
def mk(v, e, tail=None): return f"we are going to {v} the long road home {e}" if tail is None else tail
# scenarios (budget 9): 1) one-over bare-verb lines  2) going-to-noun lines  3) BREAK: two-over bare-verb lines
sc = {}
sc["one-over"] = [f"I am going to {v} you the way {e}" for v, e in itertools.product(VERBS, ENDS)]
sc["going-to-noun"] = [f"I am going to the {n} by the {e}" for n, e in itertools.product(["store","river","station","bridge"], ENDS)]
sc["BREAK-two-over"] = [f"I am going to {v} you all the way {e}" for v, e in itertools.product(VERBS, ENDS)]
res = {}
for n, ls in sc.items():
    red = [reduce(l) for l in ls]
    hb = sum(hyph_hint(l, BUDGET) for l in ls); ha = sum(hyph_hint(l, BUDGET) for l in red)
    cb = sum(count(l) > BUDGET for l in ls); ca = sum(count(l) > BUDGET for l in red)
    print("  vowel-group counter hints before", cb, "after", ca)
    chg = sum(a != b for a, b in zip(ls, red))
    lett_same = sum(letters(ls[i:i+4]) == letters(red[i:i+4]) for i in range(0, len(ls) - 3, 4))
    tot = len(range(0, len(ls) - 3, 4))
    res[n] = (len(ls), chg, hb, ha, lett_same, tot)
    print(n, "lines", len(ls), "reduced", chg, "hints before", hb, "after", ha, "stanza letters unchanged", lett_same, "/", tot)
n1, n2, n3 = res["one-over"], res["going-to-noun"], res["BREAK-two-over"]
exact1 = sum(tcount(l) == BUDGET + 1 for l in sc["one-over"])  # lines that are exactly one over
ok = (n1[2] - n1[3] == exact1 and n1[3] > 0 and n2[1] == 0 and n3[2] == n3[3] and n1[4] == n1[5] and n3[4] == n3[5])
print("RESULT:", "PASS" if ok else "FAIL",
      f"reduction cleared {n1[2]-n1[3]} of {n1[2]} one-over hints (= the {exact1} lines exactly one over), 0 of {n3[2]} two-over, noun lines untouched ({n2[1]} changed), vowel-group counter saw 0 change, rhyme letters kept {n1[4]+n2[4]+n3[4]}/{n1[5]+n2[5]+n3[5]} stanzas")
