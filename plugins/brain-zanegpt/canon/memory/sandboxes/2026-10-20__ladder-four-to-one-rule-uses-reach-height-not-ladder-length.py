import math
# OSHA 1926.1053(b)(5)(i): non-self-supporting ladder base set 1 unit out per 4 units of working length to the support point
def base_out(support_height): return support_height/4
def angle(support_height, out): return math.degrees(math.atan2(support_height, out))
rows=[]
for L in (8,12,16,20,24):          # ladder length, ft
    # to hold a 75.5 degree lean, support height h and base b satisfy h^2+b^2=L^2, b=h/4
    h=L/math.sqrt(1+1/16); b=h/4
    wrong_b=L/4                     # error: quarter of ladder LENGTH
    ang_wrong=math.degrees(math.acos(wrong_b/L))
    rows.append((L,h,b,wrong_b,ang_wrong))
    print(f"L={L:>2} ft: support h={h:5.2f} base={b:4.2f} | quarter-of-length base={wrong_b:4.2f} -> angle {ang_wrong:5.2f} deg; correct angle {angle(h,b):5.2f}")
ratio=[wb/b for _,_,b,wb,_ in rows]
diff=[angle(h,b)-a for _,h,b,_,a in rows]
ok = all(abs(angle(h,b)-75.96)<0.01 for _,h,b,_,_ in rows) and all(abs(r-17**0.5/4)<1e-9 for r in ratio) and all(0.4<d<0.5 for d in diff)
print(("RESULT: PASS" if ok else "RESULT: FAIL"),f"base = L/4 instead of h/4 sets the foot {ratio[0]-1:.1%} too far out at every length (2.00 vs 1.94 ft at 8 ft), a lean of 75.52 vs 75.96 deg, only {diff[0]:.2f} deg shallower")
