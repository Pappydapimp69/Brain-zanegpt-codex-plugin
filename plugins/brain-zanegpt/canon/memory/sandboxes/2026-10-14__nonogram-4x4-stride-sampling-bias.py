# 4x4 nonograms: exhaustive 65536 pictures; unique-clue rate, line-solvable rate, and bias of fixed-stride samples.
# PREDICTION (before run): unique ~79.9%; line propagation fails on 1-4% of unique; stride 7 (coprime) within 1 pt of truth,
# stride 256 (one picture per row-0 pattern, aligned to the bit layout) off by more than 5 pts.
from itertools import product
N=4
def clue(line):
    out=[];run=0
    for v in line:
        if v: run+=1
        elif run: out.append(run);run=0
    if run: out.append(run)
    return tuple(out)
LINES=list(product((0,1),repeat=N)); BYCLUE={}
for l in LINES: BYCLUE.setdefault(clue(l),[]).append(l)
def pic(i): return tuple(tuple((i>>(N*r+c))&1 for c in range(N)) for r in range(N))
def clues(p): return (tuple(clue(r) for r in p), tuple(clue(c) for c in zip(*p)))
allp=[pic(i) for i in range(1<<(N*N))]
groups={}
for i,p in enumerate(allp): groups.setdefault(clues(p),[]).append(i)
unique=[g[0] for g in groups.values() if len(g)==1]
isuni=set(unique)
def solve(cl):
    rc,cc=cl; g=[[None]*N for _ in range(N)]; ch=True
    while ch:
        ch=False
        for axis,cs in ((0,rc),(1,cc)):
            for k in range(N):
                cur=[g[k][j] if axis==0 else g[j][k] for j in range(N)]
                ok=[l for l in BYCLUE[cs[k]] if all(c is None or c==v for c,v in zip(cur,l))]
                for j in range(N):
                    vals={l[j] for l in ok}
                    if len(vals)==1 and cur[j] is None:
                        v=vals.pop(); ch=True
                        if axis==0: g[k][j]=v
                        else: g[j][k]=v
    return all(v is not None for row in g for v in row)
ls=[i for i in unique if solve(clues(allp[i]))]
tot=1<<(N*N)
print("pictures",tot,"unique",len(unique),"%.1f%%"%(100*len(unique)/tot),"line-solvable among unique",len(ls),"fail %.2f%%"%(100*(len(unique)-len(ls))/len(unique)))
truth=len(unique)/tot
def sample(stride): 
    idx=range(0,tot,stride); return sum(1 for i in idx if i in isuni)/len(idx)
res={}
for s in (1,3,7,64,255,256,4096):
    res[s]=sample(s); print("stride",s,"unique rate %.1f%% (err %+.1f pts)"%(100*res[s],100*(res[s]-truth)))
fail=100*(len(unique)-len(ls))/len(unique)
ok=abs(truth-0.799)<0.005 and 1<=fail<=4 and abs(res[7]-truth)<0.01 and abs(res[64]-truth)>0.05 and abs(res[4096]-truth)>0.05
print("RESULT: %s unique %.1f%%, line-solve fail %.2f%% of unique, stride7 err %+.1f pts, stride64 err %+.1f pts (my stride256 guess missed: %+.1f), stride4096 err %+.1f pts"%("PASS" if ok else "FAIL",100*truth,fail,100*(res[7]-truth),100*(res[64]-truth),100*(res[256]-truth),100*(res[4096]-truth)))
