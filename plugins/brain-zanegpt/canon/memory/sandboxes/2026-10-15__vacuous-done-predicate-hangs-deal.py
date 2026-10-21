"""Sort-puzzle deal: reshuffle until no container is already 'done'. If done() is vacuously true for an empty
container and the deal always includes empty containers, the rejection loop can never accept. Deterministic."""
import random
CAP = 4
done = lambda j: len(j) == 0 or (len(j) == CAP and all(c == j[0] for c in j))
def deal(colors, empty, reject, tries=2000, seed=5):
    r = random.Random(seed); accepted = 0
    for _ in range(tries):
        bag = [c for c in range(colors) for _ in range(CAP)]; r.shuffle(bag)
        st = [bag[i*CAP:(i+1)*CAP] for i in range(colors)] + [[] for _ in range(empty)]
        if not reject(st): accepted += 1
    return accepted
naive = lambda st: any(done(j) for j in st)
fixed = lambda st: any(len(j) and done(j) for j in st)
res = {}
for colors, empty in [(3, 2), (5, 2), (7, 2), (3, 0)]:
    res[(colors, empty)] = (deal(colors, empty, naive), deal(colors, empty, fixed))
    print(f"{colors} colours + {empty} empty jars: naive accepts {res[(colors, empty)][0]}/2000, non-empty-only accepts {res[(colors, empty)][1]}/2000")
ok = all(res[k][0] == 0 and res[k][1] > 1500 for k in [(3, 2), (5, 2), (7, 2)]) and res[(3, 0)][0] == res[(3, 0)][1]
print("RESULT: PASS a vacuously-true done() on empty jars rejects every deal (infinite loop); excluding empties accepts most; with 0 empties both agree (BREAK case shows the bug only appears with empties)" if ok else "RESULT: FAIL")
