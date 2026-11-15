# PR 24 mission cutoff regression checks

The original endpoint chart offered dates into 2037 at the final 2036 timeline hour. Selecting an unsupported cell changed the site while the timeline clamped to its last sample; the chart also claimed some dates survived based on truncated data. A new boundary test confirmed that the old model returned 1 for a mission crossing the cutoff.

The model now returns NaN for an hourly mission that lacks full track coverage. The landing-date chart limits its columns to fully covered mission windows. When none fit, it displays an explicit message instead of a chart; unsupported dates cannot be selected. The UI also handles an unavailable numeric result without calling it a battery failure.

## Verification

- Fifteen regression tests cover an exact ending boundary, a one-hour overrun, starts at or beyond the cutoff, empty or inconsistent tracks, invalid hourly windows, and a real battery failure. All 75 repository tests passed after the fix.
- At 2036-12-31 23:00, 7-, 14-, and 30-day missions each showed the unavailable message with no chart or selectable future dates.
- The last complete 14-day window starts at 2036-12-18 00:00. From a timeline set one hour later, selecting its only chart column moved to that valid time. The chart showed seven site missions and explicitly limited dates to that final start.
- Changing that case to 30 days removed the chart as unsupported; changing to 7 days restored the valid chart.
- All six annual layers loaded for 2036-01-02 through 2037-01-01. The December 1 finder scored 102,400 cells over 720 hours and returned ten candidates.
- Rechecked all 96,432 records, finite vectors, distance ranges, DSN bounds, and binary lengths. The original 2026–2028 records remain byte-for-byte identical. See `data-integrity.json`.
- Clean dependency install, TypeScript, all 75 tests, production build, and `git diff --check` passed. No browser console errors were captured. The existing build chunk warning remains.

The task file list and Verify line now include the endpoint handling and regression tests required to complete the near-end check.
