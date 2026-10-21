# Sandbox: reusable fake-ad kit (10 fixed assets) vs the anti-template rule
# (own joke/script per video). Similarity = share of 16 feature slots identical
# between two videos; the 0.5 flag line is an ASSUMPTION. Stdlib, deterministic.
import random, itertools
KIT = ["finger_cursor","red_fail_stamp","arrows","floating_numbers","level_counter",
       "fake_timer","percent_text","sad_character","chiptune_jingle","store_end_card"]
VAR = ["game_name","joke","script","voiceover","layout","trope"]
SLOTS = KIT + VAR
POOL = 6
def make_batch(n, seed, vary, kit_rot):
    rnd = random.Random(seed); vids = []
    for i in range(n):
        v = {}
        for s in KIT:
            v[s] = rnd.randrange(POOL) if s in kit_rot else 0
        for s in VAR:
            v[s] = rnd.randrange(10**6) if s in vary else 0
        vids.append(v)
    return vids
def mean_sim(vids):
    sims = [sum(a[s] == b[s] for s in SLOTS) / len(SLOTS) for a, b in itertools.combinations(vids, 2)]
    return sum(sims) / len(sims)
FLAG = 0.5
cases = {
 "1 name-swap only":            (["game_name"], []),
 "2 BREAK: own joke+script+voice+layout+trope": (VAR, []),
 "3 variable new + rotate 3 kit assets": (VAR, KIT[:3]),
 "4 variable new + rotate 6 kit assets": (VAR, KIT[:6]),
}
out = {}
for k, (vary, rot) in cases.items():
    out[k] = mean_sim(make_batch(8, 7, vary, rot)); print(f"{k}: {out[k]:.3f} {'FLAGGED' if out[k] > FLAG else 'ok'}")
c = list(out.values())
ok = (c[0] > 0.9 and abs(c[1] - 10/16) < 0.01 and c[1] > FLAG and c[2] < c[1] and c[3] < FLAG and c[2] > FLAG - 0.1)
print(f"RESULT: {'PASS' if ok else 'FAIL'} name-swap {c[0]:.2f}, own joke/script {c[1]:.2f} (still over {FLAG}), +3 kit rotated {c[2]:.2f}, +6 kit rotated {c[3]:.2f}")
