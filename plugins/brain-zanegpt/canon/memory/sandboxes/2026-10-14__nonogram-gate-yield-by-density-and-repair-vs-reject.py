# Nonogram two-gate yield (unique clues, line-solvable) by fill density, and repair-by-flip vs reject-and-retry.
from itertools import product
from collections import Counter, defaultdict
from math import comb
def clue(bits):
    out=[];run=0
    for b in bits:
        if b: run+=1
        elif run: out.append(run); run=0
    if run: out.append(run)
    return tuple(out)
def fillings(cl,n):
    res=[]
    def rec(i,k,cur):
        if k==len(cl):
            res.append(tuple(cur+[0]*(n-len(cur)))); return
        for s in range(i,n-cl[k]+1):
            rec(s+cl[k]+1,k+1,cur+[0]*(s-len(cur))+[1]*cl[k]) if True else None
    rec(0,0,[]); return res
# formula check vs enumeration (kernel claim): C(n-s+1,k)
mis=0;cnt=0
for n in range(1,9):
    for cl in {clue(b) for b in product((0,1),repeat=n)}:
        cnt+=1; mis+= len(fillings(cl,n))!=comb(n-sum(cl)+1,len(cl))
print("formula clues checked",cnt,"mismatches",mis)
FC={}
def fl(cl,n):
    k=(cl,n)
    if k not in FC: FC[k]=fillings(cl,n)
    return FC[k]
def solve_lines(R,C,h,w):
    # grid cells: None unknown; propagate
    g=[[None]*w for _ in range(h)]
    ch=True
    while ch:
        ch=False
        for lines,n,get,setc in ((R,w,lambda i:g[i],lambda i,j,v:g[i].__setitem__(j,v)),(C,h,lambda j:[g[r][j] for r in range(h)],lambda j,i,v:g[i].__setitem__(j,v))):
            for i,cl in enumerate(lines):
                cur=get(i); ok=[f for f in fl(cl,n) if all(c is None or c==x for c,x in zip(cur,f))]
                if not ok: return None
                for p in range(n):
                    vs={f[p] for f in ok}
                    if len(vs)==1 and cur[p] is None:
                        setc(i,p,vs.pop()); ch=True
    return all(c is not None for r in g for c in r)
def analyse(h,w):
    groups=defaultdict(list)
    for m in range(1<<(h*w)):
        cells=[(m>>(r*w+c))&1 for r in range(h) for c in range(w)]
        rows=tuple(clue(cells[r*w:(r+1)*w]) for r in range(h)); cols=tuple(clue(cells[c::w]) for c in range(w))
        groups[(rows,cols)].append(m)
    uniq={k:v[0] for k,v in groups.items() if len(v)==1}
    by=defaultdict(lambda:[0,0,0]) # density -> [total, unique, solvable]
    popc=lambda m:bin(m).count("1")
    for m in range(1<<(h*w)): by[popc(m)][0]+=1
    solv={}
    for k,m in uniq.items():
        by[popc(m)][1]+=1
        s=bool(solve_lines(k[0],k[1],h,w)); solv[m]=s; by[popc(m)][2]+=s
    return groups,uniq,solv,by
def sig(m,h,w):
    cells=[(m>>(r*w+c))&1 for r in range(h) for c in range(w)]
    return (tuple(clue(cells[r*w:(r+1)*w]) for r in range(h)),tuple(clue(cells[c::w]) for c in range(w)))
out={}
for (h,w) in ((4,4),(4,5)):
    groups,uniq,solv,by=analyse(h,w)
    N=1<<(h*w); U=len(uniq); S=sum(solv.values())
    print(f"{h}x{w}: pictures={N} unique={U} ({100*U/N:.1f}%) line-solvable-of-unique={S} ({100*S/U:.1f}%) stalled={U-S} ({100*(U-S)/U:.1f}%)")
    row=[(d,by[d][0],by[d][1],by[d][2]) for d in sorted(by)]
    for d,t,u,s in row: print(f"  fill={d:2d} total={t:6d} unique%={100*u/t:5.1f} stalled%ofUnique={(100*(u-s)/u if u else 0):5.1f}")
    good={m for m,s in solv.items() if s}
    # reject-and-retry yield vs repair-by-flip on rejects
    rej=[m for m in range(N) if m not in good]
    fixed1=fixed2=0
    for m in rej:
        n1=[m^(1<<i) for i in range(h*w)]
        if any(x in good for x in n1): fixed1+=1; fixed2+=1; continue
        if any((x^(1<<i)) in good for x in n1 for i in range(h*w)): fixed2+=1
    print(f"  gate yield={100*len(good)/N:.1f}% expected tries={N/len(good):.2f}; rejects={len(rej)} repaired<=1 flip={fixed1} ({100*fixed1/len(rej):.1f}%) <=2 flips={fixed2} ({100*fixed2/len(rej):.1f}%)")
    out[(h,w)]=(U/N,(U-S)/U,fixed1/len(rej),fixed2/len(rej),by)
mid=lambda by: max(by,key=lambda d:(by[d][1]-by[d][2])/max(by[d][1],1))
ok = all(abs(out[k][1]-0.02)<0.02 for k in out) and all(out[k][3]>0.95 for k in out)
print("RESULT: %s 4x4 unique %.1f%% stalled %.1f%%, 4x5 unique %.1f%% stalled %.1f%%; formula %d/%d clues exact; repair within 2 flips fixes %.1f%% / %.1f%% of rejects (peak-stall fill 4x4=%d, 4x5=%d)" % ("PASS" if ok and mis==0 else "FAIL",100*out[(4,4)][0],100*out[(4,4)][1],100*out[(4,5)][0],100*out[(4,5)][1],cnt-mis,cnt,100*out[(4,4)][3],100*out[(4,5)][3],mid(out[(4,4)][4]),mid(out[(4,5)][4])))
