Verification evidence for implementation commit 22016b77413f5310a5d70467f885e22305ebc9a1.

Task 41: Color-blind palette

The legend offers Default colors and Viridis for sunlight, Earth visibility,
Sun+DSN, longest night, and temperature. Phones expose the same choice in the
scrolling layer bar. The preference is saved as lw-palette in localStorage.

Validation completed before the PR:

- TypeScript checking passed: tsc --noEmit -p .
- Production build passed: npm run build. The existing large three.js chunk
  warning remains.
- All 25 existing tests passed: npm test.
- git diff --check passed.
- In Chromium, both palettes were selected for all five supported layers
  in the detailed 2D polar view and the whole-Moon 3D view: 20 selections
  across 10 comparison pairs.
- Every pair changed the legend gradient while preserving the displayed
  calculation timings. The rendering path reuses the existing metric caches.
- Screenshot comparison of an unobstructed map rectangle (x=380..650,
  y=350..540) confirmed that the map changed in all ten pairs. Between 84%
  and 99% of pixels changed by more than 20 in at least one RGB channel.
- Viridis and Default colors both survived a page reload.
- At 375 by 812 pixels, one palette control group was exposed in the phone
  layer bar while the legend stayed hidden. Enter activated both choices.
  The page width stayed 375 pixels, with no horizontal page overflow.
- Slope kept its original colors and did not show palette controls. Returning
  to Sun % restored the selected Viridis preference.
- No browser console errors were recorded. The viewport and original Default
  colors preference were restored after testing.

palette-checks.json records the selections, gradients, and calculation timings.
browser-summary.json records the persistence, phone, and regression checks.
image-differences.json records the ten screenshot comparisons. Each layer has
paired default- and viridis- screenshots for the detailed and whole-Moon views.

TASKS.md now lists the overlay cache, scene updates, and mobile styles needed
to wire the preference into the rendered maps and expose it on phones.

