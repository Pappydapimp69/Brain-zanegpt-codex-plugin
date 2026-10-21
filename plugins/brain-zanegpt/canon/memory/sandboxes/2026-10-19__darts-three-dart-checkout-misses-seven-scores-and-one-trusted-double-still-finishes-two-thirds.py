# Sandbox: darts double-out checkout (501 rules: finish on a double, score of exactly 0; leaving 1 or going below 0 is a bust).
# Prediction (before run): 21 one-dart finishes (D1-D20, bull); exactly 7 scores of 2..170 cannot finish in 3 darts
# (159,162,163,165,166,168,169), so 162 of 169 finish; a player who only trusts D16 finishes far fewer, fewer than 90.
SINGLES = list(range(1, 21)) + [25]
DOUBLES = [2 * n for n in range(1, 21)] + [50]
ALL = sorted(set(SINGLES + [2 * s for s in SINGLES if s != 25] + [3 * n for n in range(1, 21)] + [50]))
def finish(score, darts, doubles):
    if darts == 0: return False
    if score in doubles: return True
    if darts == 1: return False
    for s in ALL:
        r = score - s
        if r >= 2 and finish(r, darts - 1, doubles): return True
    return False
def finishable(darts, doubles): return [x for x in range(2, 171) if finish(x, darts, doubles)]
one = finishable(1, DOUBLES)
two = finishable(2, DOUBLES)
three = finishable(3, DOUBLES)
miss = [x for x in range(2, 171) if x not in three]
d16 = finishable(3, [32])
d16_2 = finishable(3, [32, 16, 8])  # D16 plus its halves D8 and D4 reach via D16 retry
print("1-dart finishes:", len(one))
print("2-dart finishes:", len(two))
print("3-dart finishes:", len(three), "of 169")
print("impossible in 3 darts:", miss)
print("only D16 as the finishing double:", len(d16), "of 169")
print("D16 or D8 or D4:", len(d16_2))
ok = len(one) == 21 and miss == [159, 162, 163, 165, 166, 168, 169] and len(three) == 162
print('prediction D16-only < 90 missed:', not len(d16) < 90, f'(got {len(d16)})')
print("RESULT:", "PASS" if ok else "FAIL",
  f"1-dart {len(one)}, 3-dart {len(three)}/169, impossible {miss}, D16-only {len(d16)}, D16/D8/D4 {len(d16_2)}")
