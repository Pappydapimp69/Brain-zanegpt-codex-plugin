# Which leap rule is used barely matters for how often a day-29 monthly repeat in skip mode loses February.
def julian(y): return y%4==0
def gregorian(y): return y%4==0 and (y%100!=0 or y%400==0)
def r833(y): return (8*y)%33 < 8          # 8 leap years per 33, evenly spread
Y=range(2000,2000+3300)                   # 3300 years = lcm-friendly span for 33 and 400 (3300=12*275: 33*100)
res={}
for name,f in (("julian",julian),("gregorian",gregorian),("8/33",r833)):
    leaps=sum(f(y) for y in Y); febs=len(Y)
    skip_fires=leaps; clamp_fires=febs
    res[name]=(leaps/febs, 1-leaps/febs)
    print(f"{name}: leap rate {leaps/febs:.4f}; day-29 skip loses {febs-skip_fires} of {febs} Februaries ({1-leaps/febs:.2%}); clamp loses 0")
vals=[v[1] for v in res.values()]
spread=max(vals)-min(vals)
# day 30/31 monthly: Feb always lost under skip regardless of rule
ok = spread<0.01 and min(vals)>0.74
print(("RESULT: PASS" if ok else "RESULT: FAIL"),f"skip loses {min(vals):.2%} to {max(vals):.2%} of Februaries under all three rules (spread {spread*100:.2f} pts); clamp loses 0")
