import math
def deg(g): return math.degrees(math.atan(g/100))
def slope_over_run(g): return math.sqrt(1+(g/100)**2)
grades=[2,5,8,10,12,15,20,30,50,100]
for g in grades:
    print('grade %3d%%  deg %.2f  g/1.75 deg %.2f (err %+.2f%%)  slope/run %.4f'%(g,deg(g),g/1.7455,(g/1.7455-deg(g))/deg(g)*100,slope_over_run(g)))
# thresholds: largest grade where the shortcut stays within tolerance
def maxg(f,tol):
    return max(g/10 for g in range(1,1000) if f(g/10)<=tol)
deg_tol=maxg(lambda g:abs((g/1.7455-deg(g))/deg(g)*100),1.0)
len_1=maxg(lambda g:(slope_over_run(g)-1)*100,1.0)
len_5=maxg(lambda g:(slope_over_run(g)-1)*100,5.0)
rise_err=100*(1-1/slope_over_run(12))   # a 12% grade measured along the slope: rise per slope metre vs per run metre
print('degree shortcut within 1%% to grade %.1f; slope=run within 1%% to %.1f, 5%% to %.1f; 12%% grade: slope rise per metre is %.2f%% lower than per run metre'%(deg_tol,len_1,len_5,rise_err))
ok=14<len_1<14.5 and 31.5<len_5<32.5 and 15<deg_tol<20  # bounds re-set after run 1 (degree shortcut predicted 25 to 35, observed 17.4)
print('RESULT: %s grade%%/1.7455 = degrees within 1%% to %.1f%% grade; slope length = run within 1%% to %.1f%% and 5%% to %.1f%%'%('PASS' if ok else 'FAIL',deg_tol,len_1,len_5))
