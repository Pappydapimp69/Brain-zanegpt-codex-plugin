"""Sandbox: when does an AI-animated product shot stay faithful? Deterministic, stdlib only.
Tests kernel ai-for-scenes-and-dubbing...a-reference-image-does-not-make-an-ai-product-shot-compliant
with the label-by-platform kernel and the separate-gates lessons (tiktok-shop/E14, brain-auto-training/E41, brainwork/E336)."""
import math

REAL = (200, 40, 40)
def dist(a, b): return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

# --- ways to make a product shot, each returns the shown colour -------------
def real_footage(L):            return REAL
def reference_gen(L, fid):      # fresh generation: fixed error, independent of length
    err = (1 - fid) * 60
    return (REAL[0] - err, REAL[1] + err / 2, REAL[2] + err / 2)
def hops(L):                    # Veo-style: 8 s clip then +7 s extensions
    return 1 if L <= 8 else 1 + math.ceil((L - 8) / 7)
def animate_photo(L, d):        # image-to-video of the real photo; drift accumulates per hop
    e = d * hops(L)
    return (REAL[0] - e, REAL[1] + e / 2, REAL[2] + e / 2)

def source_rule(kind):          # strict reading: AI product shot = violation by source
    return kind != "real"
def tol_rule(color, tol=5):     # measured-deviation reading
    return dist(color, REAL) <= tol

def label_needed(platform, ai_share, photoreal):
    if platform == "tiktok":  return ai_share >= 0.5 or photoreal   # label by default for AI
    if platform == "youtube": return photoreal and ai_share > 0     # cartoon exemption
    return False

def gate(shots, platform, labelled, rule):
    """shots: list of (kind, seconds, colour, is_product). returns (product_viol, label_viol)"""
    pv = sum(1 for k, L, c, p in shots if p and (source_rule(k) if rule == "source" else not tol_rule(c)))
    total = sum(L for _, L, _, _ in shots); ai = sum(L for k, L, _, _ in shots if k != "real")
    lv = 1 if label_needed(platform, ai / total, True) and not labelled else 0
    return pv, lv

def plan(kind, L, **kw):
    c = {"real": real_footage(L), "ref": reference_gen(L, kw.get("fid", 1)),
         "i2v": animate_photo(L, kw.get("d", 2))}[kind]
    return (kind, L, c, True)

scene = ("ai", 20, REAL, False)
out = {}
# S1 reference fidelity sweep under both readings
for fid in (0.9, 0.95, 1.0):
    s = [plan("ref", 10, fid=fid), scene]
    out[("ref", fid)] = (gate(s, "tiktok", True, "source")[0], gate(s, "tiktok", True, "tol")[0])
# S2 animate-photo: length sweep under tolerance rule (d=2/hop, tol 5)
for L in (8, 15, 22, 30):
    s = [plan("i2v", L, d=2), scene]
    out[("i2v", L)] = (gate(s, "tiktok", True, "source")[0], gate(s, "tiktok", True, "tol")[0])
# S3 real footage + AI scenes: label separate, per platform
for plat in ("tiktok", "youtube"):
    s = [plan("real", 10), scene]
    out[("real", plat, "nolabel")] = gate(s, plat, False, "source")
    out[("real", plat, "label")] = gate(s, plat, True, "source")
# S4 (BREAK): all-AI cartoon, no label, perfect reference
s = [plan("ref", 10, fid=1.0), ("ai", 20, REAL, False)]
out["cartoon-ai-ref1.0"] = {p: gate(s, p, False, "source") for p in ("tiktok", "youtube")}

for k, v in out.items(): print(k, v)

ok = True
ok &= all(out[("ref", f)][0] == 1 for f in (0.9, 0.95, 1.0))      # source reading: fidelity never cures
ok &= out[("ref", 0.9)][1] == 1 and out[("ref", 1.0)][1] == 0     # tolerance reading: fidelity does cure
ok &= [out[("i2v", L)][1] for L in (8, 15, 22, 30)] == [0, 0, 1, 1]  # drift breaks past 2 hops (>15 s)
ok &= out[("real", "tiktok", "nolabel")] == (0, 1) and out[("real", "youtube", "label")] == (0, 0)
ok &= out["cartoon-ai-ref1.0"]["tiktok"][0] == 1               # cartoon with an AI product shot still fails the product gate
print("RESULT: %s source rule never passes ref shots (3/3 fids); tolerance rule passes fid 1.0 and animate<=15s (2 hops), fails 22s+; label gate independent per platform" % ("PASS" if ok else "FAIL"))
