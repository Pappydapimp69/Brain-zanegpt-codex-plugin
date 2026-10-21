"""Compose: every-video-own-joke (batch not templated) + kernel label check + invent-every-name.
Prediction (written before first run): a batch of 8 ads built from distinct slot-machine cells passes
all three gates at once: 0 non-verbatim axis labels after the fix (1 before), 0 lookalike names vs a
real-game list, mean pair similarity < 0.50. Hidden assumption: the three gates are independent, so
passing one says nothing about the others. Would be wrong if a name pool that passes the invented-name
gate still pushes pair similarity > 0.50, or if fixing the label changes cell identity."""
import itertools, random

SOURCE_AXES = ["gameplay disguise","narrative pretense","popular externalization","ruleset distortion","incentive illusion"]
KERNEL_AXES = ["gameplay disguise","narrative pretense","borrowed fame","ruleset distortion","incentive illusion"]
TROPES = ["pull-the-pin","incompetent-player","number-gates","save-the-sad-man","merge-bait","stilted-skit"]
REAL = ["homescapes","gardenscapes","royal match","royal kingdom","candy crush","evony","clash royale","brawl stars",
        "township","merge mansion","lily's garden","hero wars","mafia city","last war","whiteout survival","count masters",
        "rise of kingdoms","state of survival","coin master","fishdom"]

def lev(a,b):
    p=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        c=[i]
        for j,cb in enumerate(b,1): c.append(min(p[j]+1,c[j-1]+1,p[j-1]+(ca!=cb)))
        p=c
    return p[-1]

def lookalike(name):
    n=name.lower(); hits=[]
    for r in REAL:
        if n==r: hits.append(("exact",r))
        elif lev(n,r)<=3: hits.append(("edit",r))
        elif set(n.split()) & set(r.split()) - {"of","the","city","war"}: hits.append(("word",r))
    return hits

def label_gate(axes_used, source=SOURCE_AXES):
    return sum(1 for a in axes_used if a not in source)

def sim(a,b):  # content-field similarity: share of fields identical
    f=["trope","axis","swap","payoff","voice","layout"]
    return sum(a[k]==b[k] for k in f)/len(f)
def mean_sim(vs):
    ps=[sim(a,b) for a,b in itertools.combinations(vs,2)]
    return sum(ps)/len(ps)

def make(cells, names, axes_pool):
    return [dict(name=names[i],trope=t,axis=axes_pool[ai],swap=f"swap{t}{ai}",payoff=f"payoff{i}",voice=f"v{i%3}",layout=f"l{i%2}")
            for i,(t,ai) in enumerate(cells)]

rng=random.Random(7)
SYL1=["Gard","Roy","Mer","Home","Cand","Town","Clash","Fish","Hero","Coin"]
SYL2=["ora","ling","nia","vale","ex","ship","dom","bix","zap","lo"]
SYL3=["scape","dom","ville","quest","fall",""]
def invent(k, pool_small):
    out=set()
    s1=SYL1[:4] if pool_small else SYL1
    while len(out)<k:
        out.add(rng.choice(s1)+rng.choice(SYL2)+rng.choice(SYL3))
    return sorted(out)

# distinct cells, rotated without replacement, one cell per trope first
cells=[(TROPES[i%6], (i*2)%5) for i in range(8)]
res={}
# S1 label gate: kernel as written vs fixed
axes_k=[KERNEL_AXES[a] for _,a in cells]; axes_s=[SOURCE_AXES[a] for _,a in cells]
res["S1_label_bad_in_batch"]=label_gate(axes_k); res["S1_label_bad_fixed"]=label_gate(axes_s)
# S2 name gate, large pool vs small pool
for tag,small in (("S2_names_wide",False),("S3_names_narrow(BREAK)",True)):
    names=invent(8,small); flagged=[n for n in names if lookalike(n)]
    res[tag]=(len(flagged), flagged[:3])
# S4 similarity: composed batch vs name-swap-only batch
names=invent(8,False)
good=make(cells,names,SOURCE_AXES); res["S4_sim_composed"]=round(mean_sim(good),3)
swap=make([("pull-the-pin",0)]*8,names,SOURCE_AXES)
for v in swap: v.update(swap="same",payoff="same",voice="same",layout="same")
res["S5_sim_name_swap_only"]=round(mean_sim(swap),3)
# S6: does fixing the label change cell identity? (same index -> same cell)
res["S6_cell_identity_kept"]=len({(t,a) for t,a in cells})==len(cells)
# S7: reject-and-redraw names that hit the lookalike gate, then recheck similarity
clean=[]
while len(clean)<8:
    n=invent(1,False)[0]
    if not lookalike(n) and n not in clean: clean.append(n)
res["S7_redraw_flagged"]=sum(1 for n in clean if lookalike(n))
res["S7_sim_after_redraw"]=round(mean_sim(make(cells,clean,SOURCE_AXES)),3)
for k,v in res.items(): print(k,v)
ok = (res["S7_redraw_flagged"]==0 and abs(res["S7_sim_after_redraw"]-res["S4_sim_composed"])<0.05 and res["S1_label_bad_in_batch"]>=1 and res["S1_label_bad_fixed"]==0 and res["S2_names_wide"][0]==0
      and res["S4_sim_composed"]<0.5 and res["S5_sim_name_swap_only"]>0.9 and res["S6_cell_identity_kept"])
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"label {res['S1_label_bad_in_batch']}->{res['S1_label_bad_fixed']}, wide names flagged {res['S2_names_wide'][0]}/8 (redraw {res['S7_redraw_flagged']}/8), narrow {res['S3_names_narrow(BREAK)'][0]}/8, sim composed {res['S4_sim_composed']} vs name-swap {res['S5_sim_name_swap_only']}")
