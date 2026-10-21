# Deterministic limiter comparison. Limit L=10 requests per W=10 s. Integer ticks (1 tick = 1 s).
L, W = 10, 10

def fixed_window(times):
    out, win, cnt = [], None, 0
    for t in times:
        w = t // W
        if w != win: win, cnt = w, 0
        if cnt < L: cnt += 1; out.append(t)
    return out

def sliding_log(times):
    out = []
    for t in times:
        if sum(1 for u in out if t - W < u <= t) < L: out.append(t)
    return out

def token_bucket(times, cap=L, rate=L / W):
    out, tok, last = [], float(cap), 0
    for t in times:
        tok = min(cap, tok + (t - last) * rate); last = t
        if tok >= 1: tok -= 1; out.append(t)
    return out

def worst_window(adm):          # most admitted in any W-second span
    return max((sum(1 for u in adm if s <= u < s + W) for s in range(0, 60)), default=0)

# 1) attacker bursts L requests at t=9 (end of window 0) and L at t=10 (start of window 1)
burst = [9] * 10 + [10] * 10
# 2) BREAK: same total load spread evenly (2 per second for 10 s): nobody is limited unfairly?
steady = [t for t in range(10, 20) for _ in range(2)]
# 3) steady well-behaved 1 req/s: no limiter should reject
calm = list(range(30))
res = {}
for name, f in (("fixed", fixed_window), ("sliding", sliding_log), ("bucket", token_bucket)):
    res[name] = (worst_window(f(burst)), len(f(steady)), len(f(calm)))
    print(name, "worst-window on boundary burst:", res[name][0], "| admitted of 20 steady:", res[name][1], "| calm admitted of 30:", res[name][2])
ok = (res["fixed"][0] == 20 and res["sliding"][0] == 10 and res["bucket"][0] <= 11
      and res["fixed"][2] == res["sliding"][2] == res["bucket"][2] == 30
      and res["fixed"][1] == 10 and res["sliding"][1] == 10 and res["bucket"][1] == 19)
print(f"RESULT: {'PASS' if ok else 'FAIL'} boundary burst admitted fixed {res['fixed'][0]} vs sliding {res['sliding'][0]} vs bucket {res['bucket'][0]} per {W} s; steady 2/s load (20 sent) admitted fixed {res['fixed'][1]} sliding {res['sliding'][1]} bucket {res['bucket'][1]}; calm 30/30 all")
