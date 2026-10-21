# Prefix-cache model: cache keyed on exact token-prefix up to a breakpoint; min size; TTL 5 ticks (refreshed on hit).
MIN=40; TTL=5
def run(calls, bp_fn):
    cache={}  # prefix tuple -> expiry
    hits=0; cached_tokens=0
    for t,blocks in enumerate(calls):
        bp=bp_fn(blocks)           # number of blocks covered by breakpoint
        prefix=tuple(blocks[:bp]); size=sum(n for _,n in prefix)
        if size>=MIN:
            if prefix in cache and cache[prefix]>=t: hits+=1; cached_tokens+=size
            cache[prefix]=t+TTL
    return hits,cached_tokens
doc=("doc",60); tools=("tools",30)
def mk(first_dyn, n=6, gap=1, query_extra=True):
    out=[]
    for i in range(n):
        q=("q%d"%i,8); d=("date%d"%i,2)
        out.append(([d,tools,doc,q] if first_dyn else [tools,doc,d,q]))
    return out
last_stable=lambda b: next(i for i,x in enumerate(b) if x[0].startswith(("date","q")) and not x[0].startswith("tools") and not x[0]=="doc") if False else sum(1 for x in b if x[0] in("tools","doc"))
# bp covers stable blocks only when stable come first; when dynamic line first, bp must include it
def bp_end_of_stable(b):
    idx=[i for i,x in enumerate(b) if x[0] in("tools","doc")]
    return max(idx)+1
A=run(mk(False),bp_end_of_stable)
B=run(mk(True),bp_end_of_stable)
print("1 stable-first:",A,"2 dynamic-line-first:",B)
# 3 TTL: calls spaced > TTL apart
def spaced(gap):
    cache={};hits=0
    p=("tools","doc")
    for k in range(5):
        t=k*gap
        if p in cache and cache[p]>=t: hits+=1
        cache[p]=t+TTL
    return hits
print("3 gap1 hits",spaced(1),"gap5",spaced(5),"gap6",spaced(6))
# 4 below-minimum silent no-cache
small=[[("tools",10),("doc",20),("q%d"%i,5)] for i in range(6)]
C=run(small,lambda b:2)
print("4 below-min:",C)
# 5 break attempt: change after breakpoint doesn't invalidate (already in 1: q varies) ; change before does
mid=[[tools,("doc%d"%(i//3),60),("q%d"%i,8)] for i in range(6)]
D=run(mid,lambda b:2)
print("5 doc swaps every 3 calls:",D)
ok = A[0]==5 and B[0]==0 and spaced(1)==4 and spaced(5)==4 and spaced(6)==0 and C[0]==0 and D[0]==4
print("RESULT: %s stable-first hits=%d, dynamic-first hits=%d, gap6 hits=0, below-min hits=0, doc-swap hits=%d"%("PASS" if ok else "FAIL",A[0],B[0],D[0]))
