import calendar, datetime as dt
def months(start_y, n):
    return [(start_y+(m//12), m%12+1) for m in range(n)]
def fires(anchor, n, mode):
    out=[]
    for y,m in months(2025,n):
        dim=calendar.monthrange(y,m)[1]
        if anchor<=dim: out.append(dt.date(y,m,anchor))
        elif mode=="clamp": out.append(dt.date(y,m,dim))
    return out
def gaps(f): return [(b-a).days for a,b in zip(f,f[1:])]
res={}
for anchor in (30,31):
  for mode in ("clamp","skip"):
    f=fires(anchor,36,mode); g=gaps(f)
    # validity: a fire is "missed" iff its month has no fire (skip mode)
    missed=36-len(f)
    for T in (30,31,32):
        flagged=sum(1 for x in g if x>T)
        # true lapse intervals: gaps spanning a missing month (>=59 days)
        lapse=sum(1 for x in g if x>=59)
        res[(anchor,mode,T)]=(flagged,lapse,missed)
        print(f"anchor={anchor} mode={mode} T={T} flagged={flagged} true_lapses={lapse} missed_months={missed}")
over=sum(res[(31,"clamp",30)][0:1]); 
clean=res[(31,"clamp",32)][0]==0 and res[(31,"skip",32)][0]==res[(31,"skip",32)][1]
ok = over>0 and clean
print("RESULT: %s T=30 flags %d of 35 clamp gaps with 0 lapses; T=32 flags 0 clamp and %d skip gaps = true lapses"%("PASS" if ok else "FAIL",over,res[(31,'skip',32)][0]))
