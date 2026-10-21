"""Scrub (seek to tick T without replay) vs three RNG designs when per-tick roll count is state-dependent.
Entity hp walks: each tick rolls once; if hp<THRESH it rolls an extra time (state-dependent count)."""
import hashlib, random
SEED=7; N=4; TICKS=60; THRESH=5
def h(*a): return int.from_bytes(hashlib.sha256(repr(a).encode()).digest()[:8],"big")/2**64

def step_logic(hp, rolls):
    d = rolls(0); hp += 1 if d>0.45 else -1
    if hp<THRESH: hp += 1 if rolls(1)>0.5 else 0      # extra roll only when low
    return hp
def n_rolls(hp): return 2 if hp<THRESH else 1  # (documentation of count rule)

def run_shared(upto, only=None):
    rng=random.Random(SEED); hps=[8]*N
    for t in range(upto):
        for e in range(N):
            hps[e]=step_logic(hps[e], lambda k: rng.random())
    return hps
def run_per_entity(upto):
    rngs=[random.Random(h(SEED,e)) for e in range(N)]; hps=[8]*N
    for t in range(upto):
        for e in range(N): hps[e]=step_logic(hps[e], lambda k,e=e: rngs[e].random())
    return hps
def run_counter(upto):
    hps=[8]*N
    for t in range(upto):
        for e in range(N): hps[e]=step_logic(hps[e], lambda k,e=e,t=t: h(SEED,e,t,k))
    return hps

# "naive scrub": assume constant roll count (1 per tick per entity) and jump the stream forward T*1 draws, then step one tick
def naive_seek_per_entity(T):
    out=[]
    for e in range(N):
        r=random.Random(h(SEED,e))
        for _ in range(T-1): r.random()       # assumes 1 roll per tick
        hp=None; out.append(r)
    return out
def seek_per_entity_state(T, e):
    # reconstruct entity e state at T under the constant-count assumption: draws skipped = T-1 but hp unknown -> must replay
    # best direct attempt: use hp from a constant-1-roll model
    r=random.Random(h(SEED,e)); hp=8
    for t in range(T):
        d=r.random(); hp+=1 if d>0.45 else -1   # ignores extra roll
    return hp
def seek_counter(T,e):
    # counter RNG: still needs hp(T-1) state, but draws for tick t are addressable; replay cost is state only, no stream coupling
    hp=8
    for t in range(T): hp=step_logic(hp, lambda k,t=t: h(SEED,e,t,k))
    return hp

ok=[]
# Scenario 1: baseline replay agreement (control)
a=run_counter(TICKS); b=run_counter(TICKS); ok.append(a==b); print("s1 replay deterministic:",a==b)
# Scenario 2: do any entities ever hit the low branch (is roll count really state-dependent)?
low=0; hps=[8]*N
for t in range(TICKS):
    for e in range(N):
        if hps[e]<THRESH: low+=1
        hps[e]=step_logic(hps[e], lambda k,e=e,t=t: h(SEED,e,t,k))
ok.append(low>0); print("s2 ticks on low branch (extra roll):",low)
# Scenario 3 (BREAK constant-count assumption): naive seek per-entity stream disagrees with true replay
true=run_per_entity(TICKS); naive=[seek_per_entity_state(TICKS,e) for e in range(N)]
bad=sum(1 for e in range(N) if true[e]!=naive[e]); ok.append(bad>0); print("s3 naive seek mismatches (per-entity stream):",bad,"of",N)
# Scenario 4: shared stream -- changing ONE entity's extra-roll rule perturbs OTHER entities' later draws
def run_shared_with_threshold_for(e0, thr0):
    rng=random.Random(SEED); hps=[8]*N
    for t in range(TICKS):
        for e in range(N):
            def lg(hp):
                d=rng.random(); hp+=1 if d>0.45 else -1
                if hp<(thr0 if e==e0 else THRESH): hp+=1 if rng.random()>0.5 else 0
                return hp
            hps[e]=lg(hps[e])
    return hps
base=run_shared_with_threshold_for(-1,THRESH); alt=run_shared_with_threshold_for(0,THRESH+3)
shared_changed=sum(1 for e in range(1,N) if base[e]!=alt[e]); print("s4 shared stream: others changed by entity0 rule tweak:",shared_changed,"of",N-1)
def run_counter_thr(e0,thr0):
    hps=[8]*N
    for t in range(TICKS):
        for e in range(N):
            th=thr0 if e==e0 else THRESH
            def lg(hp,e=e,t=t,th=th):
                hp+= 1 if h(SEED,e,t,0)>0.45 else -1
                if hp<th: hp+= 1 if h(SEED,e,t,1)>0.5 else 0
                return hp
            hps[e]=lg(hps[e])
    return hps
cb=run_counter_thr(-1,THRESH); ca=run_counter_thr(0,THRESH+3)
counter_changed=sum(1 for e in range(1,N) if cb[e]!=ca[e]); print("s5 counter rng: others changed:",counter_changed,"of",N-1)
ok.append(shared_changed>0 and counter_changed==0)
# Scenario 6: counter RNG seek to arbitrary T matches full replay at several T
chk=all(seek_counter(T,e)==run_counter(T)[e] for T in (1,13,40,60) for e in range(N)); ok.append(chk); print("s6 counter seek == replay at T=1,13,40,60:",chk)
print("RESULT: %s naive constant-count seek wrong for %d/%d entities; shared stream leaks rule change to %d/%d others, counter RNG to %d; counter seek matches replay"%("PASS" if all(ok) else "FAIL",bad,N,shared_changed,N-1,counter_changed))
