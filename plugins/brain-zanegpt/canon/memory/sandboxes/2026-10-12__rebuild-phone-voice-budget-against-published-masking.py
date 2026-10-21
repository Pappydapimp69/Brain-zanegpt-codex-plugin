"""Blind rebuild of seven#E65 ('on phone speakers a hallucinated-voice scene has
the one-place budget of 2 voices whatever the mixing; headphones 5').
Own fixture: E65's metric (half the words land) but on published speech-in-speech
effects instead of an assumed masking width: one equal mono talker -> 0.60,
1.5 dB per doubling of talkers, spatial release 6-12 dB (1-3 maskers, half
beyond), none in mono; logistic psychometric at 5/10/15 %/dB; level ducks 0/3/6 dB."""
import math
def p(x, s):
    k = 4 * s; x0 = math.log(1.5) / k
    return 1 / (1 + math.exp(-k * (x + x0)))
def budget(target, duck, rel, s):
    best = 0
    for n in range(1, 65):
        r = 0 if rel == 0 else (rel if n <= 3 else rel / 2)
        if p(duck + r - 1.5 * math.log2(n), s) >= target: best = n
    return best + 1
phone = {}; hp = {}
for s in (0.05, 0.10, 0.15):
    phone[s] = [budget(0.5, d, 0, s) for d in (0, 3, 6)]
    hp[s] = [budget(0.5, 0, r, s) for r in (6, 9, 12)]
    print(f"slope {int(s*100)}%/dB: phone(mono) 50% budget at duck 0/3/6 dB {phone[s]}   headphones 50% rel 6/9/12 {hp[s]}")
c1 = all(phone[s][0] == 2 for s in phone)                 # phone 2 with no duck
c2 = all(v == 2 for s in phone for v in phone[s])          # 'whatever the mixing'
c3 = all(4 <= v <= 6 for s in hp for v in hp[s])           # headphones about 5
print(f"phone=2 at no duck every slope: {c1}; phone=2 whatever the mixing: {c2}; headphones 4..6: {c3}")
print(f"RESULT: {'PASS' if (c2 and c3) else 'FAIL'} phone no-duck {[phone[s][0] for s in phone]}, phone+6dB {[phone[s][2] for s in phone]}, headphones {[hp[s] for s in hp]}")
