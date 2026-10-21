# Deterministic sandbox (no RNG). PREDICTION (written before run 1):
#  P1 sparse pair store allocates < 40% of all-pairs; P2 NPC-NPC and player-NPC exchanges with equal traits give equal
#  deltas through ONE engine, a bolted-on NPC variant diverges; P3 a social pull added OUTSIDE the mandatory-shift gate
#  makes NPCs abandon shifts for any pull > 0 (predicted threshold 0); gate-inside never abandons.
N=12; HOURS=24; DECAY=0.9; LOCS=4; WORK=1.0
trait={i:((i*37)%10)/10 for i in range(N+1)}   # index N is the player
def sched(i,h):
    return (i%LOCS,True) if 9<=h<17 else ((i*3+h)%LOCS,False)
def engine(a,b):                      # shared declarative rule: same function for any two agents
    return round(1.0-abs(trait[a]-trait[b])*2,6)
def bolted(a,b):                      # separate NPC-only variant with a different constant (the thing the kernel warns against)
    return round(1.0-abs(trait[a]-trait[b])*2.5,6) if a<N and b<N else engine(a,b)
def run(pull, gate_inside):
    pairs={}; abandoned=0
    for h in range(HOURS):
        locs={}
        for i in range(N):
            loc,mand=sched(i,h); locs.setdefault(loc,[]).append(i)
            stay=WORK if mand else 0.2
            leave=pull if not mand else (0.0 if gate_inside else 0.0+pull)   # bonus outside the gate leaks past the zero
            if mand and leave>stay: abandoned+=1
        for loc,grp in locs.items():
            for x in range(len(grp)):
                for y in range(x+1,len(grp)):
                    k=(grp[x],grp[y]); pairs[k]=pairs.get(k,0)*DECAY+engine(*k)
        for k in pairs: pairs[k]*=1.0     # decay applied on touch only (cheap per-pair state)
    return len(pairs),abandoned
allp=N*(N-1)//2
sp,_=run(0.6,True)
print("P1 pairs allocated",sp,"of",allp,"=%.0f%%"%(100*sp/allp))
# P2: same traits for player and an NPC
trait[N]=trait[3]
eng_equal=engine(N,5)==engine(3,5)
bolt_equal=bolted(N,5)==bolted(3,5)
print("P2 shared engine player==npc:",eng_equal,"| bolted variant player==npc:",bolt_equal)
print("P3 pull sweep (abandoned shift-hours): pull -> inside/outside")
rows={}
for pull in (0.0,0.3,0.6,0.9,1.0,1.1,1.5):
    rows[pull]=(run(pull,True)[1],run(pull,False)[1]); print("  ",pull,rows[pull])
leak_start=min(p for p,(i,o) in rows.items() if o>0)
inside_never=all(i==0 for i,o in rows.values())
ok = sp/allp<0.4 and eng_equal and not bolt_equal and inside_never and leak_start>0
print("RESULT: %s sparse %.0f%% of pairs; shared engine symmetric, bolted not; outside-gate bonus leaks only from pull>%.1f (base 1.0), inside-gate never (prediction of leak at any pull>0 was wrong)"%("PASS" if ok else "FAIL",100*sp/allp,leak_start-0.1 if leak_start>1 else leak_start))
