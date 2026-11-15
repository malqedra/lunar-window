# Site contact coverage verification

Issue: https://github.com/adqm0001/lunar-window/issues/205

Base: upstream main `bba8981260b52dee5513c236f67ff81b44b8b4ea`. Branch: `task-205-contact-coverage`.

The contact scan already stops at the end of the ephemeris, but the site panel still described it as a full week. The fix discloses the exact available hours and the active dataset's last timestamp. The no-pass message now describes Earth/DSN availability in the covered interval without concluding that Earth is blocked all week or a relay is necessary. The volume tooltip refers to this interval too. Contact windows, rates and totals are unchanged.

## Regression checks

Six tests render the real SitePanel and use the real store, selectors, contact scan and rate calculations. A synchronous real visibility-series calculation replaces the browser worker; unrelated thermal computation is omitted.

- At least seven days remaining, including exactly 168 h: normal label, 168 contact hours and 151 GB in the constant-contact fixture.
- At 167 h remaining: an explicit 167 h label and cutoff, avoiding a duration rounded back to seven days.
- Actual committed main ephemeris and Shackleton site, last hour: 1 h available, cutoff 2036-12-31 23:00 UTC, no full-week or relay conclusion.
- Replay-length fixture: cutoff 2025-03-31 23:00 UTC, 1 h / one pass / 0.9 GB preserved.
- Earth overhead with no DSN station available: no false blocked-horizon or necessary-relay claim.

Four cases fail on the original code; two full-week controls pass before and after. All 146 tests across 16 files pass, as do TypeScript checking and the production build. Vite retains its existing large three.js chunk advisory.

## Production Chromium checks

Desktop viewport 1280×720. Before: the public site at current main. After: a local production build.

1. Main dataset, Shackleton ridge A, hour 96431 / 2036-12-31 23:00 UTC. Before: next 7 days and an all-week blocked-Earth/relay conclusion despite only one hour remaining (`before-final-hour.jpg`). After: available 1 h, the cutoff timestamp and an interval-only no-contact message (`after-final-hour.jpg`).
2. Main dataset, Connecting ridge B, hour 7649 / 2026-11-15 17:00 UTC. Full-week label, 147 h of contact, 19 passes, approximately 132 GB; pass rows and rates load (`after-full-week.jpg`).
3. Actual IM-2 replay, Athena target, hour 1079 / 2025-03-31 23:00 UTC. Available 1 h, the replay's cutoff, Goldstone pass, 1 h contact and approximately 0.9 GB (`after-replay-cutoff.jpg`).
4. No console errors captured in the fixed main, full-week or replay tabs. Both the terrain and whole-Moon views loaded during the checks. Screenshots use different camera positions; no renderer changes are included.
