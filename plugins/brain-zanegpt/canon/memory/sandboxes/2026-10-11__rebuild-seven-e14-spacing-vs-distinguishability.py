"""Rebuild of seven E14 (own fixture). Claim: a spacing assertion (sites far
apart) is necessary but not sufficient for a distinguishability requirement;
a renderer that draws every site the same passes it while making a
wrong-place claim unverifiable.
Model: 4 sites with positions and a rendered form. A wrong-place lie names a
different site; the player can only catch it if the site they remember
standing at LOOKS different from the one named. Player check = compare forms.
"""
SITES = {"spring": (2, 2), "cairn": (18, 3), "ford": (4, 17), "hollow": (17, 18)}


def spacing_ok(min_d=8):
    pts = list(SITES.values())
    return all(abs(a[0] - b[0]) + abs(a[1] - b[1]) >= min_d
               for i, a in enumerate(pts) for b in pts[i + 1:])


def catch_rate(forms):
    caught = total = 0
    for real in SITES:
        for claimed in SITES:
            if claimed == real:
                continue
            total += 1
            caught += forms[real] != forms[claimed]
    return caught / total


def main():
    same = {s: "pole-and-lamp" for s in SITES}
    distinct = {"spring": "pool", "cairn": "stack", "ford": "stones", "hollow": "dip"}
    half = {"spring": "pool", "cairn": "pool", "ford": "stones", "hollow": "stones"}
    sp = spacing_ok()
    rates = {n: catch_rate(f) for n, f in (("same", same), ("distinct", distinct), ("half", half))}
    print(f"spacing test: {'pass' if sp else 'FAIL'}; wrong-place catch rate: " +
          ", ".join(f"{k} {v:.3f}" for k, v in rates.items()))
    checks = [
        ("spacing test passes regardless of rendering", sp),
        ("identical forms make a wrong-place lie uncatchable (0.0)", rates["same"] == 0.0),
        ("distinct forms make every wrong-place lie catchable (1.0)", rates["distinct"] == 1.0),
        ("break case: two shared forms catch only part of the lies, strictly between", 0 < rates["half"] < 1),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; spacing pass, "
          f"catch same {rates['same']:.3f} half {rates['half']:.3f} distinct {rates['distinct']:.3f}")


if __name__ == "__main__":
    main()
