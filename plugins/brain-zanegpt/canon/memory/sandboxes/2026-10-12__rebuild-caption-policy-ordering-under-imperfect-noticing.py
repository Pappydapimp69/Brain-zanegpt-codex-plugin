"""Blind rebuild of seven#E64. Own fixture: a grid of audience mixes
(hear-only H, hear+captions HC, captions-only C) and a probability d that a
caption reader NOTICES a mismatch (uncaptioned sound, or a marked caption),
instead of certain noticing. Also an 'unseen-voice tell' break: under identical
captions a caption saying an unnamed voice spoke is itself a tell if real
unseen voices are rare (applies to hearers too, so it is not caption-specific)."""
from fractions import Fraction as F
def land(policy, H, HC, C, d):
    # share of the audience for whom a hallucinated sound lands unspoiled
    if policy == "none":     return H + HC          # C never perceives it
    if policy == "realonly": return H + HC * (1 - d)  # C sees nothing for it
    if policy == "tagged":   return H + (HC + C) * (1 - d)
    if policy == "same":     return H + HC + C
mixes = [(F(a, 10), F(b, 10), F(10 - a - b, 10)) for a in range(0, 11) for b in range(0, 11 - a)]
ds = [F(1, 5), F(1, 2), F(4, 5), F(1)]
viol = []
for H, HC, C in mixes:
    for d in ds:
        n, r, t, s = (land(p, H, HC, C, d) for p in ("none", "realonly", "tagged", "same"))
        if not (r <= n): viol.append(("real>none", H, HC, C, d))
        if HC > 0 and not (r < n): viol.append(("real==none", H, HC, C, d))
        if not (s >= max(n, r, t)): viol.append(("same<other", H, HC, C, d))
        # 'marking is as bad': tagged no better than realonly?
        if t > r: viol.append(("tagged>realonly", H, HC, C, d))
print(f"mixes {len(mixes)} x d {len(ds)}")
kinds = {}
for v in viol: kinds[v[0]] = kinds.get(v[0], 0) + 1
print("violations by kind:", kinds)
ex = [v for v in viol if v[0] == "tagged>realonly"][:1]
if ex: print("example tagged>realonly:", [str(x) for x in ex[0]])
# break the 'identical reaches everyone' line: unseen-voice tell
for p_real_unseen in (F(1, 20), F(1, 4), F(1, 2)):
    # half the shore sounds are hallucinated voices, all unseen; real voices unseen at p
    post = F(1, 2) / (F(1, 2) + F(1, 2) * p_real_unseen)
    print(f"P(fake | 'unnamed voice' caption) with real-unseen {p_real_unseen}: {float(post):.3f}")
core = kinds.get("real>none", 0) == 0 and kinds.get("real==none", 0) == 0 and kinds.get("same<other", 0) == 0
print(f"RESULT: {'PASS' if core else 'FAIL'} real-only < none in every mix with HC>0 at every d; same >= all; "
      f"tagged > real-only in {kinds.get('tagged>realonly',0)} cells (only when d<1: 'as bad' is the d=1 corner)")
