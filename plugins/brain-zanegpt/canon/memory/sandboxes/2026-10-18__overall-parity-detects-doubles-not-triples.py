# Sandbox: Hamming(7,4) SEC vs extended (8,4) SECDED over EVERY data word and error pattern.
# Run 1 prediction (missed: I counted SECDED doubles as C(7,2)*16=336 but the 8-bit word has C(8,2)*16=448): SEC corrects 112/112 single errors but "corrects" 336/336 doubles to a wrong word;
# SECDED corrects 128/128 singles and flags 336/336 doubles; BREAK: on triples SECDED still miscorrects >=90% of
# 896 patterns (odd weight looks like a single error), so one parity bit moves the blind spot, it does not remove it.
# Run 2 prediction (after run 1): SECDED flags 448/448 doubles; all else as above.
from itertools import combinations
def enc(d):
    d1,d2,d3,d4=d; p1=d1^d2^d4; p2=d1^d3^d4; p3=d2^d3^d4
    c=[p1,p2,d1,p3,d2,d3,d4]; return c+[sum(c)%2]
def dec(w, ext):
    c=list(w[:7]); s=(c[0]^c[2]^c[4]^c[6])+2*(c[1]^c[2]^c[5]^c[6])+4*(c[3]^c[4]^c[5]^c[6])
    par=sum(w)%2
    if ext and s and not par: return None            # double error flagged
    if s: c[s-1]^=1
    elif ext and par: pass                            # error in the parity bit only
    return (c[2],c[4],c[5],c[6])
words=[tuple((i>>k)&1 for k in range(4)) for i in range(16)]
def trial(nerr, ext):
    ok=wrong=flag=0; n=8 if ext else 7
    for d in words:
        for pos in combinations(range(n),nerr):
            w=enc(d)[:n] if ext else enc(d)[:7]
            for p in pos: w[p]^=1
            r=dec(w+([0] if not ext else []), ext) if not ext else dec(w,True)
            if r is None: flag+=1
            elif r==d: ok+=1
            else: wrong+=1
    return ok,wrong,flag
r={}
for name,(k,ext) in {"SEC single":(1,False),"SEC double":(2,False),"SECDED single":(1,True),"SECDED double":(2,True),"SECDED triple (BREAK)":(3,True)}.items():
    r[name]=trial(k,ext); print(name,"corrected=%d miscorrected=%d flagged=%d"%r[name])
tri=r["SECDED triple (BREAK)"]; tot=sum(tri)
ok=(r["SEC single"][0]==112 and r["SEC double"][1]==336 and r["SECDED single"][0]==128
    and r["SECDED double"][2]==448 and tri[1]/tot>=0.9)
print("RESULT: %s SEC miscorrects 336/336 doubles, SECDED flags 448/448 doubles but miscorrects %d/%d triples; 16 of 256 words used"
      %("PASS" if ok else "FAIL",tri[1],tot))
