"""New-half pick: tension-as-information-gap + film + GAME-ADS hook-in-three-seconds-sound-off.
The gap opener (the proposition: 'can you save him?') must be READ by 3 s with sound off.
How many words fit by 3 s under each caption reading standard?
  BBC subtitle guidelines 160-180 wpm (2.67-3.0 words/s), Netflix English adult 20 chars/s,
  this film engine's caption sizing NEED = 1 + words/2.6 s, and the kernel's quoted
  '5-10 words per second' (not found in TikTok's published guidance in this run).
Fixed test propositions (real phrasing style of fail ads), deterministic arithmetic.
PREDICTION (written before running): by 3 s BBC allows 8-9 words, Netflix about 10
(at ~5.5 chars per word incl. space), the film engine 5; the kernel's 10 words/s is >= 3x
BBC's upper rate; of the 6 test propositions, at most half are readable by 3 s under BBC."""
PROPS = ["Save him!", "Can you save the cat?", "Pull the right pin or he drowns",
         "Only 1% can pour the last glass correctly", "Can you guide the water to the plants before they dry?",
         "This level is impossible, the last move looks easy but everyone fails it"]
words = lambda s: len(s.split()); chars = lambda s: len(s)
t_bbc_fast = lambda s: words(s) / 3.0          # 180 wpm
t_bbc_slow = lambda s: words(s) / (160 / 60)   # 160 wpm
t_nflx = lambda s: chars(s) / 20.0
t_film = lambda s: 1 + words(s) / 2.6
t_k10 = lambda s: words(s) / 10.0
rows = []
for p in PROPS:
    r = (p, words(p), chars(p), t_bbc_slow(p), t_bbc_fast(p), t_nflx(p), t_film(p), t_k10(p))
    rows.append(r)
    print(f"{r[1]:2d}w {r[2]:3d}c  BBC {r[3]:.2f}-{r[4]:.2f}s  Netflix {r[5]:.2f}s  film {r[6]:.2f}s  kernel@10w/s {r[7]:.2f}s  | {p}")
max_words = {"BBC 180wpm": int(3 * 3.0), "BBC 160wpm": int(3 * 160 / 60), "film engine": int((3 - 1) * 2.6),
             "Netflix (5.5 c/w)": int(3 * 20 / 5.5), "kernel 10 w/s": 30}
print("max words readable by 3 s:", max_words)
readable_bbc = sum(r[4] <= 3 for r in rows)
ratio = 10 / 3.0
ok = max_words["BBC 180wpm"] in (8, 9) and max_words["film engine"] == 5 and ratio >= 3 and readable_bbc <= 3
print(f"RESULT: {'PASS' if ok else 'FAIL'} by 3 s: BBC {max_words['BBC 160wpm']}-{max_words['BBC 180wpm']} words, Netflix ~{max_words['Netflix (5.5 c/w)']}, "
      f"film engine {max_words['film engine']}; kernel's 10 w/s is {ratio:.1f}x BBC's fastest; test propositions readable by 3 s (BBC fast): {readable_bbc}/6")
