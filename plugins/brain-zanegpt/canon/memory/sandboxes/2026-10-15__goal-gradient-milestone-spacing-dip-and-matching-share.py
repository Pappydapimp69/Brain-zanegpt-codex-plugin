# Deterministic sandbox: goal-gradient vigor + milestone spacing, shaping ladder, matching share.
N = 10
def vigor(k): return 1.0 / (N - k)          # k steps done, goal gradient
# S1: gradient shape
print("S1 vigor k=0:", vigor(0), "k=9:", vigor(9), "ratio", vigor(9)/vigor(0))
mono = all(vigor(k+1) > vigor(k) for k in range(N-1))
print("S1 monotonic:", mono)

# S2: agent persists while motivation >= theta. motivation = base + vigor + bonus*decay^(steps since milestone)
def completes(milestones, theta, base=0.0, bonus=1.0, decay=0.5):
    last = None
    for k in range(N):
        if k in milestones: last = k
        m = base + vigor(k) + (bonus * decay ** (k - last) if last is not None else 0.0)
        if m < theta: return False, k
    return True, N
uniform = {2, 5, 8}            # evenly spaced
front   = {0, 1, 2}            # dense early
thetas = [t/20 for t in range(1, 41)]
def count(ms, **kw): return sum(completes(ms, t, **kw)[0] for t in thetas)
print("S2 completion count over theta grid: uniform", count(uniform), "front", count(front))
# S3 (break): bonus-free agent -> milestones irrelevant; and a large decay (sticky bonus) -> front-loading helps
print("S2b bonus=0: uniform", count(uniform, bonus=0), "front", count(front, bonus=0))
print("S2c decay=0.9: uniform", count(uniform, decay=0.9), "front", count(front, decay=0.9))
mid_dip = min(range(N), key=lambda k: vigor(k)+ (1.0*0.5**(k-2) if k>=2 else 0))
print("S2d minimum-motivation step under front-load:", mid_dip)

# S4: shaping (successive approximations) ladder vs all-or-nothing, rare target
# learner raises skill by 1 per reinforced attempt; attempts succeed iff skill >= criterion
def attempts_to_target(target, shaped):
    skill, crit, n = 0, (1 if shaped else target), 0
    while skill < target:
        n += 1
        if skill >= crit - 1 and (shaped or skill + 1 >= target):
            skill += 1
            if shaped: crit = skill + 1
        if n > 1000: return n
    return n
print("S4 attempts shaped vs direct, target 8:", attempts_to_target(8, True), attempts_to_target(8, False))
# S5: matching: share = rA/(rA+rB) tracks relative rate, not absolute total
def share(rA, rB): return rA/(rA+rB)
print("S5 share (6,2)/(60,20)/(6,6)/(60,60):", share(6,2), share(60,20), share(6,6), share(60,60))
ok = (vigor(9)/vigor(0) >= 3 and mono and count(front) > count(uniform)
      and count(uniform, bonus=0) == count(front, bonus=0)
      and attempts_to_target(8, True) <= 8 and share(6,2) == share(60,20) != share(6,6))
print("RESULT:", "PASS" if ok else "FAIL", "gradient 10x, front>uniform", count(front), count(uniform))
