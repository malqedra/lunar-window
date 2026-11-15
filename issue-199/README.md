# Rover destination verification

Issue: https://github.com/adqm0001/lunar-window/issues/199

The live reproduction planned Connecting ridge B → Shackleton ridge A at 2026-11-15 17:00 UTC (400 m/h, 20°). Changing To to de Gerlache ridge C, without another search, made the old Go to destination button select C while retaining the route to A.

The fix keeps a small destination snapshot with each successful route. Its action names and selects that route's target, independently of the editable form. A target with a reused id but different coordinates, or a removed target, disables the action and shows an explanation. Route clear, failed searches and field changes clear the snapshot. Search/physics code is unchanged by this fix.

Verified on Windows in production Chromium at 1280×720 and a 375×812 phone viewport:

- Repeated the original reproduction: editing To to C leaves Go to Shackleton ridge A, and pressing it selects A.
- Planned B → C at 800 m/h and 25°. Closing/reopening resets the form's To to A, but the retained route action still says Go to de Gerlache ridge C. Pressing it in the phone viewport selects C, confirmed in Site details.
- Eight regression tests use the real store and render the actual panel in Node. A hook adapter makes the render read the current client snapshot rather than Zustand's unloaded SSR snapshot. Tests cover reopening, mismatched form target, renaming, removed/reused targets and clear/failure/field transitions; they failed before the implementation.
- Updated to main bba8981, including the separate route-search and shared-link fixes, and reran the original reproduction successfully. The updated A route retained the same 25.5 km / 8.8 d statistics.
- All 148 tests, TypeScript checking and the production build pass on the updated branch. The build retains Vite's existing large three.js chunk advisory.
- No browser console errors in either fixed-build verification session.

Screenshots are alongside this file. Phone checks are viewport tests, not physical mobile/Safari verification. This fix does not add stale-input warnings for the rest of the rover form.
