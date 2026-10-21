# Sandbox: after dropping the largest lag from a sparse lag set, is "next configured lag" the new cutoff?
# Prediction: next-lag is ALWAYS right when window is wide (2w-1>=P, every lag valid) and wrong for some narrow windows;
# residue closed form (contiguous window) is right everywhere. Oracle: brute-force tick simulation.
import itertools
P = 9
def valid_bf(w, L):
    return any((t % P) < w and ((t - L) % P) < w for t in range(L, L + 3 * P))
def cut(w, lags):
    v = [L for L in lags if valid_bf(w, L)]
    return max(v) if v else 0
def closed(w, lags):
    v = [L for L in lags if (L % P) <= w - 1 or (L % P) >= P - (w - 1)]
    return max(v) if v else 0
stat = {"wide": [0, 0, 0], "narrow": [0, 0, 0]}  # cases, nextlag wrong, closed wrong
pool = list(range(1, 19))
# all lag sets of size 3 from 1..18 containing 18 (the dropped max) -> deterministic enumeration
for rest in itertools.combinations(range(1, 18), 2):
    full = sorted(rest) + [18]
    dropped = full[:-1]
    for w in range(1, P + 1):
        kind = "wide" if 2 * w - 1 >= P else "narrow"
        truth = cut(w, dropped)
        nextlag = dropped[-1]
        s = stat[kind]; s[0] += 1; s[1] += nextlag != truth; s[2] += closed(w, dropped) != truth
ok = stat["wide"][1] == 0 and stat["narrow"][1] > 0 and stat["wide"][2] == 0 and stat["narrow"][2] == 0
print(stat)
print(f"RESULT: {'PASS' if ok else 'FAIL'} wide cases={stat['wide'][0]} nextlag_wrong={stat['wide'][1]}; narrow cases={stat['narrow'][0]} nextlag_wrong={stat['narrow'][1]}; closed_form_wrong={stat['wide'][2]+stat['narrow'][2]}")
