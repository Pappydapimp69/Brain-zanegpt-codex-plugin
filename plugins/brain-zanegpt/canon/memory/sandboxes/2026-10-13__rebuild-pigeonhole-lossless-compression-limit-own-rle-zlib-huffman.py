# Prediction (before run): (1) no injection from the 2^L strings of length L into strictly shorter strings exists for L=1..4; (2) the best
# average length over uniform inputs, using shortest distinct codes of any length, is (L-2)+(L+2)/2^L, e.g. 1.625 at L=3 and 2.875 at L=4... I
# expect the formula to match for L=1..12; (3) my own run-length coder (letter byte + count byte per run) expands >=85% of 4^8 strings (alphabet ACGT);
# (4) zlib level 6 on 4096 deterministic hash-stream bytes yields between 4096+5 and 4096+15 bytes; (5) stored-flag wrapper bounds growth to +1 on all inputs;
# (6) a skew-tuned Huffman code over 256 symbols with 90% mass on one symbol averages under 8 bits on its own distribution but has a worst codeword over 8 bits
# and expands uniform data. Built to break: (2) for odd/small L and the exact constant.
import itertools, zlib, hashlib, heapq
def strings(n): return ["".join(p) for p in itertools.product("01",repeat=n)]
# 1. exhaustive injection search into strictly shorter strings
def shorter(L): return [s for n in range(L) for s in strings(n)]
ok1=True
for L in (1,2,3,4):
    src=strings(L); tgt=shorter(L)
    ok1 = ok1 and (len(tgt) < len(src))   # pigeonhole count: 2^L - 1 < 2^L
    # brute-force for L<=3 by trying every function via recursion with used set
    def inj(i,used):
        if i==len(src): return True
        return any(inj(i+1,used|{t}) for t in tgt if t not in used)
    if L<=3: ok1 = ok1 and (not inj(0,frozenset()))
print("1 no injection L=1..4:",ok1)
# 2. best average
def best_avg(L):
    need=2**L; tot=0; n=0
    while need>0:
        take=min(2**n,need); tot+=take*n; need-=take; n+=1
    return tot/2**L
form=lambda L:(L-2)+(L+2)/2**L
diffs={L:round(best_avg(L)-form(L),9) for L in range(1,13)}
print("2 best_avg-formula:",diffs)
ok2=all(abs(d)<1e-9 for d in diffs.values())
# 3. own RLE
def rle(s):
    out=[];i=0
    while i<len(s):
        j=i
        while j<len(s) and s[j]==s[i]: j+=1
        out.append((s[i],j-i)); i=j
    return 2*len(out)
alls=["".join(p) for p in itertools.product("ACGT",repeat=8)]
sizes=[rle(s) for s in alls]
exp=sum(x>8 for x in sizes)/len(alls); shr=sum(x<8 for x in sizes)/len(alls); worst=max(sizes)-8
print("3 RLE expands %.3f shrinks %.3f worst +%d"%(exp,shr,worst))
ok3=exp>=0.85 and worst==8
# 4. zlib on hash-stream bytes
data=b"".join(hashlib.sha256(str(i).encode()).digest() for i in range(128))[:4096]
z=len(zlib.compress(data,6)); print("4 zlib",z)
ok4=4096+5<=z<=4096+15
# 5. flag wrapper
def wrap(b):
    c=zlib.compress(b,6)
    return b"\x01"+c if len(c)<len(b) else b"\x00"+b
tests=[data,b"a"*4000,b"",b"x",bytes(range(256))]
growth=[len(wrap(t))-len(t) for t in tests]
print("5 wrapper growth",growth)
ok5=max(growth)==1
# 6. Huffman skew
def huff(freq):
    h=[(f,i,[s]) for i,(s,f) in enumerate(freq.items())]; heapq.heapify(h); depth={s:0 for s in freq}; c=len(h)
    while len(h)>1:
        a=heapq.heappop(h); b=heapq.heappop(h)
        for s in a[2]+b[2]: depth[s]+=1
        heapq.heappush(h,(a[0]+b[0],c,a[2]+b[2])); c+=1
    return depth
freq={s:(900 if s==0 else 1) for s in range(256)}; tot=sum(freq.values())
d=huff(freq); own=sum(freq[s]*d[s] for s in freq)/tot; uni=sum(d.values())/256
print("6 huffman skew avg own %.3f uniform %.3f worst %d"%(own,uni,max(d.values())))
ok6=own<8 and max(d.values())>8 and uni>8
ok=ok1 and ok2 and ok3 and ok4 and ok5 and ok6
print("RESULT: %s no injection L=1..4; best-average formula exact L=1..12; RLE expands %.1f%% shrinks %.1f%% worst +%d; zlib 4096->%d; wrapper max growth +%d; skew huffman own %.2f bits, uniform %.2f, worst code %d"%("PASS" if ok else "FAIL",100*exp,100*shr,worst,z,max(growth),own,uni,max(d.values())))
