"""Sandbox: mechanism tests vs rate tests (kernel testing/verification/mechanism-tests-and-rate-tests-are-different-axes).
Feature: a 'party sighting' event. Each tick, a roll with probability P may fire it, but only if the party
is inside the lead's field of view. Party chases a formation slot derived from the lead's yaw. Deterministic."""
import math, sys

FOV = math.radians(120)

def fwd(yaw): return (math.cos(yaw), math.sin(yaw))

def visible(lead, yaw, party, fov=FOV, sign=1):
    dx, dy = party[0]-lead[0], party[1]-lead[1]
    d = math.hypot(dx, dy)
    if d < 1e-9: return True
    f = fwd(yaw)
    c = (dx*f[0]+dy*f[1])/d * sign
    return c >= math.cos(fov/2)

def fires(roll, p, vis):  # the feature under test
    return vis and roll < p

def sim(model, ticks, slot_dist=3.0, speed=1.0, **kw):
    """returns list of per-tick visibility booleans; party chases slot = lead - fwd*slot_dist at <= speed."""
    lead=[0.0,0.0]; yaw=0.0; party=[-slot_dist,0.0]; out=[]
    for t in range(ticks):
        act = model(t)
        if act == 'walk':
            f=fwd(yaw); lead[0]+=f[0]*speed; lead[1]+=f[1]*speed
        elif act == 'spin':
            yaw += math.radians(30)
        elif act == 'turn':
            yaw += math.pi
        f=fwd(yaw); slot=(lead[0]-f[0]*slot_dist, lead[1]-f[1]*slot_dist)
        dx,dy=slot[0]-party[0],slot[1]-party[1]; d=math.hypot(dx,dy)
        if d>1e-9:
            s=min(speed,d); party[0]+=dx/d*s; party[1]+=dy/d*s
        out.append(visible(lead,yaw,party,**kw))
    return out

def m_spin(t): return 'spin'
def m_walk(t): return 'walk'
def m_wstw(period):   # walk, stop, turn around, walk on
    def m(t):
        k=t%period
        if k==period-2: return 'stop'
        if k==period-1: return 'turn'
        return 'walk'
    return m

N=2000; P=1/4096
res={}
for name,m in [('spin',m_spin),('straight-walk',m_walk),('wstw-20',m_wstw(20)),('wstw-200',m_wstw(200))]:
    v=sim(m,N); res[name]=sum(v)
    print(f"model {name:14s} visible ticks={res[name]:4d}/{N}  expected fires at P=1/4096: {res[name]*P:.3f}")

# Scenario 1: mechanism test (roll stubbed to 0, party hand-placed in front) passes at ANY rate incl. P=0+ epsilon
mech = fires(0.0, 1e-12, visible((0,0),0.0,(2,0)))
print("S1 mechanism test (stub roll, hand-placed party) passes at P=1e-12:", mech)
# Scenario 2: rate test with stated models
rate_spin = res['spin']*P; rate_w = res['wstw-20']*P
print("S2 rate: spin model fires/2000 ticks =", rate_spin, "; wstw-20 =", round(rate_w,3))
# Scenario 3 (BREAK): rate answer depends on the behaviour model: 20- vs 200-tick cadence
ratio = res['wstw-20']/max(1,res['wstw-200'])
print(f"S3 BREAK: wstw-20 vs wstw-200 visible ticks ratio = {ratio:.1f}x")

# Scenario 4: bug matrix -- do mechanism and rate tests have private catch sets?
def mech_test(sign=1, fov=FOV):  return fires(0.0,1.0,visible((0,0),0.0,(2,0),fov=fov,sign=sign))
def rate_test(p=0.05, sign=1, fov=FOV, need=0.5):
    return sum(sim(m_wstw(20),N,sign=sign,fov=fov))*p >= need
bugs={'ok':{}, 'sign-flipped':{'sign':-1}, 'fov-too-narrow(10deg)':{'fov':math.radians(10)}, 'rate-1000x-low':{'p':0.05/1000}, 'shipped-p=1/4096':{'p':P}}
catch={}
for b,kw in bugs.items():
    kw_m={k:v for k,v in kw.items() if k in('sign','fov')}
    mt=mech_test(**kw_m); rt=rate_test(**kw)
    catch[b]=(mt,rt); print(f"S4 bug {b:24s} mechanism_pass={mt} rate_pass={rt}")
mech_only_catch=[b for b,(m,r) in catch.items() if not m and r]
rate_only_catch=[b for b,(m,r) in catch.items() if m and not r and b!='ok']
print("S4 caught only by mechanism:",mech_only_catch," caught only by rate:",rate_only_catch)

# Scenario 5: uncontrolled A/B -- same seed, build B draws one extra roll per tick
def lcg(seed):
    s=seed
    while True:
        s=(s*6364136223846793005+1442695040888963407)%(1<<64); yield (s>>11)/(1<<53)
def fire_ticks(extra_draw, vis, p=0.05):
    g=lcg(7); hits=[]
    for t,v in enumerate(vis):
        if extra_draw: next(g)       # unrelated feature in build B consumes a draw
        if fires(next(g),p,v): hits.append(t)
    return hits
vis=sim(m_wstw(20),N)
a=fire_ticks(False,vis); b=fire_ticks(True,vis)
print(f"S5 shared stream: A fires={len(a)} B fires={len(b)} identical ticks={len(set(a)&set(b))}")
def keyed(tick,purpose,seed=7):
    x=(seed*0x9E3779B97F4A7C15 ^ tick*0xBF58476D1CE4E5B9 ^ hash_purpose(purpose)*0x94D049BB133111EB)%(1<<64)
    x^=x>>31; x=(x*0xD6E8FEB86659FD93)%(1<<64); x^=x>>32
    return (x>>11)/(1<<53)
def hash_purpose(s): return sum((i+1)*ord(c) for i,c in enumerate(s))
ka=[t for t,v in enumerate(vis) if fires(keyed(t,'sighting'),0.05,v)]
kb=[t for t,v in enumerate(vis) if (keyed(t,'other'), fires(keyed(t,'sighting'),0.05,v))[1]]
print(f"S5 keyed (tick,purpose): A fires={len(ka)} B fires={len(kb)} identical={ka==kb}")

checks=[mech, res['spin']==0, res['wstw-20']>0, ratio>=5, len(a)!=len(b) or a!=b, ka==kb,
        not catch['rate-1000x-low'][1] and catch['rate-1000x-low'][0], not catch['sign-flipped'][0]]
print("checks:",checks)
print(("RESULT: PASS" if all(checks) else "RESULT: FAIL"),
 f"spin visible={res['spin']}, wstw-20={res['wstw-20']}, wstw-200={res['wstw-200']}, mech passes at P=1e-12, shared-stream A/B diverges ({len(a)} vs {len(b)}), keyed identical={ka==kb}")
