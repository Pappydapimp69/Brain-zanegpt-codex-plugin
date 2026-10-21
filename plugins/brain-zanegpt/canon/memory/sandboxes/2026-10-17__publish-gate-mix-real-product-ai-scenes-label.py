"""Sandbox: publish gate over a shot list, encoding three AI-VIDEO/TIKTOK-SHOP kernels as rules:
 K1 a reference image does not make an AI product shot compliant (AI product shot = violation, any fidelity)
 K2 label photoreal AI; obvious cartoons need none on YouTube; TikTok AI label on by default
 K3 mix real product footage with AI scenes is the safer mode
The rules are inputs (taken from the kernels), so this checks the composed accounting, not platform policy."""
SHOTS = ["scene", "scene", "product", "scene", "product", "scene", "cartoon", "scene"]  # 2 product, 1 cartoon, 5 scenes

def plan(name, product_source, scene_kind, labelled, ref_fidelity=0.0):
    shots = []
    for s in SHOTS:
        if s == "product":
            shots.append(("real" if product_source == "real" else "ai-product", ref_fidelity))
        elif s == "cartoon":
            shots.append(("ai-cartoon", 0))
        else:
            shots.append((scene_kind, 0))
    return name, shots, labelled

def violations(platform, shots, labelled):
    v = []
    for kind, fid in shots:
        if kind == "ai-product":
            v.append("product-not-real")                      # K1: fidelity irrelevant
    photoreal_ai = any(k in ("ai-photoreal", "ai-product") for k, _ in shots)
    label_needed = photoreal_ai or platform == "tiktok" and any(k.startswith("ai") for k, _ in shots)
    if label_needed and not labelled:
        v.append("missing-label")                             # K2
    return v

plans = [
    plan("all-ai+ref0.9+label", "ai", "ai-photoreal", True, 0.9),
    plan("all-ai+ref1.0+label", "ai", "ai-photoreal", True, 1.0),   # BREAK: perfect reference
    plan("mix+label", "real", "ai-photoreal", True),
    plan("mix+nolabel", "real", "ai-photoreal", False),
    plan("mix-cartoon-scenes+nolabel", "real", "ai-cartoon", False),
]
out = {}
for platform in ("youtube", "tiktok"):
    for name, shots, lab in plans:
        v = violations(platform, shots, lab)
        out[(platform, name)] = v
        print(platform, name, len(v), sorted(set(v)))
ok = True
ok &= len(out[("youtube", "all-ai+ref0.9+label")]) == 2 and len(out[("youtube", "all-ai+ref1.0+label")]) == 2   # ref fidelity buys 0
ok &= out[("youtube", "mix+label")] == [] and out[("tiktok", "mix+label")] == []
ok &= out[("youtube", "mix+nolabel")] == ["missing-label"]
ok &= out[("youtube", "mix-cartoon-scenes+nolabel")] == []                  # cartoons skip label on YouTube
ok &= out[("tiktok", "mix-cartoon-scenes+nolabel")] == ["missing-label"]    # TikTok default-on label
print("RESULT: %s mix+label = 0 violations on both platforms; all-AI with reference image 0.9 or 1.0 keeps 2 product violations; cartoon-only AI skips label on youtube but not tiktok" % ("PASS" if ok else "FAIL"))
