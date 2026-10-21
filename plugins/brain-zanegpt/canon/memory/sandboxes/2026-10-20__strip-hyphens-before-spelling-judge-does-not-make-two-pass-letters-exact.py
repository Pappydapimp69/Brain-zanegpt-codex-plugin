# Sandbox: two-pass lettering + spelling rhyme judge + hyphenated end words.
import itertools
# word: (spelling, rime_group, vowel_group)  rime_group = perfect, vowel = assonance
W = {
 "light":("light","AIT","AI"),"night":("night","AIT","AI"),"flight":("flight","AIT","AI"),
 
 
 
 "gate":("gate","EYT","EY"),"late":("late","EYT","EY"),
 "water":("wa-ter","ER","AW"),"daughter":("daugh-ter","ER","AW"),
 "ago":("a-go","OW","AO"),"below":("be-low","OW","AO"),"show":("show","OW","AO"),
 "tomorrow":("to-mor-row","OW","AO"),"borrow":("bor-row","OW","AO"),
}
names=sorted(W)
def seg_last(s): return s.split("-")[-1]
def judge_whole(a,b,strip=True):
    sa,sb=(W[a][0],W[b][0]); 
    if strip: sa,sb=sa.replace("-",""),sb.replace("-","")
    return sa[-2:]==sb[-2:]            # spelling judge: last 3 letters
def judge_last(a,b):
    return seg_last(W[a][0])[-2:]==seg_last(W[b][0])[-2:]
def gold_perfect(a,b): return W[a][1]==W[b][1]
def gold_assonant(a,b): return W[a][2]==W[b][2] and W[a][1]!=W[b][1]
def letters(st,perfect):
    """two-pass: pass1 perfect groups claim letters; pass2 assonance only to leftovers (lowercase marks)."""
    out=[None]*4;nxt=0;L="ABCD"
    for i in range(4):
        if out[i]: continue
        grp=[j for j in range(i,4) if out[j] is None and (j==i or perfect(st[i],st[j]))]
        for j in grp: out[j]=L[nxt]
        nxt+=1
    return "".join(out)
def scheme_gold(st): return letters(st,gold_perfect)
def run(perfect):
    bad=tot=0
    for st in itertools.product(names,repeat=4):
        tot+=1
        if letters(st,perfect)!=scheme_gold(st): bad+=1
    return bad,tot
res={}
for label,j in [("whole+strip",lambda a,b:judge_whole(a,b,True)),
                ("whole-nostrip",lambda a,b:judge_whole(a,b,False)),
                ("lastseg",judge_last)]:
    res[label]=run(j)
for k,(b,t) in res.items(): print(f"{k}: wrong {b}/{t} = {100*b/t:.1f}%")
# break scenario: spelling judge is blind to irregular spellings even when stripped
b,t=res["whole+strip"]
print(f"break-case wrong with strip = {b}")
ok = res["whole+strip"][0]==0 and res["whole-nostrip"][0]>0 and res["lastseg"][0]>0
print("RESULT:", "PASS" if ok else "FAIL",
      " ".join(f"{k}={100*v[0]/v[1]:.1f}%" for k,v in res.items()), f"stanzas={t}")
