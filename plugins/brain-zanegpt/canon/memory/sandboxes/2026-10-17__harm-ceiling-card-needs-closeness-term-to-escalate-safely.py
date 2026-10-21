import random
# Toy benign-violation model. harm h in 1..10, framing distance d in 1..10 (higher = more distant),
# victim closeness c in 0..1 (1 = audience identifies with victim).
# True tolerance (benign): h <= d*(1 - 0.6*c). A beat is FUNNY if 1<=h<=tolerance, score h; UNSAFE if h>tolerance.
def tol(d, c): return d*(1-0.6*c)
def run(policy, d, c, steps=6, goal=10):
    # go-big schedule climbing toward `goal`; policy caps severity from the rule card
    sched = [min(goal, 1 + round(i*(goal-1)/(steps-1))) for i in range(steps)]
    cap = {"none": 99, "ceiling_d": d, "ceiling_d_closeness": tol(d, c) if True else d}[policy]
    funny = unsafe = 0; score = 0
    for h in sched:
        h = min(h, cap)
        if h > tol(d, c): unsafe += 1
        else: funny += 1; score += h
    return funny, unsafe, score
random.seed(3)
cases = [(random.randint(2,10), random.choice([0.0,0.25,0.5,0.75,1.0])) for _ in range(300)]
def agg(policy, sel=lambda d,c: True):
    f=u=s=n=0
    for d,c in cases:
        if not sel(d,c): continue
        a,b,x = run(policy,d,c); f+=a; u+=b; s+=x; n+=1
    return n, f, u, s
out = {}
for pol in ("none","ceiling_d","ceiling_d_closeness"):
    out[pol] = {"all": agg(pol), "far(c=0)": agg(pol, lambda d,c: c==0.0), "close(c>=.75)": agg(pol, lambda d,c: c>=0.75)}
for pol,v in out.items(): print(pol, {k:(f"unsafe={x[2]} score={x[3]}") for k,x in v.items()})
far_ok = out["ceiling_d"]["far(c=0)"][2] == 0           # ceiling alone safe when victim distant
close_bad = out["ceiling_d"]["close(c>=.75)"][2] > 0    # BREAK: close victims -> still unsafe
fixed = out["ceiling_d_closeness"]["all"][2] == 0
cost = out["ceiling_d_closeness"]["all"][3] / out["ceiling_d"]["all"][3]
ok = far_ok and close_bad and fixed and out["none"]["all"][2] > out["ceiling_d"]["all"][2] > 0
print(f"score kept vs ceiling-only: {cost:.2f}")
print("RESULT: %s ceiling-only unsafe beats %d (far victims %d, close victims %d); closeness-aware ceiling %d unsafe; no-card %d" % ("PASS" if ok else "FAIL", out["ceiling_d"]["all"][2], out["ceiling_d"]["far(c=0)"][2], out["ceiling_d"]["close(c>=.75)"][2], out["ceiling_d_closeness"]["all"][2], out["none"]["all"][2]))
