"""Sandbox: batch of fake-ad videos. Unique invented names pass an edit-distance lookalike gate, yet once the batch
exceeds the 5 premise axes, axis repeats read as templated (anti-template kernel). Also checks the axis label against source."""
import itertools
AXES_KERNEL = ["pin-pull", "fake-ui", "king-bait", "borrowed fame", "bait-switch"]
SOURCE_LABELS = {"pin-pull", "fake-ui", "king-bait", "popular externalization", "bait-switch"}
SYL = ["ka","mo","zu","ti","re","vo","na","li","su","be","do","fa","gi","hu","jo","pe"]
def name(i):  # deterministic distinct 3-syllable names
    a,b,c = i%16, (i*5+3)%16, (i*7+11)%16
    return (SYL[a]+SYL[b]+SYL[c]).title()
def lev(a,b):
    d=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        p,d[0]=d[0],i
        for j,y in enumerate(b,1):
            p,d[j]=d[j],min(d[j]+1,d[j-1]+1,p+(x!=y))
    return d[-1]
def lookalike_flags(names):
    return sum(1 for a,b in itertools.combinations(names,2) if lev(a.lower(),b.lower())<=2)
def template_dupes(videos):
    seen,dup=set(),0
    for v in videos:
        k=(v["axis"],v["format"],v["joke"])
        dup+= k in seen; seen.add(k)
    return dup
FORMATS=["shorts","long","community-post"]
def batch(n, fresh_joke):
    return [dict(name=name(i),axis=AXES_KERNEL[i%5],format=FORMATS[(i//5)%3] if fresh_joke else "shorts",
                 joke=f"j{i}" if fresh_joke else "swap-name") for i in range(n)]
res={}
for n in (5,12,30):
    for fresh in (False,True):
        b=batch(n,fresh)
        res[(n,fresh)]=(lookalike_flags([v["name"] for v in b]), template_dupes(b))
        print(f"n={n} fresh_joke={fresh} lookalike_pairs={res[(n,fresh)][0]} template_dupes={res[(n,fresh)][1]}")
label_miss=[a for a in AXES_KERNEL if a not in SOURCE_LABELS]
print("kernel labels absent from source:",label_miss)
checks=[
 res[(12,False)][0]==0 and res[(30,False)][0]==0,          # names unique -> gate silent
 res[(5,False)][1]==0 and res[(12,False)][1]==7 and res[(30,False)][1]==25,  # template dupes appear past 5 axes
 res[(30,True)][1]==0,                                       # fresh jokes/format rotation clear it
 label_miss==["borrowed fame"],
]
print("checks",checks)
print(("RESULT: PASS" if all(checks) else "RESULT: FAIL"),f"lookalike gate silent (0 pairs) while template dupes {res[(12,False)][1]}/12 and {res[(30,False)][1]}/30 with swap-name jokes; fresh jokes 0; label misses {label_miss}")
