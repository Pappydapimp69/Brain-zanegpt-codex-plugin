"""Reaction-cut pause placement on a real 2:00 captioned film (What Changed).
Deterministic, stdlib only. A reactor reacts to a trigger phrase inside a caption.
Policies: SNAP (pause at the end of the caption holding the trigger),
WORD (pause on the trigger word, then run the caption back from its start),
CUT (pause on the trigger word, resume where it stopped: the line is split),
INTERVAL (pause every P seconds regardless of content).
Metrics: lines split, seconds replayed, lag from trigger word to pause.
TOL is an assumed comment-lag tolerance (seconds), not measured."""
CAPS=[[0.5, 6.88, "October 12. The film ended on an empty chair: nothing was watching Brain think."], [7.28, 15.65, "Five days later, the system that chair looked at is not the same system."], [16.5, 24.04, "On October 15 the count fell on purpose: 2,472 notes to 1,827, one family of echoes removed."], [24.44, 28.9, "By October 17 it had grown back to 2,141."], [29.3, 39.65, "Whether the removed family deserves any weight is still open. Settled is not the same as true."], [40.5, 46.5, "Brain also learns two ways now. One half still mends the weakest links."], [46.9, 55.21, "A new half follows the paths that get used most. They share one budget and hand each other work."], [55.61, 63.53, "Since October 15: 138 lessons from the new half, 81 from the old, 97 handoffs across the bridge."], [63.93, 68.98, "The tool passes no verdict. The owner decides."], [69.83, 73.53, "Therefore the chair is no longer empty."], [73.93, 82.32, "Conscience sits in it. It reads everything, reports what changed, and cannot steer."], [83.17, 90.32, "On October 17 the intake got stricter. A citation to nothing is held at the door."], [90.72, 96.34, "So is a second name for a project that already has one."], [96.74, 103.65, "The guards are one day old. New, not proven."], [104.5, 110.12, "2,141 notes. 130 questions tracked, 21 with evidence, the rest still open."], [110.52, 119.65, "Open is not a failure here. It is how the system keeps from fooling itself."]]
TRIG=[(2,"echoes removed"),(4,"still open"),(6,"hand each other work"),(7,"81 from the old"),(10,"cannot steer"),(15,"fooling itself")]
TOL=5.0
def tword(ci,phrase):
    s,e,t=CAPS[ci];w=t.split();pw=phrase.split();n=len(w)
    for i in range(n-len(pw)+1):
        if [x.strip(".,:") for x in w[i:i+len(pw)]]==[x.strip(".,:") for x in pw]:return s+(e-s)*(i+len(pw))/n
    raise ValueError(phrase)
def run(caps,trig,policy,P=15.0):
    global CAPS;old=CAPS;CAPS=caps
    split=0;replay=0.0;lags=[]
    if policy=="INTERVAL":
        t=P
        while t<caps[-1][1]:
            if any(s<t<e for s,e,_ in caps):split+=1
            t+=P
        CAPS=old;return dict(split=split,replay=0.0,maxlag=None,pauses=int(caps[-1][1]//P))
    for ci,ph in trig:
        s,e,_=caps[ci];tw=tword(ci,ph)
        if policy=="SNAP":lags.append(e-tw)
        elif policy=="WORD":lags.append(0.0);replay+=tw-s
        elif policy=="CUT":lags.append(0.0);split+=1 if tw<e-1e-6 else 0
    CAPS=old;return dict(split=split,replay=round(replay,2),maxlag=round(max(lags),2),pauses=len(trig))
def scen(name,caps,trig):
    r={p:run(caps,trig,p) for p in("SNAP","WORD","CUT","INTERVAL")};print(name);[print("  ",p,r[p]) for p in r];return r
base=scen("1) real film, 6 triggers",CAPS,TRIG)
# 2) clustered: triggers in back-to-back captions (6,7,8 and 9,10)
clu=TRIG+[(8,"owner decides"),(9,"no longer empty")];clu.sort()
c2=scen("2) clustered triggers in consecutive captions",CAPS,clu)
# 3) BREAK: one long caption (12 s) with the trigger early in it
long=[list(c) for c in CAPS];long[10]=[73.93,85.93,"Conscience cannot steer. It sits in the chair, reads everything and reports what changed to the owner."]
c3=scen("3) BREAK: 12 s caption, trigger in its first quarter",long,[(2,"echoes removed"),(10,"cannot steer")])
dur=CAPS[-1][1]
ok1=base["SNAP"]["split"]==0 and base["SNAP"]["replay"]==0 and base["SNAP"]["maxlag"]<=TOL
ok2=c2["SNAP"]["split"]==0 and c2["SNAP"]["maxlag"]<=TOL
brk=c3["SNAP"]["maxlag"]>TOL
print("interval split share %d/%d, WORD replay %.1f s = %.0f%% of %.0f s"%(base["INTERVAL"]["split"],base["INTERVAL"]["pauses"],base["WORD"]["replay"],100*base["WORD"]["replay"]/dur,dur))
print(("RESULT: PASS " if ok1 and ok2 and brk else "RESULT: FAIL ")+"snap-to-caption-end: 0 split, 0 replay, max lag %.2f s real / %.2f s clustered; 15 s interval split %d of %d pauses; run-back replays %.1f s (%.0f%%); breaks on a 12 s caption with an early trigger (lag %.2f s > %.0f s)"%(base["SNAP"]["maxlag"],c2["SNAP"]["maxlag"],base["INTERVAL"]["split"],base["INTERVAL"]["pauses"],base["WORD"]["replay"],100*base["WORD"]["replay"]/dur,c3["SNAP"]["maxlag"],TOL))
