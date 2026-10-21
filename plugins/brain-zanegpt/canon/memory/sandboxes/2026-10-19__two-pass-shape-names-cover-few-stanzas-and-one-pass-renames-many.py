"""Prediction (before run): exhaustive 4-line stanzas over an 8-word end pool (perfect key + assonance key).
Shapes from Pattison: AABB, ABAB, ABBA, XXAA (first couplet unrhymed, last couplet rhymes).
(1) two-pass uppercase pattern names one of the 4 shapes in 5-25% of stanzas (most stanzas are none of them);
(2) one-pass 'any rhyme counts' assigns a DIFFERENT shape name than two-pass in >=15% of stanzas that two-pass names;
(3) BREAK: on a pool where assonance never occurs without a perfect partner the two labellers agree 100%."""
import itertools
POOL={"day":("ay","a"),"way":("ay","a"),"fate":("ate","a"),"late":("ate","a"),
      "night":("ight","i"),"light":("ight","i"),"time":("ime","i"),"stone":("one","o")}
def two_pass(keys):
    out=[None]*4; perf={}
    for i,(p,a) in enumerate(keys):
        if sum(k[0]==p for k in keys)>1: perf.setdefault(p,"ABCD"[len(perf)]); out[i]=perf[p]
    rest=[i for i in range(4) if out[i] is None]
    nxt="abcd"
    used={}
    for i in rest:
        grp=[j for j in rest if keys[j][1]==keys[i][1]]
        if len(grp)>1: used.setdefault(keys[i][1],nxt[len(used)]); out[i]=used[keys[i][1]]
        else: out[i]="x"
    return out
def one_pass(keys):
    out=[None]*4; g={}
    for i,(p,a) in enumerate(keys):
        m=[j for j in range(4) if j!=i and (keys[j][0]==p or keys[j][1]==a)]
        if m:
            root=min([i]+m); out[i]=g.setdefault(root,"ABCD"[len(g)])
        else: out[i]="x"
    return out
def shape(letters):
    s="".join(l.upper() for l in letters)
    # canonicalise: x stays x
    names={"AABB":"AABB","ABAB":"ABAB","ABBA":"ABBA","XXAA":"XXAA"}
    m={};c=""
    for ch in s:
        if ch=="X": c+="X"
        else: c+=m.setdefault(ch,"AB"[len(m)] if len(m)<2 else "C")
    return names.get(c)
def run(pool):
    n=named=diff=0
    for st in itertools.product(pool,repeat=4):
        k=[pool[w] for w in st]
        a=shape(two_pass(k)); b=shape(one_pass(k))
        n+=1
        if a: named+=1
        if a and a!=b: diff+=1
    return n,named,diff
n,named,diff=run(POOL)
perfect_only={w:POOL[w] for w in ("day","way","fate","late","night","light")}
perfect_only={w:(p,w[:1]+p) for w,(p,a) in perfect_only.items()}   # assonance = unique, never shared
n2,named2,diff2=run(perfect_only)
print(f"stanzas={n} two-pass names a shape in {named} ({named/n:.1%}); one-pass names it differently in {diff} ({diff/max(named,1):.1%}); no-assonance pool diff {diff2}")
ok=0.05<=named/n<=0.25 and diff/named>=0.15 and diff2==0
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" two-pass names {named/n:.1%} of stanzas, one-pass disagrees on {diff/max(named,1):.1%} of those; no-assonance pool disagrees {diff2}")
