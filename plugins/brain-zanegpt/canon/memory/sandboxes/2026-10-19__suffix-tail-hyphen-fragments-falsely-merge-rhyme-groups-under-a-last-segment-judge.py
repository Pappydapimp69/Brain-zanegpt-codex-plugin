import itertools
# word -> (hyphenated form, perfect rime of whole word, stressed vowel)
BANK={
 "running":("run-ning","unning","u"),"sunning":("sun-ning","unning","u"),
 "singing":("sing-ing","inging","i"),"bringing":("bring-ing","inging","i"),
 "dancing":("danc-ing","ancing","a"),"chancing":("chanc-ing","ancing","a"),
 "dreamed":("dream-ed","eamed","e"),"seemed":("seemed","eemed","e"),
 "fire":("fi-re","ire","i2"),"higher":("high-er","igher","i2"),
 "night":("night","ight","i2"),"light":("light","ight","i2"),
}
def key(w,judge):
    h,rime,_=BANK[w]
    if judge=="whole" or "-" not in h: return rime
    seg=h.split("-")[-1]          # last fragment is the key
    return "~"+seg
def letters(stanza,judge):
    ks=[key(w,judge) for w in stanza]
    vs=[BANK[w][2] for w in stanza]
    out=[None]*4;nxt=0;grp={}
    for i,k in enumerate(ks):                  # pass 1: perfect groups
        if ks.count(k)>1:
            if k not in grp: grp[k]=chr(65+len(grp))
            out[i]=grp[k]
    ag={}
    for i,v in enumerate(vs):                  # pass 2: assonance, lowercase, never merges perfect groups
        if out[i] is None:
            if vs.count(v)>1 and v not in ag: ag[v]=chr(97+len(ag))
            out[i]=ag.get(v,"x")
    return "".join(out)
def canon(s):                                  # relabel by first appearance, keep case
    m={};o=""
    for c in s:
        if c=="x": o+=c;continue
        if c not in m: m[c]=(chr(65+len(m)) if c.isupper() else chr(97+len(m)))
        o+=m[c]
    return o
names=list(BANK);tot=0;bad=0;false_merge=0;lost=0;suffix_bad=0;suffix_tot=0
for st in itertools.product(names,repeat=4):
    a=canon(letters(st,"whole"));b=canon(letters(st,"last"));tot+=1
    ing=all(w.endswith("ing") or w.endswith("ed") for w in st)
    if ing: suffix_tot+=1
    if a!=b:
        bad+=1
        if ing: suffix_bad+=1
        if a.count(a[0])>=0 and sum(c.isupper() for c in b)>sum(c.isupper() for c in a): false_merge+=1
        elif sum(c.isupper() for c in b)<sum(c.isupper() for c in a): lost+=1
print("stanzas",tot,"mislettered",bad,"false-merge(more perfect rhymes)",false_merge,"lost(fewer)",lost)
print("suffix-only stanzas",suffix_tot,"mislettered",suffix_bad)
ok=false_merge>0 and lost>0 and suffix_bad>0.5*suffix_tot
print("RESULT:","PASS" if ok else "FAIL",f"last-segment mislettered {bad}/{tot}; false merges {false_merge}, lost rhymes {lost}; suffix-tail stanzas {suffix_bad}/{suffix_tot}")
