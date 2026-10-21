# Sandbox: reduced forms (gonna/wanna) as line ENDINGS, two-pass lettering, hyphenation.
import itertools
# line-ending token: (full-form ending, reduced ending, gold rime group of the SUNG form)
# Full forms "going to"/"want to"/"have to" all end in the word "to" -> spelling judge calls them perfect rhymes.
L = {
 "g_to":("going to","gon-na","NA"),   # sung: gonna
 "w_to":("want to","wan-na","NA"),    # sung: wanna
 "h_to":("have to","haf-ta","TA"),    # sung: hafta
 "k_of":("kind of","kin-da","DA"),    # sung: kinda
 "go":("go","go","OH"),"know":("know","know","OH"),
}
names=sorted(L)
def key(tok,form,strip):
    s=L[tok][0 if form=="full" else 1]
    if strip: s=s.replace("-","")
    return s.split()[-1][-2:] if form=="full" else s[-3:]
def judge(form,strip,lastseg=False):
    def j(a,b):
        if lastseg and form=="red":
            return L[a][1].split("-")[-1][-2:]==L[b][1].split("-")[-1][-2:]
        return key(a,form,strip)==key(b,form,strip)
    return j
def gold(a,b): return L[a][2]==L[b][2]
def letters(st,perf):
    out=[None]*4;n=0
    for i in range(4):
        if out[i]: continue
        for j in range(i,4):
            if out[j] is None and (j==i or perf(st[i],st[j])): out[j]=ABC[n]
        n+=1
    return "".join(out)
ABC="ABCD"
def run(j):
    bad=tot=0
    for st in itertools.product(names,repeat=4):
        tot+=1; bad+= letters(st,j)!=letters(st,gold)
    return bad,tot
sc={"full-form":judge("full",True),"reduced-stripped":judge("red",True),
    "reduced-hyphenated-whole":judge("red",False),"reduced-lastseg(BREAK)":judge("red",True,True)}
res={k:run(j) for k,j in sc.items()}
for k,(b,t) in res.items(): print(f"{k}: wrong {b}/{t} = {100*b/t:.1f}%")
ok=res["reduced-stripped"][0]<res["full-form"][0]
print("RESULT:","PASS" if ok else "FAIL"," ".join(f"{k}={100*b/t:.1f}%" for k,(b,t) in res.items()),f"stanzas={t}")
