import zlib, itertools
def rle(b):
    out=bytearray(); i=0
    while i<len(b):
        j=i
        while j<len(b) and b[j]==b[i] and j-i<255: j+=1
        out+=bytes([j-i,b[i]]); i=j
    return bytes(out)
def stored(b):  # 1-byte flag fallback: best of rle / raw
    c=rle(b)
    return b'\x01'+c if len(c)<len(b) else b'\x00'+b
ok=True
# S1 pigeonhole exhaustive over alphabet {a,b}, length<=12: 8190 inputs
ins=[bytes(t) for n in range(1,13) for t in itertools.product(b'ab',repeat=n)]
rl=[rle(x) for x in ins]
grow=sum(len(c)>len(x) for c,x in zip(rl,ins)); shrink=sum(len(c)<len(x) for c,x in zip(rl,ins))
print("S1 rle over",len(ins),"inputs: grew",grow,"shrunk",shrink)
ok&=grow>0 and len(set(rl))==len(ins)
# S2 stored fallback caps growth to +1 byte, still can't shrink all
st=[stored(x) for x in ins]
maxg=max(len(c)-len(x) for c,x in zip(st,ins)); shr=sum(len(c)<len(x) for c,x in zip(st,ins))
print("S2 stored fallback: max growth",maxg,"shrunk",shr,"of",len(ins))
ok&=maxg==1 and shr<len(ins)
# S3 BREAK: deterministic LCG high-entropy bytes through zlib: expands
x=12345; d=bytearray()
for _ in range(4096):
    x=(x*1103515245+12345)&0x7fffffff; d.append((x>>16)&255)
z=len(zlib.compress(bytes(d),9)); print("S3 zlib on 4096 LCG bytes ->",z)
ok&=z>4096
# S4 small messages: per-message zlib expands, batching shrinks (E24 link)
msgs=[b'{"id":%d,"ok":true,"v":"alpha"}'%i for i in range(64)]
per=sum(len(zlib.compress(m)) for m in msgs); raw=sum(map(len,msgs)); bat=len(zlib.compress(b''.join(msgs)))
print("S4 raw",raw,"per-msg",per,"batch64",bat)
ok&=per>raw and bat<raw
print("RESULT: %s growth: rle grew %d/%d, fallback cap +%d, zlib random %d>4096, per-msg %d>%d>batch %d"%("PASS" if ok else "FAIL",grow,len(ins),maxg,z,per,raw,bat))
