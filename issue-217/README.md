# Finder snapshot pin verification

Issue: https://github.com/adqm0001/lunar-window/issues/217

Base: upstream main `e103f29`. Branch: `task-217-finder-pins`.

Finder rank ids such as best:1 are reused by later searches. The fix gives finder pins identities based on their exact coordinates and keeps their saved labels/horizons. The same location remains recognizable if its rank changes. Built-in and custom-point identities retain their existing behavior. Saved finder snapshots remain available to selection, comparison, split cameras, Landing dates and share links after their originating search is replaced or cleared. Removing or evicting a selected snapshot resolves selection to a valid site.

## Automated checks

Eleven new cases cover two different locations reusing best:1, independent removal, removing via the current finder result, rank changes at the same location, selection through finder/field reset, selected-pin removal and six-pin eviction, built-in/custom rename/removal controls, actual Compare/site inspector rendering and a fresh shared-link round trip.

The component tests use the real store and selectors, mock unrelated worker results and expose menu choices without browser focus effects. Ten cases fail on the unchanged upstream source; the built-in/custom control passes. All 319 tests across 38 files pass with the fix, as do TypeScript and the production build. Existing three.js range-test stderr and Vite's large-chunk advisory remain.

## Production Chromium checks

1280×720, hour 7649 / 2026-11-15 17:00 UTC, polar field. The public site was checked before; the local production build was checked after.

1. Open Find best site and rank with the default 14-day, ≤50 h night, 50% flat, Balanced settings. Pin result #1 at 88.597°S, 67.730°W.
2. Choose Max comms and 0% flat ground, then rank again. New #1 is at 88.589°S, 67.857°W.
3. Before: the new location incorrectly says Added while Compare contains only the old coordinate (`before-wrong-added-state.jpg`). Pressing Added removes that old pin and closes Compare (`before-pin-removed.jpg`).
4. After: the new location offers + Compare. Pinning it keeps both coordinate columns and their own statistics (`after-two-snapshots.jpg`).
5. Selecting the old column opens the original coordinate and horizon, despite the newer best:1 result. Side by side shows both saved destinations and selects the old left-hand snapshot (`after-split-snapshots.jpg`).
6. Unpinning the old column leaves only the new one and its statistics, with a valid built-in selection replacing the removed selected snapshot (`after-one-snapshot-removed.jpg`).
7. A fresh page opened from the older snapshot's shared URL restores it as a named custom point at 88.597°S, 67.730°W (`after-shared-old-snapshot.jpg`).
8. Repeated the two-search comparison, old-column selection and split/removal checks after the final coordinate-identity refinement. No console errors captured in the fixed or shared-link tabs.

The screenshots show different camera positions as the selections and split views change. No renderer or physical-model changes are included.
