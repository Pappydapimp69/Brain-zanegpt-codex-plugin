import math
# ladder on frictionless wall, floor friction mu, person at fraction s of length up: slip if tan(theta) < (1/2 + s)/mu... derive:
# torque about foot: N_wall*L*sin(t) = W*s*L*cos(t) + Wl*(L/2)cos(t) ; use W (person) and ladder weight Wl.
# horizontal: mu*N_floor >= N_wall, N_floor = W+Wl. Safe iff tan(t) >= (W*s + Wl/2)/(mu*(W+Wl)).
def min_angle(mu, s, W=800.0, Wl=100.0):
    return math.degrees(math.atan((W*s + Wl/2)/(mu*(W+Wl))))
rule_angle = math.degrees(math.atan(4))      # 4:1 rule: base = height/4 -> tan = 4
print('4:1 angle %.2f deg'%rule_angle)
for mu in (0.5,0.4,0.3,0.2,0.15,0.1):
    print('mu %.2f need %.2f deg at top (s=1) -> 4:1 %s'%(mu,min_angle(mu,1.0),'safe' if rule_angle>=min_angle(mu,1.0) else 'SLIPS'))
# threshold mu where 4:1 stops being safe at the top step
lo,hi=0.01,1.0
for _ in range(60):
    mid=(lo+hi)/2
    if min_angle(mid,1.0)<=rule_angle: hi=mid
    else: lo=mid
thr=hi; print('threshold mu at top %.4f'%thr)
# heavier person raises threshold: W=1500 N
print('threshold shift: need at mu 0.15, W=1500, s=1: %.2f deg'%min_angle(0.15,1.0,W=1500))
mid=lambda: None
lo,hi=0.01,1.0
for _ in range(60):
    m=(lo+hi)/2
    if min_angle(m,0.5)<=rule_angle: hi=m
    else: lo=m
thr_mid=hi
print('threshold mu at mid-ladder %.4f'%thr_mid)
ok = 0.2<thr<0.3 and thr_mid<thr and min_angle(0.4,1.0)<rule_angle and min_angle(0.1,1.0)>rule_angle
print(('RESULT: PASS' if ok else 'RESULT: FAIL')+' 4:1 (75.96 deg) is safe at the top step for mu>=%.3f (mid-ladder %.3f), slips at mu 0.10 (needs %.1f deg) and at mu 0.15 with a 1500 N climber needs %.1f deg'%(thr,thr_mid,min_angle(0.1,1.0),min_angle(0.15,1.0,W=1500)))
