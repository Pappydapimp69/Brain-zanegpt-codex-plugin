"""Check the braille letter table that brainwork/E169 and the BRAILLE decade-shift
kernel typed from memory (and the digit/number-sign/letter-sign assumptions of
braille-digits-reuse-a-to-j/E1) against a published source: liblouis tables
latinLetterDef6Dots.uti, digits6Dots.uti and en-ueb-g1.ctb (liblouis master,
fetched 2026-10-15). Reads the table files from the directory in argv[1] if given;
otherwise uses the values below, transcribed verbatim from those files.
PREDICTION (written before running): all 26 letters equal the kernel's generated
cells (ten base cells, +dot 3, +dots 3,6, w = 2456, French order); digits 1-9,0 equal
a-j; number sign 3456; the sign that ends numeric mode is 56."""
import os, re, sys
TRANSCRIBED = {"letters": dict(zip("abcdefghijklmnopqrstuvwxyz",
    "1 12 14 145 15 124 1245 125 24 245 13 123 134 1345 135 1234 12345 1235 234 2345 136 1236 2456 1346 13456 1356".split())),
    "digits": dict(zip("0123456789", "245 1 12 14 145 15 124 1245 125 24".split())), "numsign": "3456", "nonumsign": "56"}
def load(d):
    t = {"letters": {}, "digits": {}}
    for line in open(os.path.join(d, "latinLetterDef6Dots.uti")):
        m = re.match(r"\s*lowercase\s+([a-z])\s+(\d+)", line)
        if m: t["letters"][m.group(1)] = m.group(2)
    for line in open(os.path.join(d, "digits6Dots.uti")):
        m = re.match(r"\s*digit\s+(\d)\s+(\d+)", line)
        if m: t["digits"][m.group(1)] = m.group(2)
    g1 = open(os.path.join(d, "en-ueb-g1.ctb")).read()
    t["numsign"] = re.search(r"^numsign\s+(\d+)", g1, re.M).group(1)
    t["nonumsign"] = re.search(r"^nonumsign\s+(\d+)", g1, re.M).group(1)
    return t
src = load(sys.argv[1]) if len(sys.argv) > 1 else TRANSCRIBED
print("source:", "liblouis files in " + sys.argv[1] if len(sys.argv) > 1 else "transcribed values")
BASE = ["1", "12", "14", "145", "15", "124", "1245", "125", "24", "245"]
FRENCH = "abcdefghij" "klmnopqrst" "uvxyz"
norm = lambda s: "".join(sorted(s))
gen = {}
for i, ch in enumerate(FRENCH):
    b = BASE[i % 10]
    gen[ch] = norm(b if i < 10 else b + "3" if i < 20 else b + "36")
gen["w"] = "2456"
letter_mism = [c for c in gen if norm(src["letters"][c]) != gen[c]]
naive = {}
for i, ch in enumerate("abcdefghijklmnopqrstuvwxyz"):          # 26-letter English order, no w exception
    b = BASE[i % 10]
    naive[ch] = norm(b if i < 10 else b + "3" if i < 20 else b + "36")
naive_mism = [c for c in naive if norm(src["letters"][c]) != naive[c]]
digit_ok = all(norm(src["digits"][d]) == gen["abcdefghij"[(int(d) - 1) % 10]] for d in "1234567890")
print(f"letters: kernel rule mismatches {letter_mism or 'none'}; naive English-order rule mismatches {naive_mism}")
print(f"digits equal a-j cells: {digit_ok}; numsign {src['numsign']}; numeric-mode terminator {src['nonumsign']}")
ok = not letter_mism and naive_mism == list("wxyz") and digit_ok and src["numsign"] == "3456" and src["nonumsign"] == "56"
print(f"RESULT: {'PASS' if ok else 'FAIL'} published liblouis table: 26/26 letters match the decade rule in French order "
      f"(naive order misses {''.join(naive_mism)}); digits = a-j; numsign {src['numsign']}; terminator {src['nonumsign']}")
