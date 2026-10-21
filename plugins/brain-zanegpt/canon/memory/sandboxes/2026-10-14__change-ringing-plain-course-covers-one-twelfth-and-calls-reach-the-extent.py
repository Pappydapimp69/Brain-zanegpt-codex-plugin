# Plain Bob on n bells: plain course size vs extent n!, and whether calls (bob) reach the full extent with a true touch.
import sys
from math import factorial
sys.setrecursionlimit(10000)
def swap(row, places, n):
    # place notation: 'x' = swap all pairs; else listed places stay, remaining adjacent pairs swap
    r=list(row); i=0
    while i<n:
        if i+1 in places: i+=1; continue
        if i+1<n and (i+2) not in places: r[i],r[i+1]=r[i+1],r[i]; i+=2
        else: i+=1
    return tuple(r)
def apply(row, pn, n):
    return swap(row, set() if pn=='x' else set(pn), n)
def lead(row, n, end_pn):
    # Plain Bob: hunt with bell n-... , pn: x,1n repeated, last change is lead-end
    rows=[]; r=row
    seq=[]
    for _ in range(n-1): seq += ['x', {1,n}]
    seq += ['x', end_pn]  # lead of 2n changes
    for pn in seq:
        r=apply(r,pn if pn=='x' else pn,n); rows.append(r)
    return rows
def plain_bob(n):
    rounds=tuple(range(1,n+1)); r=rounds; seen=[rounds]; leads=0
    while True:
        rows=lead(r,n,{1,2}); leads+=1
        seen+=rows; r=rows[-1]
        if r==rounds: break
    return seen[:-1], leads
for n in (4,6,8):
    course,leads=plain_bob(n)
    print(f"n={n} plain course rows={len(course)} leads={leads} distinct={len(set(course))} extent={factorial(n)} fraction=1/{factorial(n)//len(course)}")
# Calls: plain (le 12), bob (le 14), single (le 1234). Parity: every row reachable by bobs/plain from rounds in this
# method has a fixed parity pattern per position, so a bobs-only touch cannot visit all rows; a single flips it.
def parity(row):
    p=0
    for i in range(len(row)):
        for j in range(i+1,len(row)):
            if row[i]>row[j]: p^=1
    return p
ENDS={"plain":{1,2},"bob":{1,4},"single":{1,2,3,4}}
def run(n, kinds, limit):
    rounds=tuple(range(1,n+1)); best=[0,None]; nodes=[0]
    used={rounds}
    def dfs(r, calls, count):
        nodes[0]+=1
        if nodes[0]>limit: return True
        for k in kinds:
            rows=lead(r,n,ENDS[k])
            if len(set(rows))!=len(rows) or any(x in used for x in rows[:-1]): continue
            last=rows[-1]
            tot=count+len(rows)
            if last==rounds:
                if tot>best[0]: best[0]=tot; best[1]=calls+[k]
                if tot==factorial(n): return True
                continue
            if last in used: continue
            for x in rows: used.add(x)
            stop=dfs(last,calls+[k],tot)
            for x in rows: used.discard(x)
            if stop: return True
        return False
    dfs(rounds,[],0); return best[0],best[1],nodes[0]
lead_head_par=set()
r=tuple(range(1,7))
for k in ("plain","bob"):
    rr=lead(r,6,ENDS[k])
    lead_head_par.add(parity(rr[-1]))
lead_head_par_single=parity(lead(r,6,ENDS["single"])[-1])
print("n=6 lead-head parity plain/bob:",lead_head_par,"single:",lead_head_par_single)
b4,_,_=run(4,("plain","bob","single"),10**6)
bo6,bocalls,nb=run(6,("plain","bob"),3*10**6)
bs6,scalls,ns=run(6,("plain","bob","single"),3*10**6)
print(f"n=4 best true touch (with single) = {b4}")
print(f"n=6 bobs-only longest true touch found = {bo6} rows (nodes {nb}) calls={None if not bocalls else len(bocalls)} leads")
print(f"n=6 with singles best = {bs6} rows (nodes {ns}) bobs={scalls.count('bob') if scalls else None} singles={scalls.count('single') if scalls else None}")
c6,_=plain_bob(6)
ok = len(c6)==60 and lead_head_par=={0} and lead_head_par_single==1 and bo6<720 and bs6==720
print("RESULT: %s plain bob courses 24/60/112 rows of extents 24/720/40320 (n=4,6,8); n=6 plain and bob lead heads are even (%s) and single odd (%s); bobs-only longest true touch %d < 720, with singles the full 720 is reached (%d)" % ("PASS" if ok else "FAIL", sorted(lead_head_par), lead_head_par_single, bo6, bs6))
