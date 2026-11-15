# Task 51 verification

The field contains 250 × 250 points at 20 m spacing, 180 azimuths and a 2 m observer height. It includes the mesh heights and slope layers required by the existing field loader. The four generated files total 3,039,662 bytes (about 3.04 MB).

The grid centre is (-11505, -12495) metres in the existing south polar projection, 4.5767 m from Connecting ridge B. Snapping each coordinate to 5 + 10k metres gives exact coincident cell centres with the 250 m pole grid every 500 m. The task specification and architecture document this choice.

Checks run on the final data:

- Production `loadField` streams, decompresses and undeltas all three arrays in the committed Vitest tests. All 100 shared points × 180 directions match the existing pole field exactly (0° maximum decoded difference; task tolerance approximately 0.3°).
- Fresh C++ computation of all 11,250,000 raw horizons, re-encoded at the declared offset and step, matches every committed byte.
- Independent vectorized Python ray calculation at 49 locations, including all corners and interior points, agrees with the unchanged C++ engine within 0.0000286103°. Both use 20 m initial ray steps, 2% growth and a 250 km range. The Python reference does not use the C++ early-exit bound.
- All 1,000,000 mesh heights checked against bilinear samples of the measured DEM; maximum rounding difference 0.5 m. Both slope layers checked for dimensions, units and percentage bounds.
- The generator was rerun and all four files were byte-identical, including gzip headers. SHA256 hashes and full numerical results are in `data-checks.json`.
- Five Python regressions cover extent, spacing, row order, modulo-256 deltas, row/column/azimuth layout, clamping, nonfinite input rejection, flat ground, and analytic sloped planes.
- All 63 web tests pass. Three new artifact tests use the production loader and field lookup helpers, including shifted centre, four corners, outside-boundary rejection and progress completion.
- Clean `npm ci`, TypeScript check, production build and `git diff --check` pass. The initial in-place install hit a Windows directory permission error; moving only the old dependency directory to scratch and installing into a fresh directory succeeded. The existing three.js chunk-size warning remains.
- Production app loaded at Connecting ridge B with both polar and whole-Moon overlays complete, and no browser console errors. No app behavior or render code changes in this task.

Reproduction from the repository root, with `pipeline/requirements.txt` installed and `g++` on PATH:

```sh
python pipeline/build_site_field.py
python -m unittest discover -s pipeline -p 'test_*.py'
python /path/to/this/evidence/verify.py
cd web
npm ci
npx tsc --noEmit -p .
npm test
npm run build
```

The manual `verify.py` rebuilds the files and asserts byte stability before doing the full engine/reference comparisons. The C++ compiler used was GCC from the official w64devkit 2.11.0 release, archive SHA256 `54c2bb9962e8a30c8270e34c5efc3d5fee579f53087fa7d435b95fbba2af7b2b`, verified before extraction.

Data limitations are inherited from the requested pole format: 20 m is sampling spacing of the measured 40 m terrain, not new measured detail. Encoded horizons clamp to −8°..17.5°. Raw elevations span −3.9286°..37.4914°; 296,856 of 11,250,000 samples exceed 17.5° and saturate. The approximately 0.05° quantization bound applies to unsaturated samples. The metadata and architecture state the clamp. Selecting this new dataset in Monte Carlo remains task 52.
