from fractions import Fraction as F
# wear per interval by position: FL FR RL RR (front-drive, crowned road)
def run(rates, pattern, intervals):
    pos={'A':'FL','B':'FR','C':'RL','D':'RR'}  # tire -> position
    w={t:F(0) for t in pos}
    for _ in range(intervals):
        for t,p in pos.items(): w[t]+=rates[p]
        pos={t:pattern[p] for t,p in pos.items()}
    return max(w.values())-min(w.values())
straight={'FL':'RL','RL':'FL','FR':'RR','RR':'FR'}
cross={'FL':'RR','RR':'FL','FR':'RL','RL':'FR'}
none={p:p for p in ['FL','FR','RL','RR']}
add={'FL':F(20,10),'FR':F(22,10),'RL':F(10,10),'RR':F(12,10)}      # additive: front +1.0, right +0.2
nonadd={'FL':F(20,10),'FR':F(24,10),'RL':F(10,10),'RR':F(12,10)}   # front/right gaps do not add
sym={'FL':F(2),'FR':F(2),'RL':F(1),'RR':F(1)}
for name,r in (('additive',add),('symmetric',sym),('non-additive BREAK',nonadd)):
    print(name,'none',float(run(r,none,10)),'straight',float(run(r,straight,10)),'cross',float(run(r,cross,10)))
ok = (run(add,cross,10)==0 and run(add,straight,10)==2 and run(add,none,10)==F(10)*(F(22,10)-F(10,10))
      and run(sym,straight,10)==0 and run(nonadd,cross,10)==1 and run(nonadd,straight,10)==3)
print(('RESULT: PASS' if ok else 'RESULT: FAIL')+' additive gaps: cross spread %s, straight %s, none %s of 10 intervals; symmetric straight %s; non-additive cross %s'%(run(add,cross,10),run(add,straight,10),run(add,none,10),run(sym,straight,10),run(nonadd,cross,10)))
