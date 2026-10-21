# PREDICTION (written before run 1): fixed-svc N=16,c=4 -> thr 4.00 lat 4.0; variable service at N=c leaves servers idle so thr<3.9 (REFUTED by run 1: shared stayed 4.00); separate queues lose throughput at N=c.
import heapq
SV=[0.1,1.9,0.5,1.5,1.0,0.3,1.7,1.0]   # deterministic service pattern, mean 1.0
def sim(N,c,var,pooled,T=4000.0):
    cnt=[0]
    def svc():
        s=SV[cnt[0]%len(SV)] if var else 1.0; cnt[0]+=1; return s
    ev=[]; done=0; lat=0.0
    if pooled:
        free=c; q=[]  # queue of submit times
        for i in range(N): q.append(0.0)
        t=0.0
        while True:
            while free and q:
                s0=q.pop(0); free-=1; heapq.heappush(ev,(t+svc(),s0))
            if not ev: break
            t,s0=heapq.heappop(ev)
            if t>T: break
            done+=1; lat+=t-s0; free+=1; q.append(t)
    else:
        qs=[[] for _ in range(c)]; busy=[False]*c; nxt=[0]
        def submit(t):
            k=nxt[0]%c; nxt[0]+=1; qs[k].append(t)
        for i in range(N): submit(0.0)
        t=0.0
        def start(t):
            for k in range(c):
                if not busy[k] and qs[k]:
                    s0=qs[k].pop(0); busy[k]=True; heapq.heappush(ev,(t+svc(),(k,s0)))
        start(0)
        while ev:
            t,(k,s0)=heapq.heappop(ev)
            if t>T: break
            done+=1; lat+=t-s0; busy[k]=False; submit(t); start(t)
    return done/T, lat/max(done,1)
c=4
print("N  | fixed-svc shared thr,lat | var shared thr,lat | var separate thr,lat")
rows={}
for N in (2,4,6,8,16):
    a=sim(N,c,False,True); b=sim(N,c,True,True); d=sim(N,c,True,False); rows[N]=(a,b,d)
    print(N,"%.2f %.2f | %.2f %.2f | %.2f %.2f"%(a+b+d))
ok=True
ok&=abs(rows[16][0][0]-4)<0.05 and abs(rows[16][0][1]-4.0)<0.1          # kernel: 4 servers, 16 in flight -> thr 4, lat 4
ok&=rows[2][0][0]<rows[4][0][0]-1.5                                       # below capacity thr = N
ok&=abs(rows[16][1][0]*rows[16][1][1]-16)<0.5                             # Little L=lambda W holds under variability
ok&=rows[4][1][0]>3.99                                                    # BREAK (my prediction said <3.9, refuted): shared queue at N=c stays work-conserving even with variable service
ok&=rows[4][2][0]<3.5 and rows[6][2][0]>3.99                              # separate queues lose ~22% at N=c, recover by N=1.5c
print("RESULT: %s cap N=c holds for a shared queue (4.00/s, even with variable service) but per-server queues drop to %.2f/s at N=c and recover by N=6; N=16 gives thr 4.00 lat 4.0 either way"%("PASS" if ok else "FAIL",rows[4][2][0]))
