# Prediction (before run): 4 stutter-hook titles ("Ha-ha-hallelujah" style lines) and 4 timing-hyphen titles
# (de-sire style), plus 4 end-word stanzas with a hyphenated rhyme word.
#  rejoin-all : rhyme 4/4 right; title: stutter 0/4, timing 4/4  -> 8 titles: 4/8
#  split-all  : rhyme <=2/4 right (last-fragment judge); title stutter 4/4, timing 0/4 -> 4/8
#  per-purpose (rejoin for rhyme, dual-view for title): rhyme 4/4, titles 8/8.
import re
def toks_join(s): return re.sub(r"(?<=\w)-(?=\w)", "", s.lower()).split()
def toks_split(s): return re.sub(r"(?<=\w)-(?=\w)", " ", s.lower()).split()
def contains(title, line, view): 
    t, l = view(title), view(line)
    return any(l[i:i+len(t)] == t for i in range(len(l) - len(t) + 1))
# (title as typed in the title field, lyric line as sung)
STUT = [("hallelujah", "Ha-ha-hallelujah tonight"), ("baby", "Ba-ba-baby come home"), ("goodbye", "Go-go-goodbye my love"), ("forever", "F-f-forever and a day")]
TIME = [("desire", "I de-sire you"), ("beautiful", "so beau-ti-ful tonight"), ("fire", "a fi-re burns"), ("remember", "re-mem-ber me")]
def title_ok(pairs, view):
    n = 0
    for t, l in pairs:
        n += contains(t, l, view)
    return n
# dual view: either view contains the title
def dual(s): return None
def title_dual(pairs): return sum(contains(t, l, toks_join) or contains(t, l, toks_split) or any(
    l2 for l2 in [l] if t in " ".join(toks_split(l)).replace(" ", "")  and False) for t, l in pairs)
# stutter: join view gives "hahahallelujah" (no match); split view: "ha ha hallelujah" -> contains "hallelujah" yes
# note f-f-forever: split view "f f forever" contains "forever".
rj_s, rj_t = title_ok(STUT, toks_join), title_ok(TIME, toks_join)
sp_s, sp_t = title_ok(STUT, toks_split), title_ok(TIME, toks_split)
dl_s = sum(contains(t, l, toks_join) or contains(t, l, toks_split) for t, l in STUT)
dl_t = sum(contains(t, l, toks_join) or contains(t, l, toks_split) for t, l in TIME)
print("title join-all  stutter", rj_s, "/4 timing", rj_t, "/4")
print("title split-all stutter", sp_s, "/4 timing", sp_t, "/4")
print("title dual      stutter", dl_s, "/4 timing", dl_t, "/4")
# rhyme: stanza ends; rhyme key = last 3 letters; hyphenated end words
# 4 intended rhyming end-word pairs; first word carries a timing hyphen
PAIRS = [("lo-ve", "a-bove"), ("de-sire", "fire"), ("to-night", "light"), ("hea-ven", "sev-en")]
def key(w): return w.replace("-", "")[-3:]
def lastseg(w): return w.split("-")[-1][-3:]
def rhyme_ok(p, judge): return judge(p[0]) == judge(p[1])
ST = PAIRS
r_join = sum(rhyme_ok(p, key) for p in ST); r_split = sum(rhyme_ok(p, lastseg) for p in ST)
print("rhyme rejoin", r_join, "/4 last-segment", r_split, "/4")
ok = (rj_s, rj_t, sp_s, sp_t, dl_s + dl_t, r_join) == (0, 4, 4, 0, 8, 4)
print("RESULT:", "PASS" if ok else "FAIL", f"rejoin-all titles {rj_s+rj_t}/8 (stutter {rj_s}), split-all titles {sp_s+sp_t}/8 (timing {sp_t}), dual-view {dl_s+dl_t}/8, rhyme rejoin {r_join}/4 vs last-segment {r_split}/4")
