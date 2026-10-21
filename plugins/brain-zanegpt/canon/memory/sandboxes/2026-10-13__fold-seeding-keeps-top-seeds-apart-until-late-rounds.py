# Single-elimination bracket seeding: fold (1 vs N, recursive) vs adjacent (1v2,3v4,...). Deterministic.
def fold(n):
    s=[1]
    while len(s)<n:
        m=len(s)*2+1; s=[x for a in s for x in (a,m-a)]
    return s            # bracket order of seeds, n power of 2
def adjacent(n): return list(range(1,n+1))
def play(order,upset=None):
    """stronger (lower seed number) wins unless upset(a,b,round) says the weaker wins.
       returns list of rounds (list of (a,b)) and champion."""
    rounds=[];cur=order;r=0
    while len(cur)>1:
        pairs=[(cur[i],cur[i+1]) for i in range(0,len(cur),2)]
        rounds.append(pairs); nxt=[]
        for a,b in pairs:
            lo,hi=min(a,b),max(a,b); w=hi if (upset and upset(lo,hi,r)) else lo; nxt.append(w)
        cur=nxt; r+=1
    return rounds,cur[0]
def first_meeting_round(order,x,y):
    rounds,_=play(order)   # chalk
    # chalk may eliminate before meeting; instead compute structural meeting round: smallest r where x,y in same block of size 2^(r+1)
    n=len(order);ix,iy=order.index(x),order.index(y);r=0
    while ix>>(r+1)!=iy>>(r+1): r+=1
    return r+1             # round number (1 = first round)
for n in (8,16,32,64):
    rounds=n.bit_length()-1
    f,a=fold(n),adjacent(n)
    # structural: top-4 seeds pairwise earliest meeting round
    ft=min(first_meeting_round(f,x,y) for x in range(1,5) for y in range(x+1,5))
    at=min(first_meeting_round(a,x,y) for x in range(1,5) for y in range(x+1,5))
    # chalk results: finalists
    _,cf=play(f); rf,_=play(f); fin_f=sorted(set(sum(rf[-1],()))) if True else 0
    ra,_=play(a); fin_a=sorted(set(sum(ra[-1],())))
    print("n=%2d rounds=%d | top-4 earliest meeting: fold R%d adjacent R%d | chalk finalists fold %s adjacent %s"%(n,rounds,ft,at,fin_f,fin_a))
    assert fin_f==[1,2] and ft==rounds-1
    assert at==1 and fin_a!=[1,2]
# BREAK: protection is only as good as the chalk assumption: one upset of seed 1 by seed 8 (n=8 and n=16)
for n,hi in ((16,16),):
    f=fold(n)
    rounds,champ=play(f,lambda lo,hi_,r:(lo==1 and hi_==16 and r==0))
    print("BREAK n=16 seed 16 upsets seed 1 in R1: finalists",sorted(set(sum(rounds[-1],()))),"champion",champ)
# BREAK 2: byes / non-power-of-two field: 12 teams padded to 16 -> byes go to top 4 seeds (fold seeding of 16 with seeds 13-16 absent)
f=fold(16); absent={13,14,15,16}
r1=[(a,b) for a,b in zip(f[::2],f[1::2])]
byes=[min(a,b) for a,b in r1 if a in absent or b in absent]
print("12-team field byes go to seeds",sorted(byes))
ok = sorted(byes)==[1,2,3,4]
print("RESULT: PASS fold seeding puts seeds 1-2 in opposite halves (first meeting = final) at n=8..64 while adjacent seeding makes them meet in R1; seed-16 upset removes seed 1 and byes in 12-team field go to seeds 1-4" if ok else "RESULT: FAIL")
