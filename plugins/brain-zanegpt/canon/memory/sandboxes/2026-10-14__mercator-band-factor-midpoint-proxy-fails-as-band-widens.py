import math
def y(lat): return math.log(math.tan(math.pi/4+math.radians(lat)/2))
def jac_area(lat,h=1e-5):
    # drawn area per true area on unit sphere: dy/dphi / cos(phi) * (1) -> numeric
    p=math.radians(lat); dy=(y(lat+h*57.29578)-y(lat-h*57.29578))/(2*h)
    return dy/math.cos(p)   # x stretch = 1/cos, y stretch = dy/dphi; area = product
def band_avg(a,b,n=20000):
    # true-area-weighted average of drawn/true inflation over band: weight cos(phi)
    num=den=0.0
    for i in range(n):
        l=a+(b-a)*(i+.5)/n; w=math.cos(math.radians(l))
        num+=w*jac_area(l,1e-4)/1; den+=w
    return num/den
def sec2_avg_closedform(a,b):
    A,B=math.radians(a),math.radians(b); return (math.tan(B)-math.tan(A))/(B-A)
def area_avg(a,b):
    # true-area-weighted: integral sec^2*cos dphi / integral cos dphi = (y(b)-y(a))/(sin b - sin a)
    return (y(b)-y(a))/(math.sin(math.radians(b))-math.sin(math.radians(a)))
def mid(a,b): return 1/math.cos(math.radians((a+b)/2))**2
ok=True
print("point factors:",[round(jac_area(l),3) for l in (0,45,60,83)])
assert abs(jac_area(45)-2)<1e-3 and abs(jac_area(60)-4)<1e-3 and abs(jac_area(83)-67.33)<0.1
print("cutoff:",round(math.degrees(math.atan(math.sinh(math.pi))),4))
rows=[]
for a,b in [(44,46),(40,50),(20,60),(0,80),(60,85)]:
    cf=sec2_avg_closedform(a,b); m=mid(a,b); rows.append((a,b,area_avg(a,b),m,m/area_avg(a,b)))
    print(f"band {a}-{b}: plain-angle avg {cf:.3f} area-weighted {area_avg(a,b):.3f} midpoint {m:.3f} ratio {m/cf:.3f}")
# area-weighted avg (weights cos) of sec^2 is a different quantity: report it
for a,b in [(20,60)]:
    print("cos-weighted avg",round(band_avg(a,b),3))
narrow=rows[0][4]; wide=rows[3][4]
ok = abs(narrow-1)<0.002 and abs(rows[2][2]-1.833)<0.001 and abs(rows[2][3]-1.704)<0.001 and 0.65<wide<0.72 and rows[0][4]>rows[1][4]>rows[2][4]>wide
print(("RESULT: PASS" if ok else "RESULT: FAIL"),f"midpoint/avg ratio narrow {narrow:.4f} 20-60 {rows[2][4]:.3f} 0-80 {wide:.3f} 60-85 {rows[4][4]:.3f}")
