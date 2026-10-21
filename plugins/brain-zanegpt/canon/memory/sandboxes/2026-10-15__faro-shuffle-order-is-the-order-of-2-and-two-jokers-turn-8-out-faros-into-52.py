"""Sandbox: perfect faro (riffle) shuffles. Deterministic, stdlib only.
Out-faro keeps the top card on top; in-faro moves it to second."""
def faro(deck, out=True):
    h = len(deck) // 2; a, b = deck[:h], deck[h:]
    first, second = (a, b) if out else (b, a)
    return [c for pair in zip(first, second) for c in pair]

def order(n, out=True):
    start = list(range(n)); d = faro(start, out); k = 1
    while d != start: d = faro(d, out); k += 1
    return k

def ord2(m):  # multiplicative order of 2 mod m
    k, x = 1, 2 % m
    while x != 1: x = x * 2 % m; k += 1
    return k

ok = True
# S1: 52-card deck
o52, i52 = order(52, True), order(52, False)
print(f"S1 52 cards: out-faros to restore={o52} in-faros={i52}")
ok &= (o52, i52) == (8, 52)
# S2: rule check over even sizes 4..80: out = ord2(n-1), in = ord2(n+1)
mism = [n for n in range(4, 82, 2) if order(n, True) != ord2(n - 1) or order(n, False) != ord2(n + 1)]
print(f"S2 order-of-2 rule mismatches over n=4..80 even: {mism}")
ok &= mism == []
# S3 (BREAK the '8 shuffles' habit): add two jokers -> 54 cards
o54 = order(54, True); o50 = order(50, True)
print(f"S3 out-faros to restore: 50 cards={o50} 52={o52} 54={o54}")
ok &= o54 == 52 and o50 == 21
# S4: Elmsley control - move top card (position 0) to position p with the binary of p:
# 1 = in-faro, 0 = out-faro, most significant bit first
def send_top_to(p, n=52):
    d = list(range(n))
    for bit in bin(p)[2:] if p else "":
        d = faro(d, out=(bit == "0"))
    return d.index(0)
fails = [p for p in range(52) if send_top_to(p) != p]
seq = bin(13)[2:].replace("1", "I").replace("0", "O")
print(f"S4 binary in/out control: positions 0..51 reached exactly, failures={fails}; position 13 = {seq}")
ok &= fails == []
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" 52 cards restore after {o52} out-faros vs {i52} in-faros; out = ord of 2 mod n-1 and in = ord of 2 mod n+1 for all even n 4..80;"
      f" two jokers (54) need {o54} out-faros; binary I/O control places the top card at all 52 positions")
