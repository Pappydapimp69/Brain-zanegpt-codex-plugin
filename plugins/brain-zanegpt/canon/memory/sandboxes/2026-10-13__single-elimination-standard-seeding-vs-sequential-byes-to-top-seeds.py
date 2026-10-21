# Prediction (before run): with strength = reverse seed (lower seed number always wins), n players padded to 2^k with byes given to the top seeds:
# (1) standard fold seeding (1 vs 2^k, 2 vs 2^k-1 ... via recursive halves) gives a final of 1 vs 2 for all n in 5..32 (28 of 28);
# (2) sequential pairing (1v2, 3v4, ...) with byes to top seeds meets 1 vs 2 in round 1, so the real final is never 1 vs 2 for n>=4 (0 of 28 finals are 1v2 for n>=5);
# (3) games played = n-1 in every case; byes = 2^k - n, and under standard seeding all byes go to seeds 1..byes (each round-1 bye is a top seed);
# (4) built to BREAK: with ONE fixed upset (seed 1 loses its first played game), standard seeding's final is no longer 1v2 for n=16 and the
# new top seed side takes the vacated slot; count how many n in 5..32 keep seed 2 in the final (expect all, since 2 sits in the other half).
def standard(n):
    k=1
    while 2**k<n: k+=1
    order=[1]
    while len(order)<2**k:
        m=len(order)*2+1
        order=[x for s in order for x in (s,m-s)]
    return [s if s<=n else None for s in order]       # None = bye
def sequential(n):
    k=1
    while 2**k<n: k+=1
    seeds=list(range(1,n+1))+[None]*(2**k-n)
    # byes to top seeds: place a bye opposite each of the top seeds by interleaving
    order=[]
    top=seeds[:n]; byes=[None]*(2**k-n)
    pairs=[]
    for i in range(len(byes)): pairs.append((top[i],None))
    rest=top[len(byes):]
    for i in range(0,len(rest),2): pairs.append((rest[i],rest[i+1]))
    return [x for p in pairs for x in p]
def play(slots,upset_seed=None):
    games=0; rounds=0; cur=slots; first_loss_done=False; final=None
    while len(cur)>1:
        nxt=[]
        for i in range(0,len(cur),2):
            a,b=cur[i],cur[i+1]
            if a is None or b is None: nxt.append(a if b is None else b); continue
            games+=1
            w=min(a,b)
            if upset_seed is not None and not first_loss_done and upset_seed in (a,b):
                w=max(a,b); first_loss_done=True
            nxt.append(w)
            if len(cur)==2: final=(a,b)
        cur=nxt
    return games,final
res={}
ok1=ok2=ok3=0; byes_ok=0; tot=0; upset_keep2=0; upset_not_1v2_16=None
for n in range(5,33):
    tot+=1
    ss=standard(n); sq=sequential(n)
    g1,f1=play(ss); g2,f2=play(sq)
    ok1+= sorted(f1)==[1,2]
    ok2+= sorted(f2)!=[1,2]
    ok3+= g1==n-1 and g2==n-1
    nb=sum(x is None for x in ss)
    # byes must go to seeds 1..nb: the seed facing None is <= nb
    facing=[ss[i] if ss[i+1] is None else ss[i+1] for i in range(0,len(ss),2) if (ss[i] is None)!=(ss[i+1] is None)]
    byes_ok+= sorted(facing)==list(range(1,nb+1))
    _,fu=play(ss,upset_seed=1)
    upset_keep2+= 2 in fu
    if n==16: upset_not_1v2_16=sorted(fu)!=[1,2]
print("standard final 1v2:",ok1,"/",tot,"| sequential final not 1v2:",ok2,"/",tot,"| games=n-1:",ok3,"/",tot,"| byes to top seeds:",byes_ok,"/",tot)
print("upset of seed 1: seed 2 still in final",upset_keep2,"/",tot,"; n=16 final not 1v2:",upset_not_1v2_16)
ok = ok1==tot and ok2==tot and ok3==tot and byes_ok==tot and upset_keep2==tot and upset_not_1v2_16
print("RESULT: %s standard seeding final is 1v2 in %d/%d sizes (n=5..32) vs 0 for sequential pairing, games=n-1 in %d/%d, byes go to top seeds in %d/%d; after a seed-1 upset seed 2 is still in the final in %d/%d and the n=16 final is no longer 1v2"%("PASS" if ok else "FAIL",ok1,tot,ok3,tot,byes_ok,tot,upset_keep2,tot))
