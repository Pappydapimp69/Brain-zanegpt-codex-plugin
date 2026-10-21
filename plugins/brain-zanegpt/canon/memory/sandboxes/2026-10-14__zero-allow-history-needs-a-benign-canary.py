# Prediction (first): a zero-allow history over N=20 messages is produced both by a calibrated gate fed all-risky
# traffic and by a miscalibrated hold-everything gate fed mixed traffic, so the count alone cannot tell them apart
# (ambiguous in >=1 scenario); replaying one known-benign canary separates them in 3/3 scenarios; and a gate whose
# hold response visibly differs lets a prober recover its threshold in 7 probes, an identical acknowledgement in 0 bits.
RISKY_FROM=70
def gate(score,t): return "allow" if score<t else "hold"
def history(kind):
    if kind=="all-risky": return [70+i for i in range(20)]          # every message really risky
    if kind=="mixed":     return [5*i for i in range(20)]           # 0..95, mostly benign
    if kind=="all-benign":return [i for i in range(20)]
gates={"calibrated":RISKY_FROM,"miscalibrated-hold-all":0}
def zero_allow(h,t): return all(gate(s,t)=="hold" for s in h)
amb=0;canary_ok=0;rows=0
for kind in("all-risky","mixed","all-benign"):
    z={g:zero_allow(history(kind),t) for g,t in gates.items()}
    both=z["calibrated"] and z["miscalibrated-hold-all"]
    amb+=both
    # canary: known-benign score 10 replayed through each gate
    diag={g:("ok" if gate(10,t)=="allow" else "miscalibrated") for g,t in gates.items()}
    canary_ok+= diag["calibrated"]=="ok" and diag["miscalibrated-hold-all"]=="miscalibrated"
    rows+=1
    print(kind,"zero-allow:",z,"canary:",diag)
def probe_leak(distinct,t=70):
    lo,hi,n=0,100,0
    while hi-lo>1 and distinct:
        mid=(lo+hi)//2; n+=1
        if gate(mid,t)=="allow": lo=mid
        else: hi=mid
    return n,(hi if distinct else None)
leak_n,found=probe_leak(True); print("distinct hold response: probes",leak_n,"recovered threshold",found)
print("identical acknowledgement: recovered",probe_leak(False)[1])
ok=amb==1 and canary_ok==3 and found==70 and leak_n==7
print("RESULT:","PASS" if ok else "FAIL",f"zero-allow ambiguous in {amb}/3 histories (all-risky), canary separates {canary_ok}/3, distinct hold leaks threshold in {leak_n} probes, identical ack leaks none")
