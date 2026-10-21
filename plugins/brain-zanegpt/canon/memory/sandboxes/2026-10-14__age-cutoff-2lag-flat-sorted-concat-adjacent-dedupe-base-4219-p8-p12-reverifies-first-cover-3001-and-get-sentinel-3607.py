"""Prediction (before run): a sorted-concatenation adjacent-dedupe cover test (b is shadowed iff the deduped size of
sorted(ev[a]+ev[b]) equals len(ev[a]) and ev[b] is nonempty) at new base 4219 gives, for P8..P12, the same averages as the
first-cover dict path (base 3001): P11 215/11 at N=P and 460/11 at N=2P, P12 25 and 53, flats exactly [P, 2P], and a
base-0 control differs at N=P. Built to break: a deliberately wrong rule (shadow whenever lengths are equal) must differ.
Stdlib, deterministic."""
from fractions import Fraction as F

def events(P, T, w, N):
    return {L: [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w] for L in range(1, N + 1)}

def dedup_len(xs):
    xs = sorted(xs)
    return (1 if xs else 0) + sum(1 for i in range(1, len(xs)) if xs[i] != xs[i - 1])

def count_new(P, T, N, wrong=False):
    sh = 0
    for w in range(1, P):
        ev = events(P, T, w, N)
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                if not ev[b]:
                    continue
                if wrong:
                    sh += len(ev[a]) == len(ev[b])
                else:
                    sh += dedup_len(ev[a] + ev[b]) == len(ev[a])
    return sh

def count_dict(P, T, N):  # reference: first-cover dict path (base 3001 entry)
    sh = 0
    for w in range(1, P):
        ev = events(P, T, w, N)
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                first = {}
                for x in ev[a]:
                    first.setdefault(x, a)
                cut = a if first else 0
                for x in ev[b]:
                    if x not in first:
                        first[x] = b; cut = b
                last = b if ev[b] else (a if ev[a] else 0)
                sh += (last != cut)
    return sh

def avg(fn, P, base, N):
    return F(sum(fn(P, base + r, N) for r in range(P)), P)

REC = {11: (F(215, 11), F(460, 11)), 12: (F(25), F(53))}
ok = True; out = []
for P in (8, 9, 10, 11, 12):
    Ns = list(range(P - 1, 2 * P + 2))
    A = {N: avg(count_new, P, 4219, N) for N in Ns}
    flats = [N for N in Ns[1:] if A[N] == A[N - 1]]
    match = (P not in REC) or (A[P], A[2 * P]) == REC[P]
    ref = avg(count_dict, P, 3001, P) == A[P] and avg(count_dict, P, 3001, 2 * P) == A[2 * P]
    ctrl = avg(count_new, P, 0, P) != A[P]
    wrong = avg(lambda p, t, n: count_new(p, t, n, True), P, 4219, P) != A[P]
    print(P, flats, match, ref, ctrl, wrong, flush=True)
    ok = ok and flats == [P, 2 * P] and match and ref and ctrl and wrong
    out.append(f"P{P} flats={flats} avgP={A[P]} avg2P={A[2*P]} ref={ref} ctrl_differs={ctrl} wrong_differs={wrong}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
