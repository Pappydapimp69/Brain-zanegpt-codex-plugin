"""Sandbox: monorepo atomic cross-project change vs polyrepo (semver-pinned / semver-violating) rollout.
Kernels: ideas:VERSION-CONTROL/repo-topology/monorepo-vs-polyrepo/..., ideas:VERSION-CONTROL/versioning/semantic-versioning/...,
sibling ideas:VERSION-CONTROL/code-review/effectiveness (review is by file owners; touched-owner count measured).
Deterministic, no RNG."""
N = 200                      # targets
DEPS = {i: ([(i - 1) // 3] + ([(i * 5) % (i // 2 + 1)] if i % 4 == 0 else []) if i > 0 else []) for i in range(N)}  # deps lower index
DEPS[0] = []
REV = {i: [] for i in range(N)}
for i, ds in DEPS.items():
    for d in set(ds): REV[d].append(i)
def closure(root):
    seen, st = set(), [root]
    while st:
        x = st.pop()
        for y in REV[x]:
            if y not in seen: seen.add(y); st.append(y)
    return seen
LIB = 5
direct = sorted(REV[LIB]); affected = closure(LIB)
print("direct dependents", len(direct), "transitive affected", len(affected), "of", N)

# S1 monorepo: one commit edits lib+direct dependents; broken intermediate states = 0
mono_commits, mono_broken = 1, 0
mono_ci_affected, mono_ci_all = len(affected) + 1, N
# S2 polyrepo, semver MAJOR, consumers pinned, each migrates at its own cadence (index-based, deterministic)
cad = {c: 1 + (c % 5) * 3 for c in direct}           # days until each consumer migrates
skew_days = sum(cad.values()); finish = max(cad.values())
poly_broken_pinned = 0
# S3 polyrepo, breaking change shipped as PATCH with ^ range: every direct consumer breaks on next CI
poly_broken_patch = len(direct)
# S4 monorepo with only naive build-all CI vs affected-only
print(f"S1 mono: commits={mono_commits} broken={mono_broken} ci(affected)={mono_ci_affected} ci(all)={mono_ci_all}")
print(f"S2 poly semver-major pinned: broken={poly_broken_pinned} skew consumer-days={skew_days} finish day={finish}")
print(f"S3 poly breaking-as-patch : broken consumers={poly_broken_patch}")
# S5 BREAK: a leaf-heavy change, root-level change affects everything -> affected-only saves nothing
root_aff = len(closure(0)) + 1
print(f"S5 root change: affected={root_aff} of {N} (affected-only saving {N-root_aff})")
# S6 owner load: a monorepo atomic change needs sign-off from every affected owner (owner = target%10)
owners = {t % 10 for t in affected | {LIB}}
print("S6 owners to review in one commit:", len(owners))
ok = (mono_broken == 0 and poly_broken_pinned == 0 and skew_days > 0 and poly_broken_patch == len(direct) > 0
      and mono_ci_affected < mono_ci_all and (N - root_aff) < (N - mono_ci_affected) and len(owners) > 1)
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" atomic mono change 0 broken states vs poly-major skew {skew_days} consumer-days / poly-patch {poly_broken_patch} broken; "
      f"affected-only CI {mono_ci_affected}/{N} for lib change but {root_aff}/{N} for root change; {len(owners)} owners to review")
