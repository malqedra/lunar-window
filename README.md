Verification evidence for implementation commit 14979496f4452dad4d1ce704c421d8c42e353b35.

Task 42: Terrain view factor per cell

The thermal shader now computes F once per cell, before its time loops, by
averaging sin squared of the positive horizon elevation over all azimuth bins.
Angles from horizonAt are converted from degrees to radians. The comment cites
the horizontal-surface sky-view-factor integral in HORAYZON (2022), equation 5:
https://doi.org/10.5194/gmd-15-6817-2022. F is its terrain complement.

This prepares the factor for the terrain-heating terms in tasks 43 and 44.
The production output channels remain Tmax, Tmean, Tmin, and ice depth.

Verification completed before opening the PR:

- TypeScript checking: tsc --noEmit -p . passed.
- Production build: npm run build passed, with the existing large three.js
  chunk warning.
- Existing tests: npm test passed all 25 tests.
- Twelve analytic GPU cases passed. These cover negative and zero horizons,
  10, 15, 30, 45, and 90 degree rings, partial obstructions, four versus 180
  azimuth bins, degree conversion, normalization, and row ordering.
- The actual GPU engine read back F for all 102,400 cells of the committed
  180-bin polar field. Every factor was finite and in [0,1]. The largest
  absolute difference from the double-precision CPU reference was
  1.9104322078467018e-7, below the 2e-6 tolerance.
- Shackleton floor, row 185 and column 190: GPU F=0.0904238075,
  CPU F=0.0904239779, within the task's expected 0.05 to 0.15 range.
- An open cell with one degree mean slope, row 4 and column 213, gave
  GPU F=0.0001955838. Synthetic flat and negative horizons gave exactly zero.
- Regression against the original shader at 515b6b0 compared all four output
  channels for every cell over a 720-hour window and an 8,760-hour window:
  819,200 Float32 values total. Every value matched exactly.
- The app loaded its detailed and global temperature layers with Shackleton
  floor selected, with no console errors.
- git diff --check passed.

To expose F for verification, the local Vite helper served an in-memory shader
variant that temporarily replaced the output with vec4(F,0,0,1). The production
file kept its normal output throughout. The same helper served the original
shader for the regression comparison. Both helpers are included with this
evidence and are outside the feature PR.

Reproduce with Node and the repository's web dependencies installed:

    node task-42-server.mjs /absolute/path/to/lunar-window ./results

Then open http://127.0.0.1:5173/__task42.html. The helper writes gpu-report.json
to the supplied results directory. No live app state or credentials are used.

The committed byte horizon field is capped at 17.5 degrees. At Shackleton all
180 field samples hit that cap, giving F about 0.0904. The named site's separate
720-bin horizon gives about 0.1326. This existing input-data limit matters when
the later heating terms use the field; no terrain data was changed in task 42.

