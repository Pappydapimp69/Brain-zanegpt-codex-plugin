# Sandbox: ISO 216 A-series (published table A0..A10 in mm, ISO 216:2007) vs three ways to derive it.
import math
ISO = [(841,1189),(594,841),(420,594),(297,420),(210,297),(148,210),(105,148),(74,105),(52,74),(37,52),(26,37)]  # (short,long)
def chain(rnd):
    s,l = ISO[0]; out=[(s,l)]
    for _ in range(10):
        s,l = rnd(l/2), s       # new short = half of old long (rounded), new long = old short
        out.append((s,l))
    return out
floor = chain(math.floor)
nearest_half_up = chain(lambda x: math.floor(x+0.5))
def exact_nearest():
    out=[]
    for n in range(11):
        area=1e6/2**n; s=math.sqrt(area/math.sqrt(2)); l=s*math.sqrt(2)
        out.append((math.floor(s+0.5), math.floor(l+0.5)))
    return out
ex = exact_nearest()
def hits(t): return sum(a==b for a,b in zip(t,ISO))
ratio_err = max(abs(l/s-math.sqrt(2))/math.sqrt(2) for s,l in ISO)
print("floor chain", hits(floor), "of 11; half-up chain", hits(nearest_half_up), "of 11; exact-nearest", hits(ex), "of 11")
print("first miss half-up:", next((i,nearest_half_up[i],ISO[i]) for i in range(11) if nearest_half_up[i]!=ISO[i]))
print("first miss exact:", next((i,ex[i],ISO[i]) for i in range(11) if ex[i]!=ISO[i]))
print(f"worst aspect error vs sqrt2 in table: {ratio_err:.2%}")
ok = hits(floor)==11 and hits(nearest_half_up)<11 and hits(ex)<11 and ratio_err<0.01
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" floor-halving chain from A0 841x1189 matches ISO table {hits(floor)}/11, half-up chain {hits(nearest_half_up)}/11, exact-sqrt2 nearest {hits(ex)}/11; worst aspect error {ratio_err:.2%}")
