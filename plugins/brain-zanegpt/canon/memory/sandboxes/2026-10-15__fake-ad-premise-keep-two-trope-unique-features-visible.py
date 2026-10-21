# Fake-mobile-ad premise slot machine: does "one trope + one absurd swap" stay readable?
# A deterministic reader identifies the trope from visible features, weighting each feature
# by inverse frequency across tropes (shared grammar-kit features weigh almost nothing).
# Recognised = top-1 is the true trope AND retained score >= 50% of its unswapped score.
# The 50% bar and the feature lists are ASSUMED model inputs, not audience data.
import math
from itertools import combinations

KIT = {"finger_cursor", "fail_stamp", "help_text", "level_counter", "store_card", "play_now"}
# slot roles: sig = what makes this trope this trope, pay = the payload the joke can replace
TROPES = {
    "pull_the_pin": {"sig": ["pins", "chambers"], "pay": ["lava_hazard", "gold_pile"],
                     "kit": ["finger_cursor", "fail_stamp", "play_now"]},
    "incompetent_player": {"sig": ["wrong_choice_replay", "king_character"], "pay": ["rising_water"],
                           "kit": ["fail_stamp", "help_text", "finger_cursor"]},
    "number_gates": {"sig": ["plus_minus_gates", "crowd_runner"], "pay": ["boss_tower"],
                     "kit": ["level_counter", "play_now"]},
    "save_sad_man": {"sig": ["crying_man", "pick_one_of_two"], "pay": ["ruined_house"],
                     "kit": ["help_text", "fail_stamp", "store_card"]},
    "merge_evolution": {"sig": ["merge_grid", "evolution_chain"], "pay": ["final_form_monster"],
                        "kit": ["level_counter", "finger_cursor"]},
    "live_action_skit": {"sig": ["real_actors", "stilted_line"], "pay": ["power_number"],
                         "kit": ["store_card", "play_now"]},
}
# a few tropes share a payload-like object with another, to make the reader's job honest
TROPES["incompetent_player"]["pay"].append("lava_hazard")   # king also dies in lava in some ads

def feats(t):
    d = TROPES[t]
    return d["sig"] + d["pay"] + d["kit"]

ALL = {t: set(feats(t)) for t in TROPES}
df = {}
for fs in ALL.values():
    for f in fs:
        df[f] = df.get(f, 0) + 1
N = len(TROPES)
idf = {f: math.log((N + 1) / df[f]) for f in df}

def score(visible, t):
    return sum(idf[f] for f in visible if f in ALL[t])

def recognised(t, swapped):
    visible = [f for f in feats(t) if f not in swapped] + ["absurd_%d" % i for i in range(len(swapped))]
    scores = {u: score(visible, u) for u in TROPES}
    best = max(scores, key=lambda u: (scores[u], u == t))
    rivals = [scores[u] for u in TROPES if u != t]
    full = score(feats(t), t)
    return best == t and scores[t] > max(rivals) and scores[t] >= 0.5 * full

def top_idf(t, role):
    return max(TROPES[t][role], key=lambda f: idf[f])

res = {}
# S1 swap one payload feature (the kernel's example: pins hold back paperwork instead of lava)
res["pay1"] = sum(recognised(t, {top_idf(t, "pay")}) for t in TROPES)
# S2 swap the single most distinctive signature feature
res["sig1"] = sum(recognised(t, {top_idf(t, "sig")}) for t in TROPES)
# S3 swap one kit feature (cheapest swap of all)
res["kit1"] = sum(recognised(t, {TROPES[t]["kit"][0]}) for t in TROPES)
# S4 BREAK: swap k features, every combination, k = 1..3
by_k = {}
for k in (1, 2, 3):
    tot = ok = 0
    for t in TROPES:
        for combo in combinations(feats(t), k):
            tot += 1
            ok += recognised(t, set(combo))
    by_k[k] = (ok, tot)
# S5 which single features are unsafe to swap: list per trope
unsafe = {t: [f for f in feats(t) if not recognised(t, {f})] for t in TROPES}
# S6 two swaps where both are payload/kit (signature kept intact)
tot2 = ok2 = 0
for t in TROPES:
    soft = TROPES[t]["pay"] + TROPES[t]["kit"]
    for combo in combinations(soft, 2):
        tot2 += 1
        ok2 += recognised(t, set(combo))

print("idf: kit features", {f: round(idf[f], 2) for f in sorted(KIT)})
print("S1 payload single swap recognised %d/6" % res["pay1"])
print("S2 signature single swap recognised %d/6" % res["sig1"])
print("S3 kit single swap recognised %d/6" % res["kit1"])
for k, (ok, tot) in by_k.items():
    print("S4 any %d-swap recognised %d/%d = %.0f%%" % (k, ok, tot, 100.0 * ok / tot))
print("S5 unsafe single swaps:", {t: v for t, v in unsafe.items() if v})
print("S6 two soft swaps (signature intact) recognised %d/%d = %.0f%%" % (ok2, tot2, 100.0 * ok2 / tot2))

# S7 BREAK on role: the first-second hook frame shows only 3 features (top signature, first payload,
# first kit item). Swap the signature or the payload there.
def recognised_sparse(t, swap_role):
    shown = [top_idf(t, "sig"), TROPES[t]["pay"][0], TROPES[t]["kit"][0]]
    full = score(shown, t)
    gone = {"sig": shown[0], "pay": shown[1]}[swap_role]
    visible = [f for f in shown if f != gone] + ["absurd_0"]
    sc = {u: score(visible, u) for u in TROPES}
    rivals = max(sc[u] for u in TROPES if u != t)
    return sc[t] > rivals and sc[t] >= 0.5 * full
sp_sig = [t for t in TROPES if not recognised_sparse(t, "sig")]
sp_pay = [t for t in TROPES if not recognised_sparse(t, "pay")]
print("S7 sparse hook frame: signature swap lost %d/6 %s; payload swap lost %d/6 %s" % (len(sp_sig), sp_sig, len(sp_pay), sp_pay))
# S8 role-agnostic predictor over all 3-swaps: count trope-unique features left visible
from collections import defaultdict
uq = defaultdict(lambda: [0, 0])
for t in TROPES:
    for combo in combinations(feats(t), 3):
        u = sum(1 for f in feats(t) if f not in combo and df[f] == 1)
        uq[u][1] += 1
        uq[u][0] += recognised(t, set(combo))
print("S8 3-swaps by unique features left:", {u: "%d/%d" % tuple(v) for u, v in sorted(uq.items())})

one_swap_safe = by_k[1][0] == by_k[1][1]
k3_drops = by_k[3][0] < by_k[3][1]
role_matters_sparse = len(sp_sig) > len(sp_pay)
ok = one_swap_safe and k3_drops and role_matters_sparse
print("prediction check: payload>=5/6 %s, signature<=3/6 %s (full view)" % (res["pay1"] >= 5, res["sig1"] <= 3))
print("RESULT: %s full view any single swap %d/%d, 2-swap %d/%d, 3-swap %d/%d; signature swap %d/6 = payload %d/6 at full view; sparse hook frame signature swap loses %d/6 vs payload %d/6; 3-swaps by unique left %s"
      % ("PASS" if ok else "FAIL", by_k[1][0], by_k[1][1], by_k[2][0], by_k[2][1], by_k[3][0], by_k[3][1],
         res["sig1"], res["pay1"], len(sp_sig), len(sp_pay), {u: "%d/%d" % tuple(v) for u, v in sorted(uq.items())}))
