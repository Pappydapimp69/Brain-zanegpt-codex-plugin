import math
R=6371000.0
def exact(h,k=1.0): Re=k*R; return math.sqrt(2*Re*h+h*h)/1000   # km, tangent length
def rule(h,c): return c*math.sqrt(h)
hs=[2,10,50,100,300,1000,10000,12000]
rows=[]
for h in hs:
    e1,e43=exact(h,1.0),exact(h,4/3)
    rows.append((h,e1,e43,(rule(h,3.57)-e1)/e1*100,(rule(h,3.57)-e43)/e43*100,(rule(h,4.12)-e43)/e43*100))
    print('h=%6d  opt %.2f  radio %.2f  3.57 vs optical %+.2f%%  3.57 vs radio %+.2f%%  4.12 vs radio %+.2f%%'%rows[-1])
# two-antenna link: sum of the two horizons
d=lambda h1,h2,k:exact(h1,k)+exact(h2,k)
link=d(30,10,4/3); ruled=rule(30,4.12)+rule(10,4.12)
print('30 m mast to 10 m mast: exact %.2f km, rule %.2f km'%(link,ruled))
# BREAK: the rule at k=4/3 loses precision only through the h^2 term; check worst over table
worst43=max(abs(r[5]) for r in rows); worst357=max(abs(r[3]) for r in rows); under=min(r[4] for r in rows)
print('worst 4.12 error %.3f%%, worst 3.57 vs optical %.3f%%, 3.57 vs radio worst %.2f%%'%(worst43,worst357,under))
ok=worst43<0.5 and worst357<0.5 and -14<under<-13 and abs(link-ruled)/link<0.005
print('RESULT: %s 4.12 rule within %.2f%% of 4/3 earth horizon to 12 km height; 3.57 within %.2f%% of optical but %.1f%% short of radio; link %.2f vs %.2f km'%('PASS' if ok else 'FAIL',worst43,worst357,-under,link,ruled))
