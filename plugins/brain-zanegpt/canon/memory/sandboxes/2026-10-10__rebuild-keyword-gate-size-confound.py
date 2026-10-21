# Own fixture: synthetic Zipf vocabulary, deterministic LCG, 60 headings of 6-9 content words.
import math
s=12345
def rnd():
    global s; s=(s*1103515245+12345)&0x7fffffff; return s/0x7fffffff
V=2000
w=[f"w{i}" for i in range(V)]
cum=[];t=0
for i in range(V): t+=1/(i+1); cum.append(t)
def draw():
    x=rnd()*t; lo,hi=0,V-1
    while lo<hi:
        m=(lo+hi)//2
        if cum[m]<x: lo=m+1
        else: hi=m
    return w[lo]
def doc(n): return [draw() for _ in range(n)]
bg=[doc(100) for _ in range(300)]   # held-out background
df={}
for d in bg:
    for x in set(d): df[x]=df.get(x,0)+1
idf=lambda x: math.log((len(bg)+1)/(df.get(x,0)+1))
heads=[]
while len(heads)<60:
    h=sorted(set(draw() for _ in range(rnd()*3>1 and 8 or 7)))
    if len(h)>=5: heads.append(h)
def count_gate(h,d):
    ds=set(d); return sum(x in ds for x in h)>=max(2,round(0.3*len(h)))
def idf_gate(h,d):
    ds=set(d); return sum(idf(x) for x in h if x in ds)>=0.5*sum(idf(x) for x in h)
def fp(g,n):
    k=0;tot=0
    for h in heads:
        for _ in range(3): tot+=1; k+=g(h,doc(n))
    return k/tot
def recall(g):
    k=0
    for h in heads:
        d=doc(200); 
        for j,x in enumerate(h): d[j*20]=x   # plant all heading words
        k+=g(h,d)
    return k/len(heads)
sizes=[50,200,800,3200]
A=[fp(count_gate,n) for n in sizes]; B=[fp(idf_gate,n) for n in sizes]
print("count gate FP",A); print("idf gate FP",B); print("recall",recall(count_gate),recall(idf_gate))
# low-idf edit: plant only the 3 most common heading words
def lowrecall(g):
    k=0
    for h in heads:
        c=sorted(h,key=idf)[:3]; d=doc(200)
        for j,x in enumerate(c): d[j*20]=x
        k+=g(h,d)
    return k/len(heads)
lr=lowrecall(idf_gate); print("idf recall on common-word-only edits",lr)
num=[A[3]-A[0]>=0.5, B[3]<=0.10, recall(idf_gate)>=0.9, B[3]<A[3]]
rule=[A[3]>A[0] and B[3]>B[0],      # size confound real for both gates
      0<B[3]<A[3],                  # shrinks but never vanishes
      lr<=0.5,                      # common-word edits lost
      B[0]<A[0]]
print("numeric predictions held",sum(num),"/4; rule-of-thumb claims reproduced",sum(rule),"/4")
print(f"RESULT: {'PASS' if all(rule) else 'FAIL'} rule claims {sum(rule)}/4 (numeric bounds {sum(num)}/4 held); countFP {A[0]:.2f}->{A[3]:.2f}, idfFP {B[0]:.2f}->{B[3]:.2f}, idf recall {recall(idf_gate):.2f}, low-idf recall {lr:.2f}")
