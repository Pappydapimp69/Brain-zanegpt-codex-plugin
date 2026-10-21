"""Rebuild of mirage E13 (own fixture). Claim: a window constant encoding 'how
long X normally takes' degrades with no error when X's duration moves: the
event still fires, its interior stops being reached; set the window from the
mechanism feeding it (duration plus headroom).
Model: a call's duration is BASE + jitter, jitter over 0..JIT in whole ticks
(enumerated, no randomness). The offer completes if the call ends inside the
window. Old regime BASE 8; new regime BASE 25 (the mechanism changed).
"""
JIT = 6


def completion(window, base):
    ok = sum(1 for j in range(JIT + 1) if base + j <= window)
    return ok / (JIT + 1)


def main():
    old_win = 14                  # tuned against the old regime
    derived = 25 + JIT + 1        # duration + headroom from the mechanism
    a = completion(old_win, 8)
    b = completion(old_win, 25)
    c = completion(derived, 25)
    edge = completion(derived - 3, 25)
    print(f"old window 14: old regime {a:.3f}, new regime {b:.3f}; derived window {derived}: {c:.3f}; "
          f"derived minus 3: {edge:.3f}")
    checks = [
        ("old window completes >= 0.9 in the old regime", a >= 0.9),
        ("same window completes 0.0 after the duration moves (silent: nothing errors)", b == 0.0),
        ("a window derived from the mechanism restores 1.0", c == 1.0),
        ("break case: a derived window without headroom is partial", 0 < edge < 1),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; 14 old {a:.3f} new {b:.3f}; "
          f"derived {c:.3f}; no headroom {edge:.3f}")


if __name__ == "__main__":
    main()
