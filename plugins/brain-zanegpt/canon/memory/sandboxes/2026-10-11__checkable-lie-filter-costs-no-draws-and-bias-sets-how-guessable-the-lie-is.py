"""Deceptive roster lines: pick the speaker of a lie. Uniform vs biased-to-checkable (filter over an already-shuffled order).
World: party of 6 follows a lead who walks/stops/turns; an actor is CHECKABLE if >20 m from the lead (out of earshot) or gone.
PREDICTION (before run): (1) checkable share of lies rises with bias b (0 -> ~uniform share, 1.0 -> 100% when one exists);
(2) draws consumed per lie are identical for every b (filter, not a reroll); (3) fallback (no checkable actor exists) happens in a non-zero minority of lie events;
(4) a player heuristic 'a line from a checkable speaker is a lie' gets precision rising with b but below 1.0 at b=1.0 because truthful lines also come from checkable speakers;
BREAK: when truthful lines are ALSO biased toward the same speakers, the heuristic's precision falls back to the base rate."""
import hashlib
def h(*a): return int.from_bytes(hashlib.sha256(repr(a).encode()).digest()[:8],"big")
DRAWS=[0]
def draw(*a): DRAWS[0]+=1; return h(*a)
def shuffled(seed,n):
    keys=sorted(range(n),key=lambda i:draw(seed,"s",i)); return keys
def world(session,t):
    # distances of 6 actors from lead; stragglers lag during walks. deterministic.
    out=[]
    for i in range(6):
        base=4+3*i                       # formation spread
        lag=((session*3+i*5+t*7)%11)*(2.2 if (t//4)%2==0 else 0.4)   # walking phases create stragglers, stops let them close
        gone=(h(session,i,t//9)%23==0)
        out.append((base+lag,gone))
    return out
def checkable(w,i): return w[i][1] or w[i][0]>20
def pick(seed,w,bias_on):
    order=shuffled(seed,6)
    if bias_on:
        for i in order:
            if checkable(w,i): return i,True,False
        return order[0],False,True
    return order[0],checkable(w,order[0]),False
def run(b_percent, truth_bias=False, SESS=60, T=40):
    lies=chk=fb=0; draws=0; tp=fp=0; tl=0; n_truth_chk=0; n_truth=0
    for s in range(SESS):
        for t in range(T):
            w=world(s,t)
            if not any(checkable(w,i) for i in range(6)): pass
            # a lie event happens every step
            use_bias = (h(s,t,"b")%100)<b_percent
            DRAWS[0]=0
            i,c,f=pick((s,t),w,use_bias); draws+=DRAWS[0]
            lies+=1; chk+=c; fb+=f
            # a truthful line at the same step
            order=shuffled((s,t,"truth"),6)
            if truth_bias:
                ti=next((j for j in order if checkable(w,j)),order[0])
            else: ti=order[0]
            n_truth+=1; n_truth_chk+=checkable(w,ti)
            # player heuristic flags a line from a checkable speaker as a lie
            tp+=c; fp+=checkable(w,ti)
    prec=tp/(tp+fp) if tp+fp else 0
    return dict(lies=lies,share=chk/lies,fallback=fb/lies,draws_per=draws/lies,prec=prec,truth_chk=n_truth_chk/n_truth)
res={b:run(b) for b in (0,50,80,100)}
for b,r in res.items(): print(f"bias {b:>3}%: checkable lies {r['share']:.3f} fallback {r['fallback']:.3f} draws/lie {r['draws_per']:.1f} heuristic precision {r['prec']:.3f}")
brk=run(100,truth_bias=True); print(f"BREAK truthful lines biased too: precision {brk['prec']:.3f} (base rate of checkable truths {brk['truth_chk']:.3f})")
ok=[res[0]['share']<res[50]['share']<res[80]['share']<=res[100]['share'],
    len({round(r['draws_per'],6) for r in res.values()})==1,
    0<res[100]['fallback']<0.5,
    res[0]['prec']<res[100]['prec']<1.0,
    brk['prec']<res[100]['prec'] and abs(brk['prec']-0.5)<0.15]
print("checks",ok)
print("RESULT: %s checkable lies %.2f->%.2f as bias 0->100%%, draws/lie constant at %.0f, fallback %.2f, heuristic precision %.2f->%.2f (not 1.0), falls to %.2f if truthful lines share the bias"%(
 "PASS" if all(ok) else "FAIL",res[0]['share'],res[100]['share'],res[100]['draws_per'],res[100]['fallback'],res[0]['prec'],res[100]['prec'],brk['prec']))
