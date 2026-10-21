"""Gap pass for ideas:LEGAL/copyright/ai-and-copyright/pure-ai-output-cant-be-copyrighted-training-data-fair-use-is-still-unsettled
with ideas:LEGAL/copyright/fair-use/fair-use-has-no-safe-duration-or-credit-line-only-a-case-by-case-test.
A rule MODEL, not legal advice. Deterministic, stdlib only.
Part A  per-element claim (US Copyright Office 2023 guidance as quoted in the kernel) vs two whole-work binary rules.
Part B  Q1 (copyrightability) and Q2 (training fair use) answered independently vs a conflating tool.
Part C  push 1: jurisdiction. UK CDPA s.9(3) computer-generated works (from memory, unverified here).
Part D  push 2: training rulings recorded from memory (unverified): three US district decisions, all
        copying whole works; does any amount-only bright line fit them?
"""
from itertools import product

KINDS = ('human', 'ai', 'ai_edited')   # ai_edited = AI material with human creative modification

def kernel_claim(elems, human_arranged):
    """Return the set of claimable components under the kernel's US rule."""
    claim = set()
    for i, k in enumerate(elems):
        if k == 'human':
            claim.add(f'e{i}')
        elif k == 'ai_edited':
            claim.add(f'e{i}:edits')          # only the human modifications, not the AI base
    if human_arranged and len(elems) >= 2:
        claim.add('selection_arrangement')
    return claim

def binary_taint(elems, human_arranged):    # "any AI material -> not registrable"
    return set() if any(k != 'human' for k in elems) else {f'e{i}' for i in range(len(elems))} | ({'selection_arrangement'} if human_arranged else set())

def binary_any_human(elems, human_arranged):  # "any human involvement -> whole work protected"
    involved = human_arranged or any(k != 'ai' for k in elems)
    return {f'e{i}' for i in range(len(elems))} | {'selection_arrangement'} if involved else set()

works = [(e, arr) for e in product(KINDS, repeat=4) for arr in (False, True)]
stats = dict(n=len(works), registrable=0, taint_wrong=0, taint_denies_registrable=0,
             anyhuman_wrong=0, anyhuman_overclaims_ai=0, pure_ai=0, pure_ai_registrable=0,
             all_ai_but_arranged_registrable=0)
for elems, arr in works:
    k = kernel_claim(elems, arr)
    t, h = binary_taint(elems, arr), binary_any_human(elems, arr)
    stats['registrable'] += bool(k)
    stats['taint_wrong'] += t != k
    stats['taint_denies_registrable'] += bool(k) and not t
    stats['anyhuman_wrong'] += h != k
    stats['anyhuman_overclaims_ai'] += any(f'e{i}' in h and elems[i] != 'human' for i in range(4))
    if all(x == 'ai' for x in elems):
        stats['pure_ai'] += 1
        stats['pure_ai_registrable'] += bool(k) and not arr
        stats['all_ai_but_arranged_registrable'] += bool(k) and arr
print("Part A:", stats)

# Part B: two questions. Kernel: Q2 is 'unsettled' whatever the output facts are.
def kernel_q2(output_registrable, trained_on_copyrighted): return 'unsettled' if trained_on_copyrighted else 'no question'
def conflating_q2(output_registrable, trained_on_copyrighted):
    if not trained_on_copyrighted: return 'no question'
    return 'lawful' if not output_registrable else 'infringing'   # "output is not anyone's work, so training was fine"
patterns = list(product((False, True), (False, True)))
definite_kernel = sum(kernel_q2(*p) in ('lawful', 'infringing') for p in patterns)
definite_conf = sum(conflating_q2(*p) in ('lawful', 'infringing') for p in patterns)
q2_depends_on_q1_kernel = len({kernel_q2(r, True) for r in (False, True)}) > 1
q2_depends_on_q1_conf = len({conflating_q2(r, True) for r in (False, True)}) > 1
print(f"Part B: definite training answers kernel {definite_kernel}/4, conflating tool {definite_conf}/4; "
      f"Q2 varies with Q1: kernel {q2_depends_on_q1_kernel}, conflating {q2_depends_on_q1_conf}")

# Part C: jurisdiction push (UK CDPA 1988 s.9(3) and s.12(7): author of a computer-generated work is the person
# who made the arrangements; 50-year term. From memory, not fetched in this pass.)
def q1_by_jurisdiction(elems, arr, jur):
    if jur == 'US':
        return bool(kernel_claim(elems, arr))
    if jur == 'UK':
        return True   # computer-generated works protected, author = arranger (model of s.9(3))
pure = ('ai',) * 4
c_us, c_uk = q1_by_jurisdiction(pure, False, 'US'), q1_by_jurisdiction(pure, False, 'UK')
print(f"Part C: pure AI output protectable? US {c_us}, UK {c_uk}")

# Part D: training rulings, from memory (unverified): case, court level, amount copied, commercial, outcome
RULINGS = [
    ('Thomson Reuters v. Ross (non-generative)', 'district', 1.0, True, 'not fair use'),
    ('Bartz v. Anthropic (lawfully bought books)', 'district', 1.0, True, 'fair use'),
    ('Kadrey v. Meta', 'district', 1.0, True, 'fair use'),
]
fits = {}
for threshold in (0.1, 0.3, 0.5, 1.01):
    pred = ['fair use' if amt < threshold else 'not fair use' for _, _, amt, _, _ in RULINGS]
    fits[threshold] = sum(p == r[4] for p, r in zip(pred, RULINGS))
best_amount_fit = max(fits.values())
same_amount_split = len({r[2] for r in RULINGS}) == 1 and len({r[4] for r in RULINGS}) > 1
appellate = sum(r[1] != 'district' for r in RULINGS)
print(f"Part D: amount-only bright line best fit {best_amount_fit}/3 {fits}; identical amount and commercial status, "
      f"outcomes split {same_amount_split}; appellate rulings recorded {appellate}")

ok = (stats['taint_denies_registrable'] > 0 and stats['anyhuman_overclaims_ai'] > 0
      and stats['pure_ai_registrable'] == 0 and stats['all_ai_but_arranged_registrable'] == 1
      and definite_kernel == 0 and definite_conf == 2 and not q2_depends_on_q1_kernel
      and c_us is False and c_uk is True and best_amount_fit == 2 and same_amount_split and appellate == 0)
print(f"RESULT: {'PASS' if ok else 'FAIL'} US per-element rule: {stats['registrable']}/{stats['n']} works registrable, "
      f"taint rule denies {stats['taint_denies_registrable']}, any-human rule overclaims AI elements in {stats['anyhuman_overclaims_ai']}; "
      f"pure AI 0 except human-arranged; conflating tool answers training {definite_conf}/4 definitely vs kernel 0; "
      f"claim stops holding in UK model (pure AI protectable) and 'unsettled' means split district rulings (amount-only fit {best_amount_fit}/3)")
