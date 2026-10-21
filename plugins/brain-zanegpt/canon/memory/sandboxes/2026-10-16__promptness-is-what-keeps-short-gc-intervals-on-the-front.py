"""Sandbox: GC interval front for a fully cached 5-item loop (size 5, 995 hits/1000), with and without the kernel's
fourth goal, promptness (mean wait for a dead object to be reclaimed = interval/2 accesses).
Time = hits + 100*misses + (1000//interval) * 10*slots. Pause = 10*slots (same for every interval). Footprint = slots.
Prediction (before running): without promptness only the longest interval (50 or larger) is on the front, because
shorter intervals add collections but cannot lower pause or footprint; with promptness added every interval stays on
the front; for intervals 2,5,10,25,50,100 the front without promptness is {100} and with it is all 6.
Wrong if a shorter interval is on the front without promptness (it would need a lower time)."""
ACC=1000; SLOTS=5; HITS=995
IV=[2,5,10,25,50,100]
def objs(iv,prompt):
    t=HITS+100*(ACC-HITS)+(ACC//iv)*10*SLOTS
    o=[t,10*SLOTS,SLOTS]
    if prompt: o.append(iv/2)
    return tuple(o)
def front(prompt):
    pts={iv:objs(iv,prompt) for iv in IV}
    return [k for k,v in pts.items() if not any(all(a<=b for a,b in zip(u,v)) and u!=v for j,u in pts.items() if j!=k)]
a,b=front(False),front(True)
print("front without promptness",a); print("front with promptness",b)
# BREAK case: make pause grow with interval (more garbage per collection) - does a short interval become dominated-free?
def objs2(iv): return (HITS+100*(ACC-HITS)+(ACC//iv)*10*SLOTS, 10*SLOTS+iv, SLOTS, iv/2)
pts={iv:objs2(iv) for iv in IV}
c=[k for k,v in pts.items() if not any(all(x<=y for x,y in zip(u,v)) and u!=v for j,u in pts.items() if j!=k)]
print("front with pause growing with interval",c)
checks=[a==[100], b==IV, c==IV]
print("checks",checks)
print("RESULT:","PASS" if all(checks) else "FAIL",f"front without promptness {a}, with promptness {b}, pause growing with interval {c}")
