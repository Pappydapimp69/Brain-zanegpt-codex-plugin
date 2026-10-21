# Sandbox: rhyme lettering over end words carrying BOTH hyphen meanings
# (timing marks inside one word vs stutter repeats of a word).
# Views: last (last fragment), rejoin (strip all hyphens), smart (collapse repeated fragments, then rejoin).
import itertools
RHYME = {"light":"ight","night":"ight","sight":"ight","fire":"ire","desire":"ire","higher":"ire",
 "beautiful":"ul","wonderful":"ul","shine":"ine","mine":"ine","line":"ine",
 "run":"un","sun":"un","one":"un","baby":"aby","maybe":"aby","crazy":"azy","lazy":"azy",
 "go":"o","slow":"o","know":"o"}
LEX_END = sorted(RHYME)
def true_word(tok):
    # ground truth: timing hyphens join; stutter repeats collapse to one word
    parts = tok.split("-")
    if len(set(parts)) == 1 and len(parts) > 1: return parts[0]
    return "".join(parts)
def view(tok, kind):
    parts = tok.split("-")
    if kind == "last": return parts[-1]
    if kind == "rejoin": return "".join(parts)
    if len(set(parts)) == 1 and len(parts) > 1: return parts[0]
    return "".join(parts)
def key(w): return RHYME.get(w, "?"+w)   # unknown word -> unique key (no rhyme)
def letters(words):
    seen, out = {}, []
    for w in words:
        k = key(w)
        if k not in seen: seen[k] = "ABCDEFGH"[len(seen)]
        out.append(seen[k])
    return "".join(out)
def shape(l):  # canonical scheme
    m, o = {}, ""
    for c in l: m.setdefault(c, "ABCD"[len(m)]); o += m[c]
    return o
timing_toks = ["beau-ti-ful","won-der-ful","de-si-re","fi-re","high-er","la-zy","cra-zy","ba-by","may-be"]
stutter_toks = ["run-run-run","sun-sun","go-go-go","slow-slow","night-night","light-light","shine-shine","mine-mine"]
plain = ["light","night","sight","fire","shine","line","run","sun","go","slow","know","one"]
def stanzas(pool):
    out=[]
    for a,b in itertools.permutations(pool,2):
        for scheme in ("AABB","ABAB"):
            pass
    return out
# stanza = 4 end tokens drawn so that the TRUE scheme is known
def build(pool_a, pool_b):
    res=[]
    for a1,a2 in itertools.permutations(pool_a,2):
        for b1,b2 in itertools.permutations(pool_b,2):
            if key(true_word(a1))==key(true_word(a2)) and key(true_word(b1))==key(true_word(b2)) and key(true_word(a1))!=key(true_word(b1)):
                res.append((a1,a2,b1,b2))
    return res
def score(label, st, kind):
    ok=0
    for a1,a2,b1,b2 in st:
        for order in ((a1,a2,b1,b2),(a1,b1,a2,b2)):
            truth = shape(letters([true_word(t) for t in order]))
            ok += shape(letters([view(t,kind) for t in order]))==truth
    n=len(st)*2
    print(f"{label:34s} {kind:7s} {ok}/{n}")
    return ok,n
timing_st = build(["beau-ti-ful","won-der-ful","de-si-re","fi-re","high-er","la-zy","cra-zy","ba-by","may-be"],
                  ["beau-ti-ful","won-der-ful","de-si-re","fi-re","high-er","la-zy","cra-zy","ba-by","may-be"])
stutter_st = build(["run-run-run","sun-sun","go-go-go","slow-slow","night-night","light-light","shine-shine","mine-mine"],
                   ["run-run-run","sun-sun","go-go-go","slow-slow","night-night","light-light","shine-shine","mine-mine"])
mixed_st = build(["be-au-ti-ful","won-der-ful","la-zy","cra-zy","fi-re","de-si-re"],
                 ["run-run-run","sun-sun","night-night","light-light","shine-shine","mine-mine"])
# NB 'be-au-ti-ful' typo guard: unknown key => unique, ok
R={}
for lab,st in (("timing-only",timing_st),("stutter-only",stutter_st),("mixed (BREAK: timing+stutter)",mixed_st)):
    for k in ("last","rejoin","smart"): R[(lab,k)]=score(lab,st,k)
# prediction check
t_rejoin=R[("timing-only","rejoin")]; s_rejoin=R[("stutter-only","rejoin")]
s_last=R[("stutter-only","last")]; smart=[R[(l,"smart")] for l in ("timing-only","stutter-only","mixed (BREAK: timing+stutter)")]
all_smart = all(a==b for a,b in smart)
print("smart perfect everywhere:",all_smart,"| rejoin timing perfect:",t_rejoin[0]==t_rejoin[1],"| rejoin stutter wrong:",s_rejoin[1]-s_rejoin[0],"| last stutter perfect:",s_last[0]==s_last[1])
ok = all_smart and t_rejoin[0]==t_rejoin[1] and s_rejoin[0]<s_rejoin[1]
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
 f"rejoin timing {t_rejoin[0]}/{t_rejoin[1]}, rejoin stutter {s_rejoin[0]}/{s_rejoin[1]}, last-fragment stutter {s_last[0]}/{s_last[1]}, smart {[f'{a}/{b}' for a,b in smart]}")
