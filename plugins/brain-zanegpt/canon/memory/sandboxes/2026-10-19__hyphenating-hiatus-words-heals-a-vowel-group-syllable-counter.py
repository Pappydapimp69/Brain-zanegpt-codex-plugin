"""Does hyphenating words at their true syllable breaks change what a vowel-group syllable
counter (with silent-e rule) reports, and does it re-arm a 'budget 9 + slack 3' warning?
Own fixture, stdlib only, deterministic."""
import re

# word -> hyphenated true-syllable spelling
FIX = [
    "fi-er", "ho-ur", "po-em", "qui-et", "i-de-a", "ra-di-o", "li-on", "cru-el", "di-et", "ri-ot",
    "ta-ble", "ap-ple", "lit-tle", "peo-ple", "ma-ny", "ha-ppy", "sun-light", "be-fore", "to-night", "sil-ver",
    "love", "make", "time", "day", "light", "dream", "fire-fly", "storm", "moon", "heart",
]
TRUE = {w.replace("-", ""): w.count("-") + 1 for w in FIX}
# 'fire','hour' style one-syllable spellings are excluded on purpose: the fixture holds 2-syllable readings

def count(token):
    t = token.lower()
    g = len(re.findall(r"[aeiouy]+", t))
    if t.endswith("e") and not t.endswith("le") and g > 1:
        g -= 1
    return max(g, 1) if t else 0

def counter_plain(w):  return count(w.replace("-", ""))
def counter_hyph(w):   return sum(count(seg) for seg in w.split("-"))

plain_err = [w for w in FIX if counter_plain(w) != TRUE[w.replace("-", "")]]
hyph_err = [w for w in FIX if counter_hyph(w) != TRUE[w.replace("-", "")]]
fixed = [w for w in plain_err if w not in hyph_err]
broken = [w for w in FIX if w not in plain_err and w in hyph_err]
print("plain counter wrong:", len(plain_err), plain_err)
print("hyphenated counter wrong:", len(hyph_err), hyph_err)
print("healed by hyphenation:", len(fixed), "newly broken:", len(broken), broken)

# BREAK: hyphens at the wrong place (middle letter) instead of the true boundary
def mid_split(w):
    flat = w.replace("-", "")
    return flat[:len(flat) // 2] + "-" + flat[len(flat) // 2:]
wrong_split_err = [w for w in FIX if sum(count(x) for x in mid_split(w).split("-")) != TRUE[w.replace("-", "")]]
print("wrong-place hyphens: counter wrong on", len(wrong_split_err), "of 30")

# Warning: fires when counted syllables > BUDGET + SLACK
BUDGET, SLACK = 9, 3
hiatus = [w for w in FIX if w in ("fi-er", "po-em", "qui-et", "i-de-a", "ra-di-o", "li-on", "cru-el", "di-et", "ri-ot", "ho-ur")]
fill = ["sun-light", "be-fore", "sil-ver"]
fire_plain = fire_hyph = total = 0
for a in hiatus:
    for b in hiatus:
        line = [a, b] + fill + ["day", "light"]                   # 2 hiatus + 3 fill + 2 mono
        true_syl = sum(TRUE[w.replace("-", "")] for w in line)
        if true_syl <= BUDGET + SLACK:
            continue
        total += 1
        fire_plain += sum(counter_plain(w) for w in line) > BUDGET + SLACK
        fire_hyph += sum(counter_hyph(w) for w in line) > BUDGET + SLACK
print(f"lines truly over budget+slack: {total}; warning fires plain {fire_plain}, hyphenated {fire_hyph}")
ok = len(fixed) >= 8 and len(broken) <= 2 and fire_hyph > fire_plain
print(f"RESULT: {'PASS' if ok else 'FAIL'} plain counter wrong on {len(plain_err)}/30 words, hyphenated on {len(hyph_err)}/30 "
      f"(healed {len(fixed)}, newly broken {len(broken)}), wrong-place hyphens wrong on {len(wrong_split_err)}/30; crowded-line warning fired {fire_plain}/{total} plain vs {fire_hyph}/{total} hyphenated")
