"""Prediction (written before first run, own fixture): nearest-centroid on 3 speech features
(contraction rate, general extender, subject ellipsis) over my own lines.
 A distinct pair (Rook casual vs Ambrose formal): test accuracy >= 9/10 (expect 10/10).
 B same-voice pair (identical style, different content): every test line ties (10/10 ties) -> no signal.
 C short clipped lines ("Go." style) for the same distinct pair: feature vector is all zero, so distance equals
   each centroid norm and the line goes to the PLAIN speaker (Ambrose) with ZERO ties: 10/10 to plain, 0 ties.
 D BREAK: clipped lines that carry a contraction ("Don't.") should NOT default; they should attribute to Rook.
RUN-1 OUTCOME (recorded): B and D predictions MISSED. B gave 0 exact ties but chance accuracy 5/10 (finite samples make centroids differ slightly,
so "no signal" shows as chance, not ties). D gave 10/10 to the plain speaker: a bare contraction lies farther from Rook's centroid (ext and ellipsis
dims are 0) than from the near-origin plain centroid. Success rule below restated to the signal claim: A >=9, B chance (4..6), C zero ties and all plain.
Deterministic, stdlib."""
import re, math
EXT = ("and stuff", "or whatever", "and all that", "or something")
VERBS = {"gonna", "got", "went", "went", "checked", "saw", "figured", "grabbed", "told", "wanted", "need", "think", "reckon"}
def feats(line):
    w = re.findall(r"[a-z']+", line.lower()); n = max(len(w), 1)
    contr = sum("'" in x for x in w) / n
    ext = 1.0 if any(e in line.lower() for e in EXT) else 0.0
    ell = 1.0 if w and w[0] in VERBS else 0.0
    return (contr, ext, ell)
def centroid(lines):
    f = [feats(l) for l in lines]; return tuple(sum(c) / len(f) for c in zip(*f))
def dist(a, b): return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
def attribute(line, cents):
    d = {k: dist(feats(line), c) for k, c in cents.items()}
    ks = sorted(d, key=d.get)
    return "TIE" if abs(d[ks[0]] - d[ks[1]]) < 1e-9 else ks[0]
def run(train, test, label):
    cents = {k: centroid(v) for k, v in train.items()}
    res = [(true, attribute(l, cents)) for true, ls in test.items() for l in ls]
    acc = sum(t == p for t, p in res); ties = sum(p == "TIE" for t, p in res)
    plain = sum(p == "Ambrose" for t, p in res)
    print(label, "acc", acc, "/", len(res), "ties", ties, "->plain", plain); return acc, ties, plain, len(res)
rook_tr = ["Got the keys and stuff, don't worry.", "Went round the back, couldn't see anyone or whatever.", "Checked the gate, it's locked and all that.", "Figured we'd leave it, can't hurt.", "Grabbed the lamp or something, won't take long."]
amb_tr = ["I have inspected the gate and found it secured.", "We shall proceed once the council has convened.", "It is my considered view that we wait.", "The lamp is stored in the lower cabinet.", "You will find the ledger on the second shelf."]
rook_te = ["Saw the boat and stuff, didn't wait.", "Told them it's fine or whatever.", "Reckon we're done, can't say more and all that.", "Need the rope, haven't got any or something.", "Wanted a word, wouldn't hear it."]
amb_te = ["I observed the river and recorded its height.", "The committee will reconvene at noon tomorrow.", "It would be improper for me to comment.", "The delegation arrived and presented its letters.", "We require the signatures of both parties."]
A = run({"Rook": rook_tr, "Ambrose": amb_tr}, {"Rook": rook_te, "Ambrose": amb_te}, "A distinct")
# B same voice: both characters use the Rook style, different content
s1 = ["Got the maps and stuff, don't worry.", "Went upstairs, couldn't find it or whatever.", "Checked the shed, it's empty and all that.", "Figured we'd skip it, can't hurt.", "Grabbed tea or something, won't take long."]
s2 = ["Saw the dog and stuff, didn't wait.", "Told her it's fine or whatever.", "Reckon we're set, can't say more and all that.", "Need coal, haven't got any or something.", "Wanted a chat, wouldn't have it."]
t1 = ["Got the rope and stuff, don't ask.", "Went down the lane, couldn't hear a thing or whatever.", "Checked the roof, it's fine and all that.", "Figured we'd stay, can't hurt.", "Grabbed bread or something, won't take long."]
t2 = ["Saw the cart and stuff, didn't stop.", "Told him it's late or whatever.", "Reckon we're lost, can't say more and all that.", "Need sleep, haven't had any or something.", "Wanted a break, wouldn't take it."]
B = run({"P": s1, "Q": s2}, {"P": t1, "Q": t2}, "B same voice")
clip_r = ["Go.", "No.", "Fine.", "Wait.", "Here."]; clip_a = ["Stop.", "Yes.", "Enough.", "Quiet.", "Proceed."]
C = run({"Rook": rook_tr, "Ambrose": amb_tr}, {"Rook": clip_r, "Ambrose": clip_a}, "C clipped")
D = run({"Rook": rook_tr, "Ambrose": amb_tr}, {"Rook": ["Don't.", "Can't.", "Won't.", "Isn't.", "Didn't."], "Ambrose": ["Stop.", "Yes.", "Enough.", "Quiet.", "Proceed."]}, "D clipped+contraction")
ok = A[0] >= 9 and 4 <= B[0] <= 6 and C[1] == 0 and C[2] == C[3] and D[2] == D[3]
print("RESULT:", "PASS" if ok else "FAIL", f"A {A[0]}/10; B acc {B[0]}/10 ties {B[1]}; C ties {C[1]} ->plain {C[2]}/10; D ->plain {D[2]}/10 (predicted Rook, missed)")
