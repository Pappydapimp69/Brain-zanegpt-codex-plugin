# Fixed-window limiter: LIMIT requests per WINDOW ticks. Clients need to complete NEED requests.
LIMIT, WINDOW, NEED = 10, 60, 25
class Server:
    def __init__(s, banned=()): s.reqs={}; s.rej=0; s.banned=set(banned); s.log=[]
    def call(s, cid, t):
        if cid in s.banned: s.rej+=1; return 403, {}
        w=t//WINDOW; n=s.reqs.get(w,0)
        h=lambda used: {"remaining":LIMIT-used,"reset":(w+1)*WINDOW,"retry_after":(w+1)*WINDOW-t}
        if n>=LIMIT: s.rej+=1; return 429, h(n)
        s.reqs[w]=n+1; return 200, h(n+1)
def blind(cid, srv):                      # retry next tick on any non-200
    t=0; done=0; sent=0
    while done<NEED and t<2000:
        st,_=srv.call(cid,t); sent+=1
        if st==200: done+=1
        t+=1
    return t, sent
def backoff(cid, srv, honor403=True):     # exponential backoff, no header use
    t=0; done=0; sent=0; wait=1
    while done<NEED and t<2000:
        st,_=srv.call(cid,t); sent+=1
        if st==200: done+=1; wait=1; t+=1
        elif st==403 and honor403: return t, sent
        else: t+=wait; wait=min(wait*2,64)
    return t, sent
def aware(cid, srv):                       # reads remaining; sleeps to reset when 0
    t=0; done=0; sent=0
    while done<NEED and t<2000:
        st,h=srv.call(cid,t); sent+=1
        if st==200:
            done+=1
            t = h["reset"] if h["remaining"]==0 else t+1
        else: t += h["retry_after"]
    return t, sent
r={}
for name,fn in (("blind",blind),("backoff",backoff),("aware",aware)):
    s=Server(); t,sent=fn("c",s); r[name]=(t,sent,s.rej); print(f"{name:8s} finish t={t} sent={sent} rejected={s.rej}")
# sibling kernel: 401/403 is not 429 -> retrying a 403 is pure waste
s1=Server(banned=("c",)); t,sent=backoff("c",s1,honor403=False); w403=s1.rej
s2=Server(banned=("c",)); t2,sent2=backoff("c",s2,honor403=True)
print("403 retried like 429: rejected", w403, "| status-aware: rejected", s2.rej)
# BREAK: 5 header-aware clients on one shared window all wake at the reset together
def herd(k):
    s=Server(); ts=[0]*k; done=[0]*k; waking=[0]*k; sent=0
    t=0
    while min(done)<NEED and t<2000:
        for i in range(k):
            if waking[i]<=t and done[i]<NEED:
                st,h=s.call(i,t)
                if st==200: done[i]+=1; waking[i]= h["reset"] if h["remaining"]==0 else t
                else: waking[i]=t+h["retry_after"]
        t+=1
    return s.rej
print("5 aware clients sharing a window, rejections:", herd(5), "| 1 client:", r["aware"][2])
ok = (r["aware"][2]==0 and r["blind"][2]>r["backoff"][2]>0 and r["aware"][0]<=r["backoff"][0]
      and w403>s2.rej==1 and herd(5)>0)
print("RESULT: %s headers cut rejections to %d vs backoff %d vs blind %d at finish t=%d vs %d; 403 retried %d times vs 1; 5 aware clients sharing a window still collide (%d rejections)" % ("PASS" if ok else "FAIL", r["aware"][2], r["backoff"][2], r["blind"][2], r["aware"][0], r["backoff"][0], w403, herd(5)))
