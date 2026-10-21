# Ten-pin bowling rules (USBC): a strike scores 10 + next two balls, a spare 10 + next ball, 10th frame earns
# 1 fill ball after a spare and 2 after a strike, fill balls count only as bonus. Perfect game = 12 strikes = 300.
# Compare a correct scorer against a naive 'every frame looks ahead two balls and the loop runs over all rolls' scorer.
def good(r):
    s = i = 0
    for f in range(10):
        if r[i] == 10: s += 10 + r[i+1] + r[i+2]; i += 1
        elif r[i] + r[i+1] == 10: s += 10 + r[i+2]; i += 2
        else: s += r[i] + r[i+1]; i += 2
    return s
def naive(r):  # treats the fill balls as frames 11 and 12
    s = i = 0
    while i < len(r):
        if r[i] == 10: s += 10 + sum(r[i+1:i+3]); i += 1
        elif i+1 < len(r) and r[i] + r[i+1] == 10: s += 10 + sum(r[i+2:i+3]); i += 2
        else: s += sum(r[i:i+2]); i += 2
    return s
cases = {
 "perfect game 12 strikes": ([10]*12, 300),
 "all fives 21 balls (spares)": ([5]*21, 150),
 "gutter game": ([0]*20, 0),
 "all nines no mark": ([9, 0]*10, 90),
 "tenth frame strike then 7 3": ([0, 0]*9 + [10, 7, 3], 20),
 "tenth frame spare then 10": ([0, 0]*9 + [4, 6, 10], 20),
 "official example 10 frames mixed": ([10, 7, 3, 9, 0, 10, 0, 8, 8, 2, 0, 6, 10, 10, 10, 8, 1], 167),
}
bad_good = bad_naive = 0
for k, (r, want) in cases.items():
    g, n = good(r), naive(r); bad_good += g != want; bad_naive += n != want
    print("%-34s want %3d good %3d naive %3d" % (k, want, g, n))
print("RESULT: %s correct scorer wrong on %d of %d known games; naive wrong on %d (perfect game naive %d vs 300)" % (
    "PASS" if bad_good == 0 and bad_naive > 0 else "FAIL", bad_good, len(cases), bad_naive, naive([10]*12)))
