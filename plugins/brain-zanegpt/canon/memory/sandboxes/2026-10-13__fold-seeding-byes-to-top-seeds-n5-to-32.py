# Prediction (written before run): for every n in 5..32 fold seeding gives byes to seeds 1..(m-n),
# no bye-vs-bye pair, games = n-1, chalk final = 1 v 2, seeds 1-4 not meeting before semis;
# sequential pairing with byes to top seeds fails the 1v2 final for most n; upset of seed 1 keeps seed 2 in final.
def fold(m):
    o=[1]
    while len(o)<m:
        s=len(o)*2
        o=[x for p in o for x in (p,s+1-p)]
    return o
def play(order,n,upset=None):
    rnd=1;cur=order[:];games=0;meet={}
    while len(cur)>1:
        nxt=[]
        for i in range(0,len(cur),2):
            a,b=cur[i],cur[i+1]
            if a>n and b>n: raise SystemExit("bye v bye")
            if b>n: nxt.append(a);continue
            if a>n: nxt.append(b);continue
            games+=1;meet[frozenset((a,b))]=rnd
            w=min(a,b)
            if upset and frozenset((a,b))==frozenset(upset): w=max(a,b)
            nxt.append(w)
        cur=nxt;rnd+=1
    return cur[0],games,meet,rnd-1
def seqorder(m):  # adjacent: 1,2,3,4... byes at the end slots
    return list(range(1,m+1))
bad=[];sumpairs=0
for n in range(5,33):
    m=1
    while m<n:m*=2
    o=fold(m)
    byes=sorted(o[i+1 if o[i]<=n and o[i+1]>n else i] for i in range(0,m,2) if o[i]>n or o[i+1]>n)
    byeseeds=sorted(min(o[i],o[i+1]) for i in range(0,m,2) if max(o[i],o[i+1])>n)
    if byeseeds!=list(range(1,m-n+1)): bad.append(("byes",n))
    if any(o[i]+o[i+1]!=m+1 for i in range(0,m,2)): bad.append(("sum",n))
    w,g,meet,R=play(o,n)
    if g!=n-1: bad.append(("games",n))
    if meet.get(frozenset((1,2)))!=R: bad.append(("final",n))
    for a in (1,2,3,4):
        for b in (1,2,3,4):
            if a<b and meet.get(frozenset((a,b)),R)<R-1: bad.append(("early",n,a,b))
print("fold failures:",bad)
seqfail=0
for n in range(5,33):
    m=1
    while m<n:m*=2
    try:
        w,g,meet,R=play(seqorder(m),n)
    except SystemExit: seqfail+=1;continue
    if meet.get(frozenset((1,2)))!=R: seqfail+=1
print("sequential 1v2-final failures:",seqfail,"of 28")
# break: upset of seed 1 in its first real match, n=11 (m=16)
n=11;o=fold(16)
_,_,meet,R=play(o,n)
first=[k for k,v in meet.items() if 1 in k and v==min(v2 for k2,v2 in meet.items() if 1 in k2)][0]
w,g,meet2,R=play(o,n,upset=tuple(first))
fin=[tuple(sorted(k)) for k,v in meet2.items() if v==R][0]
print("n=11 upset of seed1 by",sorted(first),"-> final",fin,"seed2 in final:",2 in fin)
# break 2: byes to top seeds do NOT make seeds 3,4 safe from 1,2 at n=5..: check round seeds 1-4 first possible meeting exists
ok=not bad and seqfail>=20 and 2 in fin
print("RESULT:","PASS" if ok else "FAIL","fold: byes to seeds 1..m-n, games n-1, final 1v2, no early top-4 meeting at all 28 n; sequential fails %d/28; seed-1 upset keeps seed 2 in final (%s)"%(seqfail,fin))
