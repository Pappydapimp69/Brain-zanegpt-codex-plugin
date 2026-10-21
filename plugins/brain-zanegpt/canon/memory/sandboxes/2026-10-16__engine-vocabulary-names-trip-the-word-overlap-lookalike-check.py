# Names for an engine-first batch borrow words from the engine's theme; word-overlap against real titles then
# flags clean names. Compare with syllable-invented names. Real titles are public mobile-game names.
import random
REAL = ["Homescapes","Gardenscapes","Royal Match","Candy Crush","Clash of Clans","Hay Day","Toon Blast","Lords Mobile",
 "Last War","Whiteout Survival","State of Survival","Puzzles and Survival","Rise of Kingdoms","Merge Mansion",
 "Township","Fishdom","Coin Master"]
STOP = {"of","and","the"}
rw = {w.lower() for t in REAL for w in t.split()} - STOP
ENG = {  # engine -> theme words a writer would reach for
 "deadpan": ["royal","last","kingdom","match"], "escalation": ["war","survival","clash","rise"],
 "bait-switch": ["puzzle","merge","candy","coin"], "wrong-hero": ["lords","hay","garden","home"],
 "anti-climax": ["blast","day","fish","town"], "literalism": ["match","royal","master","coin"],
 "rule-of-three": ["survival","mobile","war","clash"], "callback": ["home","garden","scapes","mansion"]}
SYL = ["ba","ko","mi","ru","ta","ne","so","li","pu","ze"]
def vocab_name(rng, e): return " ".join(rng.sample(ENG[e], 2)).title()
def syl_name(rng): return "".join(rng.choice(SYL) for _ in range(3)).title()
def flagged(n): return any(w.lower() in rw for w in n.split())
rng = random.Random(3); N = 4000
engs = list(ENG)
v = sum(flagged(vocab_name(rng, rng.choice(engs))) for _ in range(N))/N
s = sum(flagged(syl_name(rng)) for _ in range(N))/N
# break scenario: vocabulary names but the writer is told to avoid real-title words
safe = {e: [w for w in ws if w not in rw] for e, ws in ENG.items()}
sf = sum(flagged(" ".join(rng.sample(safe[e], min(2, len(safe[e]))) or ["x"])) for e in [rng.choice(engs) for _ in range(N)])/N
print("engine-vocabulary names flagged %.3f; syllable names flagged %.3f; vocabulary minus real-title words flagged %.3f" % (v, s, sf))
print("real-title word list size %d; engines with every theme word in it: %d of 8" % (len(rw), sum(all(w in rw for w in ws) for ws in ENG.values())))
print("RESULT: %s word-overlap flags %.0f%% of engine-vocabulary names vs %.0f%% of syllable names; stripping real-title words from the engine vocabularies drops it to %.0f%%" % (
    "PASS" if v > .5 and s == 0 and sf == 0 else "FAIL", 100*v, 100*s, 100*sf))
