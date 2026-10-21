# Eager-propagation WFC (no backtracking) + deterministic restart: which contradictions does restart rescue?
# Tiles = (N,E,S,W) sockets in {0,1}; 3-tile sets from 16 possible tiles; 4x4 grid.
import itertools
N=4
TILES=list(itertools.product((0,1),repeat=4))
def ok(a,b,d):  # a's side d facing b. d: 0 E-neighbor,1 S-neighbor
    return a[1]==b[3] if d==0 else a[2]==b[0]
def propagate(dom):
    ch=True
    while ch:
        ch=False
        for r in range(N):
            for c in range(N):
                for (dr,dc,d) in ((0,1,0),(1,0,1)):
                    r2,c2=r+dr,c+dc
                    if r2>=N or c2>=N: continue
                    A,B=dom[r][c],dom[r2][c2]
                    nA=[a for a in A if any(ok(a,b,d) for b in B)]
                    nB=[b for b in B if any(ok(a,b,d) for a in A)]
                    if len(nA)<len(A) or len(nB)<len(B):
                        dom[r][c],dom[r2][c2]=nA,nB; ch=True
                    if not nA or not nB: return False
    return True
def run(ts,attempt):
    dom=[[list(ts) for _ in range(N)] for _ in range(N)]
    if not propagate(dom): return False
    while True:
        cand=[(len(dom[r][c]),r,c) for r in range(N) for c in range(N) if len(dom[r][c])>1]
        if not cand: return True
        _,r,c=min(cand)
        d=dom[r][c]; dom[r][c]=[d[(attempt+r*3+c)%len(d)]]   # deterministic pick keyed by attempt
        if not propagate(dom): return False
def solvable(ts):  # exhaustive via backtracking
    g=[[None]*N for _ in range(N)]
    def rec(i):
        if i==N*N: return True
        r,c=divmod(i,N)
        for t in ts:
            if c and not ok(g[r][c-1],t,0): continue
            if r and not ok(g[r-1][c],t,1): continue
            g[r][c]=t
            if rec(i+1): return True
        g[r][c]=None; return False
    return rec(0)
K=8
first_ok=rescued=lost_unsat=lost_sat=0; tot=0
for ts in itertools.combinations(TILES,3):
    tot+=1
    if run(ts,0): first_ok+=1; continue
    if any(run(ts,a) for a in range(1,K+1)): rescued+=1; continue
    if solvable(ts): lost_sat+=1
    else: lost_unsat+=1
print(f"sets={tot} first-try ok={first_ok} rescued by <= {K} restarts={rescued} "
      f"never rescued: satisfiable={lost_sat} unsatisfiable={lost_unsat}")
fail=tot-first_ok
print(f"first-try failures={fail}; restart rescue rate={rescued}/{fail}")
ok_=lost_unsat>0 and rescued>0 and fail>0
print("RESULT:", "PASS" if ok_ else "FAIL",
 f"restart rescued {rescued}/{fail}; {lost_unsat} unrescuable sets have no solution at all, {lost_sat} satisfiable ones still lost")
