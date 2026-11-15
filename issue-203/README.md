# Rover destination slope verification

Issue: https://github.com/adqm0001/lunar-window/issues/203

Base: upstream main `bba8981`. Branch: `task-203-rover-goal-slope`.

The destination was exempt from the existing terrain slope limit. The fix removes that exemption and returns an actionable failure for a destination above the selected limit. It preserves the existing slope layer, units and model, exact-limit targets and a zero-distance start=goal result.

## Regression checks

- Flat 3×3 field, 250 m cells, 48 hours of sunlight, start (0,1), goal (1,1), speed 0.4 km/h, no Earth-link constraint.
- Before: a 50° goal and 20° limit returned a 0.25 km route arriving at hour 0.625.
- Nine new cases cover that report; 15°/20°/25° boundaries and the next encoded 0.25° step; raising the limit enough; and a zero-distance result on steep terrain.
- Five new cases fail on the original implementation. Four controls pass before and after. Existing transit-slope and shadow tests pass.
- All 149 tests across 15 files pass. TypeScript checking and the production build pass. Vite retains its existing large three.js chunk advisory.

## Production browser checks

Chromium, 1280×720, main's public site before and the local production build after. No renderer or shader changes.

Real terrain target `Steep`: latitude −89.374485°, longitude −130.724159°. In the 320×320 horizon grid it maps to column 102, row 209. The existing mean-slope byte is 104, or 26°. Start at Connecting ridge B, 2026-11-15 17:00 UTC, 400 m/h, Earth-link rule off.

1. Before, with a 20° limit, the tool accepts a 9.9 km route into this 26° destination, arriving 2026-11-22 11:37 UTC. See `before-steep-target-form.jpg` and `before-steep-target-route.jpg`.
2. After, the same target gives: “The destination cell is too steep (26.0°; limit 20°). Choose a gentler destination.” See `after-steep-target.jpg`.
3. Raising the UI limit to 25° still rejects this 26° target and reports the updated limit.
4. Selecting Shackleton ridge A and returning the limit to 20° succeeds: 25.5 km, arrival 2026-11-24 11:37 UTC, 100% time in sunlight. See `after-valid-route.jpg`.
5. No console errors were captured in the fixed production tab.

These checks cover the stated slope bug and nearby controls. They do not establish that every route or browser is bug free.
