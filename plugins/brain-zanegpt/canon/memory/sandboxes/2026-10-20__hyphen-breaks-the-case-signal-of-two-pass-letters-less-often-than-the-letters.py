# Sandbox: two-pass letters carry a case signal (UPPER = resolved rhyme, lower = assonance only, x = none).
# Does hyphenating end words under a last-fragment judge corrupt the open/stable verdict as often as the letters?
import itertools
LEX = {  # word: (hyphenated, perfect key, vowel key)
 "light":("light","ight","i"),"night":("night","ight","i"),
 "fire":("fi-re","ire","i"),"higher":("hi-gher","ire","i"),
 "stone":("stone","one","o"),"alone":("a-lone","one","o"),
 "rain":("rain","ain","a"),"again":("a-gain","ain","a"),
 "kind":("kind","ind","i"),"home":("home","ome","o"),
 "sea":("sea","ea","e"),"free":("free","ee","e"),
 "gold":("gold","old","o"),"told":("told","old","o"),
}
WORDS=list(LEX)
def key_whole(w):
    p=LEX[w.replace("-","")]; return p[1],p[2]
def key_last(w):   # dictionary judge that only sees the final fragment; unknown fragment keys on itself
    f=w.split("-")[-1]
    return (LEX[f][1],LEX[f][2]) if f in LEX else (f,f)
def letters(ws,key):
    ks=[key(w) for w in ws]; out=[None]*len(ws); up=iter("ABCD")
    for i in range(len(ws)):                                  # pass 1: resolved (perfect) groups, UPPER
        if out[i] is None and any(ks[j][0]==ks[i][0] for j in range(len(ws)) if j!=i):
            L=next(up)
            for j in range(len(ws)):
                if out[j] is None and ks[j][0]==ks[i][0]: out[j]=L
    lo=iter("abcd")
    for i in range(len(ws)):                                  # pass 2: assonance among the rest, lower
        if out[i] is None and any(out[j] is None and j!=i and ks[j][1]==ks[i][1] for j in range(len(ws))):
            L=next(lo)
            for j in range(len(ws)):
                if out[j] is None and ks[j][1]==ks[i][1]: out[j]=L
    return "".join(c or "x" for c in out)
def shape(s): return "".join("U" if c.isupper() else ("l" if c.islower() and c!="x" else "x") for c in s)
def verdict(s): return "stable" if all(c.isupper() for c in s if c!="x") and "x" not in s else "open"
tot=let_bad=shape_bad=verd_bad=0
hyph={w:LEX[w][0] for w in WORDS}
for ws in itertools.product(WORDS,repeat=4):
    base=letters(list(ws),key_last)                      # same judge on plain words (= truth, since whole words are in the dictionary)
    seen=letters([hyph[w] for w in ws],key_last)
    tot+=1
    if base!=seen: let_bad+=1
    if shape(base)!=shape(seen): shape_bad+=1
    if verdict(base)!=verdict(seen): verd_bad+=1
whole=sum(1 for ws in itertools.product(WORDS,repeat=4) if letters(ws,key_whole)!=letters([hyph[w] for w in ws],key_whole))
print(f"stanzas={tot} whole-word judge, hyphenated vs plain: changed={whole}")
print(f"last-fragment judge, hyphenated vs plain: letters changed={let_bad} ({let_bad/tot:.1%}), case shape changed={shape_bad} ({shape_bad/tot:.1%}), open/stable verdict flipped={verd_bad} ({verd_bad/tot:.1%})")
ok = whole==0 and let_bad>0 and verd_bad>0 and verd_bad<let_bad and shape_bad<=let_bad
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" hyphens alone change letters in {let_bad}/{tot}, case shape {shape_bad}/{tot}, open-stable verdict {verd_bad}/{tot}; whole-word judge {whole}")
