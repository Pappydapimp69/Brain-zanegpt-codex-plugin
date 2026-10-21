# Curiosity vs felt confidence P (Kang et al. 2009 fitted curve): c(P) = 0.49 - 0.39 P + 4.77 P (1-P).
# Fluency illusion (Carpenter et al. 2013): fluent delivery adds ~0.22 to felt-minus-actual, disfluent ~0.03.
# Assumption under test: the audience's FELT confidence (true seeded knowledge + overconfidence) drives curiosity.
def c(P): P = min(1.0, max(0.0, P)); return 0.49 - 0.39*P + 4.77*P*(1-P)
OVER = {"fluent": 0.22, "disfluent": 0.03}
grid = [i/100 for i in range(0, 101)]
def best_true_seed(style): return max(grid, key=lambda p: c(p + OVER[style]))
for style in OVER:
    b = best_true_seed(style)
    print("%-9s best true seed P=%.2f  curiosity there %.3f" % (style, b, c(b + OVER[style])))
seed = 0.46   # the textbook ~50% seed (formula peak is 0.459)
loss = (c(seed + OVER["disfluent"]) - c(seed + OVER["fluent"])) / c(seed + OVER["disfluent"]) * 100
print("seeding to %.2f: disfluent %.3f vs fluent %.3f (fluent %.1f%% lower)" % (seed, c(seed+OVER["disfluent"]), c(seed+OVER["fluent"]), loss))
# BREAK: at a low seed (0.10) the same overconfidence should HELP
low = (c(0.10 + OVER["fluent"]), c(0.10 + OVER["disfluent"])); print("seed 0.10: fluent %.3f vs disfluent %.3f" % low)
# Curiosity-weighted recall proxy is NOT modeled: actual learning was equal in the source study.
ok = best_true_seed("fluent") < best_true_seed("disfluent") - 0.1 and loss > 10 and low[0] > low[1]
print("RESULT: %s fluent best seed %.2f vs disfluent %.2f; the 0.46 seed costs a fluent teller %.1f%% curiosity, a 0.10 seed gains %.3f" % ("PASS" if ok else "FAIL", best_true_seed("fluent"), best_true_seed("disfluent"), loss, low[0]-low[1]))
