# Mixed ramp of 8 beats: severity [1,1,2,3,3,4,4,5]. Two ways to make severe beats safe:
#  DISTANCE d: severe beat (s>=3) is funny (value s) iff s<=d; mild (s<=2) value s*closeness(d), closeness=1 (d<=2),0.5 (d=3),0 (d>=4). harm = -2.
#  CUE c (competing-norm / safe cue, closeness stays d=1): any beat with s<=1+c is safe; severe value s; mild value s*(1-f) where f is
#   the fraction of mild-beat funniness the cue mutes (f=0: cue is free; f=1: cue flattens mild like distance does).
#  g = fraction of SEVERE-beat funniness the cue mutes (the surreal-mutes-the-harm failure); distance never mutes severe value.
RAMP=[1,1,2,3,3,4,4,5]
def closeness(d): return 1.0 if d<=2 else 0.5 if d==3 else 0.0
def by_distance(d):
    t=0
    for s in RAMP:
        if s>d: t-=2
        elif s<=2: t+=s*closeness(d)
        else: t+=s
    return t
def by_cue(c,f,g=0.0):
    t=0; d=1
    for s in RAMP:
        if s>1+c: t-=2
        elif s<=2: t+=s*(1-f)
        else: t+=s*(1-g)
    return t
best_d=max(by_distance(d) for d in range(1,6))
print("distance-only best over d=1..5:",best_d)
grid={}
for g in (0.0,0.1,0.2,0.3,0.5):
    row=[]
    for f in (0.0,0.25,0.5,0.75,1.0):
        v=max(by_cue(c,f,g) for c in range(5)); row.append(v); grid[(g,f)]=v
    print(f"g={g:.1f} cue best at f=0,.25,.5,.75,1:",[round(x,2) for x in row])
wins=[k for k,v in grid.items() if v>best_d]; losses=[k for k,v in grid.items() if v<best_d]
free=grid[(0.0,0.0)]; always_ok=grid[(0.0,1.0)]>=best_d
# BREAK: severe-muting cue with g=0.3 at f=0.5 must lose to plain distance
ok = free>best_d and always_ok and grid[(0.3,0.5)]<best_d and grid[(0.1,0.0)]>best_d
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" distance best {best_d}; free cue {free}; cue wins {len(wins)} of 25 (g,f) cells and loses {len(losses)}; at g=0.3,f=0.5 cue {grid[(0.3,0.5)]:.2f}")
