# Hamming(7,4) vs extended (8,4) SECDED: exhaustive, deterministic.
from itertools import product
G=[[1,0,0,0,1,1,0],[0,1,0,0,1,0,1],[0,0,1,0,0,1,1],[0,0,0,1,1,1,1]]
H=[[1,1,0,1,1,0,0],[1,0,1,1,0,1,0],[0,1,1,1,0,0,1]]
def enc(d): return tuple(sum(d[i]*G[i][j] for i in range(4))%2 for j in range(7))
def syn(w): return tuple(sum(H[r][j]*w[j] for j in range(7))%2 for r in range(3))
CW=[enc(d) for d in product((0,1),repeat=4)]
cols={tuple(H[r][j] for r in range(3)):j for j in range(7)}
def dec7(w):
    s=syn(w)
    if s==(0,0,0): return w,"ok"
    w=list(w); w[cols[s]]^=1; return tuple(w),"corrected"
def enc8(d): c=enc(d); return c+(sum(c)%2,)
def dec8(w):
    s=syn(w[:7]); p=sum(w)%2
    if s==(0,0,0) and p==0: return w[:7],"ok"
    if p==1:
        c=list(w[:7])
        if s!=(0,0,0): c[cols[s]]^=1
        return tuple(c),"corrected"
    return None,"detected"
# 1) counting: every 7-bit word within distance 1 of exactly one codeword (perfect code)
def dist(a,b): return sum(x!=y for x,y in zip(a,b))
cover=[sum(dist(w,c)<=1 for c in CW) for w in product((0,1),repeat=7)]
print("sphere cover: 16*(1+7)=%d vs 2^7=128; all words covered exactly once: %s"%(16*8,set(cover)=={1}))
# 2) single and double errors over all codewords
def run(enc_,dec_,n,k):
    out={}
    for t in (1,2,3):
        res={"right":0,"silent_wrong":0,"detected":0}
        for d in product((0,1),repeat=4):
            c=enc_(d)
            for pos in __import__("itertools").combinations(range(n),t):
                w=list(c)
                for p in pos: w[p]^=1
                r,st=dec_(tuple(w))
                if st=="detected": res["detected"]+=1
                elif r==c[:7]: res["right"]+=1
                else: res["silent_wrong"]+=1
        out[t]=res
    return out
r7=run(enc,dec7,7,4); r8=run(enc8,dec8,8,4)
print("Hamming7",r7); print("SECDED8",r8)
# 3) correlated pair flips (beta-style common cause): P(word loss) per beta, p=0.01
def loss(res,n,p,beta):
    # independent flips prob p each; common-cause pair flip prob beta*p*n/2 per adjacent-pair (approx, exact enumeration over t)
    from math import comb
    tot=0
    for t in (2,3):
        tot_t=sum(res[t].values()); bad=res[t]["silent_wrong"]
        tot+=comb(n,t)*p**t*(1-p)**(n-t)*bad/tot_t if tot_t else 0
    tot+=beta*p*(res[2]["silent_wrong"]/sum(res[2].values()))
    return tot
for beta in (0,0.1):
    print("beta",beta,"silent-wrong rate p=.01: h7=%.2e secded=%.2e"%(loss(r7,7,.01,beta),loss(r8,8,.01,beta)))
ok7=r7[1]["right"]==16*7 and r7[2]["silent_wrong"]==16*21
ok8=r8[1]["right"]==16*8 and r8[2]["detected"]==16*28 and r8[2]["silent_wrong"]==0 and r8[3]["silent_wrong"]>0
ok=ok7 and ok8 and set(cover)=={1}
print("RESULT: %s Hamming7 miscorrects 21/21 doubles per codeword (perfect code), SECDED detects 28/28 doubles but triples still miscorrect %d/%d"%("PASS" if ok else "FAIL",r8[3]["silent_wrong"],sum(r8[3].values())))
