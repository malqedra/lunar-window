# Task 47 verification

The ephemeris pipeline now ends at 2037-01-01 UTC, exclusively. It generated 96,432 hourly samples from 2026-01-01 00:00 through 2036-12-31 23:00 UTC. Only the end date changed in the generator. The generated vector data, DSN elevations, and metadata are included in the task branch.

## Data verification

- Regenerated with Skyfield 1.55 and NumPy 2.5.4, using the repository's NASA DE421 and lunar-frame kernels downloaded by the existing `fetch_data.fetch` helper.
- All original 26,304 hourly vector records and DSN elevation records are byte-for-byte identical to the committed 2026–2028 data.
- Checked binary lengths, sample count, metadata, finite vectors, plausible Sun/Earth distances, and DSN bounds for all 96,432 samples. The existing 4,096-hour GPU layout requires 24 rows.
- Compared the committed float32 vectors with JPL Horizons apparent azimuth/elevation at Connecting ridge B, Malapert Mountain, and Apollo 11. Thirteen samples per site/body through 2036, for 78 comparisons. Maximum azimuth difference: 0.000033242 degrees; maximum elevation difference: 0.000019059 degrees. All passed the 0.001-degree tolerance.
- See `data-integrity.json` for lengths, hashes, distance bounds, and representative records; `horizons-2036.json` for the external comparison.

## App verification

- The original timeline clamped at 2028-12-31 23:00 UTC. The new timeline reaches 2036-12-31 23:00 UTC. Advancing beyond the end clamps correctly; stepping back one day and forward restores the final hour.
- All six annual overlays (Sun, Earth, Sun+DSN, Night, Temp, Ice) loaded in the detailed area and whole-Moon engines for 2036-01-02 through 2037-01-01. The existing engines automatically use coarser sampling for annual windows; no shader or sampling policy changed.
- Landing-date grid at 2036-06-01 simulated 2,520 missions across the following six months. Selecting a grid cell moved the timeline to 2036-11-19.
- Finder at 2036-12-01 scored 102,400 cells for a 30-day mission and returned ten candidates. Selecting the first result opened Best spot #1.
- Captured browser console errors: none. Screenshots and JSON observations are saved beside this report.
- The overview's hard-coded year labels and date-range copy are the separate dependent Task 48.

## Required checks

- `python -m py_compile pipeline/ephemeris.py`: passed.
- `tsc --noEmit -p .`: passed.
- `npm test`: all 25 existing tests passed. This branch starts from upstream main, where Task 49's additional tests have not yet merged.
- `npm run build`: passed, retaining the existing large three.js chunk warning.
- `git diff --check`: passed.

Task 47 is checked in this task branch's `TASKS.md`; upstream reflects it once the PR is merged.
