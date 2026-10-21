"""sfc32 stream. Compare saving full state words vs {seed,count} replay; show roll-order desync between two clients;
and a canonical (sorted-key) fingerprint vs insertion-order fingerprint. Deterministic.
Prediction (before run): (1) state-word restore costs 0 rolls and gives identical next 100 rolls; count-replay costs `count` rolls, same output;
(2) two clients applying the same rolls in a different ORDER diverge (the single shared stream is order-sensitive) and the fingerprint catches it;
(3) inserting ONE extra roll early shifts every later roll (golden replay breaks), while per-system sub-streams keep unrelated systems unchanged;
(4) insertion-order JSON fingerprint differs for logically equal states, canonical fingerprint does not."""
import json
M=0xFFFFFFFF
class Sfc32:
    def __init__(s,a,b,c,d): s.s=[a&M,b&M,c&M,d&M]; s.rolls=0
    @classmethod
    def seeded(cls,seed):
        r=cls(0,seed,seed*3+1,1)
        for _ in range(12): r.next()
        r.rolls=0; return r
    def next(s):
        a,b,c,d=s.s
        t=(a+b+d)&M; d=(d+1)&M
        a=b^(b>>9); b=(c+(c<<3))&M
        c=((c<<21)|(c>>11))&M; c=(c+t)&M
        s.s=[a,b,c,d]; s.rolls+=1; return t
    def state(s): return list(s.s)
def fp(obj,canon):
    txt=json.dumps(obj,sort_keys=canon)
    h=2166136261
    for ch in txt.encode(): h=((h^ch)*16777619)&M
    return h
# 1: save/restore
r=Sfc32.seeded(42)
for _ in range(1000): r.next()
saved=r.state(); count=r.rolls
a=Sfc32(*saved); b=Sfc32.seeded(42); replay_cost=0
while b.rolls<count: b.next(); replay_cost+=1
same=[a.next() for _ in range(100)]==[b.next() for _ in range(100)]
print(f"restore cost state=0 rolls, count-replay={replay_cost} rolls, identical next100={same}")
# 2: roll order desync between clients: events handled in different order
def play(order):
    r=Sfc32.seeded(7); world={"loot":0,"crit":0}
    for ev in order: world[ev]=r.next()%100
    return world
w1=play(["loot","crit"]); w2=play(["crit","loot"])
desync = w1!=w2 and fp(w1,True)!=fp(w2,True)
print("order desync:",w1,w2,"fingerprints differ:",fp(w1,True)!=fp(w2,True))
# 3: one extra roll early
def run_shared(extra):
    r=Sfc32.seeded(9)
    if extra: r.next()
    return [r.next()%100 for _ in range(5)]
def run_split(extra):
    ra=Sfc32.seeded(9); rb=Sfc32.seeded(10)
    if extra: ra.next()
    return [rb.next()%100 for _ in range(5)]   # system B reads only its own stream
shared_changed=run_shared(False)!=run_shared(True)
split_b_unchanged=run_split(False)==run_split(True)
print("shared stream shifted by 1 extra roll:",shared_changed," split B unchanged:",split_b_unchanged)
# 4: fingerprint canonical
s1={"b":1,"a":2}; s2={"a":2,"b":1}
ins_diff=fp(s1,False)!=fp(s2,False); can_same=fp(s1,True)==fp(s2,True)
print("insertion-order fp differs:",ins_diff," canonical equal:",can_same)
ok = same and replay_cost==1000 and desync and shared_changed and split_b_unchanged and ins_diff and can_same
print("RESULT: %s replay_cost=%d order_desync=%s shared_shift=%s split_isolated=%s canon_fp=%s"%("PASS" if ok else "FAIL",replay_cost,desync,shared_changed,split_b_unchanged,can_same))
