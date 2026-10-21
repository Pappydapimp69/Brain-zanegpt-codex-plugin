"""Prediction (before run): exhaustive 4-line stanzas over a 9-word end pool, two-pass lettering.
Under a last-segment judge, PREFIX hyphens (re-turn, dis-turb) break 0% of stanzas because the last
segment keeps the word's rhyme; SUFFIX-tail hyphens (burn-ing) break >=20%; a whole-word judge breaks 0%
for both. Break case: a pool where prefix words collide with a bare word (turn vs re-turn) must still be 0%."""
import itertools
# word: (perfect key, assonance key)
W = {"return":("urn","u"),"burn":("urn","u"),"disturb":("urb","u"),"herb":("urb","u"),
     "burning":("urning","u"),"turning":("urning","u"),"morning":("orning","o"),"warning":("orning","o"),"cat":("at","a")}
PREFIX = {"return":"re-turn","disturb":"dis-turb"}
SUFFIX = {"burning":"burn-ing","turning":"turn-ing","morning":"morn-ing","warning":"warn-ing"}
SEG = {"turn":("urn","u"),"turb":("urb","u"),"burn":("urn","u"),"morn":("orn","o"),"warn":("orn","o"),"ing":("ing","i")}
def letters(keys):
    out=[None]*4;perf={}
    for i,(p,a) in enumerate(keys):
        if sum(k[0]==p for k in keys)>1:
            perf.setdefault(p,"ABCD"[len(perf)]);out[i]=perf[p]
    for i,(p,a) in enumerate(keys):
        if out[i] is None:
            hit=[perf[q] for q,b in keys if q in perf and b==a]
            out[i]=hit[0].lower() if hit else "x"
    return "".join(out)
def last_seg_key(word,form):
    h=form.get(word,word)
    seg=h.split("-")[-1]
    return SEG.get(seg,W[word])
def run(form):
    n=bad_last=bad_whole=0
    for st in itertools.product(W,repeat=4):
        n+=1
        base=letters([W[w] for w in st])
        if letters([W[w] for w in st])!=base: bad_whole+=1   # whole-word judge ignores hyphens
        if letters([last_seg_key(w,form) for w in st])!=base: bad_last+=1
    return n,bad_last,bad_whole
n,pl,pw=run(PREFIX); _,sl,sw=run(SUFFIX); _,bl,bw=run({**PREFIX,**SUFFIX})
print(f"stanzas={n} prefix: last-seg breaks {pl} ({pl/n:.1%}) whole {pw}; suffix: last-seg breaks {sl} ({sl/n:.1%}) whole {sw}; both {bl} ({bl/n:.1%})")
ok = pl==0 and pw==sw==bw==0 and sl/n>=0.20
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" prefix last-seg {pl/n:.1%}, suffix last-seg {sl/n:.1%}, mixed {bl/n:.1%}, whole-word 0")
