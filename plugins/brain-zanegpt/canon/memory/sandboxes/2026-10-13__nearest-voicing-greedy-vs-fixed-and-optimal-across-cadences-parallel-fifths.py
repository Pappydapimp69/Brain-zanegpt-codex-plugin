# Deterministic sandbox: nearest-voicing greedy (runtime) vs fixed root-position vs offline optimum,
# over cadence progressions; also counts parallel perfect 5ths/8ves bass-vs-upper (first-species rule).
import itertools
PC={'I':[0,4,7],'IV':[5,9,0],'V':[7,11,2],'vi':[9,0,4],'ii':[2,5,9]}
ROOT={k:v[0] for k,v in PC.items()}
LO,HI=55,79
def voicings(ch):
    opts=[[p for p in range(LO,HI+1) if p%12==pc] for pc in PC[ch]]
    return [tuple(sorted(c)) for c in itertools.product(*opts)]
def dist(a,b): return sum(abs(x-y) for x,y in zip(a,b))  # both sorted -> optimal matching
def fixed(ch):  # root-position close voicing above C4 (60)
    r=PC[ch][0]; base=60+r if r<=7 else 48+r
    return tuple(sorted(60+((pc-60)%12) for pc in PC[ch]))
def greedy(seq):
    cur=fixed(seq[0]);out=[cur]
    for ch in seq[1:]:
        cur=min(voicings(ch),key=lambda v:(dist(cur,v),v));out.append(cur)
    return out
def fixedpath(seq): return [fixed(c) for c in seq]
def optimal(seq):
    best={v:(0,[v]) for v in voicings(seq[0])}
    for ch in seq[1:]:
        nb={}
        for v in voicings(ch):
            nb[v]=min(((c+dist(p,v),path+[v]) for p,(c,path) in best.items()),key=lambda t:t[0])
            nb[v]=(nb[v][0],nb[v][1]+[]) if False else (nb[v][0],nb[v][1]+[v] if False else nb[v][1])
        # rebuild path properly
        nb={}
        for v in voicings(ch):
            c,path=min(((c+dist(p,v),path) for p,(c,path) in best.items()),key=lambda t:t[0])
            nb[v]=(c,path+[v])
        best=nb
    return min(best.values(),key=lambda t:t[0])[1]
def total(path): return sum(dist(a,b) for a,b in zip(path,path[1:]))
def common_kept(seq,path):  # shared pitch classes held at the same pitch in same voice
    kept=tot=0
    for (c1,c2),(a,b) in zip(zip(seq,seq[1:]),zip(path,path[1:])):
        sh=set(PC[c1])&set(PC[c2]); tot+=len(sh)
        kept+=sum(1 for p in a if p%12 in sh and p in b)
    return kept,tot
def bass(ch,prev=None): return 36+ROOT[ch]
def parallels(seq,path):
    n=0
    for i in range(len(seq)-1):
        b1,b2=bass(seq[i]),bass(seq[i+1])
        if b1==b2: continue
        for u1,u2 in zip(path[i],path[i+1]):
            if u1==u2: continue
            i1,i2=(u1-b1)%12,(u2-b2)%12
            if i1==i2 and i1 in (0,7): n+=1
    return n
SCEN={
 'authentic V-I':['V','I'],'plagal IV-I':['IV','I'],'deceptive V-vi':['V','vi'],
 'half I-IV-V':['I','IV','V'],
 'long adversarial':['I','V','vi','IV','I','V','vi','ii','V','I','IV','V','vi','I'],
 'root-leaps':['I','V','IV','I','vi','V','IV','I'],
}
res={}
for name,seq in SCEN.items():
    g,f,o=greedy(seq),fixedpath(seq),optimal(seq)
    res[name]=(total(g),total(f),total(o),common_kept(seq,g),parallels(seq,g),parallels(seq,f))
    print(name,'greedy',total(g),'fixed',total(f),'opt',total(o),'common kept/shared',res[name][3],'parallels greedy/fixed',res[name][4],res[name][5])
beats=all(r[0]<=r[1] for r in res.values())
strict=sum(1 for r in res.values() if r[0]<r[1])
gap=[n for n,r in res.items() if r[0]>r[2]]
ck=all(r[3][0]==r[3][1] for r in res.values())
print('greedy<=fixed all:',beats,'strictly better in',strict,'of',len(res))
print('greedy suboptimal vs offline optimum in:',gap)
print('common tones always retained by greedy:',ck)
ok=beats and strict>=4 and ck
print(('RESULT: PASS' if ok else 'RESULT: FAIL'),'greedy<=fixed %s strict %d/6 commontones-kept %s suboptimal-vs-optimum %s'%(beats,strict,ck,gap))
