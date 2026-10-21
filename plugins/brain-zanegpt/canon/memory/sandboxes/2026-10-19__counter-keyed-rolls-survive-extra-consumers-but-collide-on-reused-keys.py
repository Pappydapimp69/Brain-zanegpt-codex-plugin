"""Prediction (before run): 20 entities x 10 ticks of attack rolls.
(1) shared sfc32 stream: adding one cosmetic consumer changes >=50% of attack outcomes [run 1 got 48.5%, FAIL: a fair coin decorrelated flips ~50%, so threshold was wrong; run 2 prediction: 40-60%];
(2) counter-keyed rolls hash(seed, entity, tick, purpose) change 0 outcomes under added consumers AND shuffled order;
(3) BREAK: attack and crit rolls sharing one key (purpose omitted) make P(crit and attack)=0.5 instead of 0.25;
(4) save size: sfc32 4 words, counter-keyed 1 word (seed)."""
M=0xFFFFFFFF
def sfc32(a,b,c,d):
    def nxt():
        nonlocal a,b,c,d
        t=(a+b+d)&M; d=(d+1)&M; a=b^(b>>9); b=(c+(c<<3))&M; c=((c<<21)|(c>>11))&M; c=(c+t)&M
        return t/4294967296
    for _ in range(12): nxt()
    return nxt
def h(*k):
    x=0x811C9DC5
    for v in k:
        for byte in str(v).encode()+b"|":
            x=((x^byte)*0x01000193)&M
    x^=x>>16; x=(x*0x7feb352d)&M; x^=x>>15; x=(x*0x846ca68b)&M; x^=x>>16
    return x/4294967296
E,T=20,10
def shared(extra):
    r=sfc32(1,2,3,4); out={}
    for t in range(T):
        for e in range(E):
            if extra and e%7==0: r()           # added cosmetic consumer
            out[(e,t)]=r()<0.5
    return out
def keyed(extra,shuffle):
    out={}
    order=[(e,t) for t in range(T) for e in range(E)]
    if shuffle: order=order[::-1]
    for e,t in order:
        if extra: h(99,e,t,"cosmetic")
        out[(e,t)]=h(42,e,t,"attack")<0.5
    return out
a=shared(False);b=shared(True)
flip=sum(a[k]!=b[k] for k in a)/len(a)
ka=keyed(False,False);kb=keyed(True,True)
kflip=sum(ka[k]!=kb[k] for k in ka)
# break: purpose omitted -> attack and crit share the key
both=sum((h(42,e,t)<0.5)and(h(42,e,t)<0.5) for e in range(E) for t in range(T))/(E*T)
both_ok=sum((h(42,e,t,"attack")<0.5)and(h(42,e,t,"crit")<0.5) for e in range(E) for t in range(T))/(E*T)
print(f"shared-stream flips {flip:.1%}; keyed flips {kflip}; joint hit/crit reused key {both:.1%} vs purpose-keyed {both_ok:.1%}; save words 4 vs 1")
ok=0.4<=flip<=0.6 and kflip==0 and abs(both-0.5)<0.08 and both_ok<0.35
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" shared stream flips {flip:.1%} of 200 rolls, counter-keyed 0, reused key joint {both:.1%} vs {both_ok:.1%}")
