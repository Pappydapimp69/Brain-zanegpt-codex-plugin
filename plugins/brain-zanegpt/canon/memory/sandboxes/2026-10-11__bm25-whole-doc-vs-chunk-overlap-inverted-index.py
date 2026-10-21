# Sandbox: whole-doc vs chunked retrieval on an inverted index scored with BM25 (k1,b).
import math
from collections import defaultdict
# Hard corpus: 4 docs x 14 sentences; EVERY doc contains all a_j and b_k words; only the
# adjacent-sentence PAIRING differs: doc i pairs a_j with b_((j+i)%4). Pair j sits at sentence 3j+1+(i%2).
FILL = ["the system logs events daily","users review the report weekly","teams plan the next release",
        "data moves between the services","the cache holds recent values","operators check the dashboard"]
def make_doc(i):
    s=[FILL[(i+k)%len(FILL)]+f" n{k}" for k in range(14)]
    for j in range(4):
        p=3*j+1+(i%2)
        s[p]=f"step a{j} runs here"; s[p+1]=f"then b{(j+i)%4} finishes"
    return s
DOCS=[make_doc(i) for i in range(4)]
QUERIES=[(f"a{j} b{(j+i)%4}",i) for i in range(4) for j in range(4)]
def tok(t): return t.lower().split()
class Index:
    def __init__(s, units):  # units: list of (doc_id, [words])
        s.post = defaultdict(dict); s.len = {}; s.owner = {}
        for u,(d,w) in enumerate(units):
            s.owner[u]=d; s.len[u]=len(w)
            for t in w: s.post[t][u] = s.post[t].get(u,0)+1
        s.N=len(units); s.avg=sum(s.len.values())/s.N
    def search(s, q, k1=1.2, b=0.75):
        sc=defaultdict(float)
        for t in tok(q):
            pl=s.post.get(t,{}); df=len(pl)
            if not df: continue
            idf=math.log(1+(s.N-df+.5)/(df+.5))
            for u,tf in pl.items():
                sc[u]+=idf*tf*(k1+1)/(tf+k1*(1-b+b*s.len[u]/s.avg))
        best={}
        for u,v in sc.items():
            d=s.owner[u]; best[d]=max(best.get(d,0),v)
        return sorted(best,key=lambda d:(-best[d],d))
def units(size, overlap):
    out=[]
    for d,sents in enumerate(DOCS):
        if size is None: out.append((d,[w for s in sents for w in tok(s)])); continue
        step=max(1,size-overlap); i=0
        while True:
            out.append((d,[w for s in sents[i:i+size] for w in tok(s)]))
            if i+size>=len(sents): break
            i+=step
    return out
def mrr(size, overlap, **kw):
    ix=Index(units(size,overlap)); r=0
    for q,d in QUERIES:
        rk=ix.search(q,**kw); r+=1/(rk.index(d)+1) if d in rk else 0
    return r/len(QUERIES)
def mrr(size, overlap, **kw):
    ix=Index(units(size,overlap)); r=0
    for q,d in QUERIES:
        rk=ix.search(q,**kw); r+=1/(rk.index(d)+1) if d in rk else 0
    return r/len(QUERIES)
R={}
R["whole b=.75"]=mrr(None,0); R["whole b=0"]=mrr(None,0,b=0)
for sz in (1,2,3,4,8): R[f"chunk{sz} ov0"]=mrr(sz,0)
R["chunk2 ov1"]=mrr(2,1); R["chunk3 ov1"]=mrr(3,1); R["chunk4 ov1"]=mrr(4,1)
for k,v in R.items(): print(f"{k:16s} MRR={v:.3f}")
ok = R["whole b=.75"]<0.7 and R["chunk1 ov0"]<0.7 and R["chunk2 ov1"]==1.0 and R["chunk2 ov0"]<1.0
print("RESULT: "+("PASS" if ok else "FAIL")+" "+"; ".join(f"{k}={v:.2f}" for k,v in R.items()))
