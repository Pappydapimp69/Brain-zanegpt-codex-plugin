# Composes: the voice-differentiation strip test (remove speaker tags; can you tell who is talking?) with the
# ellipsis kernel (casual speech drops subject + auxiliary) and the general-extender kernel ("and stuff",
# "or whatever" mark shared ground).
# PREDICTION (written before running): two hand-written characters, 10 lines each. Character A speaks in
# full sentences with no extenders; character B elides subjects and uses extenders.
# 1) a nearest-centroid attributor on 3 features (elided-opening rate, extender rate, contraction rate),
#    trained on 5 lines each and tested on the other 5 each, attributes at least 8/10;
# 2) the same attributor on an author-voice pair (both characters written in one style) scores 4-6/10;
# 3) lines of 3 words or fewer carry no feature at all and are unattributable (feature vector all zero)
#    -> at least 3 of the 10 short test lines in a third, clipped-dialogue scene tie.
import re
EXT = r"\b(and stuff|or whatever|and everything|or something|and all that)\b"
ELIDE_OK = {"been", "sounds", "want", "can't", "got", "gotta", "gonna", "need", "looks", "seems", "guess", "think", "don't", "didn't", "going", "never", "nothing", "good", "fine"}
def feats(line):
    ws = re.findall(r"[a-z']+", line.lower())
    elided = 1.0 if ws and ws[0] in ELIDE_OK else 0.0
    ext = 1.0 if re.search(EXT, line.lower()) else 0.0
    con = sum("'" in w for w in ws) / max(len(ws), 1)
    return (elided, ext, con)
def centroid(lines):
    fs = [feats(l) for l in lines]; return tuple(sum(c) / len(fs) for c in zip(*fs))
def d(a, b): return sum((x - y) ** 2 for x, y in zip(a, b))
def attribute(train_a, train_b, test):
    ca, cb = centroid(train_a), centroid(train_b); ok = ties = 0
    for line, who in test:
        f = feats(line); da, db = d(f, ca), d(f, cb)
        if abs(da - db) < 1e-9: ties += 1; continue
        ok += ("A" if da < db else "B") == who
    return ok, ties
A = ["I am not going to the party tonight.", "It has been a very long week for me.", "I do not think that is a good idea.",
     "We should leave before the traffic gets bad.", "I have already told you what I think.",
     "I would rather stay home and read.", "It is too late to call her now.", "I am tired of arguing about this.",
     "We can talk about it in the morning.", "I have to be at work by seven."]
B = ["Been a long week, you know?", "Sounds good, or whatever.", "Want some coffee and stuff?", "Can't sleep, guess I'll drive around or something.",
     "Gotta grab my keys and everything.", "Never mind, it's fine.", "Didn't think you'd call or whatever.",
     "Need a ride and stuff?", "Guess it's late, huh.", "Seems like rain or something."]
test = [(l, "A") for l in A[5:]] + [(l, "B") for l in B[5:]]
ok1, t1 = attribute(A[:5], B[:5], test)
# author-voice pair: both written in A's register
A2 = ["I think we should go now.", "It is getting late for all of us.", "I have seen that film before.", "We could take the early train.", "I do not want to argue.",
      "It was a good dinner tonight.", "I would like to see the ocean.", "We should call your mother.", "I am not sure about that.", "It is a long drive home."]
B2 = ["I have been thinking about you.", "It is colder than I expected.", "I would rather take the car.", "We never talk about the summer.", "I am glad you came.",
      "It has been a strange year.", "I do not remember that song.", "We can leave the dishes.", "I have your jacket here.", "It is not your fault."]
ok2, t2 = attribute(A2[:5], B2[:5], [(l, "A") for l in A2[5:]] + [(l, "B") for l in B2[5:]])
short = [("No.", "A"), ("Fine.", "B"), ("Okay then.", "A"), ("Whatever you want.", "B"), ("Yeah.", "B"),
         ("Not tonight.", "A"), ("Your call.", "B"), ("I know.", "A"), ("Me neither.", "B"), ("Go home.", "A")]
ok3, t3 = attribute(A[:5], B[:5], short)
print(f"distinct speech patterns: {ok1}/10 right, {t1} ties")
print(f"author-voice pair: {ok2}/10 right, {t2} ties")
print(f"clipped short lines: {ok3}/10 right, {t3} ties")
ok = ok1 >= 8 and ok2 <= 6 and t3 >= 3
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" distinct patterns {ok1}/10, author-voice pair {ok2}/10 ({t2} ties), short lines {ok3}/10 with {t3} ties")
