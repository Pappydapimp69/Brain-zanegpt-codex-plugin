"""Tune a depth bias on a small angle list, then score on held-out angles/scenes.
Receiver error ~ k*tan(theta) (texel depth variance). acne = bias<err; gap = max(0,bias-err). Deterministic."""
import math
def err(theta,k): return k*math.tan(math.radians(theta))
def score(bias_fn,angles,k):
    acne=sum(1 for a in angles if bias_fn(a)<err(a,k))
    gap=max(max(0.0,bias_fn(a)-err(a,k)) for a in angles)
    return acne,gap
def tune_const(angles,k):
    # smallest constant bias (grid) with zero acne on the tuning list
    for b in [i*0.0001 for i in range(0,400)]:
        if score(lambda a:b,angles,k)[0]==0: return b
    return None
def tune_slope(angles,k):
    for c in [i*0.0001 for i in range(0,400)]:
        f=lambda a:min(0.02,c*(1+math.tan(math.radians(a))))
        if score(f,angles,k)[0]==0: return c
    return None
K=0.0004
narrow=[10,30,50]                      # one "class": non-grazing
mixed=[10,30,50,70,80,85,88]           # includes grazing class
heldout=list(range(0,90))
b_n=tune_const(narrow,K); b_m=tune_const(mixed,K)
print(f"const tuned narrow={b_n:.4f} mixed={b_m:.4f}")
for name,b in (("narrow",b_n),("mixed",b_m)):
    tr=score(lambda a:b,narrow if name=="narrow" else mixed,K); ho=score(lambda a:b,heldout,K)
    print(f"{name}: train acne={tr[0]} gap={tr[1]:.4f} | heldout acne={ho[0]}/90 gap={ho[1]:.4f}")
# second held-out scene: texel error scale doubles (lower-res map)
for name,b in (("narrow",b_n),("mixed",b_m)):
    ho2=score(lambda a:b,heldout,2*K); print(f"{name}: heldout scene K x2 acne={ho2[0]}/90")
# slope-scaled tuned on narrow
c=tune_slope(narrow,K); f=lambda a:min(0.02,c*(1+math.tan(math.radians(a))))
ho=score(f,heldout,K); print(f"slope tuned narrow c={c:.4f}: heldout acne={ho[0]}/90 gap={ho[1]:.4f}")
okA = score(lambda a:b_n,narrow,K)[0]==0 and score(lambda a:b_n,heldout,K)[0]>0   # narrow overfits
okB = score(lambda a:b_m,heldout,K)[0] <= 1                                        # mixed generalises on same scene
okC = score(lambda a:b_m,heldout,2*K)[0] > 0                                       # BREAK: even mixed fails when scene changes
print("RESULT: %s narrow_heldout_acne=%d mixed_heldout_acne=%d mixed_scene2_acne=%d"%("PASS" if okA and okB and okC else "FAIL",
  score(lambda a:b_n,heldout,K)[0],score(lambda a:b_m,heldout,K)[0],score(lambda a:b_m,heldout,2*K)[0]))
