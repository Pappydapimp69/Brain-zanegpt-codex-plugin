# Prediction (written before run): across 3 scenarios, a gap scanner over two-pass letters
# keeps true gap 1 only when ad-libs are excluded AND hyphens rejoined; either fault alone
# changes the gap or letters in >=1 scenario; both faults together fail in all 3 stanzas.
import re
def rejoin(w): return w.replace("-", "")
def rkey(w):  # crude perfect-rhyme key: from last vowel group to end
    return rejoin(w).lower()[-3:]
def vk(w):  # assonance key: last vowel group only
    m = re.findall(r"[aeiouy]+", rejoin(w).lower())
    return m[-1] if m else w
def letters(ends, judge):
    out, groups = [], {}
    # pass1 perfect
    for e in ends:
        k = judge(e)
        groups.setdefault(k, len(groups))
    cnt = {}
    for e in ends: cnt[judge(e)] = cnt.get(judge(e), 0) + 1
    res, nxt, m = [], 0, {}
    for e in ends:
        k = judge(e)
        if cnt[k] > 1:
            if k not in m: m[k] = "ABCDEF"[len(m)]
            res.append(m[k])
        else: res.append("x")
    return "".join(res)
def gap(lets):
    for i, c in enumerate(lets):
        if c != "x":
            for j in range(i + 1, len(lets)):
                if lets[j] == c: return j - i
    return None
def run(lines, rejoin_on, excl_on):
    body = [l for l in lines if not (excl_on and l[2])]
    ends = [l[0] for l in body]
    judge = (lambda e: rkey(e)) if rejoin_on else (lambda e: e.split("-")[-1].lower()[-3:])
    lt = letters(ends, judge)
    return lt, gap(lt)
# (end word, text, is_adlib)
S1 = [("night",1,0),("oh-yeah",1,1),("light",1,0),("a-bove",1,0)]       # true gap 1 (night/light)
S2 = [("to-night",1,0),("light",1,0),("ah",1,1),("way",1,0)]
S3 = [("de-sire",1,0),("fire",1,0),("hey",1,1),("hold",1,0)]             # BREAK: silent-e hyphen
truth = {"S1":1,"S2":1,"S3":1}
tot = {}
for name, S in (("S1",S1),("S2",S2),("S3",S3)):
    for rj in (0,1):
        for ex in (0,1):
            lt, g = run(S, rj, ex)
            tot[(name,rj,ex)] = g
            print(name, "rejoin",rj,"exclude",ex,"letters",lt,"gap",g)
ok_both = all(tot[(n,1,1)] == 1 for n in truth)
bad_neither = sum(tot[(n,0,0)] != 1 for n in truth)
bad_one = sum(tot[(n,r,e)] != 1 for n in truth for r,e in ((1,0),(0,1)))
print("both-correct",ok_both,"neither-wrong",bad_neither,"single-fault wrong",bad_one,"of 6")
print(("RESULT: PASS" if ok_both and bad_neither>=2 and bad_one>=1 else "RESULT: FAIL"),
      f"both fixes {ok_both}, neither wrong {bad_neither}/3, single fault wrong {bad_one}/6")
