import itertools
# word: (true syllables, hyphenated form, perfect key)
L={"tonight":(2,"to-night","AIT"),"delight":(2,"de-light","AIT"),"ago":(2,"a-go","OH"),"below":(2,"be-low","OH"),
   "away":(2,"a-way","AY"),"today":(2,"to-day","AY"),"remain":(2,"re-main","AIN"),"explain":(2,"ex-plain","AIN"),
   "night":(1,"night","AIT"),"go":(1,"go","OH"),"day":(1,"day","AY"),"main":(1,"main","AIN")}
FILL=5; BUDGET=6   # line = 5 fillers + end word; true syllables = 5 + word syllables -> 7 > 6 flagged by true count
W=list(L)
def lastseg(w): return w.split("-")[-1]
def key_last_segment(f): return lastseg(f)[-3:]
def key_token(f): return f[-3:]
def letters(keys):
    seen={}; out=[]
    for k in keys:
        seen.setdefault(k,chr(65+len(seen))); out.append(seen[k])
    return "".join(out)
def run(judge, hint):
    changed=0; n=0
    for st in itertools.product(W,repeat=4):
        n+=1
        base=letters([judge(w) for w in st])
        forms=[]
        for w in st:
            flagged = (FILL+L[w][0] > BUDGET) if hint=="true" else (FILL+1 > BUDGET)  # vowel-group-ish undercount: 1 per word
            forms.append(L[w][1] if flagged else w)
        new=letters([judge(f) for f in forms])
        changed+= base!=new
    return changed,n
for name,j in (("last-segment",key_last_segment),("whole-token",key_token)):
    for hint in ("true","undercount"):
        c,n=run(j,hint); print(f"judge={name} hint={hint} letters_changed={c}/{n}")
a=run(key_last_segment,"true")[0]; b=run(key_token,"true")[0]; c=run(key_token,"undercount")[0]
ok = a>0 and b==0 and c==0
print(("RESULT: PASS" if ok else "RESULT: FAIL"),f"last-segment judge letters changed in {a}/20736 stanzas under the true-syllable hint, 0 under the undercount hint (hint silent); whole-token judge changed {b}/{c}")
