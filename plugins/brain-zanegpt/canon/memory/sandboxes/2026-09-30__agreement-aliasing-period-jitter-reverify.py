# PREDICTION (before run): state = 5-on window at start of each period; strict P=15 vs jittered periods alternating 15,16 (super-cycle 31).
# Strict: agreement flags 0/620 at L=15,30. Jitter: agreement flags >0 but <600 at L=15 and 30, exactly 0 at L=31 and 62.
# Age tag (L>2) flags 600/600 at every lag>2 in both worlds. Breaker: L=1 strict (agreement flags some, both flag).
N=620
def world(periods):
    s=[];k=0
    while len(s)<N+70:
        P=periods[k%len(periods)];k+=1
        s+= [1]*5+[0]*(P-5)
    return s
def stale_flags(st,L,thr=2):
    agree=sum(1 for t in range(N) if st[t]!=st[t+L])   # hint made at t, state at t+L
    # a hint is truly stale when state changed; age tag flags all L>thr
    age=N if L>thr else 0
    return agree,age
ok=True
for name,per in(("strict15",[15]),("jitter15/16",[15,16])):
    st=world(per)
    for L in(1,15,30,31,62):
        a,g=stale_flags(st,L); print(name,L,"agree",a,"age",g)
S=world([15]);J=world([15,16])
ok&=stale_flags(S,15)[0]==0 and stale_flags(S,30)[0]==0
ok&=all(0<stale_flags(J,L)[0]<N for L in(15,30))
ok&=stale_flags(J,31)[0]==0 and stale_flags(J,62)[0]==0
ok&=all(stale_flags(w,L)[1]==N for w in(S,J) for L in(15,30,31,62))
ok&=stale_flags(S,1)[0]>0
print("RESULT: %s agreement aliases to 0 only at true cycle multiples (strict 15,30; jitter 31,62); age tag flags all 620"%("PASS" if ok else "FAIL"))
