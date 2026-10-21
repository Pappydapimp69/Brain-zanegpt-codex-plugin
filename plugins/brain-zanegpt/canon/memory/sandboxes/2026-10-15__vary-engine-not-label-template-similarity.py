"""Sandbox: ads batch; does assigning different comic-engine LABELS prevent 'templated' batches?
Kernels/entries exercised together: ideas:AI-VIDEO/every-video-gets-its-own-joke-and-script (template
check: only the game name swapped = mass-produced), ideas:COMEDY-CRAFT/vary-the-comic-engine-not-the-topic
(assign a different engine per idea), fake-ad-kernel-source-check/E1 (verify the labels, not just numbers).
PREDICTION (before first run): swapping only game name across 6 ads gives max pairwise similarity >=0.9
(flagged); assigning 6 different engine labels with genuinely different beat structure gives max <=0.4
(clear); BUT relabelling the same beat structure with 6 different engine names still gives max >=0.9, i.e.
label diversity passes a label-only check while the content check flags it (the break scenario). Assumption:
the engine label reflects the beat structure. Wrong if the relabelled batch scores <0.5 on content."""
import itertools
def feats(ad):
    b = ad["beats"]
    f = {("bg", x, y) for x, y in zip(b, b[1:])}          # beat-to-beat structure bigrams
    f |= {("voice", ad["voice"]), ("layout", ad["layout"]), ("end", ad["end"]), ("len", len(b))}
    return f                                              # game name deliberately excluded
def sim(a, b):
    A, B = feats(a), feats(b); return len(A & B) / len(A | B)
def maxpair(batch):
    return max(sim(a, b) for a, b in itertools.combinations(batch, 2))
def label_check(batch): return len({a["engine"] for a in batch}) == len(batch)
games = ["Farm", "Tanks", "Gems", "Words", "Racer", "Chef"]
base = dict(beats=["setup", "ask", "grow", "cosmic", "deadpan"], voice="vo_a", layout="L1", end="deadpan_line")
A = [dict(base, game=g, engine="escalation") for g in games]
engines = ["escalation", "literalism", "role_reversal", "anticlimax", "callback", "genre_switch"]
structs = [["setup","ask","grow","cosmic","deadpan"], ["claim","literal","literal2","fallout"], ["swap","player_fails","ad_fails","swap_back","shrug","end"],
           ["promise","build","build2","nothing"], ["gag","other","gag_again","gag_twice","twist"], ["trailer","genre","genre2","record_scratch","game"]]
voices = ["vo_a","vo_b","vo_c","vo_d","vo_e","vo_f"]; layouts = ["L1","L2","L3","L4","L5","L6"]; ends = ["deadpan_line","cut","logo","silence","callback_line","freeze"]
B = [dict(game=games[i], engine=engines[i], beats=structs[i], voice=voices[i], layout=layouts[i], end=ends[i]) for i in range(6)]
C = [dict(base, game=games[i], engine=engines[i]) for i in range(6)]        # BREAK: labels differ, content identical
D = [dict(a) for a in B]; 
for a in D: a["end"] = "deadpan_line"                                       # varied engines, shared endpoint
E = [dict(a) for a in B]
for a in E: a["voice"], a["layout"] = "vo_a", "L1"                          # varied engines, shared voice+layout skin
rows = {}
for name, batch in [("1 name-swap only", A), ("2 distinct engines+content", B), ("3 labels vary, content same (BREAK)", C),
                    ("4 engines vary, shared endpoint", D), ("5 engines vary, shared voice+layout", E)]:
    rows[name[0]] = (maxpair(batch), label_check(batch))
    print("%-40s max-sim %.2f  labels-distinct %s  flagged(>=0.6) %s" % (name, maxpair(batch), label_check(batch), maxpair(batch) >= 0.6))
ok = (rows["1"][0] >= 0.9 and rows["2"][0] <= 0.4 and rows["3"][0] >= 0.9 and rows["3"][1] and rows["4"][0] < 0.6 and rows["5"][0] < 0.6)
print("RESULT: %s name-swap %.2f, distinct %.2f, relabelled-same-content %.2f (labels distinct=%s), shared-end %.2f, shared-skin %.2f"
      % ("PASS" if ok else "FAIL", rows["1"][0], rows["2"][0], rows["3"][0], rows["3"][1], rows["4"][0], rows["5"][0]))
