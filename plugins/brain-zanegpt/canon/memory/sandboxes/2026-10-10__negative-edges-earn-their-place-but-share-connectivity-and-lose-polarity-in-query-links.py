"""T21 evidence sandbox: does the co-verification graph need NEGATIVE edges?

PREDICTIONS (written before the final run; the first exploratory probe had
already shown edge totals, so only the NEW quantities below are real
predictions):
  P1  >= 30 refuted file-pairs are re-offered as untested seams if the graph
      is positive-only (confirmatory; a probe had hinted ~38).
  P2  the 20 best weakest-link seams barely change (<= 3 pairs differ) when
      negative edges are removed, i.e. negative edges are NOT load-bearing for
      the head of the ranking.
  P3  >= 10 idea kernels have EVERY declared applying lesson refuted, so the
      one-hop `applies` link in a query shows a never-successfully-applied
      kernel with no polarity marker.
  P4  >= 20 edges are flagged incompatible while also carrying compatible
      evidence (the flag is an OR, a refutation overwrites confirmations).
  P5  splitting polarity into its own edge set (negative edges kept out of
      components, degree and the in-graph test; still blocking re-test)
      re-offers 0 refuted pairs AND removes the connectivity inflation.

Reads the linked canon through the CLI module itself (read-only). Run from a
directory that was linked with `brain link --mode read-only`. Stdlib only,
no RNG, no timing. Last line is RESULT.
"""
import importlib.machinery
import importlib.util
import os
import sys
from itertools import combinations


# ---------------------------------------------------------------- synthetic
def synthetic():
    """Tiny graph built to BREAK 'positive-only is enough'.
    A-B composed twice (positive). C-D refuted once. E bridges only via a
    refuted edge to B. Shared tags make every non-edge a seam candidate."""
    tags = {n: {"t1", "t2"} for n in "ABCDEF"}
    pos = {("A", "B"), ("B", "C")}          # C is in a proven cluster
    neg = {("C", "D"), ("B", "E")}          # refuted pairs
    def seams(edge_set, in_graph_set):
        tested = {frozenset(p) for p in edge_set}
        out = set()
        for a, b in combinations(sorted(tags), 2):
            if frozenset((a, b)) in tested:
                continue
            if a in in_graph_set or b in in_graph_set:
                out.add((a, b))
        return out
    nodes = lambda es: {n for p in es for n in p}
    positive_only = seams(pos, nodes(pos))
    merged = seams(pos | neg, nodes(pos | neg))
    split = {p for p in seams(pos, nodes(pos)) if frozenset(p) not in
             {frozenset(q) for q in neg}}
    reoffered = {p for p in positive_only if frozenset(p) in {frozenset(q) for q in neg}}
    # connectivity: component of A with merged vs split edges
    def comp(es, start):
        adj = {}
        for a, b in es:
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)
        seen, st = set(), [start]
        while st:
            c = st.pop()
            if c in seen:
                continue
            seen.add(c)
            st.extend(adj.get(c, ()) - seen)
        return seen
    return {
        "reoffered_when_positive_only": len(reoffered),
        "reoffered_when_split": len(split & {tuple(sorted(q)) for q in neg}),
        "cluster_merged": len(comp(pos | neg, "A")),
        "cluster_split": len(comp(pos, "A")),
        "extra_seams_from_neg_only_nodes": len(merged - split),
    }


