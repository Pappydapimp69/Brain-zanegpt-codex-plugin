# Siteswap: landing-permutation test vs simulation vs state-orbit return (ground state)
from itertools import product
MAXT, N = 6, 5
def perm_ok(s):
    n=len(s); return len({(i+t)%n for i,t in enumerate(s)})==n
def sim_ok(s):
    # simulate 3 periods after warm-up: each beat exactly one ball lands iff a throw is made (no collisions, no gaps)
    n=len(s); H=max(s)+1; land=[0]*(n*(2+H)+H)
    for b in range(n*(2+H)):
        t=s[b%n]
        if t>0: land[b+t]+=1
    lo=H; hi=n*(2+H)
    # in steady state window every beat must receive exactly 1 landing if throw >0, 0 if throw==0
    for b in range(lo,hi):
        need=1 if s[b%n]>0 else 0
        if land[b]!=need: return False
    return True
def orbit(s):
    # state = set of beats (relative) where balls land; start from ground-normalised steady state
    n=len(s); H=max(s)
    st=set()  # find steady state by warm-up
    cur=set()
    seen=[]
    # warm up: balls in flight come from throws before time 0 (periodic past)
    for k in range(1,H+1):
        for j in range(n):
            b=-(k)   # throw beat
    cur={ (b+s[b%n]) for b in range(-H,0) if b+s[b%n]>=0 }
    states=[]; 
    for b in range(0,n*3):
        states.append(frozenset(x-b for x in cur))
        if b in cur: cur.remove(b)
        t=s[b%n]
        if t>0: cur.add(b+t)
    return states
tot=pp=both=0; avg_only_wrong=0; ret_fail=0; distinct=[]
for s in product(range(MAXT+1),repeat=N):
    tot+=1
    p=perm_ok(s); m=sim_ok(s)
    avg=(sum(s)%N==0)
    if p!=m: both+=0; print("MISMATCH",s)
    if avg and not p: avg_only_wrong+=1
    if p:
        pp+=1
        st=orbit(s)
        # steady orbit must repeat with the period: state at beat n == state at 0
        if st[0]!=st[N]: ret_fail+=1
        distinct.append(len(set(st[:N])))
print("sequences",tot,"valid",pp,"avg-passes-but-invalid",avg_only_wrong,"orbit-return-failures",ret_fail)
print("max distinct states in a period",max(distinct),"min",min(distinct))
# BREAK: multiplex (two balls on one beat) is rejected by the permutation test though balls-per-beat can still average out
mux=(4,4,0,0,0)  # both land? beat0->4, beat1->5=0 ... check
print("break case 44000: perm",perm_ok(mux),"sim",sim_ok(mux),"avg",sum(mux)%N==0)
ok = all(perm_ok(s)==sim_ok(s) for s in product(range(MAXT+1),repeat=N)) and ret_fail==0 and avg_only_wrong>0
print("RESULT: %s permutation test matches landing simulation on %d seqs; avg alone wrong on %d; orbit returns on all %d valid"%("PASS" if ok else "FAIL",tot,avg_only_wrong,pp))
