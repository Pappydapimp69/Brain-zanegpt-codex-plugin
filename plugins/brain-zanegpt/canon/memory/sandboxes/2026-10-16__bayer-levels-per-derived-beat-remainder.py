# Sandbox: split the 16 Bayer 4x4 level changes across k game-derived beats.
def build(n):
    if n == 1: return [[0]]
    h = build(n//2); q = [[0,2],[3,1]]; m = n//2
    return [[4*h[r%m][c%m] + q[r//m][c//m] for c in range(n)] for r in range(n)]
B = build(4)
assert sorted(v for r in B for v in r) == list(range(16))
def floor_split(k):  return [16//k]*k
def remainder_split(k):
    base, extra = divmod(16, k)
    return [base + (1 if i < extra else 0) for i in range(k)]
res_floor = [k for k in range(1, 17) if sum(floor_split(k)) != 16]
res_rem = [k for k in range(1, 17) if sum(remainder_split(k)) != 16]
spread = max(max(remainder_split(k)) - min(remainder_split(k)) for k in range(1, 17))
print("floor leaves residual for k =", res_floor, "count", len(res_floor))
print("remainder split unfinished count", len(res_rem), "max step spread", spread)
# break: one step of 0 beats (a k=0 sheet) must be rejected, and k>16 gives zero-step beats
zero_steps = [k for k in range(17, 21) if 0 in remainder_split(k)]
print("k>16 gives zero-step beats for k =", zero_steps)
ok = len(res_floor) == 11 and not res_rem and spread <= 1 and zero_steps == [17,18,19,20]
print("RESULT: %s floor stalls short of level 16 for 11/16 beat counts, remainder split 0/16, spread<=1, k>16 yields idle beats" % ("PASS" if ok else "FAIL"))
