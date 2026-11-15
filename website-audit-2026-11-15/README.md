# Lunar Window website audit — 15 November 2026

Audit only: no application fixes, task commits or pull requests were made.

The live GitHub Pages site was tested in the Codex in-app Chromium browser on Windows. Viewports: 1280×720, 1600×1000, 375×812, 812×375 and 820×1180. Phone and tablet coverage is viewport testing, not physical Android/iPhone or Safari testing.

Existing issues in all states, their relevant comments, and open/draft PR scopes were checked before testing and again before reporting. Deployments changed during the audit. The final observed bundle was index-CYctQxVn.js, which matches the production build of main revision 6dc67b89382ef25e0a0d90f080228cb696ca54ea. The five affected implementations were unchanged between the earlier audited b0b4d4e revision and that revision.

## Confirmed new findings

1. **Lander map and Monte Carlo odds stay current-looking after parameters change.** At 2026-11-15 03:00 UTC, Connecting ridge B, Small CLPS lander, Sun-tracking panels, 14 days: run the map, then set panel power to zero. The battery verdict updates to dead after 11 h, but 32.1% landing survival and the previous map remain without a stale-result warning. Re-running gives 0.0%. The random percentage varies by run.
2. **Reopening the landing finder resets the form but retains results from the previous mission.** Search for 90 days, close and reopen: the form selects 14 days while the old 2,160-hour search summary and candidates remain. A fresh 14-day search uses 336 hours and gives different results.
3. **Sharing a landing-finder result loses the selected site.** A copied URL contains s=best:1 and l=score. Opening it in a fresh tab selects Connecting ridge B and terrain instead. The camera survives, leaving it aimed at a different place from the selected site. Custom point sharing, including punctuation in names, worked.
4. **The thermal panel presents truncated data as a 13-month temperature prediction and annual ice result.** At 2036-12-31 23:00 UTC, Shackleton ridge A, the right panel says Coldest / hottest (13 months): 26 K / 26 K and water ice stable at the surface, although only the final 24-hour day remains. The summary correctly says Available data · 24 h. The ice legend also discloses 24 h of 365 d, but still describes a full-year classification. The replay likewise shows a 13-month thermal heading for its shorter dataset. This is distinct from the standalone lander cutoff issue #128 and the summary-heading fix #129.
5. **Moon cutaway core labels overlap in its default view.** At 1600×1000, clicking Inside the Moon places the solid inner core, fluid outer core and partially molten layer labels on top of one another. Their 36.8 px-tall boxes are separated vertically by only about 10–11 px. Mantle and crust remain readable.

Related follow-up for existing #129: Compare still calls the final day's statistics next 30 d, next 12 mo and Longest night, 12 mo. The contact section also calls its truncated results next 7 days and says Earth stays hidden all week. These observations belong with the existing coverage-label report, rather than a duplicate of that report.

## Coverage and checks

Exercised startup, site selection, 2D/3D switching, map pan/zoom, every analysis layer, landing search (14/90 days), lander presets/power/map/Monte Carlo, lander close-up, landing dates (6/12-month windows), a successful rover route, report generation and Go to best spot, validation and skyline windows, modal Escape focus restoration, custom point rename/Escape/remove and share, Compare and split view, phone tabs/playback, the nine tour steps, mission replay and exit, regional analysis and return, whole Moon and cutaway, and recording stop/download. The recording produced a nonempty WebM; media playback/encoding quality was not separately inspected. Cinema hiding was visually observed at the end; its keyboard automation was not a comprehensive shortcut audit.

On main revision 6dc67b89382ef25e0a0d90f080228cb696ca54ea in an isolated checkout:

- npm test: **99 tests passed** across 9 files.
- TypeScript checking: **passed**.
- npm run build: **passed**. Vite gives its existing advisory for a chunk over 500 kB.
- The final fresh live page had **no console errors**. An earlier tab encountered a failed lazy import while a Pages deployment changed its asset names; the supplied Reload action recovered it. This single deployment-transition observation is retained in observations.json, not filed as a separately reproduced bug.

Previously tracked problems were not refiled. In particular, #128 tracks incomplete lander missions, #143/#146 track physical-phone dragging, #148 tracks camera-distance drift, and #88 tracks slow-network startup. Several known text/performance fixes merged during the audit; observations from older tabs are not claims that those fixes regressed.

This audit does not establish absence of bugs. Physical Safari/mobile behavior, the reported Iris Xe configuration, network throttling, detailed GPU profiling, exhaustive numerical validation, and video encoding quality remain outside this run.

Screenshots and machine-readable observations are alongside this report. GitHub issue links will be appended after posting.
