"""Own-fixture rebuild: beat-ledger Chekhov checker. 3 eight-beat stories, 2 spotlighted details each.
Events: (beat, detail, kind) kind in intro|spot|mention|use. Final beat = 7.
PREDICTION (before run): unmutated 0 flags in 3/3; delete_use caught by R1 in 6/6; echo_only caught by R1 6/6 while
promise-only(mentioned again later) misses 6/6; remove_intro caught by R2 6/6; dead_end caught by R3 and NOT R1 6/6 while promise-only misses 6/6;
deleting a background mention flags 0; motif (spot + only mentions, deliberate) flagged until exempt."""
FINAL=7
def S(*ev): return list(ev)
stories={
 "lighthouse":S((0,"key","intro"),(1,"key","spot"),(2,"lamp","mention"),(4,"key","use"),(7,"key","use"),
                (0,"flare","intro"),(2,"flare","spot"),(5,"flare","use"),(7,"flare","use"),(3,"rain","mention")),
 "market":S((1,"coin","spot"),(3,"coin","use"),(7,"coin","use"),(0,"map","intro"),(2,"map","spot"),(6,"map","use"),(7,"map","use"),(4,"cart","mention"),(5,"cart","mention")),
 "orchard":S((0,"saw","intro"),(2,"saw","spot"),(5,"saw","use"),(7,"saw","use"),(1,"ladder","intro"),(3,"ladder","spot"),(4,"ladder","use"),(7,"ladder","use"),(6,"crow","mention")),
}
def spotted(ev): return sorted({d for b,d,k in ev if k=="spot"})
def check(ev, exempt=()):
    flags=[]
    for d in spotted(ev):
        if d in exempt: continue
        spot=min(b for b,x,k in ev if x==d and k=="spot")
        uses=[b for b,x,k in ev if x==d and k=="use"]
        if not [u for u in uses if u>spot]: flags.append(("R1",d))
        for u in uses:
            if not any(x==d and k in("intro","spot") and b<=u for b,x,k in ev): flags.append(("R2",d)); break
        if FINAL not in uses and uses: flags.append(("R3",d))
        if FINAL not in uses and not uses: flags.append(("R3",d))
    # R2 also for non-spotlighted used details
    for d in {x for b,x,k in ev if k=="use"}-set(spotted(ev)):
        u=min(b for b,x,k in ev if x==d and k=="use")
        if not any(x==d and k in("intro","spot") and b<=u for b,x,k in ev): flags.append(("R2",d))
    return flags
def promise_only(ev):   # naive: spotlighted detail merely appears again later in any form
    out=[]
    for d in spotted(ev):
        spot=min(b for b,x,k in ev if x==d and k=="spot")
        if not [1 for b,x,k in ev if x==d and b>spot]: out.append(d)
    return out
def mut(ev,d,kind):
    e=list(ev)
    if kind=="delete_use": return [t for t in e if not(t[1]==d and t[2]=="use")]
    if kind=="echo_only": return [(b,x,"mention" if(x==d and k=="use") else k) for b,x,k in e]
    if kind=="remove_intro": return [t for t in e if not(t[1]==d and t[2] in("intro","spot") and t[0]<min(bb for bb,xx,kk in e if xx==d and kk=="use"))]+[]
    if kind=="dead_end": return [t for t in e if not(t[1]==d and t[2]=="use" and t[0]==FINAL)]
ok=[]
base=[len(check(ev)) for ev in stories.values()]; ok.append(base==[0,0,0]); print("unmutated flags:",base)
want={"delete_use":"R1","echo_only":"R1","remove_intro":"R2","dead_end":"R3"}
for m,rule in want.items():
    caught=notR1=pmiss=n=0
    for name,ev in stories.items():
        for d in spotted(ev):
            n+=1; me=mut(ev,d,m); fl=[f for f in check(me) if f[1]==d]
            if m=="remove_intro":
                # keep one spot so 'spotlight' remains: re-add spot only after use is impossible -> just test R2 on use w/o earlier intro
                pass
            caught+= any(r==rule for r,_ in fl)
            notR1+= not any(r=="R1" for r,_ in fl)
            pmiss+= d not in promise_only(me)
    print(f"{m}: caught by {rule} {caught}/{n}; R1 silent {notR1}/{n}; promise-only misses {pmiss}/{n}")
    ok.append(caught==n)
    if m in("echo_only","dead_end"): ok.append(pmiss==n)
    if m=="dead_end": ok.append(notR1==n)
# background deletion
bg=0
for name,ev in stories.items():
    for d in {x for b,x,k in ev if k=="mention"}:
        bg+=len(check([t for t in ev if not(t[1]==d and t[2]=="mention")]))
ok.append(bg==0); print("background mention deletions flagged:",bg)
# motif
mot=stories["lighthouse"]+[(1,"fog","spot"),(4,"fog","mention"),(7,"fog","mention")]
f1=[f for f in check(mot) if f[1]=="fog"]; f2=[f for f in check(mot,exempt=("fog",)) if f[1]=="fog"]
ok.append(len(f1)>0 and not f2); print("motif flagged:",f1,"after exempt:",f2)
print("RESULT: %s unmutated 0 flags; each rule caught its mutation; promise-only misses echo/dead-end; background silent; motif flagged then exempted"%("PASS" if all(ok) else "FAIL"))
