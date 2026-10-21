# Sandbox: age cutoff on top of a state-validity gate, in a periodic vs quasiperiodic world.
# A press with lag L at time t is ACCEPTED by validity iff state[t-L]==state[t].
# Cutoff C additionally rejects L>C. Loss(C) = accepted presses that the cutoff removes.
T=600
def fib_word(n):
    a,b="0","01"
    while len(b)<n+200: a,b=b,b+a
    return [int(c) for c in b]
FW=fib_word(T+200)
def periodic(p): return [1 if (i%p)<p//3 else 0 for i in range(T+200)]
def rot(alpha=0.6180339887498949): return [1 if (i*alpha)%1<alpha else 0 for i in range(T+200)]
def accepted(s,L): return sum(1 for t in range(200,200+T) if s[t-L]==s[t])
def loss(s,lags,C): return sum(accepted(s,L) for L in lags if L>C)
def lossless_threshold(s,lags):
    # smallest C with zero loss = largest lag that has any accepted press
    got=[L for L in lags if accepted(s,L)>0]
    return max(got)
res={}
lags=[12,24,36,48,60]
P=periodic(12)
# 1) periodic p12: lags multiples of 12 -> lossless at largest valid lag
thr=lossless_threshold(P,lags); res["periodic_thr"]=thr
print("periodic p12 thr",thr,"loss at C=12:",loss(P,lags,12),"loss at C=thr:",loss(P,lags,thr))
# 2) Fibonacci word, near-recovery lags 55,89 (+decoys)
flags=[34,55,89]
acc={L:accepted(FW,L) for L in flags}
print("fib accepted",acc)
t2=lossless_threshold(FW,flags)
print("fib thr",t2,"loss at C=55:",loss(FW,flags,55),"loss at C=89:",loss(FW,flags,89))
# 3) break scenario: irrational rotation with same lags
acc3={L:accepted(rot(),L) for L in flags}
print("rot accepted",acc3)
t3=lossless_threshold(rot(),flags)
print("rot thr",t3,"loss at C=55:",loss(rot(),flags,55),"loss at C=89:",loss(rot(),flags,89))
# claim: lossless threshold == largest lag with accepted presses (89 here), NOT the best near-recovery lag (55)
ok = (thr==60 and loss(P,lags,thr)==0 and loss(P,lags,12)>0
      and t2==89 and loss(FW,flags,89)==0 and loss(FW,flags,55)>0
      and t3==89 and loss(rot(),flags,89)==0 and loss(rot(),flags,55)>0)
print("RESULT: %s fib_loss55=%d rot_loss55=%d periodic_loss12=%d thr(fib/rot/per)=%d/%d/%d"%("PASS" if ok else "FAIL",loss(FW,flags,55),loss(rot(),flags,55),loss(P,lags,12),t2,t3,thr))
