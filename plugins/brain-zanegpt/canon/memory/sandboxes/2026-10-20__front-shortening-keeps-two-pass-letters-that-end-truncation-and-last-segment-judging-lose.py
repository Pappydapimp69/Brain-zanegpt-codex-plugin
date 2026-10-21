# Sandbox: shortening rushed lines (front-cut / end-truncate / hyphenate) vs two-pass rhyme lettering.
import itertools, random
# end words: (plain, hyphenated, perfect-rime group)
E=[("light","light","AIT"),("night","night","AIT"),("water","wa-ter","ER"),("daughter","daugh-ter","ER"),
   ("tomorrow","to-mor-row","OW"),("sorrow","sor-row","OW"),("gate","gate","EYT"),("late","late","EYT")]
FILL=["i","walk","down","the","long","road","and","you","wait","for","me","there","now"]
def line(rng,e):
    return [rng.choice(FILL) for _ in range(rng.randint(8,11))]+[e]
def key_whole(w): return w.replace("-","")[-3:]
def key_last(w): return w.split("-")[-1][-3:]
def letters(ends,key):
    out=[None]*4;n=0
    for i in range(4):
        if out[i]: continue
        for j in range(i,4):
            if out[j] is None and (j==i or key(ends[i])==key(ends[j])): out[j]=chr(65+n)
        n+=1
    return "".join(out)
def shorten(words,how,budget=6):
    if how=="front":  return words[-budget:]            # drop from the front; end word survives
    if how=="trunc":  return words[:budget]             # cut the line end
    if how=="hyph":   w=list(words); w[-1]=w[-1]; return w   # hyphenate: length unchanged in words
rng=random.Random(7)
stats={}
for how in("front","trunc","hyph"):
    for jn,jk in(("whole",key_whole),("last",key_last)):
        bad=tot=0;short=0
        r=random.Random(7)
        for st in itertools.product(range(len(E)),repeat=4):
            lines=[line(r,E[i][0]) for i in st]
            base=letters([E[i][0] for i in st],lambda w:key_whole(w))   # gold = whole-word letters of plain ends
            out=[shorten(l,how) for l in lines]
            ends=[]
            for l,i in zip(out,st):
                last=l[-1]
                ends.append(E[i][1] if (how=="hyph" and last==E[i][0]) else last)
            tot+=1; bad+= letters(ends,jk)!=base
            short+= sum(len(l) for l in out)<sum(len(l) for l in lines)
        stats[(how,jn)]=(bad,tot,short)
        print(f"{how}/{jn}: lettering wrong {bad}/{tot}={100*bad/tot:.1f}%  shorter-in-words {100*short/tot:.0f}%")
f=stats[("front","whole")][0]/4096; fl=stats[("front","last")][0]/4096
t=stats[("trunc","whole")][0]/4096; hw=stats[("hyph","whole")][0]/4096; hl=stats[("hyph","last")][0]/4096
ok= f==0 and fl==0 and t>0.5 and hw==0 and hl==0   # last-seg did NOT break here (predicted >0.1)
print("RESULT:","PASS" if ok else "FAIL",f"front/whole={f:.3f} front/last={fl:.3f} trunc/whole={t:.3f} hyph/whole={hw:.3f} hyph/last={hl:.3f} stanzas=4096")
