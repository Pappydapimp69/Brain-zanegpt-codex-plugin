# Read of a multi-bit counter while it changes: every changed bit may show old or new value. Exhaustive, no RNG.
from itertools import product
def gray(n): return n ^ (n>>1)
def ungray(g):
    n=0
    while g: n^=g; g>>=1
    return n
def worst_error(seq, decode, modulus):
    """max circular distance between any torn read and the true old/new value, over every transition incl. wrap."""
    worst=0
    L=len(seq)
    for i in range(L):
        a,b=seq[i],seq[(i+1)%L]
        changed=[k for k in range(max(a,b).bit_length()) if (a^b)>>k&1]
        for pick in product((0,1),repeat=len(changed)):
            v=a
            for k,p in zip(changed,pick):
                if p: v^=1<<k
            d=decode(v); old=decode(a); new=decode(b)
            # error relative to the nearer of old/new
            err=min(abs(d-old),abs(d-new))
            worst=max(worst,err)
    return worst, max(bin(seq[i]^seq[(i+1)%L]).count("1") for i in range(L))
rows={}
for k in (3,4,6,8):
    n=1<<k
    wb,hb=worst_error(list(range(n)),lambda v:v,n)
    wg,hg=worst_error([gray(i) for i in range(n)],ungray,n)
    rows[k]=(wb,hb,wg,hg); print(f"k={k} 2^k states: binary worst torn-read error {wb} (max bits changing {hb}) | gray {wg} (max bits {hg})")
# boundary: a mod-10 counter (BCD-style decade) using the first 10 gray codes does NOT wrap in one bit
g10=[gray(i) for i in range(10)]
w10,h10=worst_error(g10,ungray,10)
print(f"mod-10 truncated gray: max bits at wrap {h10}, worst torn-read error {w10}")
# fix: symmetric middle slice of a 4-bit gray sequence (start at 3) wraps in one bit
mid=[gray(i) for i in range(3,13)]
wm,hm=worst_error(mid,ungray,10)
print(f"mod-10 middle-slice gray (codes 3..12): max bits {hm}, worst torn-read error in underlying steps {wm}")
# error unit for the slice: positions inside the slice
pos={c:i for i,c in enumerate(mid)}
def worst_slice():
    w=0;L=len(mid)
    for i in range(L):
        a,b=mid[i],mid[(i+1)%L]
        ch=[k for k in range(4) if (a^b)>>k&1]
        for p in product((0,1),repeat=len(ch)):
            v=a
            for k,x in zip(ch,p):
                if x: v^=1<<k
            if v in pos: w=max(w,min(abs(pos[v]-i),abs(pos[v]-(i+1)%L)))
            else: w=max(w,99)
    return w
ws=worst_slice()
print("middle-slice torn reads land on valid codes with error:",ws)
ok = all(r[0]==(1<<k)//2-1 for k,r in rows.items()) and all(r[2]==0 and r[3]==1 for r in rows.values()) and h10>1 and hm==1 and ws<=1
print("RESULT:","PASS" if ok else "FAIL",f"binary torn-read error 2^(k-1)-1 (k=3..8: {[r[0] for r in rows.values()]}) vs gray 0 ({[r[2] for r in rows.values()]}); truncated mod-10 gray wraps in {h10} bits, middle slice {hm}")
