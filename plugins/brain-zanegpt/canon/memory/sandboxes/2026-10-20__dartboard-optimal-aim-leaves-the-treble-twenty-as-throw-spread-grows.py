# Sandbox: standard dartboard (BDO/WDF dimensions in mm), expected score of an aim point under an isotropic Gaussian
# throw error, by deterministic grid integration (no RNG). Prediction (before run): the best aim for sigma 10 mm sits
# within 8 mm of the treble-20 centre; for sigma 40 mm the best aim is >= 20 mm from treble-20 and its expected score
# is lower; and the clockwise number ring has a neighbour-difference sum above the sorted ring.
import math
RING=[20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5]
def score(x,y):
    r=math.hypot(x,y)
    if r<=6.35: return 50
    if r<=15.9: return 25
    if r>170: return 0
    ang=(math.degrees(math.atan2(x,y))+360+9)%360          # 0 deg = up, clockwise; sector 20 centred on up
    n=RING[int(ang//18)]
    if 99<=r<=107: return 3*n
    if 162<=r<=170: return 2*n
    return n
STEP=4
SC={}
for i in range(-60,61):
    for j in range(-60,61): SC[(i,j)]=score(i*STEP,j*STEP)
def expected(ax,ay,sigma):
    k=int(3*sigma/STEP)+1; num=den=0.0
    ci,cj=round(ax/STEP),round(ay/STEP)
    for i in range(ci-k,ci+k+1):
        for j in range(cj-k,cj+k+1):
            w=math.exp(-(((i*STEP-ax)**2+(j*STEP-ay)**2)/(2*sigma*sigma)))
            s=SC.get((i,j),0)
            num+=w*s; den+=w
    return num/den
t20=(0,103)
res={}
for sigma in (10,25,40):
    best=(expected(*t20,sigma),t20)           # the exact treble-20 centre is always a candidate
    for ax in range(-100,101,8):
        for ay in range(-100,121,8):
            e=expected(ax,ay,sigma)
            if e>best[0]+1e-9: best=(e,(ax,ay))
    res[sigma]=best
    d=math.hypot(best[1][0]-t20[0],best[1][1]-t20[1])
    print(f"sigma {sigma}: best aim {best[1]} expected {best[0]:.1f} distance from T20 centre {d:.0f} mm; T20 expected {expected(*t20,sigma):.1f}")
diff=lambda r: sum(abs(r[i]-r[(i+1)%20]) for i in range(20))
print("neighbour-difference sum standard", diff(RING), "sorted", diff(sorted(RING)))
d10=math.hypot(res[10][1][0]-t20[0],res[10][1][1]-t20[1]); d40=math.hypot(res[40][1][0]-t20[0],res[40][1][1]-t20[1])
ok = d10<=8 and d40>=20 and res[40][0]<res[10][0] and diff(RING)>diff(sorted(RING))
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" best aim {d10:.0f} mm from T20 at sigma 10, {d40:.0f} mm at sigma 40; expected {res[10][0]:.1f} vs {res[40][0]:.1f}; ring neighbour sum {diff(RING)} vs sorted {diff(sorted(RING))}")
