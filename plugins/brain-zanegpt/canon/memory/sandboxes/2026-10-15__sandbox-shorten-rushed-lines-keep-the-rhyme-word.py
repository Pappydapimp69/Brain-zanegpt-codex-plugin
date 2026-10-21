# Does the "shorter lines" fix for a rushed vocal keep the rhyme scheme shape?
# Rhyme key = last vowel group to end of the final word (orthographic, deliberately simple).
import re
STANZAS = {
 "AABB": ["we were walking down the long and winding road beneath the pale moon light",
          "and I could hear your voice still calling out to me tonight",
          "the river keeps on running the way it did before",
          "and I will never find the way to love you any more"],
 "ABAB": ["every window in this house is streaming with the autumn rain",
          "and I am standing here a stranger in the dark alone",
          "the memories keep falling like a wave of silent pain",
          "you left your name behind me carved in cold and heavy stone"],
 "ABBA": ["the lanterns burned all evening in the wide and open sky",
          "and every promise that we made was turned to ancient gold",
          "the winter wind came sweeping through and left the harbour cold",
          "and now the only kite I own is lost and cannot fly"],
 "XXAA": ["the clock upon the mantel keeps on counting out the past",
          "the garden folded quietly along the crumbling wall",
          "I asked you if you wanted to be someone who would stay",
          "and you were already a shadow walking far away"],
}
def key(line):
    w = re.sub(r"[^a-z]", "", line.split()[-1].lower())
    m = list(re.finditer(r"[aeiouy]+", w))
    return w[m[-1].start():] if m else w
def letters(lines):
    seen, out = {}, []
    for l in lines:
        k = key(l); seen.setdefault(k, chr(65 + len(seen))); out.append(seen[k])
    return "".join(out)
def shape(lines):
    L = letters(lines)
    if L == "AABB": return "AABB"
    if L == "ABAB": return "ABAB"
    if L == "ABBA": return "ABBA"
    if L == "ABCC": return "XXAA"
    return "other:" + L
def syl(line): return sum(len(re.findall(r"[aeiouy]+", w.lower())) for w in line.split())
def first_n(l, n=5): return " ".join(l.split()[:n])
def last_n(l, n=5): return " ".join(l.split()[-n:])
def hyph(l): return " ".join("-".join(re.findall(r"[^aeiouy]*[aeiouy]+(?:[^aeiouy]+$)?", w)) or w for w in l.split())
VARIANTS = {"original": lambda l: l, "keep-first-5": first_n, "keep-last-5": last_n, "hyphenate": hyph}
res = {}
for name, fn in VARIANTS.items():
    kept = 0; words = 0; sy = 0; n = 0; shapes = {}
    for want, lines in STANZAS.items():
        new = [fn(l) for l in lines]
        s = shape(new); shapes[want] = s; kept += s == want
        words += sum(len(l.replace("-", " ").split()) if name != "hyphenate" else len(l.split()) for l in new)
        sy += sum(syl(l.replace("-", " ")) for l in new); n += len(new)
    res[name] = (kept, words / n, sy / n, shapes)
    print(f"{name:13s} shape kept {kept}/4 words/line {words/n:.1f} syllables/line {sy/n:.1f} {shapes}")
o, f, l, h = (res[k] for k in ("original", "keep-first-5", "keep-last-5", "hyphenate"))
ok = o[0] == 4 and f[0] <= 1 and l[0] == 4 and l[1] <= 5.0 and h[0] == 4 and abs(h[2] - o[2]) < 0.01 and h[1] == o[1]
print("RESULT: %s shorten-from-the-front keeps %d/4 shapes at %.1f words/line (from %.1f), cutting the line end keeps %d/4, hyphenation keeps %d/4 but leaves words/line %.1f and syllables %.1f unchanged"
      % ("PASS" if ok else "FAIL", l[0], l[1], o[1], f[0], h[0], h[1], h[2]))
