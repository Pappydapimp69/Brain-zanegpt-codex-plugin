# Deterministic tick model of three netcode limits. No RNG, no real timing.
D=3  # one-way delay in ticks
# 1) reliable+ordered vs unordered+maxRetransmits=0 : position sent every tick for 60 ticks, ticks %10==0 lost on first send
def max_age(reliable):
    arrivals={}  # tick sent -> arrival tick
    for k in range(60):
        lost=(k%10==0 and k>0)
        arrivals[k]=(k+D+2*D) if (lost and reliable) else (None if lost else k+D)
    worst=0
    for t in range(10,60):
        if reliable:
            # ordered: delivery of k waits for all earlier; delivery time = running max
            run=0;deliv={}
            for k in range(60): run=max(run,arrivals[k]); deliv[k]=run
            got=[k for k in range(60) if deliv[k]<=t]
        else:
            got=[k for k in range(60) if arrivals[k] is not None and arrivals[k]<=t]
        worst=max(worst,t-max(got))
    return worst
age_rel,age_unr=max_age(True),max_age(False)
# 2) lag-compensation rewind: target exposed ticks 0..9, hidden from 10. shot at t=15.
def hit(L_effective,t=15): return (t-L_effective)<=9
def outcome(L,cap): return hit(min(L,cap) if cap is not None else L)
liar_uncapped=outcome(20,None); liar_capped=outcome(20,5)
honest_high_uncapped=outcome(8,None)   # honest 8-tick client saw old position: true hit
honest_high_capped=outcome(8,5)        # cap robs them
# 3) backpressure: producer 3 msgs/tick, link drains 2/tick, buffer limit 20; closes when exceeded
def sock(check):
    buf=0;sent=0
    for t in range(100):
        for _ in range(3):
            if check and buf>=10: continue          # skip/coalesce when buffered amount high
            buf+=1;sent+=1
            if buf>20: return "CLOSED",t
        buf=max(0,buf-2)
    return "OPEN",sent
nocheck,chk=sock(False),sock(True)
print("max position age reliable/ordered",age_rel,"unordered no-retransmit",age_unr)
print("rewind: liar uncapped",liar_uncapped,"liar cap5",liar_capped,"honest(8) uncapped",honest_high_uncapped,"honest(8) cap5",honest_high_capped)
print("socket no check",nocheck,"with check",chk)
ok=(age_rel>age_unr and liar_uncapped and not liar_capped and honest_high_uncapped and not honest_high_capped
    and nocheck[0]=="CLOSED" and chk[0]=="OPEN")
print(f"RESULT: {'PASS' if ok else 'FAIL'} ordered channel worst staleness {age_rel} vs {age_unr} ticks; uncapped rewind lets a 20-tick liar hit through cover but cap 5 also robs an honest 8-tick player; unchecked sender closes socket at tick {nocheck[1]}, checked stays open")
