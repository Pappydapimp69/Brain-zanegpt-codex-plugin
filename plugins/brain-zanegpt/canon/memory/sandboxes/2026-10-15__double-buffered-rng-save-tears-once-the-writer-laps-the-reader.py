"""Train edge: zanegpt E12 (a save that copies PRNG state words while the sim
steps can be torn; write into the inactive of two buffers and flip a 1-bit
index; Gray-coded index for more slots) + brainwork E293 (a Gray counter read
mid-change is old or new - for ONE step per read).
Composed question: the 1-bit flip is a 1-bit Gray counter, so does the double
buffer inherit the one-step limit? If the generator completes 2 updates while
the saver is still copying, the second update writes into the slot being read.
Exhaustive interleavings, no rng. Reader: read the slot index, then 4 words.
Writer update: write 4 words into the next slot, then publish the index.
Every interleaving of the reader's ops with k writer updates is enumerated.
Torn = the 4 words read do not all come from one version. Schemes: single
buffer (copy live words), double buffer + 1-bit flip, 4-slot ring stepped in
Gray order, seqlock (version counter odd while writing; reader re-reads the
counter after copying and retries on change - counted as a retry, not a tear).
PREDICTION (written before running): single buffer tears for k >= 1; double
buffer 0 torn at k = 1 but tears at k = 2; a 4-slot ring 0 torn up to k = 3
and tears at k = 4 (the writer laps back to the reader's slot after n-1 others);
the seqlock never returns a torn copy at any k (it retries instead).
"""
import sys
from itertools import combinations
print("python", sys.version.split()[0])
W = 4
def interleavings(nr, nw):
    for pos in combinations(range(nr + nw), nr):
        yield set(pos), nr + nw
def run(scheme, k, slots=2):
    torn = total = retries = 0
    nr = 1 + W + (1 if scheme == "seqlock" else 0)
    nw = k * W if scheme == "single" else (k * (W + 2) if scheme == "seqlock" else k * (W + 1))
    for rpos, n in interleavings(nr, nw):
        if scheme == "single":
            mem = [0] * W
        else:
            mem = [[0] * W for _ in range(slots)]
        idx = 0; version = 0; seq = 0
        wq = []
        for u in range(1, k + 1):
            if scheme == "single":
                wq += [("w", None, i, u) for i in range(W)]
            elif scheme == "seqlock":
                wq += [("s+", None, None, u)] + [("w", 0, i, u) for i in range(W)] + [("s+", None, None, u)]
            else:
                tgt = u % slots if slots == 2 else [0, 1, 3, 2][u % 4]
                wq += [("w", tgt, i, u) for i in range(W)] + [("pub", tgt, None, u)]
        wi = 0; got = []; rslot = None; s0 = None; rstep = 0
        for t in range(n):
            if t in rpos:
                if scheme == "single":
                    if rstep == 0: pass
                    else: got.append(mem[rstep - 1])
                elif scheme == "seqlock":
                    if rstep == 0: s0 = seq
                    elif rstep <= W: got.append(mem[0][rstep - 1])
                    else:
                        if seq != s0 or s0 % 2: retries += 1; got = None
                else:
                    if rstep == 0: rslot = idx
                    else: got.append(mem[rslot][rstep - 1])
                rstep += 1
            else:
                op = wq[wi]; wi += 1
                if op[0] == "w":
                    if scheme == "single": mem[op[2]] = op[3]
                    else: mem[op[1]][op[2]] = op[3]
                elif op[0] == "pub": idx = op[1]
                elif op[0] == "s+": seq += 1
        total += 1
        if got is not None and len(set(got)) > 1: torn += 1
    return torn, total, retries
res = {}
for scheme, ks, slots in (("single", (1, 2), 1), ("double", (1, 2, 3), 2), ("ring4", (1, 2, 3, 4), 4), ("seqlock", (1, 2, 3), 1)):
    for k in ks:
        if scheme == "seqlock":
            pass
        t, n, rt = run("seqlock" if scheme == "seqlock" else ("single" if scheme == "single" else "buf"), k, slots)
        res[(scheme, k)] = (t, n, rt)
        print(f"{scheme:8s} k={k}: torn {t}/{n}" + (f", retries {rt}" if scheme == "seqlock" else ""))
c = [res[("single", 1)][0] > 0, res[("double", 1)][0] == 0, res[("double", 2)][0] > 0,
     all(res[("ring4", k)][0] == 0 for k in (1, 2, 3)), res[("ring4", 4)][0] > 0,
     all(res[("seqlock", k)][0] == 0 for k in (1, 2, 3))]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/6; single k1 torn {res[('single',1)][0]}/{res[('single',1)][1]}; double k1 {res[('double',1)][0]}, k2 {res[('double',2)][0]}/{res[('double',2)][1]}; ring4 k3 {res[('ring4',3)][0]}, k4 {res[('ring4',4)][0]}/{res[('ring4',4)][1]}; seqlock torn {sum(res[('seqlock',k)][0] for k in (1,2,3))}, retries k1-3 {[res[('seqlock',k)][2] for k in (1,2,3)]}")
