import itertools
def verdict(keys):
    last={};cds=[];first=None
    for i,k in enumerate(keys):
        if k is None: continue
        if k in last:
            cds.append(i-last[k])
            if first is None: first=i+1
        last[k]=i
    if not cds: return "none"
    return "stable" if max(cds)<=1 and first<=2 else "open"
def keys(assign,hyph,judge):
    out=[]
    for i,g in enumerate(assign):
        if i in hyph and judge=="last": out.append(None)   # fragment rhymes with nothing
        else: out.append(g)
    return out
named={"AABB":(0,0,1,1),"ABAB":(0,1,0,1),"ABBA":(0,1,1,0),"XXAA":(2,3,0,0)}
by_k={0:[0,0],1:[0,0],2:[0,0],3:[0,0],4:[0,0]}
whole_flips=0;total=0
for a in itertools.product(range(4),repeat=4):
    base=verdict(keys(a,set(),"whole"))
    for r in range(5):
        for h in itertools.combinations(range(4),r):
            total+=1
            if verdict(keys(a,set(h),"whole"))!=base: whole_flips+=1
            by_k[r][1]+=1
            if verdict(keys(a,set(h),"last"))!=base: by_k[r][0]+=1
print("flips by #hyphenated end words (last-segment):",{r:f"{v[0]}/{v[1]}" for r,v in by_k.items()})
print("whole-word judge flips:",whole_flips,"of",total)
for n,a in named.items():
    base=verdict(keys(a,set(),"whole"))
    one=[verdict(keys(a,{i},"last")) for i in range(4)]
    print(n,"plain",base,"one-line hyphenated verdicts",one)
tot1=by_k[1][0]
ok=whole_flips==0 and by_k[0][0]==0 and tot1>0
print("RESULT:","PASS" if ok else "FAIL",f"last-segment flips {tot1}/{by_k[1][1]} single-hyphen cases, {sum(v[0] for v in by_k.values())}/{total} overall; whole-word {whole_flips}")
