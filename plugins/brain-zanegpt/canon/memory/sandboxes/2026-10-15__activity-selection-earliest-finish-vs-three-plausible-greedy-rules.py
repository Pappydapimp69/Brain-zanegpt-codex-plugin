# Exhaustive deterministic check: which greedy rule maximizes the number of non-overlapping intervals?
from itertools import combinations
G=7   # time grid 0..6; intervals [s,e) with s<e
ALL=[(s,e) for s in range(G) for e in range(s+1,G)]
def overlap(a,b): return a[0]<b[1] and b[0]<a[1]
def optimum(iv):
    best=0
    for r in range(len(iv),0,-1):
        for c in combinations(iv,r):
            if all(not overlap(a,b) for a,b in combinations(c,2)): return r
    return 0
def greedy(iv, key):
    chosen=[]
    for x in sorted(iv,key=key):
        if all(not overlap(x,c) for c in chosen): chosen.append(x)
    return len(chosen)
rules={
 "earliest_finish": lambda x:(x[1],x[0]),
 "earliest_start":  lambda x:(x[0],x[1]),
 "shortest":        lambda x:(x[1]-x[0],x[0]),
 "latest_start":    lambda x:(-x[0],x[1]),
}
# fewest-conflicts is instance dependent: handle separately
def fewest_conflicts(iv):
    chosen=[]; rem=list(iv)
    while rem:
        x=min(rem,key=lambda a:(sum(overlap(a,b) for b in rem if b!=a),a[1],a[0]))
        chosen.append(x); rem=[b for b in rem if not overlap(x,b)]
    return len(chosen)
fail={k:0 for k in rules}; fail["fewest_conflicts"]=0; total=0; smallest={}
for n in range(1,9):
    for iv in combinations(ALL,n):
        total+=1; opt=optimum(iv)
        for k,f in rules.items():
            if greedy(iv,f)!=opt:
                fail[k]+=1; smallest.setdefault(k,iv)
        if fewest_conflicts(iv)!=opt: fail["fewest_conflicts"]+=1; smallest.setdefault("fewest_conflicts",iv)
print("instances (<=8 intervals on 0..6 grid):",total)
for k,v in fail.items(): print(f"{k:17} suboptimal on {v:6d} instances; smallest counterexample: {smallest.get(k)}")
# a counterexample rule (earliest-start, 1 long interval hides 3 short ones) generalizes: ratio
long=[(0,100)]+[(i*10+1,i*10+6) for i in range(10)]
print("earliest_start picks",greedy(long,rules["earliest_start"]),"vs optimum",10)
# latest_start is the time-mirror of earliest_finish, so it must also be optimal (symmetry control)
ok = fail["earliest_finish"]==0 and fail["latest_start"]==0 and fail["earliest_start"]>0 and fail["shortest"]>0
print("RESULT:","PASS" if ok else "FAIL",f"earliest-finish suboptimal on {fail['earliest_finish']} of {total} instances; earliest_start {fail['earliest_start']}, shortest {fail['shortest']}, latest_start {fail['latest_start']}, fewest_conflicts {fail['fewest_conflicts']}")
