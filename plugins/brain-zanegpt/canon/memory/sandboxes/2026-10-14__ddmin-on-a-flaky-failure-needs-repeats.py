# Prediction (first): ddmin over 16 preemption points with true culprit {3,11}. With a deterministic failure
# (p=1) it returns exactly {3,11} in 100% of offsets. With a heisenbug that shows only with p=0.044 per run
# (sandbox-kernel-concurrency/E1's rare-preemption rate), 1 run per test returns the exact set in <25% of offsets;
# repeating each test r=68 times (95% detection) recovers >=90%; the result is never SMALLER than the culprit.
PHI=0.6180339887498949
def make_test(p,r,offset):
    st={"n":offset}
    def test(S):   # True = failure observed
        has=3 in S and 11 in S
        for _ in range(r):
            st["n"]+=1
            if has and (st["n"]*PHI)%1.0 < p: return True
        return False
    return test
def ddmin(items,test):
    n=2; c=list(items)
    while len(c)>=2:
        sz=max(1,len(c)//n); chunks=[c[i:i+sz] for i in range(0,len(c),sz)]; red=False
        for ch in chunks:
            if test(ch): c=ch;n=2;red=True;break
        if not red:
            for ch in chunks:
                comp=[x for x in c if x not in ch]
                if comp and test(comp): c=comp;n=max(n-1,2);red=True;break
        if not red:
            if n>=len(c): break
            n=min(len(c),2*n)
    return c
def trial(p,r,off):
    t=make_test(p,r,off); full=list(range(16))
    guard=0
    while not t(full):         # must see the failure once to start (as a real debugger would)
        guard+=1
        if guard>2000: return None
    return ddmin(full,t)
def rate(p,r,offs=range(200)):
    exact=0;nonmin=0;smaller=0
    for o in offs:
        res=trial(p,r,o)
        if res is None: continue
        s=set(res)
        if s=={3,11}: exact+=1
        elif {3,11}<=s: nonmin+=1
        else: smaller+=1
    return exact/len(offs),nonmin/len(offs),smaller
rows={}
for p,r in [(1.0,1),(0.5,1),(0.044,1),(0.044,20),(0.044,68)]:
    rows[(p,r)]=rate(p,r); e,nm,sm=rows[(p,r)]; print(f"p={p} repeats={r}: exact {e:.3f} non-minimal {nm:.3f} smaller-than-culprit {sm}")
ok=rows[(1.0,1)][0]==1.0 and rows[(0.044,1)][0]<0.25 and rows[(0.044,68)][0]>=0.9 and all(v[2]==0 for v in rows.values())
print("RESULT:","PASS" if ok else "FAIL",f"ddmin exact {rows[(1.0,1)][0]:.2f} at p=1; {rows[(0.044,1)][0]:.2f} at p=0.044 x1 run; {rows[(0.044,20)][0]:.2f} x20; {rows[(0.044,68)][0]:.2f} x68")
