"""Compose: hyphenate-to-slow + two-pass letters + write-the-reduced-form.
Prediction (written before run): over all 4-line stanzas from an 8-word end pool,
(a) reducing before lettering changes letters in >=10% of stanzas (gotta/lotta rhyme only reduced),
(b) whole-word judge keeps letters identical after hyphenating reduced forms in 100%,
(c) last-segment judge breaks >=10%."""
import itertools
# word -> (rhyme key perfect, assonance key)
FULL = {"got to":("u","u"),"lot of":("uv","o"),"going to":("u","u"),"do":("u","u"),
        "want to":("u","u"),"sort of":("uv","o"),"kind of":("uv","i"),"fine":("ine","i")}
RED  = {"got to":"gotta","lot of":"lotta","going to":"gonna","do":"do",
        "want to":"wanna","sort of":"sorta","kind of":"kinda","fine":"fine"}
RKEY = {"gotta":("ota","o"),"lotta":("ota","o"),"gonna":("ona","o"),"do":("u","u"),
        "wanna":("ona","o"),"sorta":("orta","o"),"kinda":("inda","i"),"fine":("ine","i")}
HYPH = {"gotta":"got-ta","lotta":"lot-ta","gonna":"gon-na","wanna":"wan-na","sorta":"sor-ta","kinda":"kin-da","fine":"fine","do":"do"}
def letters(keys):
    out=[];perf={};res=[]
    for i,(p,a) in enumerate(keys):
        if sum(1 for k in keys if k[0]==p)>1:
            if p not in perf: perf[p]="ABCD"[len(perf)]
            out.append(perf[p]);res.append(a)
        else: out.append(None)
    for i,(p,a) in enumerate(keys):
        if out[i] is None:
            hit=[perf[q] for (q,b) in keys if q in perf and b==a]
            out[i]=hit[0].lower() if hit else "x"
    return "".join(out)
def norm(s): return s
def key_whole(w): return RKEY[w]
def key_last(h):  # last-segment judge: rhyme on text after final hyphen
    seg=h.split("-")[-1]
    return RKEY.get(seg,(seg,seg[-1]))
pool=list(FULL); n=0;a=b=c=0
for st in itertools.product(pool,repeat=4):
    n+=1
    full=letters([FULL[w] for w in st])
    red=[RED[w] for w in st]
    lr=letters([RKEY[w] for w in red])
    if lr!=full:a+=1
    lh=letters([key_whole(w) for w in red])  # hyphen stripped/whole-word
    if lh!=lr:b+=1
    ll=letters([key_last(HYPH[w]) for w in red])
    if ll!=lr:c+=1
print(f"stanzas={n} reduction_changes_letters={a} ({a/n:.1%}) whole_word_hyphen_breaks={b} ({b/n:.1%}) last_segment_breaks={c} ({c/n:.1%})")
ok = a/n>=0.10 and b==0 and c/n>=0.10
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" reduction flips {a/n:.1%}, whole-word hyphen breaks {b}, last-segment breaks {c/n:.1%}")
