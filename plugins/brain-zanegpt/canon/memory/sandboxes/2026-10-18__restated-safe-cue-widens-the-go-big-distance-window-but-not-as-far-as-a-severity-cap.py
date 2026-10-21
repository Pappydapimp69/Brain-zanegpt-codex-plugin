# Composes escalation-needs-matching-distance (severe harm needs the matched distance), rule-card-severity-cap-flattens-
# the-distance-dial (cover 0.8-0.5d up to the split 0.3, 0.2+0.7d above; laugh = s if s<=b else max(0, s-3(s-b));
# go-big s=i/6 had 1 of 11 distances within 95% of best, a 0.3 cap 9 of 11) and restating-the-safe-cue-survives-a-costly-
# restatement (a cue decaying 0.6 a beat, restated every second beat, each restating beat losing q of its laugh).
# Added: the cue raises the cover to b + c(1-b), c = c0*0.6^age. Window = distances (of 11, step 0.1) within 95% of the
# schedule's own best total.
# PREDICTION (before run): with c0 0.7 and q 0.2 the restated cue lifts go-big from 1 to at least 5 of 11 distances,
# but stays under the card's 9; card plus cue adds at most 1 distance over the card alone (the cap already flattens);
# BREAK: with c0 0.4 and q 0.5 the restated cue leaves go-big at 2 or fewer.
def laugh(s, b): return s if s <= b else max(0.0, s - 3 * (s - b))
def cover(d, s, split=0.3): return 0.8 - 0.5 * d if s <= split else 0.2 + 0.7 * d
def total(sched, d, c0=0.0, q=0.0, every=2):
    t, age = 0.0, 0
    for k, s in enumerate(sched):
        c = c0 * 0.6 ** age
        b = cover(d, s); b = b + c * (1 - b)
        x = laugh(s, b)
        if c0 and age == 0 and k > 0: x *= 1 - q
        t += x; age += 1
        if c0 and age >= every: age = 0
    return t
ds = [i / 10 for i in range(11)]
def window(sched, **kw):
    ts = [total(sched, d, **kw) for d in ds]; m = max(ts)
    return sum(1 for t in ts if t >= 0.95 * m), m
big = [i / 6 for i in range(1, 7)]
card = [0.05 * i for i in range(1, 7)]
w_big, m_big = window(big)
w_cue, m_cue = window(big, c0=0.7, q=0.2)
w_card, m_card = window(card)
w_cc, _ = window(card, c0=0.7, q=0.2)
w_brk, _ = window(big, c0=0.4, q=0.5)
print(f"go-big window {w_big} (best total {m_big:.2f}); go-big + restated cue c0 .7 q .2 window {w_cue} (best {m_cue:.2f}); card window {w_card} (best {m_card:.2f}); card + cue window {w_cc}; break c0 .4 q .5 go-big window {w_brk}")
ok = w_big == 1 and 5 <= w_cue < w_card and w_cc <= w_card + 1 and w_brk <= 2
print(f"RESULT: {'PASS' if ok else 'FAIL'} windows of 11: go-big {w_big}, go-big+cue {w_cue}, card {w_card}, card+cue {w_cc}; break (c0 .4, q .5) {w_brk}; best totals go-big+cue {m_cue:.2f} vs card {m_card:.2f}")
