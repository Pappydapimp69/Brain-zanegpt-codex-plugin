# Prediction (written first): Plain Bob Minimus (4 bells) plain course = 24 distinct rows = the full extent 4!.
# Plain Bob Doubles (5 bells) plain course = 40 distinct rows (1/3 of 5! = 120) and returns to rounds;
# calling bobs (lead-end 145 instead of 125) links courses toward the 120-row extent; a bob called at only
# ONE lead end does NOT reach 120 (built to break "any bob extends the course").
from math import factorial
def apply(row,pn,n):
    r=list(row)
    if pn=='x': places=set()
    else: places={int(c) for c in pn}
    i=1
    while i<n:
        if i in places: i+=1; continue
        if i+1 in places or i+1>n: i+=1; continue
        r[i-1],r[i]=r[i],r[i-1]; i+=2
    return tuple(r)
def parse(s): return ['x' if t=='x' else t for t in s.replace('x','.x.').replace('..','.').strip('.').split('.')]
def ring(n,lead,bob_end,calls,max_leads=60):
    rounds=tuple(range(1,n+1)); row=rounds; rows=[]
    pl=parse(lead); body=pl[:-1]
    for k in range(max_leads):
        for pn in body+[bob_end if k in calls else pl[-1]]:
            row=apply(row,pn,n); rows.append(row)
        if row==rounds: return rows,True
    return rows,False
from itertools import combinations
mini,_=ring(4,"x14x14x14x12","14",set())
dop,ret=ring(5,"5.1.5.1.5.1.5.1.5.125","145",set())
print("minimus plain course rows",len(mini),"distinct",len(set(mini)),"of",factorial(4))
print("doubles plain course rows",len(dop),"distinct",len(set(dop)),"of",factorial(5),"returns",ret)
# bob at one lead end only
one,r1=ring(5,"5.1.5.1.5.1.5.1.5.125","145",{0})
print("one bob (lead 0): rows",len(one),"distinct",len(set(one)),"returns",r1)
# search for bob sets (lead indexes < 12) that reach the full extent with no repeated row
best=None;full=[];tested=0
for k in range(1,7):
    for c in combinations(range(12),k):
        rows,ret=ring(5,"5.1.5.1.5.1.5.1.5.125","145",set(c)); tested+=1
        if ret and len(rows)==120 and len(set(rows))==120: full.append(c)
print("bob sets tested",tested,"reaching true 120-row extent",len(full),"smallest",full[:1])
for c in full[:1]: print("first extent bob set",c)
ok=len(mini)==24==len(set(mini)) and len(dop)==40==len(set(dop)) and ret is True and len(set(one))<120 and len(full)>0
print("RESULT:","PASS" if ok else "FAIL",f"Minimus course {len(mini)}/24 distinct, Doubles plain course {len(dop)} of 120, one bob stays at {len(set(one))} distinct rows, {len(full)} of {tested} bob sets give a true 120-row extent")
