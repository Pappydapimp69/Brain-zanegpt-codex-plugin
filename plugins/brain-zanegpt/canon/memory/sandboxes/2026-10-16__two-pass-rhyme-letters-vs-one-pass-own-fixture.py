# Toy phonetic table: word -> (vowel, coda). perfect = same vowel+coda; assonance = same vowel, different coda.
W = {"night":("AY","T"),"light":("AY","T"),"time":("AY","M"),"mine":("AY","N"),"line":("AY","N"),"fine":("AY","N"),
     "day":("EY","-"),"way":("EY","-"),"late":("EY","T"),"made":("EY","D"),"home":("OW","M"),"stone":("OW","N"),
     "road":("OW","D"),"alone":("OW","N"),"sea":("IY","-"),"free":("IY","-"),"rain":("EY","N"),"gone":("AO","N")}
def rel(a, b):
    (va, ca), (vb, cb) = W[a], W[b]
    return "perfect" if (va, ca) == (vb, cb) else ("assonance" if va == vb else None)
def one_pass(words):
    L = []; out = []
    for i, w in enumerate(words):
        for j in range(i):
            if rel(w, words[j]): out.append(out[j]); break
        else: out.append(chr(65 + len(set(out))))
    return "".join(out)
def two_pass(words):
    out = [None] * len(words); n = 0
    for i, w in enumerate(words):                       # pass 1: perfect only -> UPPERCASE
        if out[i]: continue
        grp = [j for j in range(i, len(words)) if out[j] is None and rel(w, words[j]) == "perfect" or j == i]
        if len(grp) > 1:
            for j in grp: out[j] = chr(65 + n)
            n += 1
    m = 0
    for i, w in enumerate(words):                       # pass 2: assonance among the still-unlettered -> lowercase
        if out[i]: continue
        grp = [j for j in range(i, len(words)) if out[j] is None and (j == i or rel(w, words[j]))]
        if len(grp) > 1:
            for j in grp: out[j] = chr(97 + m)
            m += 1
    for i in range(len(out)):
        if out[i] is None: out[i] = "x"
    return "".join(out)
cases = {   # words, truth the human hears (perfect upper / assonance lower / x none)
 "stray-assonance steals": (["night","light","day","way","time"], "AAxxx"),   # plain
 "XXAA with stray vowel": (["day","way","night","light","mine"], "AABBx"),
 "ABAB perfect": (["night","day","light","way"], "ABAB"),
 "assonance-only": (["time","mine","gone","sea"], "aaxx"),
 "near-rhyme beside perfect (BREAK)": (["line","fine","time","mine"], "AAxA"),
}
truth = {"XXAA with stray vowel": "AABBx"}
diffs = 0; rows = {}
for k, (w, _) in cases.items():
    o, t = one_pass(w), two_pass(w); rows[k] = (o, t); diffs += o != t
    print("%-36s one=%s two=%s" % (k, o, t))
# the BREAK: line/fine/mine perfect, time assonant with them: two-pass should give AAxA-> letters: line,fine,mine = A, time lowercase? time alone -> x
two_break = two_pass(cases["near-rhyme beside perfect (BREAK)"][0])
one_break = one_pass(cases["near-rhyme beside perfect (BREAK)"][0])
ok = diffs >= 1 and two_break.lower().count("x") == 1 and one_break == "AAAA"
print("RESULT: %s two-pass differs from one-pass on %d of %d fixtures; near-rhyme beside a perfect trio: one-pass AAAA hides it, two-pass %s marks it unresolved; assonance-only stanza %s vs %s"
      % ("PASS" if ok else "FAIL", diffs, len(cases), two_break, *rows["assonance-only"]))
