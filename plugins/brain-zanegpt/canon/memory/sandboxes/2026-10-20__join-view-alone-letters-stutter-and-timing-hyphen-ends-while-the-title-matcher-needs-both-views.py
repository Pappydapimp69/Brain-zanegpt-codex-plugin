# Sandbox: title matcher needs BOTH hyphen views (split for stutter, join for timing). Does rhyme lettering need both too?
# PREDICTION (before run): a join-view end-word judge letters 8/8 stanzas as intended (4 stutter + 4 timing-hyphen ends);
# a last-segment (split) judge letters stutter 4/4 but timing-hyphen ends <=2/4; so lettering needs ONLY the join view,
# unlike the matcher. (iteration 2: fixed three stanzas whose intended letters did not match the spelling rime rule) BREAK: a stutter end whose pieces differ in rime from the joined word (ha-ha-ha vs hahaha) should
# still agree because the rime is read from the end.
import re
def view(w, m): return w.split('-')[-1] if m == 'split' else w.replace('-', '')
def rime(w, m):
    w = view(w, m).lower()
    g = re.search(r"[aeiouy]+[^aeiouy]+[aeiouy]$", w) or re.search(r"[aeiouy]+[^aeiouy]*$", w)
    return g.group(0) if g else w
def letters(ends, m):
    keys, out = {}, []
    for e in ends:
        k = rime(e, m); keys.setdefault(k, chr(65 + len(keys))); out.append(keys[k])
    return ''.join(out)
# (stanza ends, intended letters, kind)
STANZAS = [
    (["uh-uh-blue", "glue", "na-na-true", "due"], "AAAA", "stutter"),
    (["la-la-love", "above", "oh-oh-oh-glove", "dove"], "AAAA", "stutter"),
    (["hey-hey-day", "away", "yeah-yeah-stay", "play"], "AAAA", "stutter"),
    (["ba-ba-bright", "night", "wo-wo-wo-light", "tight"], "AAAA", "stutter"),
    (["gon-na", "Don-na", "wan-na", "An-na"], "AABB", "timing"),
    (["a-gain", "rain", "re-main", "pain"], "AAAA", "timing"),
    (["de-sire", "fire", "fi-re", "hi-re"], "AAAA", "timing"),
    (["sum-mer", "drum-mer", "win-ter", "splin-ter"], "AAAA", "timing"),
]
res = {m: {"stutter": 0, "timing": 0} for m in ("join", "split")}
for ends, want, kind in STANZAS:
    for m in ("join", "split"):
        got = letters(ends, m); res[m][kind] += got == want
        print("%-8s %-6s %-30s got=%s want=%s" % (kind, m, ends, got, want))
# BREAK: stutter end whose pieces differ from the joined rime
brk = ["ha-ha-ha", "ha", "ho-ho-ho", "no"]
bj, bs = letters(brk, "join"), letters(brk, "split")
print("BREAK laugh stutter ends: join=%s split=%s" % (bj, bs))
ok = res["join"]["stutter"] == 4 and res["join"]["timing"] == 4 and res["split"]["stutter"] == 4 and res["split"]["timing"] <= 2
print("RESULT: %s join stutter %d/4 timing %d/4; split stutter %d/4 timing %d/4; laugh break join=%s split=%s"
      % ("PASS" if ok else "FAIL", res["join"]["stutter"], res["join"]["timing"], res["split"]["stutter"], res["split"]["timing"], bj, bs))
