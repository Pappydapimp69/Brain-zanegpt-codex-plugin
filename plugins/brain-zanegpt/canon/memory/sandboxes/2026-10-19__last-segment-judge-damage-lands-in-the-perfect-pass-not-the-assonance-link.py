# Iteration 2: damage = last-segment lettering differs from WHOLE-word lettering (same spelling judge), by hyphen placement.
# Sandbox: two-pass rhyme lettering (pass 1 perfect groups, pass 2 assonance link to a resolved group)
# over syllable-hyphenated end words, with a SPELLING judge fed three views of each token.
import itertools, re
# word (hyphenated for timing) : (true perfect rime class, true assonance class)
W = {
 "light":("ight","ai"),"night":("ight","ai"),"sight":("ight","ai"),"to-night":("ight","ai"),"de-light":("ight","ai"),
 "fire":("ire","ai"),"de-sire":("ire","ai"),"high-er":("ier","ai"),
 "love":("uv","uh"),"a-bove":("uv","uh"),"dove":("uv","uh"),
 "be-lieve":("eev","ee"),"leave":("eev","ee"),"grieve":("eev","ee"),
 "tree":("ee","ee"),"free":("ee","ee"),"me":("ee","ee"),
 "day":("ay","ay"),"a-way":("ay","ay"),"stay":("ay","ay"),
 "heart":("art","ah"),"a-part":("art","ah"),"start":("art","ah"),
}
V = "aeiouy"
def spell_keys(s):
    t = s[:-1] if len(s) > 2 and s.endswith("e") and s[-2] not in V else s
    m = list(re.finditer(r"[aeiouy]+", t))
    if not m: return s, s
    g = m[-1]
    rime = s[g.start():]
    vow = t[g.start():g.end()]
    return rime, {"i":"ai","igh":"ai","y":"ai","ee":"ee","ea":"ee","o":"uh","a":"ay","ay":"ay","ie":"ee","ei":"ee","ee":"ee","u":"uh"}.get(vow, vow)
def view(tok, kind):
    if kind == "whole": return tok.replace("-", "")
    if kind == "last": return tok.split("-")[-1]
    raise
def key(tok, kind): return spell_keys(view(tok, kind))
def truth_key(tok): return W[tok]
def lettering(toks, keyf):
    ks = [keyf(t) for t in toks]
    groups = {}
    for i, (r, a) in enumerate(ks): groups.setdefault(r, []).append(i)
    letters = {}; nxt = 0
    for r, idx in groups.items():
        if len(idx) > 1:
            letters[r] = "ABCD"[nxt]; nxt += 1
    out = []
    for i, (r, a) in enumerate(ks):
        if r in letters: out.append(letters[r]); continue
        link = next((letters[kr] for kr, kk in ((k[0], k) for k in ks) if kr in letters and
                     any(ks[j][1] == a and ks[j][0] == kr for j in range(4))), None)
        out.append(link.lower() if link else "x")
    return "".join(out), len(letters)
def canon(s):
    m = {}; o = ""
    for c in s:
        k = c.lower(); m.setdefault(k, "pqrs"[len(m)]); o += m[k].upper() if c.isupper() else m[k]
    return o
def perfect_part(s): return "".join(c if c.isupper() else "." for c in s)

INSIDE = {"fire":"fi-re","de-sire":"de-si-re","high-er":"hi-gher","love":"lo-ve","a-bove":"a-bo-ve","dove":"do-ve",
          "be-lieve":"be-lie-ve","leave":"lea-ve","grieve":"grie-ve","heart":"hear-t","a-part":"a-par-t","start":"star-t"}
def conv(tok): return INSIDE.get(tok, tok)
words = list(W)
stanzas = list(itertools.combinations(words, 4))
tot = len(stanzas)
def damage(tokf):
    d = dp = da = 0
    for st in stanzas:
        toks = [tokf(t) for t in st]
        # truth for judging = whole-word view of the same tokens
        a, _ = lettering(toks, lambda x: key(x, "whole")); b, _ = lettering(toks, lambda x: key(x, "last"))
        if canon(a) != canon(b):
            d += 1
            if [c.isupper() for c in a] != [c.isupper() for c in b]: dp += 1
            else: da += 1
    return d, dp, da
out = {}
for name, f in (("boundary hyphens (to-night, a-way)", lambda t: t), ("inside-rime hyphens (fi-re, lo-ve, star-t)", conv)):
    d, dp, da = damage(f); out[name] = (d, dp, da)
    print(f"{name:44s} last-vs-whole differ {d}/{tot} = {100*d/tot:.1f}%  perfect-pass {dp}  assonance-only {da}")
# BREAK: all-boundary stanzas only (every word either unhyphenated or boundary-hyphenated) must be 0 by construction; check inside-only words
only_inside = [w for w in words if conv(w) != w]
ins_st = list(itertools.combinations(only_inside, 4))
di = 0
for st in ins_st:
    toks = [conv(t) for t in st]
    di += canon(lettering(toks, lambda x: key(x, "whole"))[0]) != canon(lettering(toks, lambda x: key(x, "last"))[0])
print(f"inside-rime words only: {di}/{len(ins_st)} differ")
b = out["boundary hyphens (to-night, a-way)"]; i = out["inside-rime hyphens (fi-re, lo-ve, star-t)"]
ok = b[0] == 0 and i[0] > 0 and i[1] > i[2]
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
  f"boundary hyphens {b[0]}/{tot} differ; inside-rime hyphens {i[0]}/{tot} ({100*i[0]/tot:.1f}%), perfect-pass {i[1]} vs assonance-only {i[2]}; inside-only words {di}/{len(ins_st)}")
