# Sandbox: Bayer 4x4 two-colour dither of a 64-step ramp, with and without a filmic toe (ACES fit).
# Check column: naive check (17 levels exist overall) vs per-region checks (levels in darkest quarter, monotone).
B=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
def aces(v): return max(0.0,min(1.0,(v*(2.51*v+0.03))/(v*(2.43*v+0.59)+0.14)))
def level(val):  # number of 'on' pixels in a 4x4 block at constant value val
    return sum(1 for y in range(4) for x in range(4) if val>(B[y][x]+0.5)/16)
def ramp(curve,n=64): return [level(curve((i+0.5)/n)) for i in range(n)]
ident=lambda v:v
toe=lambda v:aces(v*0.9)  # exposure placing the scene near the toe
def report(name,c):
    r=ramp(c);dark=r[:16]
    allL=len(set(r));darkL=len(set(dark));mono=all(a<=b for a,b in zip(r,r[1:]))
    naive=allL>=15            # naive check: nearly all 17 levels appear anywhere
    region=darkL>=4 and mono   # derived check: shadows keep >=4 levels
    print(f"{name}: levels={allL} dark_levels={darkL} mono={mono} naive={naive} region={region}")
    return allL,darkL,mono,naive,region
a=report("identity",ident)
b=report("filmic-toe",toe)
# break scenario: a dark-only scene authored near black, toe applied: naive still counts the lit corner
def dark_scene(v): return toe(v*0.25)
c=report("dark-scene+toe",dark_scene)
ok = a[4] and a[3] and (not b[4]) and b[3] and (not c[3])
print("RESULT: %s identity dark=%d toe dark=%d (naive passes toe=%s, region passes toe=%s) dark-scene levels=%d"%("PASS" if ok else "FAIL",a[1],b[1],b[3],b[4],c[0]))
