"""Sandbox: does a frame-zero sound (film E14: hook needs sound at frame 0) change which variant wins
an IPM x D1 ranking (rank-ipm-times-d1 E1), and does decomposing the winner (kernel concept-then-variants) keep it?
Model (assumed): variant = (hook 0.8/1.0/1.2, fidelity 0.4/0.7/1.0, frame0 sound on/off).
 IPM = 10*hook*(1.6-0.6*fidelity)*sound_boost ; sound_boost = 1+S*(1+K*(1-fidelity)) when sound on else 1
 (K = how much more the sound lifts low-fidelity, over-promising ads; K=0 means sound is an independent factor)
 D1 = 0.15+0.25*fidelity. No randomness."""
HOOKS = (0.8, 1.0, 1.2); FID = (0.4, 0.7, 1.0)
def variants(S, K):
    out = []
    for h in HOOKS:
        for f in FID:
            for snd in (True, False):
                boost = 1 + S * (1 + K * (1 - f)) if snd else 1.0
                ipm = 10 * h * (1.6 - 0.6 * f) * boost
                d1 = 0.15 + 0.25 * f
                out.append(dict(h=h, f=f, snd=snd, ipm=ipm, d1=d1, score=ipm * d1))
    return out
def win(vs, key):
    return max(vs, key=lambda v: v[key])
base = variants(0.0, 0.0)
w0 = win(base, "score")
res = {}
for K in (0.0, 1.0, 2.0, 4.0, 8.0, 16.0):
    vs = variants(0.25, K)
    wi, ws = win(vs, "ipm"), win(vs, "score")
    res[K] = (wi["f"], ws["f"], ws["snd"], ws["h"])
    print("K=%-4s IPM-only winner fid %.1f | IPM*D1 winner fid %.1f sound=%s hook=%.1f" % (K, wi["f"], ws["f"], ws["snd"], ws["h"]))
# recut step: remove the sound layer from the IPM*D1 winner (film E13: dead air) -> score loss
vs0 = variants(0.25, 0.0); w = win(vs0, "score")
nosound = [v for v in vs0 if (v["h"], v["f"]) == (w["h"], w["f"]) and not v["snd"]][0]
loss = 1 - nosound["score"] / w["score"]
flip_K = [K for K in res if res[K][1] != 1.0]
print("recut loss from dropping frame-zero sound: %.3f ; K at which IPM*D1 winner leaves fidelity 1.0: %s" % (loss, flip_K))
ok = (res[0.0][1] == 1.0 and res[0.0][2] is True and abs(loss - (1 - 1 / 1.25)) < 1e-9 and res[0.0][0] == 0.4 and len(flip_K) >= 1 and res[16.0][1] != 1.0)
print("RESULT: %s with independent sound (K=0) IPM*D1 still picks fidelity 1.0 with sound on, IPM-only picks 0.4; dropping the sound in a recut loses %.0f percent; once sound lifts low-fidelity ads enough (first flip K=%s) the IPM*D1 winner leaves fidelity 1.0" % ("PASS" if ok else "FAIL", loss * 100, flip_K[0] if flip_K else None))