# --------------------------------------------------------------- real canon
def load_brain():
    p = os.path.expanduser(os.path.join("~", ".brain", "Brain", "bin", "brain"))
    loader = importlib.machinery.SourceFileLoader("brainmod", p)
    spec = importlib.util.spec_from_loader("brainmod", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def real(m):
    bases = m._analyze_bases()
    entries = m._load_entries(bases)
    idx = m._slug_index(bases)
    edges, _nt = m._cv_build_graph(entries, idx)
    out = {"entries": len(entries), "edges": len(edges)}
    inc = {k for k, r in edges.items() if r["incompatible"]}
    out["inc_edges"] = len(inc)
    inc_refs = [len(m._composed_refs(e, idx)) for e in entries
                if m._field(e["block"], "polarity").strip().lower() == "incompatible"]
    out["inc_entries_3plus_refs"] = sum(1 for n in inc_refs if n >= 3)
    out["inc_entries_0_or_1_ref"] = sum(1 for n in inc_refs if n <= 1)
    out["inc_entries"] = sum(
        1 for e in entries
        if m._field(e["block"], "polarity").strip().lower() == "incompatible")

    # per-edge polarity evidence (replays the builder's own edge keys)
    skip = m._ignored_files(entries) if m._collapse_skipped() else set()
    fold = lambda n: m.SKIPPED_NODE if n in skip else n
    pol = {}
    for e in entries:
        refs = {fold(r) for r in m._composed_refs(e, idx)}
        if not refs:
            continue
        explicit = bool(m._field(e["block"], "composed") or m._field(e["block"], "linked"))
        isinc = explicit and m._field(e["block"], "polarity").strip().lower() == "incompatible"
        parts = sorted(refs | {fold(e["file"])})
        for a, b in combinations(parts, 2):
            d = pol.setdefault((a, b), [0, 0])
            d[0 if isinc else 1] += 1
    out["mixed_edges"] = sum(1 for d in pol.values() if d[0] and d[1])

    # seams: current graph vs positive-only counterfactual (ranked lists)
    cur, _ = m._seam_candidates(entries, idx)
    orig = m._graph
    m._graph = lambda en, ix: (
        {k: r for k, r in orig(en, ix)[0].items() if not r["incompatible"]},
        orig(en, ix)[1])
    try:
        posonly, _ = m._seam_candidates(entries, idx)
    finally:
        m._graph = orig
    key = lambda c: frozenset((c[2], c[3]))
    sc, sp = {key(c) for c in cur}, {key(c) for c in posonly}
    incset = {frozenset(k) for k in inc}
    out["seams_current"] = len(sc)
    out["seams_posonly"] = len(sp)
    out["reoffered_refuted"] = len(sp & incset - sc)
    out["only_offered_because_of_neg"] = len(sc - sp)
    out["top20_diff"] = len({key(c) for c in cur[:20]} ^ {key(c) for c in posonly[:20]}) // 2

    # connectivity inflation
    pos_edges = {k: r for k, r in edges.items() if not r["incompatible"]}
    big = lambda es: max((len(c) for c in m._components(es)), default=0)
    out["giant_current"], out["giant_posonly"] = big(edges), big(pos_edges)
    degp = m._edge_degree(pos_edges)
    touched = {n for k in inc for n in k}
    out["neg_touched_nodes"] = len(touched)
    out["neg_only_degree_nodes"] = sum(1 for n in touched if degp.get(n, 0) == 0)

    # split design: seams use positive in-graph, minus refuted pairs
    split_seams = sp - incset
    out["split_reoffered"] = len(split_seams & incset)
    out["split_vs_current_extra"] = len(sc - split_seams)

    # query link polarity: kernels whose every applying lesson is refuted
    applied = {}
    for e in entries:
        val = m._field(e["block"], "composed")
        if not val:
            continue
        dec = m._declared_kernel_refs(val)[0]
        isinc = m._field(e["block"], "polarity").strip().lower() == "incompatible"
        for k in dec:
            applied.setdefault(k, []).append(isinc)
    out["kernels_applied"] = len(applied)
    out["kernels_all_refuted"] = sum(1 for v in applied.values() if v and all(v))
    out["kernels_any_refuted"] = sum(1 for v in applied.values() if any(v))
    return out


def main():
    s = synthetic()
    print("synthetic:", s)
    try:
        r = real(load_brain())
    except Exception as ex:  # canon unavailable -> cannot verify
        print("real canon unavailable:", type(ex).__name__)
        print("RESULT: FAIL real canon could not be read; synthetic only: %s" % s)
        return
    for k in sorted(r):
        print(f"  {k:32s} {r[k]}")
    checks = {
        "P1 >=30 refuted pairs re-offered": r["reoffered_refuted"] >= 30,
        "P2 top20 weakest-link differs by <=3": r["top20_diff"] <= 3,
        "P3 >=10 kernels all-refuted": r["kernels_all_refuted"] >= 10,
        "P4 >=20 mixed-polarity edges": r["mixed_edges"] >= 20,
        "P5 split design re-offers 0 and shrinks giant": (
            r["split_reoffered"] == 0 and r["giant_posonly"] < r["giant_current"]),
        "S1 synthetic positive-only re-offers refuted": s["reoffered_when_positive_only"] == 2,
        "S2 synthetic split re-offers 0": s["reoffered_when_split"] == 0,
        "S3 synthetic merged inflates cluster": s["cluster_merged"] > s["cluster_split"],
    }
    for k, v in checks.items():
        print(("  ok   " if v else "  MISS ") + k)
    bad = [k for k, v in checks.items() if not v]
    if bad:
        print("RESULT: FAIL %d/%d predictions missed: %s" % (len(bad), len(checks), "; ".join(bad)))
    else:
        print("RESULT: PASS all %d checks held; refuted pairs re-offered by positive-only=%d, "
              "mixed-polarity edges=%d, all-refuted kernels=%d, giant %d->%d"
              % (len(checks), r["reoffered_refuted"], r["mixed_edges"],
                 r["kernels_all_refuted"], r["giant_current"], r["giant_posonly"]))


main()
