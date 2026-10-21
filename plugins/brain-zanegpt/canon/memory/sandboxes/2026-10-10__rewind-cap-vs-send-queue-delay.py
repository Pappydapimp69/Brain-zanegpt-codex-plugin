# Deterministic sandbox: lag-comp rewind cap vs transport-added latency.
# Target runs from x=0 toward cover at x>=COVER_X at SPEED u/ms from t=0 (start x=0).
# Shooter fires at server time T; client claims latency L = rtt/2 + transport_delay.
# Server rewinds target to T-min(L,CAP) and hits if that position is exposed (x<COVER_X).
SPEED=0.2; COVER_X=20.0   # target enters cover at t=100ms
def pos(t): return max(0.0,SPEED*t)
def hit(T,claimed,cap):
    r=min(claimed,cap); return pos(T-r) < COVER_X
def true_visible(T,real_lat):  # what the shooter actually saw
    return pos(T-real_lat) < COVER_X
T=150.0  # server time of arrival; target already 10 units into cover (x=30)
# transport delay models
def ws_queue_delay(send_rate,drain_rate,ticks,tick_ms=16):  # bufferedAmount growth -> added ms
    buf=0
    for _ in range(ticks): buf=max(0,buf+send_rate-drain_rate)
    return buf/drain_rate*tick_ms
def dc_reliable_stall(loss_every,rto): return rto  # one lost packet stalls everything behind it by RTO
rows=[]
print("S1 rewind cap, base 40ms latency, no transport delay")
for cap in (1000,100,50):
    h=hit(T,40,cap); rows.append(("S1",cap,h)); print(" cap",cap,"hit",h)
print("S2 websocket send-queue: sender 2x drain for N ticks inflates claimed latency")
for ticks in (0,5,20):
    q=ws_queue_delay(2,1,ticks); L=40+q
    print(" ticks",ticks,"queue_ms",round(q),"uncapped hit",hit(T,L,1000),"cap100 hit",hit(T,L,100))
print("S3 reliable datachannel HOL stall of 200ms RTO vs unreliable")
Lrel=40+dc_reliable_stall(1,200); Lunr=40
print(" reliable claimed",Lrel,"uncapped hit",hit(T,Lrel,1000),"cap100 hit",hit(T,Lrel,100))
print(" unreliable claimed",Lunr,"uncapped hit",hit(T,Lunr,1000))
print("S4 BREAK: cap harms a legit high-ping shooter (real latency 180ms, shot at T=150 vs target still exposed in his view)")
# shooter true view: target at T-180 = -30 -> x=0 exposed; in cover test use T=250: target x=50 in cover now, view T-180=70 -> x=14 exposed
T2=250.0
legit=true_visible(T2,180)
print(" shooter saw exposed:",legit,"cap100 server hit:",hit(T2,180,100),"cap200 hit:",hit(T2,180,200))
# first run (cap100) was predicted to block; it did not: target only 50ms into cover, 100ms rewind still exposed.
# So the cap must be below time-in-cover (50ms here) to block. Sweep caps:
Lq=40+ws_queue_delay(2,1,20)
blocked={c: (not hit(T,Lq,c)) for c in (200,100,60,50,20)}
print("queue-inflated shot blocked by cap:",blocked)
rel_blocked={c:(not hit(T,Lrel,c)) for c in (100,50)}
print("HOL-stalled shot blocked by cap:",rel_blocked)
# honest-shooter cost of the cap that blocks: legit 80ms shooter at T2
T3=170.0; legit80=true_visible(T3,80); print("legit 80ms shooter saw exposed:",legit80,"server hit at cap50:",hit(T3,80,50),"cap100:",hit(T3,80,100))
ok = (hit(T,Lq,1000) and blocked[50] and not blocked[100] and rel_blocked[50] and not rel_blocked[100] and legit80 and not hit(T2,80,50) and exp_break_dummy if False else True)
checks = hit(T,Lq,1000) and blocked[50] and not blocked[100] and rel_blocked[50] and legit80 and (not hit(T3,80,50)) and legit and not hit(T2,180,100)
print("RESULT: %s cap blocks transport-inflated shots only when cap < time-in-cover (50ms ok, 100ms leaks); same cap also denies a legit 80ms shooter"%("PASS" if checks else "FAIL"))
