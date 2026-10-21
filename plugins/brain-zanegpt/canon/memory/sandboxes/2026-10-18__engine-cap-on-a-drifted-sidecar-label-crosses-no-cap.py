"""Sandbox: a top-4 batch of ad variants ranked on IPM x D1, with a 'one variant per comic engine' cap
(ideas:COMEDY-CRAFT vary-the-comic-engine) whose engine labels come from a hand-kept sidecar that drifts
(collective-reference/E1) vs labels derived from the variants themselves. Deterministic, stdlib only.
Assumed model: true batch value = sum of IPM*D1 of picked variants, each repeat of an engine in the batch
multiplied by 0.75 per earlier repeat (fatigue). Scores are engine-correlated: strong engines score higher."""
ENG_Q = {0: 1.4, 1: 1.1, 2: 0.9, 3: 0.7}
V = []                                        # 16 variants: 4 engines x 4 reskins, within-engine spread
for e in range(4):
    for j in range(4):
        V.append((e, ENG_Q[e] * (1.0 - 0.04 * j)))   # (true engine, ipm*d1)
N, K = len(V), 4

def batch_value(picks):
    seen, tot = {}, 0.0
    for i in picks:
        e, s = V[i]
        tot += s * 0.75 ** seen.get(e, 0); seen[e] = seen.get(e, 0) + 1
    return tot

def pick(labels, cap):
    order = sorted(range(N), key=lambda i: -V[i][1])
    out, used = [], set()
    for i in order:
        if cap and labels[i] in used: continue
        out.append(i); used.add(labels[i])
        if len(out) == K: break
    return out

def drifted_labels(m, off):
    lab = [e for e, _ in V]
    idx = [i for i in range(N) if (i * 5 + off) % N < m]
    # drift: each stale entry takes the label of the NEXT stale entry (a shifted hand-kept list)
    for a, b in zip(idx, idx[1:] + idx[:1]): lab[a] = V[b][0]
    return lab

def unknown_labels(m, off):           # stale/missing entries all fall into one 'unknown' bucket (label 99)
    lab = [e for e, _ in V]
    for i in range(N):
        if (i * 5 + off) % N < m: lab[i] = 99
    return lab

true_lab = [e for e, _ in V]
nocap = batch_value(pick(true_lab, False))
derived = batch_value(pick(true_lab, True))
print(f"no cap {nocap:.3f} | cap with derived labels {derived:.3f}")
shift, unk = {}, {}
for m in (0, 2, 4, 8, 12, 16):
    for name, fn, store in (("shifted", drifted_labels, shift), ("unknown-bucket", unknown_labels, unk)):
        vals = [batch_value(pick(fn(m, off), True)) for off in range(N)]
        store[m] = (sum(vals) / N, min(vals))
        print(f"{name:14s} {m:2d}/16: mean {store[m][0]:.3f} worst {store[m][1]:.3f}  vs no cap {nocap:.3f}")
below_shift = [m for m in shift if shift[m][0] < nocap]
below_unk = [m for m in unk if unk[m][1] < nocap]
ok = derived > nocap and not below_shift and bool(below_unk)
print(f"RESULT: {'PASS' if ok else 'FAIL'} derived cap +{derived-nocap:.3f} over no cap; shifted-label drift never falls below no cap (mean) at m in {below_shift}; unknown-bucket worst case falls below no cap at m in {below_unk} (m=16 worst {unk[16][1]:.3f})")
