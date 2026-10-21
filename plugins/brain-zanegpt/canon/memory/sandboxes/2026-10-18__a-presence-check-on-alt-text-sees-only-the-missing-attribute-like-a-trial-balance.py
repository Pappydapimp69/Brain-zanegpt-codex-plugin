# Composes ideas:ERROR-CORRECTION/single-error-correcting-code-miscorrects-double-errors (a parity-type check sees only
# errors that change the parity; one more check turns silent corruption into a detected failure),
# trial-balance-sees-only-the-unbalanced-error (a balanced book hides omissions, wrong-account postings and cancelling
# pairs) and ideas:ACCESSIBILITY/images/alt-text/empty-alt-is-not-the-same-as-no-alt (decorative images need alt="",
# a missing attribute can be announced as the file name).
# Model: 20 images, 12 meaningful (each has a known subject phrase) and 8 decorative. Alt errors injected one class at a
# time: MISSING (no attribute), FILENAME (alt is the file name), SWAP (two meaningful images exchange alts), EMPTY-ON-
# MEANING (alt="" on a meaningful image), WRONG-WORDS (a plausible alt about another subject), and the correct
# decorative alt="". Checks: P presence (attribute exists), N non-empty, F non-empty and not a file name, W F plus
# the alt shares a subject word with the image's known subject (the account-check-digit analogue).
# PREDICTION (before run): P detects only MISSING (8 of 8 decorative + 12 of 12 meaningful = 20/20) and 0 of FILENAME,
# SWAP, EMPTY, WRONG; N catches MISSING and EMPTY but false-flags all 8 correct decorative empties; F adds FILENAME;
# W catches 12 of 12 SWAPs unless the swapped pair shares a subject word (BREAK: 1 sibling pair sharing "dog" is
# missed, so W detects 10 of 12) and still passes WRONG-WORDS that reuse the image's own subject word.
import itertools
SUBJ = ["red dog", "blue boat", "dog park", "old bridge", "city map", "green tea", "paper crane", "night sky",
        "tall tower", "river bend", "wooden door", "snow field"]
IMG = [dict(id=i, kind="meaning", subj=s, file=f"IMG_{4800+i}.jpg") for i, s in enumerate(SUBJ)] + \
      [dict(id=12 + j, kind="deco", subj="", file=f"IMG_{4900+j}.jpg") for j in range(8)]
def correct(im): return im["subj"] if im["kind"] == "meaning" else ""
def P(alt, im): return alt is not None
def N(alt, im): return bool(alt)
def F(alt, im): return bool(alt) and not alt.upper().startswith("IMG_")
def W(alt, im):
    if im["kind"] == "deco": return alt == ""
    return F(alt, im) and bool(set(alt.split()) & set(im["subj"].split()))
CHECKS = dict(P=P, N=N, F=F, W=W)
def count(select, make):
    """errors detected = checks that FLAG (return False) the injected alt; select = images that get an error."""
    det = {k: 0 for k in CHECKS}; tot = 0
    for im in select:
        alt = make(im); tot += 1
        for k, chk in CHECKS.items():
            if not chk(alt, im): det[k] += 1
    return det, tot
MEAN = [im for im in IMG if im["kind"] == "meaning"]; DECO = [im for im in IMG if im["kind"] == "deco"]
rows = {}
rows["MISSING"] = count(IMG, lambda im: None)
rows["FILENAME"] = count(IMG, lambda im: im["file"])
rows["EMPTY-ON-MEANING"] = count(MEAN, lambda im: "")
# WRONG-WORDS (run 2): keeps the image's own first word but describes another subject, e.g. "red tower"; run 1 used a
# phrase with no shared word, which W flagged 12/12, so the prediction about reused words was not what run 1 built.
rows["WRONG-WORDS"] = count(MEAN, lambda im: im["subj"].split()[0] + " " + SUBJ[(im["id"] + 5) % 12].split()[1])
# SWAP: image i gets the alt of image (i+1) mod 12 (a cyclic exchange); the dog pair (ids 0 and 2) is not adjacent so
# also run the sibling swap 0 <-> 2 which shares the word "dog".
rows["SWAP"] = count(MEAN, lambda im: SUBJ[(im["id"] + 1) % 12])
rows["SWAP-SIBLINGS"] = count([MEAN[0], MEAN[2]], lambda im: SUBJ[2] if im["id"] == 0 else SUBJ[0])
rows["CORRECT-DECO(false flags)"] = count(DECO, lambda im: "")
for k, (d, t) in rows.items(): print(f"{k:26s} of {t:2d}: " + " ".join(f"{c} {d[c]:2d}" for c in CHECKS))
m, e, s, sib, fl = rows["MISSING"][0], rows["EMPTY-ON-MEANING"][0], rows["SWAP"][0], rows["SWAP-SIBLINGS"][0], rows["CORRECT-DECO(false flags)"][0]
wrong_pass = rows["WRONG-WORDS"][0]["W"]
ok = (m["P"] == 20 and rows["FILENAME"][0]["P"] == 0 and s["P"] == 0 and fl["N"] == 8 and rows["FILENAME"][0]["F"] == 20
      and s["W"] == 12 and sib["W"] == 0 and wrong_pass < 12)
print(f"RESULT: {'PASS' if ok else 'FAIL'} presence check flags missing {m['P']}/20, filename {rows['FILENAME'][0]['P']}/20, swaps {s['P']}/12; "
      f"non-empty check false-flags {fl['N']}/8 correct decorative empties; word-overlap check flags swaps {s['W']}/12 but sibling swaps {sib['W']}/2 and wrong-words {wrong_pass}/12")
