"""ROTOR-MACHINES/enigma kernel (rotors I II III, reflector B, NO plugboard): the machine is an
involution and never maps a letter to itself; check vector AAAAA -> BDZGO at AAA. Extend:
(1) does the property survive a 10-pair plugboard (the wartime configuration)? (2) how much
does it help a codebreaker place a known plaintext crib? For a crib of length L slid along
a ciphertext, any offset where some crib letter equals the ciphertext letter under it is
impossible. Measure the share of offsets eliminated on real Enigma ciphertext.
PREDICTION (written before running): the vector BDZGO reproduces; with 10 plugboard pairs,
0 self-maps over 20,000 key presses and decrypt(encrypt(x)) == x; crib elimination matches
1 - (25/26)^L within 5 points (about 54% at L 20, 73% at L 33)."""
A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ROT = {"I": ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q"), "II": ("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E"), "III": ("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V")}
REF = "YRUHQSLDPXNGOKMIEBFZCWVJAT"
class Enigma:
    def __init__(self, order=("I", "II", "III"), pos="AAA", plugs=""):
        self.w = [ROT[r][0] for r in order]; self.n = [A.index(ROT[r][1]) for r in order]
        self.p = [A.index(c) for c in pos]
        self.plug = list(range(26))
        for pair in plugs.split():
            a, b = A.index(pair[0]), A.index(pair[1]); self.plug[a], self.plug[b] = b, a
    def step(self):
        p, n = self.p, self.n
        if p[1] == n[1]: p[0] = (p[0] + 1) % 26; p[1] = (p[1] + 1) % 26      # middle double-step
        elif p[2] == n[2]: p[1] = (p[1] + 1) % 26
        p[2] = (p[2] + 1) % 26
    def fwd(self, c, i):
        s = self.p[i]; return (A.index(self.w[i][(c + s) % 26]) - s) % 26
    def bwd(self, c, i):
        s = self.p[i]; return (self.w[i].index(A[(c + s) % 26]) - s) % 26
    def key(self, ch):
        self.step(); c = self.plug[A.index(ch)]
        for i in (2, 1, 0): c = self.fwd(c, i)
        c = A.index(REF[c])
        for i in (0, 1, 2): c = self.bwd(c, i)
        return A[self.plug[c]]
    def enc(self, s): return "".join(self.key(c) for c in s)
vec = Enigma().enc("AAAAA")
PL = "AT BS DE FM IR KN LZ OW PV XY"
class LCG:
    def __init__(self, s): self.s = s
    def r(self, m): self.s = (6364136223846793005 * self.s + 1442695040888963407) % 2 ** 64; return (self.s >> 33) % m
g = LCG(3); plain = "".join(A[g.r(26)] for _ in range(20000))
ct = Enigma(pos="QEV", plugs=PL).enc(plain)
selfmaps = sum(a == b for a, b in zip(plain, ct))
back = Enigma(pos="QEV", plugs=PL).enc(ct) == plain
res = {}
for L in (10, 20, 33):
    crib = plain[5000:5000 + L]                    # a known L-letter fragment (true offset 5000)
    offs = range(0, 19000)
    elim = sum(any(crib[k] == ct[o + k] for k in range(L)) for o in offs)
    res[L] = (elim / len(offs), 1 - (25 / 26) ** L, not any(crib[k] == ct[5000 + k] for k in range(L)))
    print(f"crib length {L}: offsets eliminated {res[L][0]:.1%} (theory {res[L][1]:.1%}); true offset survives: {res[L][2]}")
ok = vec == "BDZGO" and selfmaps == 0 and back and all(abs(a - b) < 0.05 and t for a, b, t in res.values())
print(f"RESULT: {'PASS' if ok else 'FAIL'} vector {vec}; with plugboard 0 self-maps: {selfmaps == 0} ({selfmaps}), round trip: {back}; "
      f"crib elimination L10 {res[10][0]:.0%}, L20 {res[20][0]:.0%}, L33 {res[33][0]:.0%} vs theory {res[10][1]:.0%}/{res[20][1]:.0%}/{res[33][1]:.0%}")
