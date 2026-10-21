# Exhaustive interleavings of 2 workers each doing: check(stock>0) ; decrement. Stock=1.
from itertools import combinations
def run(sched, locked):
    stock = [1]; sold = 0; pc = [0, 0]; seen = [None, None]; holder = None
    # steps per worker: 0 acquire?,1 check,2 act,3 release? (locked variants vary)
    def steps(mode):
        if mode == "none": return ["chk", "act"]
        if mode == "whole": return ["lock", "chk", "act", "unlock"]
        if mode == "check-only": return ["lock", "chk", "unlock", "act"]
        if mode == "act-only": return ["chk", "lock", "act", "unlock"]
    prog = steps(locked)
    n = len(prog)
    for w in sched:
        if pc[w] >= n: continue
        op = prog[pc[w]]
        if op == "lock":
            if holder is not None and holder != w: continue  # blocked: skip turn
            holder = w
        elif op == "unlock": holder = None
        elif op == "chk": seen[w] = stock[0] > 0
        elif op == "act":
            if seen[w]: stock[0] -= 1; sold += 1
        pc[w] += 1
    # drain
    for w in (0, 1):
        while pc[w] < n:
            op = prog[pc[w]]
            if op == "lock" and holder not in (None, w): break
            if op == "lock": holder = w
            elif op == "unlock": holder = None
            elif op == "chk": seen[w] = stock[0] > 0
            elif op == "act" and seen[w]: stock[0] -= 1; sold += 1
            pc[w] += 1
    return sold
res = {}
for mode in ["none", "check-only", "act-only", "whole"]:
    n = len(["x"] * (2 if mode == "none" else 4)); T = 2 * n; bad = tot = 0
    for pos in combinations(range(T), n):
        sched = [0 if i in pos else 1 for i in range(T)]
        tot += 1; bad += run(sched, mode) > 1
    res[mode] = (bad, tot); print(mode, "oversold", bad, "of", tot)
ok = res["none"][0] > 0 and res["check-only"][0] > 0 and res["act-only"][0] > 0 and res["whole"][0] == 0
print("RESULT: %s oversell interleavings none=%d/%d check-only=%d/%d act-only=%d/%d whole=%d/%d" % (("PASS" if ok else "FAIL",) + tuple(x for m in ["none","check-only","act-only","whole"] for x in res[m])))
