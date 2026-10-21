# Deterministic: goal-gradient vigor g=1/remaining + decaying milestone bonus (b*d^gap).
# Agent quits at first step whose motivation < theta. Compare milestone layouts (same count).
import itertools
N=10
def mot(k,ms,b,d):
    g=1.0/(N-k)
    bonus=sum(b*d**(k-m) for m in ms if m<=k)
    return g+bonus
def completes(ms,b,d,th):
    return all(mot(k,ms,b,d)>=th for k in range(N))
def margin(ms,b,d):  # highest theta survived
    return min(mot(k,ms,b,d) for k in range(N))
layouts={'uniform':[0,3,6],'front':[0,1,3],'back':[0,6,8],'none':[]}
# matching-law share of choice between two cards (sibling kernel) from reinforcement rates
def share(ra,rb): return ra/(ra+rb)
# shaping (sibling): per-step criterion rises; milestone at each criterion step = successive approximation
print('goal-gradient vigor ratio 9/10 vs 0/10:',round(mot(9,[],0,0)/mot(0,[],0,0),2))
res={}
for b,d in [(0.5,0.5),(0.5,0.8),(0.5,0.2),(0.1,0.5)]:
    row={n:round(margin(ms,b,d),3) for n,ms in layouts.items()}
    res[(b,d)]=row
    print('b,d',b,d,row)
# threshold sweep: count thetas (0.05..1.0 step .05) survived
for n,ms in layouts.items():
    c=sum(completes(ms,0.5,0.5,t/20) for t in range(1,21))
    print('thetas survived',n,c)
# matching: two cards, front-loaded gives card A 3 early reinforcements of 6 total vs B
print('matching share 4:1 ->',share(4,1),'9:1 ->',share(9,1))
f=lambda n:sum(completes(layouts[n],0.5,0.5,t/20) for t in range(1,21))
ok_front=f('front')>f('uniform')
# break: slow decay (d=.8) makes milestone spacing irrelevant?
d8={n:round(margin(ms,0.5,0.8),3) for n,ms in layouts.items()}
print('slow decay margins',d8)
print('RESULT: %s front=%d uniform=%d back=%d none=%d; margins(b.5,d.5)=%s'%('PASS' if ok_front else 'FAIL',f('front'),f('uniform'),f('back'),f('none'),res[(0.5,0.5)]))
