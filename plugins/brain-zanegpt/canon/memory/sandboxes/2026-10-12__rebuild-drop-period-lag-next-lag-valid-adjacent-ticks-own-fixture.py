"""Own fixture, original sandbox not opened. Iteration 3 of 3 (iterations 1-2 used a landing-coverage cutoff reading that did not
correlate with adjacency at all: 41/182/5/27 cross-tab at P8, so that reading was abandoned as not the entry's meaning).
Prediction (before run): reading 'lag L valid' as 'some press is legal at both its start tick and landing tick being in the window',
i.e. exists t in W with (t+L) mod P in W, lag P-1 is valid iff W has two cyclically adjacent ticks, and the windows where it is NOT valid
number Lucas(P)-1 = 46, 75, 122 at P8, P9, P10 with 0 mismatches. The same enumeration must also show that dropping lag P (lag 0 mod P,
always valid for nonempty W) leaves P-1 as the largest valid remaining lag only for adjacent windows (else cutoff falls to a smaller lag or 0).
Caveat: this reading makes the P-1 equivalence close to definitional; the independent content is the Lucas count and the fallback cutoff."""
def lucas(n):
    a, b = 2, 1
    for _ in range(n): a, b = b, a + b
    return a
def valid(P, W, L): return any(((t + L) % P) in W for t in W)
out, ok = [], True
for P in (8, 9, 10):
    notvalid = mism = fall = 0
    for mask in range(1, 1 << P):
        W = {i for i in range(P) if mask >> i & 1}
        adj = any(((i + 1) % P) in W for i in W)
        v = valid(P, W, P - 1)
        notvalid += (not v); mism += (v != adj)
        top = max([L for L in range(1, P) if valid(P, W, L)] or [0])
        fall += (top != P - 1)
    ok = ok and notvalid == lucas(P) - 1 and mism == 0 and fall == notvalid
    out.append(f"P{P} P-1 invalid={notvalid} L(P)-1={lucas(P)-1} mismatches={mism} cutoff!=P-1: {fall}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
