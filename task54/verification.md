# North polar pipeline verification

Task 54 adds a hemisphere to the offline projection, measured terrain selection, Python reference rays and C++ horizon engine. The field builder accepts `--hemisphere north` and produces `field_north.json`, `field_north.bin.gz`, `heights_north.bin.gz` and `slope_north.bin.gz`. North uses the specified projection with negative y toward longitude 0; row 0 remains +y. The north metadata has `hemisphere: "north"`. Default API and CLI calls use south.

The original file list omitted the C++ engine, its Python wrapper and the Python ray implementation, which all assumed south. The task file list now includes those required changes. `geo.py` uses great-circle geographic coordinates and requires no code change; its destinations are tested through both projections. North display and switching in the app remain task 55.

## Checks

- Seven Python regressions pass: north cardinal directions, hemisphere reflection, projection round trips across the longitude seam, pole origins, exact preservation of the original south formula, geodesic destinations in both hemispheres, and invalid hemisphere rejection.
- Clean npm install, TypeScript, all 61 web tests, production build and whitespace checks pass. The new artifact test streams and decompresses all north arrays with production `loadField`, checks metadata, dimensions, height bounds, slope percentages and completed progress.
- North rebuild is byte-identical for all four generated files. The gzip timestamp is fixed for reproducibility. Hashes and numerical results are in `data-checks.json`.
- All 18,432,000 encoded north values match a fresh native engine run. Independent vectorized Python rays at 49 points agree within 0.0000343323 degrees, using the same 20 m initial step, 2% growth and 250 km maximum range without the C++ early-exit optimization.
- All 1,638,400 north mesh heights match samples of the measured DEM within 0.5 m rounding.
- All 18,432,000 raw south float32 horizons match an executable compiled before this change bit-for-bit, including the old CLI without a hemisphere argument. The old and new Python builders also produce identical decoded horizon, height and slope arrays and identical metadata.
- An initial comparison of a south rebuild to the older committed south field found one 0.1-degree decoded difference (two delta bytes). Running the original builder produces that same difference, so it predates this change. Committed south files are untouched; all old/new computations agree exactly. Heights and slope also match the older committed arrays byte-for-byte after decompression.
- Production app loads at Connecting ridge B with both polar and whole-Moon overlays complete and no console errors. The existing three.js bundle-size warning remains.

## Sunlight map

`sunlight.py` computes the mean visible fraction of the Sun disc at all 102,400 north grid points, at each of the 8,760 hours in 2026. It uses the committed ME-frame Sun vectors, exact topocentric projections, interpolated 180-direction horizons and the existing finite-disc visibility function. The produced map is `north-sunlight-2026.png`.

Published Peary rim coordinates come from Gläser et al., *Illumination Conditions at the Lunar Poles: Implications for Future Exploration*, Tables 1 and 2 ([NASA manuscript](https://ntrs.nasa.gov/citations/20170007365)). The acceptance check is that the rim is among the brightest areas, not exact agreement with the paper's 20 m terrain and different 2017–2037 time window.

| Location | Nearest 250 m cell | Best cell within 1 km | Exact location, 720 directions |
|---|---:|---:|---:|
| Peary P, 89.7260°N, 123.11°E | 61.10% | 65.30% | 73.26% |
| Peary P0, 89.8521°N, 109.80°E | 35.68% | 58.14% | 76.45% |

The Peary P cell is at the 99.9844th percentile of the map (top 0.016%); map median is 10.97% and maximum is 83.95%. A trial check requiring the P0 neighbourhood to exceed 70% failed; that absolute number was not in the task and does not transfer from the paper's finer grid and different dates. The final test measures the requested relative brightness at the published P rim location, and the exact-point calculations document how the coarse grid can miss narrow peaks. Full results are in `sunlight-checks.json`.

## Limits and reproduction

The requested byte encoding clamps horizons to −8°..17.5°; 498,877 raw north values exceed 17.5°. This is the same limit as the pole field. The 250 m grid also cannot resolve narrow illuminated ridges. No new thermal model or user-visible physical outputs are introduced.

From the repository root with pipeline requirements installed, g++ on PATH and raw data fetched:

```sh
python pipeline/build_field.py --hemisphere north
python -m unittest discover -s pipeline -p 'test_*.py'
python /path/to/this/evidence/verify.py /path/to/pre-change-horizon-executable
python /path/to/this/evidence/sunlight.py
cd web
npm ci
npx tsc --noEmit -p .
npm test
npm run build
```

The optional pre-change executable should be compiled from `engine/horizon.cpp` at commit `78f3732` using the same compiler and flags as `pipeline/engine.py`. Without that argument, `verify.py` still compares old/new Python builders, north reconstruction and independent rays. The plot script additionally needs matplotlib. The north projection, half-metre scale, dimensions and source selection were checked against the [LOLA north DEM label](https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/polar/img/ldem_85n_40m.lbl).
