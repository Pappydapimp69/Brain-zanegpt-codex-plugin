"""Happens-before transitivity through a release/acquire chain.

Exhaustive axiomatic model (RC11 fragment, no RNG, no threads): every
reads-from choice is enumerated; an execution is consistent iff hb is
acyclic, no read reads from an hb-later write, and no read reads a write
that is mo-overwritten by a write hb-before it (read-write coherence).
hb = (sb U sw U init)+, where sw = release write -rf-> acquire read.
hb is computed twice: Floyd-Warshall closure and vector clocks joined on
acquire; the two must agree on every event pair.
"""
from itertools import product

def build(threads):
    ev = [dict(tid=-1, kind="W", loc=l, val=0, order="na", idx=0) for l in ("data", "f1", "f2")]
    for t, ops in enumerate(threads):
        for i, op in enumerate(ops):
            if op[0] == "W":
                ev.append(dict(tid=t, kind="W", loc=op[1], val=op[2], order=op[3], idx=i + 1))
            else:
                ev.append(dict(tid=t, kind="R", loc=op[1], order=op[2], reg=op[3], idx=i + 1))
    return ev

def executions(threads, coherence=True):
    ev = build(threads)
    n = len(ev)
    nthreads = len(threads)
    reads = [i for i, e in enumerate(ev) if e["kind"] == "R"]
    writes_by_loc = {}
    for i, e in enumerate(ev):
        if e["kind"] == "W":
            writes_by_loc.setdefault(e["loc"], []).append(i)
    out = []
    for choice in product(*[writes_by_loc[ev[r]["loc"]] for r in reads]):
        rf = dict(zip(reads, choice))
        edge = [[False] * n for _ in range(n)]
        for a in range(n):
            for b in range(n):
                if a == b:
                    continue
                A, B = ev[a], ev[b]
                if A["tid"] == -1 and B["tid"] != -1:
                    edge[a][b] = True  # init before everything
                elif A["tid"] == B["tid"] and A["tid"] != -1 and A["idx"] < B["idx"]:
                    edge[a][b] = True  # sb
        for r, w in rf.items():
            if ev[w]["order"] == "rel" and ev[r]["order"] == "acq":
                edge[w][r] = True  # sw
        hb = [row[:] for row in edge]
        for k in range(n):
            for i in range(n):
                if hb[i][k]:
                    for j in range(n):
                        if hb[k][j]:
                            hb[i][j] = True
        if any(hb[i][i] for i in range(n)):
            continue
        ok = True
        for r, w in rf.items():
            if hb[r][w]:
                ok = False  # reading from the future
            if coherence:
                for w2 in writes_by_loc[ev[r]["loc"]]:
                    # mo: init write first, then the single program write
                    if w2 != w and ev[w]["tid"] == -1 and hb[w2][r]:
                        ok = False
        # sb U rf acyclic (no thin air)
        sbrf = [row[:] for row in edge]
        for r, w in rf.items():
            sbrf[w][r] = True
        for k in range(n):
            for i in range(n):
                if sbrf[i][k]:
                    for j in range(n):
                        if sbrf[k][j]:
                            sbrf[i][j] = True
        if any(sbrf[i][i] for i in range(n)):
            ok = False
        if not ok:
            continue
        # vector clocks: thread components 0..nthreads-1, init is component nthreads
        vc = {}
        def clock(i):
            if i in vc:
                return vc[i]
            c = [0] * (nthreads + 1)
            for p in range(n):
                if edge[p][i]:
                    pc = clock(p)
                    c = [max(x, y) for x, y in zip(c, pc)]
            comp = ev[i]["tid"] if ev[i]["tid"] != -1 else nthreads
            c[comp] = max(c[comp], ev[i]["idx"] + (1 if ev[i]["tid"] == -1 else 0))
            vc[i] = c
            return c
        mism = 0
        for a in range(n):
            for b in range(n):
                if a == b:
                    continue
                if ev[a]["tid"] == -1 and ev[b]["tid"] == -1:
                    continue  # init writes are unordered among themselves
                comp = ev[a]["tid"] if ev[a]["tid"] != -1 else nthreads
                via_vc = clock(a)[comp] <= clock(b)[comp] and not (
                    ev[a]["tid"] == ev[b]["tid"] and ev[a]["idx"] > ev[b]["idx"])
                if ev[a]["tid"] == -1:
                    via_vc = ev[b]["tid"] != -1
                if via_vc != hb[a][b]:
                    mism += 1
        regs = {ev[r]["reg"]: ev[w]["val"] for r, w in rf.items()}
        out.append((regs, mism, n * (n - 1)))
    return out

def mp(o_w, o_r):
    return [[("W", "data", 1, "na"), ("W", "f1", 1, o_w)],
            [("R", "f1", o_r, "a"), ("R", "data", "na", "d")]]

def chain(o1w, o1r, o2w, o2r):
    return [[("W", "data", 1, "na"), ("W", "f1", 1, o1w)],
            [("R", "f1", o1r, "a"), ("W", "f2", 1, o2w)],
            [("R", "f2", o2r, "b"), ("R", "data", "na", "d")]]

def stale_mp(x):
    return x["a"] == 1 and x["d"] == 0

def stale_chain(x):
    return x["a"] == 1 and x["b"] == 1 and x["d"] == 0
# note: T2's f2 store is unconditional in this fragment; stale_chain also
# requires a==1 so the "T2 saw T1's flag" path is what is being judged.

scen = [
    ("1 MP rel/acq", mp("rel", "acq"), stale_mp, 0, True),
    ("2 MP relaxed flag (volatile-like)", mp("rlx", "rlx"), stale_mp, 1, True),
    ("3 chain all rel/acq", chain("rel", "acq", "rel", "acq"), stale_chain, 0, True),
    ("4 BREAK chain f1 store relaxed", chain("rlx", "acq", "rel", "acq"), stale_chain, 1, True),
    ("5 BREAK chain f1 load relaxed", chain("rel", "rlx", "rel", "acq"), stale_chain, 1, True),
    ("6 BREAK chain f2 store relaxed", chain("rel", "acq", "rlx", "acq"), stale_chain, 1, True),
    ("7 BREAK chain f2 load relaxed", chain("rel", "acq", "rel", "rlx"), stale_chain, 1, True),
    ("8 NEG-CONTROL chain rel/acq, coherence check off", chain("rel", "acq", "rel", "acq"), stale_chain, ">0", False),
]
allok = True
tot_mism = tot_pairs = 0
summary = []
for name, prog, pred, want, coh in scen:
    ex = executions(prog, coherence=coh)
    stale = sum(1 for regs, _, _ in ex if pred(regs))
    m = sum(x[1] for x in ex); p = sum(x[2] for x in ex)
    tot_mism += m; tot_pairs += p
    ok = (stale > 0) if want == ">0" else (stale == want)
    allok &= ok
    summary.append(f"s{name.split()[0]}={stale}")
    print(f"{name:52s} consistent={len(ex):2d} stale={stale} want={want} vc_mismatch={m}/{p} {'ok' if ok else 'MISMATCH'}")
vc_ok = tot_mism == 0
allok &= vc_ok
print(f"vector clock vs closure: {tot_mism} mismatches over {tot_pairs} ordered pairs")
print(("RESULT: PASS " if allok else "RESULT: FAIL ") +
      f"stale reads {' '.join(summary)}; vc==closure {tot_pairs - tot_mism}/{tot_pairs}")
