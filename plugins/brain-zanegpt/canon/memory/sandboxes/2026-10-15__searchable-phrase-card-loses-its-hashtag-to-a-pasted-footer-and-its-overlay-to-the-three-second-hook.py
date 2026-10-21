"""Push the TIKTOK search packaging-card kernel: one searchable phrase in voiceover,
overlay and caption, plus 2-3 hashtags; YouTube shows the FIRST 3 description
hashtags above the title and ignores ALL hashtags past 60 (kernel's statement,
modelled as written). Combined with hook-caption-budget E1: a sound-off hook's
proposition must be readable in 3 s (BBC 160-180 wpm -> 8-9 words).
Pure stdlib, deterministic.
"""
import re

def yt_shown(description, count_duplicates=True):
    tags = re.findall(r"#\w+", description)
    n = len(tags) if count_duplicates else len(set(t.lower() for t in tags))
    if n > 60:
        return [], n           # every hashtag ignored
    return tags[:3], n

PHRASE_TAG = "#fakemobilegameads"
CARD = ["#fakemobilegameads", "#mobilegames", "#parody"]
FOOTER = "Follow for more!\n#shorts #comedy #channelname #series"
CAPTION = "This pin-pull ad gets worse every level"

workflows = {}
# W1: card as written, hashtags at the top of the description
workflows["W1 card first"] = " ".join(CARD) + "\n" + CAPTION
# W2: TikTok caption pasted, card hashtags after it, then the channel footer
workflows["W2 caption+card, footer after"] = CAPTION + " " + " ".join(CARD) + "\n" + FOOTER
# W3: footer template pasted ABOVE the caption (common upload template)
workflows["W3 footer above card"] = FOOTER + "\n" + CAPTION + " " + " ".join(CARD)
# W4: card plus a TikTok-style hashtag dump of 58 tags (61 total)
dump = " ".join(f"#tag{i}" for i in range(58))
workflows["W4 card + 58-tag dump (61)"] = " ".join(CARD) + " " + dump
workflows["W5 card + 57-tag dump (60)"] = " ".join(CARD) + " " + " ".join(f"#tag{i}" for i in range(57))
# W6: 31 unique tags each written twice (62 written, 31 unique): count convention unknown
w6 = " ".join(CARD + [f"#tag{i}" for i in range(28)]) ; w6 = w6 + " " + w6
workflows["W6 31 unique x2 (62 written)"] = w6

res = {}
for name, d in workflows.items():
    shown, n = yt_shown(d)
    shown_u, _ = yt_shown(d, count_duplicates=False)
    res[name] = (PHRASE_TAG in shown, n, PHRASE_TAG in shown_u)
    print(f"{name:32s} tags {n:3d}  shown {shown}  phrase shown: {PHRASE_TAG in shown} (dupes-not-counted: {PHRASE_TAG in shown_u})")

# Overlay budget: the first-3-second overlay must carry the hook proposition AND the phrase
PROPS = ["Save him!", "Can you save the cat?", "Only 1% pass level 3",
         "Pull the right pin or he drowns", "99% of players fail this simple puzzle",
         "He has to escape the lava before the timer runs out"]
PHRASE = "fake mobile game ads"
def words(s): return len(s.split())
budget = {160: 160 * 3 // 60, 180: 180 * 3 // 60}   # 8 and 9 words in 3 s
fit = {}
for wpm, cap in budget.items():
    alone = sum(words(p) <= cap for p in PROPS)
    plus = sum(words(p) + words(PHRASE) <= cap for p in PROPS)
    fit[wpm] = (alone, plus)
    print(f"{wpm} wpm cap {cap} words: propositions fitting alone {alone}/6, with the 4-word phrase added {plus}/6")
# push: phrase length 2..6 at 180 wpm
sweep = {k: sum(words(p) + k <= budget[180] for p in PROPS) for k in range(2, 7)}
print("180 wpm, propositions that still fit by phrase length:", sweep)
merged = "Only 1% beat this fake mobile game ad"
print(f"merged proposition+phrase '{merged}': {words(merged)} words, fits 160 wpm: {words(merged) <= budget[160]}")

# Predictions written before the first run
checks = {
    "W1 shows the phrase tag": res["W1 card first"][0],
    "W2 still shows the phrase tag (footer after)": res["W2 caption+card, footer after"][0],
    "W3 footer-first hides the phrase tag": not res["W3 footer above card"][0],
    "W4 at 61 tags shows nothing": not res["W4 card + 58-tag dump (61)"][0],
    "W5 at 60 tags still shows it": res["W5 card + 57-tag dump (60)"][0],
    "with phrase: 3/6 fit at 180 wpm and 2/6 at 160": fit[180][1] == 3 and fit[160][1] == 2,
}
for k, v in checks.items(): print(("ok  " if v else "MISS"), k)
s = sum(checks.values())
print(f"RESULT: {'PASS' if s == len(checks) else 'FAIL'} {s}/{len(checks)}; footer-first hides the phrase tag, 61 tags hide all (60 keep); "
      f"overlay fits alone {fit[180][0]}/6 at 180 wpm, with phrase {fit[180][1]}/6 (160 wpm {fit[160][1]}/6); W6 dupes decide: {res['W6 31 unique x2 (62 written)'][0]} vs {res['W6 31 unique x2 (62 written)'][2]}")
