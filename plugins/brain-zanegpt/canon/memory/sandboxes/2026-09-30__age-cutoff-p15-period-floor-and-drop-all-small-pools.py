# Sandbox: P15 W5 (window ticks 0-4): period-lag-in-pool floor and leave-one-out, tick-level, no fallback.
# Prediction: (a) with 15 in pool, cutoff >= 15 always; equals 15 iff no lag >15 is valid (valid = L%15 in {0..4,11..14});
# (b) dropping 15 gives largest remaining valid lag else 0; naive "next configured lag" is wrong whenever it is invalid (e.g. 8 -> really 0 or smaller).
from itertools import combinations
P=15; W=set(range(5))
def valid_sim(L):
    T=8*P+L
    return any(t%P in W and (t-L)%P in W for t in range(L,T))
def cut(pool):
    v=[L for L in pool if valid_sim(L)]; return max(v) if v else 0
n=floor_bad=eq_bad=drop_bad=naive_wrong=0
for k in (1,2,3):
    for c in combinations(range(1,31),k):
        if 15 not in c: continue
        n+=1; full=cut(c)
        floor_bad+= full<15
        above=[L for L in c if L>15 and valid_sim(L)]
        eq_bad+= (full==15)!=(not above)
        rest=[x for x in c if x!=15]
        if rest:
            got=cut(rest); exp=max([L for L in rest if L%15 in {0,1,2,3,4,11,12,13,14}] or [0])
            drop_bad+= got!=exp
            naive_wrong+= got!=max(rest)
print("pools",n,"floor_bad",floor_bad,"eq_bad",eq_bad,"drop_bad",drop_bad,"naive_wrong",naive_wrong)
print("RESULT:",("PASS" if floor_bad==eq_bad==drop_bad==0 and naive_wrong>0 else "FAIL"),n,"pools",naive_wrong,"naive-next-lag errors")
