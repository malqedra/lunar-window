# Rover Earth-link rule verification

Issue: https://github.com/adqm0001/lunar-window/issues/200

The fix enforces the existing optional drive constraint at both endpoint cells in every sampled hour spanned by a move. It uses the same inclusive arrival-hour convention as sunlight. It does not change the ephemeris, DSN visibility calculation, or route behavior when the rule is disabled. Waiting does not require contact.

Eleven new regression cases use the reported flat 3×3 field, 250 m cells and 48 hourly samples. Seven fail on the original implementation; all pass with the fix. They cover departure-only contact, a missing middle hour with contact at departure/arrival, missing destination contact at slow and fast speeds, loss at either endpoint, waiting for a valid window at hours 3 and 31 (crossing the Uint32 boundary), rule-off/no-window controls, and an exact-hour arrival. A 250 m drive at 0.1 km/h takes 2.5 h: departure-only contact now fails, while a valid window starting at hour 3 produces departure 3 and arrival 5.5.

All 151 tests, TypeScript checking and the production build passed on main bba8981 plus this fix. The existing Vite large-chunk advisory remains.

Production Chromium on Windows, 1280×720, 15 November 2026:

- Connecting ridge B → Shackleton ridge A, 2026-11-15 17:00 UTC, 400 m/h, 20°, Earth-link rule checked: route found, 24.2 km, 8.8 d, arrival 2026-11-24 11:37 UTC. Replay starts and can be paused.
- The route's contact statistic is 90% over the whole trip; that includes waiting without contact and does not claim 100% contact while parked.
- After pausing the replay at 2026-11-17 16:37 UTC, turning the rule off and planning again also returned a route. This is a control at a later start time, not a controlled route-length comparison.
- No browser console errors. Screenshots are alongside this report.

The deterministic regressions establish the exact contact boundary behavior; the browser run verifies the production UI and worker path. The algorithm remains an hourly endpoint approximation, not a continuous radio-coverage guarantee or an optimal-path guarantee.
