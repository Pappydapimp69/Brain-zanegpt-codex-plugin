# local/sandbox-combined-waiting-city-recursion-touch-detection-and-reachability-are-independent — lessons

Project: local/sandbox-combined-waiting-city-recursion-touch-detection-and-reachability-are-independent. Newest first.

---

## E1 — sandbox combined waiting city recursion touch detection and reachability are independent
- Date: 2026-08-29
- Project: local/sandbox-combined-waiting-city-recursion-touch-detection-and-reachability-are-independent
- Tags: [mobile][input][testing][accessibility]
- What: A deterministic sandbox (five fixed device profiles, no RNG) scoring whether on-screen touch controls are SHOWN under two detection predicates and whether they can RECEIVE input under two margin strategies, including a headless-emulated profile.
- Why built: waiting-city#E6 records that `'ontouchstart' in window` alone false-negatives on real touch hardware, notably iPadOS Safari's desktop-site mode, and prescribes OR-ing with `navigator.maxTouchPoints`. recursion#E11 records that an edge-hugging control with a hand-picked fixed pixel margin can stop receiving input because an OS edge-swipe band or notch intercepts it, and prescribes `env(safe-area-inset-*)`. Both produce the same user report, so this tests whether either fix covers the other.
- Design: Five device profiles carrying an `ontouchstart` flag, a `maxTouchPoints` count, an OS gesture-band width and a notch height. Controls are scored as shown under detection-by-ontouchstart-only versus the OR'd predicate, and as reachable under a fixed 14px margin versus safe-area insets.
- Got right: Including a headless-emulated profile that reports touch capability but models no safe-area geometry or gesture band, which is what makes the harness limitation measurable alongside the two device failures rather than assumed.
- Where/why it failed: The two failures are fully independent and hit disjoint device sets. Detection-only fails on iPad desktop mode, where controls are never shown. Reachability-only fails on iPhone Safari, iPad and Android Chrome, where controls are shown but never receive the touch. Fixing detection leaves the iPhone dead; fixing insets leaves the iPad blank. The headless profile passes both checks, so a green headless suite is evidence for neither.
- Fix: Adopt both fixes together — OR the touch predicate with `maxTouchPoints`, and inset every edge-hugging control with `env(safe-area-inset-*)` rather than a constant — and treat headless mobile-viewport results as covering layout only, never device geometry or OS gesture interception.
- Why this fix: Both defects present to a user as "the buttons don't work," which invites diagnosing one, shipping its fix, and considering the class closed. The sandbox shows the fixes are disjoint in effect: neither reduces the other's failing device set at all, and the harness most teams would reach for reports success on every profile regardless of which fix is present.
- Rule of thumb: waiting-city#E6's touch-detection false-negative and recursion#E11's safe-area reachability failure are independent, hit disjoint device sets, and produce the identical user report — sandbox-confirmed detection-only failing on iPad desktop mode while reachability-only fails on iPhone, iPad and Android, with a headless-emulated profile passing both checks and evidencing neither.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b14/l32.py) and confirmed detection-only fails on ipad-desktop-mode, reachability-at-14px fails on iphone-safari, ipad-desktop-mode and android-chrome, and headless-emulated scores shown=True and reachable=True under both weak strategies. the-game-the-waiting-city#E6 and the-game-the-recursion#E11 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__the-game-the-waiting-city/E6, pappydapimp69__the-game-the-recursion/E11
- Link: session_014mRpopK9xnhvk35tT8ozkX

