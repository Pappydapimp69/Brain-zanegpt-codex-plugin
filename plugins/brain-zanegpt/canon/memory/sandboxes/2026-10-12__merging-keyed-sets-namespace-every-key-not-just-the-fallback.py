"""Train edge: brain-pitch E3 (merging two independently keyed collections into
one namespace, a generic fallback bucket like 'other' collides) composed with
sandbox-edges E23 (namespace a shared key by writer identity, whether the
store is deploy storage or UI state).
Claim under test: renaming only the fallback bucket is not enough; when the two
sources' real ids can overlap too, only namespacing EVERY key by its source
removes collisions.
Deterministic: two fixed sources. Merge = dict keyed by id; a later write to an
existing key overwrites its label and adds its members (the bug shape in E3).
Measured: members filed under a bucket whose label came from the other source.
"""

A = {"forest": ["a1", "a2"], "river": ["a3"], "other": ["a4", "a5"]}
B = {"forest": ["b1"], "camp": ["b2", "b3"], "other": ["b4"]}
LABEL = {"A": "Survey A", "B": "Survey B"}


def merge(sources, keyfn):
    out = {}
    for src, coll in sources:
        for cid, members in coll.items():
            k = keyfn(src, cid)
            if k in out:
                out[k]["label"] = LABEL[src]          # overwrite: last writer wins
                out[k]["members"] += [(src, m) for m in members]
            else:
                out[k] = {"label": LABEL[src], "members": [(src, m) for m in members]}
    return out


def misfiled(merged):
    return sum(1 for b in merged.values() for src, m in b["members"] if LABEL[src] != b["label"])


def main():
    srcs = [("A", A), ("B", B)]
    naive = misfiled(merge(srcs, lambda s, c: c))
    fallback_only = misfiled(merge(srcs, lambda s, c: f"{s}:{c}" if c == "other" else c))
    full = misfiled(merge(srcs, lambda s, c: f"{s}:{c}"))
    no_overlap = misfiled(merge([("A", {"river": ["a3"], "other": ["a4"]}), ("B", {"camp": ["b2"]})], lambda s, c: c))
    print(f"members filed under the other source's label: naive {naive}, fallback-only namespaced {fallback_only}, "
          f"every key namespaced {full}; sources with no shared ids, naive {no_overlap}")
    checks = [
        ("a naive merge misfiles members (fallback and shared ids collide)", naive > 0),
        ("namespacing only the fallback still misfiles members when real ids overlap", fallback_only > 0),
        ("namespacing every key by its source misfiles nothing", full == 0),
        ("break case: with no shared ids and one fallback, even a naive merge misfiles nothing", no_overlap == 0),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; misfiled naive {naive}, "
          f"fallback-only {fallback_only}, full {full}, no-overlap {no_overlap}")


if __name__ == "__main__":
    main()
