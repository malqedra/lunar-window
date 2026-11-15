# Skyline angular-resolution verification

Issue: https://github.com/adqm0001/lunar-window/issues/207

Base: upstream main `bba8981260b52dee5513c236f67ff81b44b8b4ea`. Branch: `task-207-skyline-resolution`.

SkylinePanel drew one vertex every 0.5° but indexed the horizon array as if every site had 720 bins. A local custom point has the active field's 180 bins, so its entire terrain profile repeated every 90° on the chart. The fix uses the existing `horizonAt` cyclic azimuth interpolation when drawing the terrain. It changes no terrain data, physics, ephemerides, path calculations or visibility percentages.

## Regression checks

Four tests render the actual chart in Node, with the real store snapshot and a simple wrapper replacing the unrelated browser portal/focus trap. They inspect its SVG terrain vertices.

- A single eastern peak in a 180-bin horizon appears once at east; no copies in other quadrants.
- Half-degree chart vertices interpolate correctly between two-degree source bins.
- Interpolation across 358°–360° wraps to the first bin and closes the profile at north.
- Every vertex of a nonconstant 720-bin profile retains its elevation.

Three tests fail on the original implementation. The 720-bin control passes before and after. All 144 tests across 16 files, TypeScript checking and production build pass. Vite retains its existing large three.js chunk advisory.

## Production Chromium checks

Viewport 1280×720. Before: public site at current main. After: local production build. Both use hour 7649 / 2026-11-15 17:00 UTC.

1. Custom point Skyline at −89.44°, −137.3708°, restored from a shared link inside the pole field. Before, the SVG's four 180-vertex quarter-profiles are identical (`before-repeated-profile.jpg`). After, the full horizon appears once, correctly aligned with N/E/S/W, and closes at north (`after-correct-profile.jpg`).
2. The Sun/Earth path circles, including their visible/hidden colors and the current Sun marker, are identical before and after. Displayed percentages remain Sun 79%, Earth 52%.
3. Named-site control: Connecting ridge B. Its entire SVG terrain path and all Sun/Earth circles are identical before and after (`before-named-site.jpg`, `after-named-site.jpg`). Displayed percentages remain Sun 100%, Earth 53%.
4. No console errors captured in the fixed production tab. Modal opening, closing and switching between the custom and named sites work.

`chart-comparison.json` records the rendered SVG terrain paths and circle elements used for the before/after comparisons.
