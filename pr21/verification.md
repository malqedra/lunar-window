# PR 21 palette regression checks

The original production build reproduced the review: Viridis appeared in the legend during playback while the globe kept its default colors. The fixed version separates global calculation from painting and keeps a reference to the metrics actually displayed. Palette changes repaint that reference during playback; pending results use the latest palette when they are applied.

- Production playback passed on Sun, Earth, Sun+DSN, Night, and Temp. The selected Viridis legend and globe agreed without pausing, with unchanged global calculation timings.
- A temporary Vite probe counted requests, actual global GPU computations, paints, and metric-object identities. Across five palette changes on each of the five layers, while multiple days elapsed, each case recorded five repaints, zero new requests, zero GPU calculations, and the same displayed metric object. Pausing resumed requests and calculations for the new day.
- With a simulated 15-second pending request, switching palettes kept a single request and the first result painted Viridis. The probe and delay exist only in the external verification helper, not the application source.
- Ten selections across both palettes and all five detailed 2D layers passed.
- The phone check also exposed native Space being consumed by the playback shortcut. The shared palette control now preserves Space activation. At 375 × 812, both palettes worked with Space and Enter, playback stayed stopped, Viridis survived a reload, and page width stayed 375 pixels. Default persistence passed on desktop too.
- Clean dependency install, TypeScript, all 60 tests, production build, and `git diff --check` passed. No browser console errors were captured.

Screenshots compare the original legend/globe mismatch with the corrected playback view. JSON files contain the production observations, phone checks, pending-request check, and global probe counters.
