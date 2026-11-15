# Tasks

What is built and what is left for Lunar Window: finished work is checked off under **Done**, open tasks follow with a spec each. Read [ARCHITECTURE.md](ARCHITECTURE.md) first: it explains the coordinate frames, data formats, engines and conventions every task below relies on. Paths are relative to the repo root unless they start with `src/`, which means `web/src/`.

## Done

Everything already built, so you know what exists before adding to it. Feature → file map in ARCHITECTURE.md §0.

### Data and engine
- [x] LOLA south polar terrain reader and projection checks (`pipeline/terrain.py`, `check_terrain.py`)
- [x] Hourly Sun and Earth ephemeris 2026–2028 (JPL DE421 via Skyfield) and DSN station visibility (`pipeline/ephemeris.py`)
- [x] C++ OpenMP horizon engine: 102,400 points × 180 directions in about a minute (`engine/horizon.cpp`)
- [x] Named-site horizons (720 directions), pole horizon field, 62.5 m heights, slope maps (`build_sites.py`, `build_field.py`)
- [x] Data compression: delta + gzip, 18 MB → 6 MB field
- [x] Global and polar terrain for the 3D Moon: 16 px/° global, 240 m and 80 m polar, 40 m polar tiles, 64 px/° global tiles (`build_globe.py`, `build_tiles.py`, `build_global_tiles.py`)

### Validation
- [x] Sun and Earth positions vs JPL Horizons: 0.00003° (`validate_horizons.py`)
- [x] Sunlight at five peaks of light vs Bussey et al. 2010: within 3.7 points on average (`validate_illumination.py`)
- [x] GPU horizons vs C++ engine: within 0.01°
- [x] Thermal model vs Diviner: equator 86–385 K (measured ≈95–390 K), Shackleton floor below 110 K
- [x] Validation window in the app, recomputing several checks live (`ValidationPanel.tsx`)

### App and rendering
- [x] App shell: glass panels, timeline with playback, live site status, keyboard shortcuts, cinema mode (H)
- [x] WebGL2 GPU engine: sunlight, Earth, Sun+DSN and longest-night maps for any date range in milliseconds (`gpu/engine.ts`)
- [x] Whole-Moon 3D globe: cube-sphere level-of-detail terrain, streamed 40 m / 80 m / 64 px/° tiles, NASA 8K color map (`three/lod.ts`)
- [x] Exact terrain shadows: horizon-field shadows on the polar patch, per-pixel ray-marched shadows everywhere else
- [x] Sky: stars, Sun, Earth at its true position and phase, Sun/Earth rays from the selected site
- [x] Realistic lighting: lunar-Lambert photometry, opposition surge, earthshine, auto exposure by Sun height, bounce light in shadows
- [x] Crater detail below the data resolution (mipmapped crater texture, crater shadows), close-range rocks with long shadows, small craters and soil roughness (`three/craterTexture.ts`)
- [x] Camera: orbit ↔ surface seamless zoom, WASD / Q E / R F, right-drag pan, collision with the ground, cinematic flights
- [x] 2D view: full-screen top-down map of the real terrain with shaded relief, pan and zoom
- [x] Hover readout: position, height and layer value under the cursor
- [x] Performance: render on demand, Saver/Balanced/High power setting with fps caps, adaptive resolution (frame ≈2.5 ms at 1600×900 on the pole)
- [x] Faster first load: Moon appears before the 25 MB polar file, which streams in the background
- [x] Inside the Moon cutaway with interior layers (Weber et al. 2011)
- [x] Phone layout: compact top bar, scrolling layer row, bottom tab bar with slide-up panels

### Analysis layers
- [x] Sunlight %, Earth in view %, Sun + DSN link %, longest night, safe slope (polar field)
- [x] Surface temperature and water ice stability from a 14-layer regolith heat-flow model on the GPU (`gpu/thermal.ts`)
- [x] Whole-Moon versions of all of these: 2.2 million points on equirectangular + two polar grids (`gpu/globalLayers.ts`)
- [x] Regional horizon fields on demand for any area below 75°S ("Analyze this area", `gpu/regionField.ts`)
- [x] Click anywhere: 720-direction horizon computed on the GPU in ~2 ms (`gpu/globalHorizon.ts`)

### Planning tools
- [x] Sites: peaks of light, Shackleton floor, missions, Artemis III regions; unlimited custom points (rename, remove)
- [x] Site panel: Sun/Earth/DSN status with countdowns, 12-month stats, ground temperature now and through the year, ice depth, 7-day DSN contact windows, skyline with Sun and Earth paths
- [x] Landing spot finder: scores 102,400 spots for a date, mission length, night limit, flat ground, priority; top 10 (`gpu/finder.ts`)
- [x] Lander simulator: panels, battery, loads, hour by hour; GPU survival map; landing-miss Monte Carlo (10,000 touchdowns); true-scale 3D lander (`lib/lander.ts`, `lib/montecarlo.ts`, `three/landerModel.ts`)
- [x] Landing dates (porkchop): survival for every site and landing date (`PorkchopPanel.tsx`)
- [x] Compare: pin sites, side-by-side table, synced timeline rows
- [x] Rover route planner: hour-by-hour light and link bitmasks on the GPU, time-dependent A*, animated rover (`lib/rover.ts`)
- [x] Artemis III report card: nine candidate regions ranked for chosen dates (`lib/regionReport.ts`)

### Sharing and presentation
- [x] Shareable links: URL keeps time, site, layer, points and camera (`state/share.ts`)
- [x] Video recording of the 3D view (● Rec, `lib/recorder.ts`)
- [x] Guided tour (9 steps) and first-visit welcome card (`Tour.tsx`)
- [x] Page title, description, icon and link preview image
- [x] Live deployment to GitHub Pages on every push to `main` (`.github/workflows/pages.yml`)
- [x] README, ARCHITECTURE.md, this task list

---

## Workflow

1. Pick an open task. Claim it by appending `— taken: <name>` to its heading in a small commit or PR, so nobody doubles up.
2. Branch: `task-<number>-<short-name>` (for example `task-23-vitest`).
3. Implement exactly the spec. If the spec turns out to be wrong, fix the spec in this file in the same PR and say why.
4. Before the PR: `cd web && npx tsc --noEmit -p . && npm run build` pass, the app loads with no console errors, and the task's **Verify** steps hold. Visual changes: before/after screenshots in the PR description.
5. **Mark it done only after checking it.** Change the task's `- [ ]` to `- [x]` in this file, in the same PR, and only once every item in its **Verify** line has actually been run and passes, plus `npx tsc --noEmit -p .` and `npm run build`. If something can't be verified (no device, no data), leave it unchecked and say what's missing in the PR.
6. Commit messages: one plain sentence saying what changed.

Tasks are independent unless **Depends on** says otherwise. Sizes: S ≈ 1–2 h, M ≈ half a day, L ≈ a day or more.

---

## Act 1: Submission (people, not code)

- [ ] **1. Video clip: whole Moon to pole** (S). On the live site press **● Rec** in the timeline (records the WebGL canvas to WebM, starts playback), drag the Moon, click "Connecting ridge B" in the site list. Press Rec again to save.

- [ ] **2. Video clip: moving shadows** (S). At the pole, speed 6 h/s, Play, record ~15 s.

- [ ] **3. Video clip: layers** (S). Record Sun % (range 1y) → ❄ Ice → Temp, a few seconds each.

- [ ] **4. Video clip: landing finder** (S). Screen-record (OBS / Win+G): ★ Find landing spot → Search → click result #1.

- [ ] **5. Video clip: rover** (S). Screen-record ⛟ Rover route: Connecting ridge B → Shackleton ridge A → Plan route → Replay.

- [ ] **6. Video clip: lander** (S). ♥ Lander sim → "See the lander on the ground", slow orbit.

- [ ] **7. Video clip: report and validation** (S). Screen-record 🏁 Artemis III report and ✓ Validation.

- [ ] **8. Voice-over script** (S). ≤ 2:30. Problem (Sun ≤ 1.6° high, moving shadows, landers freeze, Earth hidden) → what the app does → validation numbers (README table).

- [ ] **9. Edit and upload video** (M). Clips 1–7 + voice-over, ≤ 3:00, upload (unlisted YouTube is fine). **Depends on** 1–8.

- [ ] **10. Slides** (M). ~7 slides: problem, solution, three feature screenshots (`docs/`), how it works (README diagram), validation table, impact, team. Export PDF.

- [ ] **11. NASA project page** (S). Description, live link, repo link, video, slides. **Depends on** 9, 10.

## Act 2: Device testing (people, not code)

Open https://adqm0001.github.io/lunar-window/ with DevTools console open (F12). File one GitHub issue per problem: device, browser, steps, screenshot, console errors.

- [ ] **12. Integrated-graphics laptop** (S). Smoothness at Saver / Balanced / High (top bar).

- [ ] **13. Mac Safari** (S).

- [ ] **14. Firefox** (S).

- [ ] **15. Android phone** (S). Bottom tab bar, moving the camera, opening panels.

- [ ] **16. iPhone** (S).

- [ ] **17. Slow network** (S). DevTools → Network → "Fast 4G", hard reload, time until the Moon appears and until the pole is sharp.

- [ ] **18. Tour** (S). ▶ Tour, all 9 steps.

- [ ] **19. Every button** (S). Each layer chip and tool button in the layer bar; note console errors.

---

## Act 3: Tests and code health

- [x] **20. Add Vitest** (S)
  - **Files:** `web/package.json`, new `web/vitest.config.ts`.
  - **Spec:** `npm install -D vitest`. Script `"test": "vitest run"`. Config: `environment: "node"`, `include: ["src/**/*.test.ts"]`. Tests import pure modules from `src/lib` only (no WebGL, no DOM).
  - **Verify:** `npm test` runs and reports 0 tests or a trivial passing test.

- [x] **21. Tests: map projection** (S) — Depends on 20
  - **Files:** new `src/lib/astro.test.ts`.
  - **Spec:** for `(lat, lon)` in `{(-89.9, 0), (-89.5, 45), (-85, -120), (-80, 179.9), (-75, -179.9)}`: `toLatLon(...toMap(lat, lon))` equals the input within 1e-6° (compare lon modulo 360). Also `toMap(-90, any)` is `[0, 0]` within 1e-6 m.
  - **Verify:** `npm test` green.

- [x] **22. Tests: Sun disc and horizon lookup** (S) — Depends on 20
  - **Files:** `src/lib/astro.test.ts`.
  - **Spec:** `discFraction(0) = 0.5`, `discFraction(0.2665) = 1`, `discFraction(-0.2665) = 0`, monotonic on [−0.3, 0.3]. `horizonAt(h, az)` with `h = [0, 10, 20, 30]` (4 bins = 90° each): `az = 45 → 5`, `az = 0 → 0`, `az = 315 → 15` (interpolates bin 3 → bin 0, i.e. wraps), `az = 360 → 0`, `az = -45 → 15`.
  - **Verify:** `npm test` green.

- [x] **23. Tests: rover planner** (M) — Depends on 20
  - **Files:** new `src/lib/rover.test.ts`.
  - **Spec:** build a minimal `FieldData` (only `meta.horizon.size`, `meta.horizon.cellMeters = 250`, `meta.slope.size`, and `slope: Uint8Array` of length `2·n²` are read by `planRoute`; cast the rest). Build a `VisibilityBits` by hand: `words = ceil(hours/32)`, bit `h` of cell `c` at `sun[c·words + (h>>5)] >>> (h & 31) & 1`. Cases on a 5×5 grid, 48 h:
    1. All cells sunlit always: route from (0,2) to (4,2) has 5 stops, `waitHours ≈ 0`, `distanceKm = 1.0`.
    2. Column 2 dark for hours 0–23, sunlit after: arrival ≥ hour 24, `waitHours > 0`.
    3. Everything sunlit, but slope layer 0 = 200 (50°, above `maxSlopeDeg: 20`) on column 2 except row 0: the route detours through (2,0).
    4. Goal unreachable (column 2 dark always, full column): returns a `RoverFailure` (has `reason`).
  - **Verify:** `npm test` green.

- [x] **24. Tests: thermal model against Diviner** (M) — Depends on 20
  - **Files:** new `src/lib/siteThermal.test.ts`, maybe `src/lib/testData.ts` (helper).
  - **Spec:** helper reads `web/public/data/ephem.json`, `ephem.bin` (float32), `dsn.bin` (int8) and `sites.json` with `node:fs`, and builds an `Ephemeris` (`{ startMs, stepHours, count, data, dsn, stations }`, see `src/data/load.ts`). Then `siteThermal(ephem, apollo11, 0, 24 * 365)`: `max ∈ [370, 400]`, `min ∈ [80, 100]`. `siteThermal(ephem, shackletonFloor, 0, 8760)`: `max < 110`, `iceDepth === 0`.
  - **Verify:** `npm test` green in < 10 s.

- [x] **25. Run tests in CI** (S) — Depends on 20 — taken: malqedra
  - **Files:** `.github/workflows/pages.yml`.
  - **Spec:** in the `build` job, add `- name: Test` / `working-directory: web` / `run: npm test` between Install and Build. A failing test must stop the deploy.
  - **Verify:** `npm test` passes locally and the step order in the YAML is Install → Test → Build. After merge, the Actions run on `main` shows the Test step passing. To verify failure handling, use an isolated branch in a test fork with an intentional failing test and a matching temporary push trigger, then remove the fixture and restore the trigger.
  - **Verified:** [upstream main run](https://github.com/adqm0001/lunar-window/actions/runs/43649663217) passed Test, Build, and Deploy. In the [controlled fork run](https://github.com/malqedra/lunar-window/actions/runs/43666536783), the intentional test failure skipped Build, artifact upload, and Deploy. Local tests, TypeScript checking, production build, and app smoke check passed.

- [x] **26. Lazy-load tool panels** (S)
  - **Files:** `src/App.tsx`.
  - **Spec:** replace static imports of `LanderPanel`, `FinderPanel`, `RoverPanel`, `PorkchopPanel`, `ComparePanel` with `React.lazy(() => import(...))`, render inside `<Suspense fallback={null}>`.
  - **Verify:** `npm run build` prints separate chunks for them; each panel still opens.

- [x] **27. Lazy-load windows** (S)
  - **Files:** `src/components/LayerControls.tsx` (`RegionReport`), `src/components/TopBar.tsx` (`ValidationPanel`), `src/components/SitePanel.tsx` (`SkylinePanel`).
  - **Spec:** same pattern as 26.
  - **Verify:** same as 26.

- [x] **28. Separate three.js chunk** (S)
  - **Files:** `web/vite.config.ts`.
  - **Spec:** `build.rollupOptions.output.manualChunks` as a function that returns `"three"` for any id under `/node_modules/three/`. The object form `{ three: ["three"] }` only takes the core package and leaves the three/examples imports (OrbitControls, EffectComposer and passes, CSS2DRenderer) in the main chunk.
  - **Verify:** `npm run build` shows a `three-*.js` chunk; the main chunk is below 500 kB minified; the app works from `npm run preview`.

- [x] **29. Remove dead rendering code** (S)
  - **Files:** `src/three/globe.ts`.
  - **Spec:** `buildGlobe`, `buildSkirt`, `globeMaterial`, `polarTexture`, `setPolarUniforms` and the `VERT`/`FRAG` shader strings they use are not referenced anywhere (`grep -rn` to confirm). Delete them. Keep `MOON_CENTER`, `dirFromLatLon`, `worldFromLatLon`, `latLonFromWorld`.
  - **Verify:** `npx tsc --noEmit -p .` and `npm run build` pass; app looks unchanged.

- [x] **30. Web Worker skeleton** (M)
  - **Files:** new `src/workers/compute.worker.ts`, new `src/workers/client.ts`.
  - **Spec:** worker created with `new Worker(new URL("./compute.worker.ts", import.meta.url), { type: "module" })`. `client.ts` exposes `initWorker(ephem: Ephemeris)` (posts `data` and `dsn` buffers, transferred copies) and a promise-based `call<T>(type, payload): Promise<T>` with request ids.
  - **Verify:** a `ping` round trip resolves; no change in behaviour yet.

- [x] **31. Site time series in the worker** (M) — Depends on 30
  - **Files:** `src/lib/visibility.ts`, worker, callers: `src/state/selectors.ts` (`useSeries`), `src/components/Timeline.tsx`, `ComparePanel.tsx`, `SiteList.tsx`, `ValidationPanel.tsx`, `src/lib/siteThermal.ts`.
  - **Spec:** worker computes `siteSeries` (returns three `Uint8Array`s, transferred). Keep a main-thread cache keyed by `site.id`. `useSeries` becomes async-aware: return the cached series or `null` while computing; components render a placeholder for `null`.
  - **Verify:** selecting a site while the 3D view is moving doesn't stall (Performance panel shows no long main-thread task > 50 ms from `siteSeries`).

- [x] **32. Site temperature in the worker** (S) — Depends on 31
  - **Files:** `src/lib/siteThermal.ts`, `src/components/SitePanel.tsx`, `ValidationPanel.tsx`.
  - **Spec:** move `siteThermal` into the worker (it needs the series from 31). `SitePanel` shows "computing…" in the temperature section until ready.
  - **Verify:** same as 31.

- [x] **33. Rover search in the worker** (S) — Depends on 30
  - **Files:** `src/components/RoverPanel.tsx`, `src/components/Tour.tsx`, worker.
  - **Spec:** `visibilityBits` stays on the main thread (WebGL). Transfer copies of `bits.sun`, `bits.link` and `field.slope` (the field keeps using its slope, and the originals allow a main-thread fallback if the worker can't load) and the needed `meta` fields to the worker; run `planRoute` there.
  - **Verify:** Plan route keeps the UI responsive; route identical to before for Connecting ridge B → Shackleton ridge A.

- [ ] **34. Tile the 80 m polar file** (M)
  - **Files:** `pipeline/build_globe.py` (writes `polar_80m.bin.gz`), new output folder `web/public/data/polar80/`, `web/public/data/globe.json`.
  - **Spec:** split the 6250² grid into 8×8 tiles (782² each; last row/col may be smaller), each `int16` metres with row deltas, gzip, named `ty_tx.bin.gz`. Record `tile`, `tiles`, `size`, `cellMeters`, `firstCenterMeters` in `globe.json` under `polar80`. Keep `−32768` for missing.
  - **Verify:** reassembling the tiles in Python equals the old array exactly.

- [ ] **35. Load 80 m tiles on demand** (M) — Depends on 34
  - **Files:** `src/data/globe.ts` (`loadPolar80`), `src/three/lod.ts` (`refreshPolar80`, uniform `uP80`), `src/three/MoonScene.ts`.
  - **Spec:** allocate the full 6250² `Int16Array` filled with `−32768` and a matching R16I texture once. Fetch tiles nearest the camera first (sort by distance from the camera's polar-map position), max 4 in flight. For each arrival: copy into the array, `texSubImage2D` that region, mark LOD nodes whose bounds overlap that tile dirty (instead of all polar nodes).
  - **Verify:** DevTools network: first sharp view of the pole needs < 8 MB of polar80 data; heights unchanged (spot-check `globeHeight` at 5 points against the old file).
---

## Act 4: Phones and accessibility

- [x] **36. Pinch zoom in 2D map mode** (S)
  - **Files:** `src/three/MoonScene.ts` (`bindMapInput`).
  - **Spec:** track active pointers by `pointerId`. With two pointers, scale `this.mapDist` by the ratio of previous to current finger distance (clamp 0.6–3500 km), and suppress panning while two are down.
  - **Verify:** Chrome DevTools device mode with touch emulation, or a real phone: pinch zooms the 2D map.

- [x] **37. Up/down buttons on phones** (S)
  - **Files:** `src/three/MoonScene.ts`, `src/components/MobileNav.tsx`, `src/styles.css`.
  - **Spec:** add `setHeld(key: "r" | "f", down: boolean)` to `MoonScene` that adds/removes the key in `this.keys` (the same set the keyboard uses) and sets `dirty`. In the phone layout, two round buttons (▲ ▼) above the tab bar call it on `pointerdown` / `pointerup` / `pointercancel`.
  - **Verify:** on a phone viewport, holding ▲ raises the camera and ▼ lowers it, in surface, orbit and map modes.

- [x] **38. Tap to add a point on touch screens** (S)
  - **Files:** `src/three/MoonScene.ts` (`bindPicking`).
  - **Spec:** currently `pointerdown` records only `button === 0` and `pointerup` checks movement < 4 px. Make it work for touch (`pointerType === "touch"`): use a 10 px threshold and ignore if a second pointer went down in between (pinch).
  - **Verify:** on a phone viewport, a tap adds a point; a drag or pinch doesn't.

- [ ] **39. Focus outlines** (S)
  - **Files:** `src/styles.css`.
  - **Spec:** `:focus-visible` outline (2 px, `rgba(139,156,255,0.9)`, offset 2 px) for `.btn`, `.chip`, `.icon-btn`, `.m-tab`, `.result`, list rows; don't remove outlines anywhere.
  - **Verify:** Tab through the page; every control shows the outline.

- [ ] **40. Keyboard handling in windows** (S)
  - **Files:** `src/components/ValidationPanel.tsx`, `SkylinePanel.tsx`, `RegionReport.tsx` (consider a shared `src/components/Modal.tsx`).
  - **Spec:** Escape calls `onClose`; focus moves to the close button on open; Tab/Shift+Tab cycle within the modal; focus returns to the opener on close. `role="dialog"`, `aria-modal="true"`, `aria-labelledby` the title.
  - **Verify:** keyboard-only: open each window, cycle focus, Escape closes.

- [ ] **41. Color-blind palette** (M)
  - **Files:** `src/gpu/layers.ts`, `src/state/store.ts`, `src/components/LayerControls.tsx`.
  - **Spec:** add `palette: "default" | "viridis"` to the store (persist in `localStorage` like `quality`). Add viridis stops for `sun`, `earth`, `link`, `night`, `temp`; use them in `paint`, `paintGlobal` and `gradientCss` when selected. Toggle in the legend.
  - **Verify:** switch the palette; legend and both patch and whole-Moon overlays change.
---

## Act 5: Science upgrades

- [ ] **42. Terrain view factor per cell** (M)
  - **Files:** `src/gpu/thermal.ts`.
  - **Spec:** in `THERMAL_MAIN`, before the time loop, compute the fraction of the (cosine-weighted) sky covered by terrain from the horizon field: `F = (1/N) Σ_az sin²(max(h(az), 0))` over the `uAzBins` directions, using the existing `horizonAt(col, row, az)` (degrees). This is the radiative view factor from the cell to surrounding terrain.
  - **Verify:** temporarily output `F` in a channel: flat plains ≈ 0, crater floors (Shackleton floor) ≈ 0.05–0.15. Revert the debug output.

- [ ] **43. Scattered sunlight term** (M) — Depends on 42
  - **Files:** `src/gpu/thermal.ts`.
  - **Spec:** per time step add `Q_scat = F · A_t · S0 · max(0, sin(elevSun + 20°)) · L_up` to `absorbed`, where `A_t = 0.12` is terrain albedo, `20°` approximates the mean slope of sunlit crater walls facing the Sun, and `L_up = 1` if the Sun is above the ideal horizon (`sel > 0`) else 0. This is a first-order estimate (Paige et al. 2010 handle it with full view-factor matrices); keep the formula and assumptions in a comment.
  - **Verify:** Shackleton floor max temperature rises from ~26 K into roughly 35–60 K; equator unchanged (F ≈ 0).

- [ ] **44. Infrared from surrounding terrain** (M) — Depends on 42
  - **Files:** `src/gpu/thermal.ts`.
  - **Spec:** add `Q_ir = F · ε · σ · T_w⁴`, with `T_w` the temperature of sunlit walls: `T_w = ((1 − A_t) · S0 · max(0, sin(elevSun + 20°)) / (ε σ))^(1/4)` when the Sun is up, else 0.
  - **Verify:** with 43, Shackleton floor max in the Diviner range (~40–60 K); equator still 86–385 K.

- [ ] **45. Apply 42–44 to the other thermal models** (M) — Depends on 44
  - **Files:** `src/gpu/globalLayers.ts` (`THERMAL` shader; it has its own `horizonAt(ivec2, az)` over 32 directions), `src/lib/siteThermal.ts` (CPU; horizon is `site.horizon`, 720 directions).
  - **Spec:** same three changes, same constants.
  - **Verify:** site panel temperature for Shackleton crater floor and the Temp layer agree within ~5 K.

- [ ] **46. Update validation text** (S) — Depends on 45
  - **Files:** `src/components/ValidationPanel.tsx`, `README.md`, `src/components/LayerControls.tsx` (thermal note text).
  - **Spec:** replace "leaves out bounced light… ~25 K vs 30–50 K" with the new behaviour and numbers.

- [ ] **47. Extend the ephemeris to 2036** (S)
  - **Files:** `pipeline/ephemeris.py` (lines with `datetime(2026, 1, 1, …)` and `datetime(2029, 1, 1, …)`).
  - **Spec:** set the end to `datetime(2037, 1, 1, tzinfo=timezone.utc)`. Rerun `python ephemeris.py` (needs `data/raw/` from `fetch_data.py`). `ephem.bin` grows ~210 kB/year; the app reads `count` from `ephem.json`, and the GPU textures pack hours in rows of 4096, so no shader change is needed.
  - **Verify:** the timeline reaches 2036; 1-year layers, finder and porkchop work near the end of the range.

- [ ] **48. Remove hard-coded years** (S) — Depends on 47
  - **Files:** `src/components/Timeline.tsx` (`for (let y = 2026; y <= 2028; y++)` year labels), `src/components/SkylinePanel.tsx`, `src/components/Tour.tsx`, `src/components/ValidationPanel.tsx`, `README.md`.
  - **Spec:** derive the first and last year from `data.ephem.startMs` and `count`; text says "2026–<last year>".
  - **Verify:** `grep -rn "2028" web/src` returns nothing.

- [ ] **49. Link budget model** (M)
  - **Files:** `src/lib/contacts.ts`.
  - **Spec:** add `estimateRateBps(earthDistanceKm: number, opts?)`. Free-space path loss `L = (4πd/λ)²`, antenna gain `G = η(πD/λ)²`, `λ = c/f`. Defaults: X-band `f = 8.4 GHz`, `Pt = 20 W`, lander dish `D = 0.5 m, η = 0.55`, DSN `D = 34 m, η = 0.6`, `Tsys = 30 K`, required `Eb/N0 = 2 dB`, margin 3 dB, other losses 2 dB. `Pr = Pt·Gt·Gr/L/losses`, link capacity `C = Pr / (k·Tsys·(Eb/N0)·margin)`. Return `min(C, radioMaxBps)` with `radioMaxBps = 2e6` by default, because a small lander's radio, not the link, is the limit. Earth distance = norm of the Earth vector in `ephem.data` at that hour.
  - **Verify:** with the defaults at 384 400 km, `C` is about 3 Gbps (Gt ≈ 30 dBi, Gr ≈ 67 dBi, L ≈ 223 dB, Pr ≈ 4e-12 W), so the function returns the 2 Mbps radio cap. With `radioMaxBps: Infinity` it returns `C`. Document all assumptions in the function comment.

- [ ] **50. Show data rates** (S) — Depends on 49
  - **Files:** `src/components/SitePanel.tsx` ("Contact with Earth, next 7 days").
  - **Spec:** each pass row shows ≈ rate (Mbps); the summary line adds total GB for the week. A `title` tooltip lists the assumptions.

- [ ] **51. 20 m horizons around one site** (L)
  - **Files:** `pipeline/build_field.py` (pattern), new `pipeline/build_site_field.py`, `engine/horizon.cpp` (unchanged; CLI: `horizon <raw_dir> <points.f64> <out.f32> <n_az> <observer_m> <max_dist_m>`, points are `[lat, lon]` float64 pairs, output float32 `[n_points][n_az]` degrees; see `pipeline/engine.py`).
  - **Spec:** 250×250 points at 20 m spacing (5 × 5 km) centred on Connecting ridge B, 180 directions. Write `field_ridge_b.json` + `.bin.gz` in the same format as `field_pole` (see ARCHITECTURE §3), with `centerX/centerY` and `label`.
  - **Verify:** loading it with `loadField`-style code gives horizons matching the pole field at shared points within ~0.3°.

- [ ] **52. Use the 20 m field in the Monte Carlo** (M) — Depends on 51
  - **Files:** `src/lib/montecarlo.ts`, `src/components/LanderPanel.tsx`.
  - **Spec:** if the Monte Carlo target lies inside a loaded fine field, sample horizons from it instead of the active field.
  - **Verify:** success odds at Connecting ridge B differ from the coarse result, and the panel says which resolution was used.

- [ ] **53. North pole data** (S)
  - **Files:** `pipeline/fetch_data.py`.
  - **Spec:** add the north-pole counterparts of the south polar LOLA products used (same PDS directory, `…_n_…` names) to `FILES`, with sizes.
  - **Verify:** `python fetch_data.py` downloads them.

- [ ] **54. North polar projection in the pipeline** (M) — Depends on 53
  - **Files:** `pipeline/terrain.py`, `pipeline/geo.py`, `pipeline/build_field.py`.
  - **Spec:** parameterise the polar projection by hemisphere (north: `k = 2R·tan(π/4 − lat/2)`, `x = k·sin(lon)`, `y = −k·cos(lon)`), build `field_north.*` like `field_pole`.
  - **Verify:** a sunlit-fraction map of the north pole shows Peary crater's rim as one of the brightest areas.

- [ ] **55. North pole in the app** (L) — Depends on 54
  - **Files:** `src/lib/astro.ts` (`toMap`/`toLatLon` take a hemisphere), `src/data/field.ts`, `src/three/MoonScene.ts` (`mapToWorld`), `src/three/shaders.ts` (patch shader lat/lon from `vMap`), `src/gpu/engine.ts` (cell lat/lon).
  - **Spec:** fields carry `meta.hemisphere: "south" | "north"`; every map↔lat/lon conversion uses it. A button switches the active field to the north pole.
  - **Verify:** north pole shows the detailed patch with correct shadows; south unchanged.
---

## Act 6: New features

- [ ] **56. Lander shadow** (M)
  - **Files:** `src/three/lod.ts`, `src/three/shaders.ts`, `src/three/MoonScene.ts` (`updateLander`), `src/three/landerModel.ts`.
  - **Spec:** uniforms `uLanderPos` (world km), `uLanderUp`, `uLanderR = 0.0025` km, `uLanderH = 0.0045` km, `uLanderOn`. In both terrain fragment shaders, within 0.2 km of the lander, project the pixel into the lander's local tangent plane and test it against the shadow of a vertical cylinder of radius R, height H, cast away from the Sun (length `H / tan(sunElevation)`). Same idea as `rockShadow` in `src/three/craterTexture.ts`.
  - **Verify:** "See the lander on the ground" shows a long shadow pointing away from the Sun that rotates as time plays.

- [ ] **57. Split screen: rendering** (L)
  - **Files:** `src/three/MoonScene.ts`.
  - **Spec:** optional second `PerspectiveCamera` + controls. When split is on, render twice per frame with `renderer.setScissorTest(true)`, `setViewport`/`setScissor` for each half (the composer/bloom: render the second view without post-processing, or give it its own composer). Each camera keeps its own target.
  - **Verify:** two independent views, each orbitable, no flicker; GPU time roughly doubles but stays < 12 ms at 1600×900.

- [ ] **58. Split screen: UI** (M) — Depends on 57
  - **Files:** `src/components/ComparePanel.tsx`, `src/state/store.ts`.
  - **Spec:** "Side by side" toggle when ≥ 2 sites are pinned; left view flies to pin 1, right to pin 2; the shared timeline drives both.

- [ ] **59. IM-2 replay: ephemeris** (S)
  - **Files:** `pipeline/ephemeris.py`.
  - **Spec:** a second output `ephem_2025.bin` / `.json` covering 2025-02-15 to 2025-03-31 (same format). Don't change the main ephemeris.

- [ ] **60. IM-2 replay: UI** (M) — Depends on 59
  - **Files:** `pipeline/sites.py` (site `im2-athena` already exists at −84.78°, 29.13°), `src/data/load.ts`, new replay entry in `src/components/SiteList.tsx`.
  - **Spec:** "Replay IM-2" loads the 2025 ephemeris, jumps to the landing time (from Intuitive Machines / NASA public reports; cite it in a comment), selects the site, shows the 3D lander, starts playback.
  - **Verify:** lighting at the site around the landing date matches public reports of the conditions.

- [ ] **61. VR: enable WebXR** (M)
  - **Files:** `src/three/MoonScene.ts`.
  - **Spec:** `renderer.xr.enabled = true`, add three.js `VRButton` (`three/examples/jsm/webxr/VRButton.js`) to the DOM when `navigator.xr` supports `immersive-vr`.
  - **Verify:** the button appears in a WebXR-capable browser (or the WebXR emulator extension).

- [ ] **62. VR: render loop** (M) — Depends on 61
  - **Files:** `src/three/MoonScene.ts` (`loop`).
  - **Spec:** while presenting, use `renderer.setAnimationLoop` and render the scene directly (skip the composer/bloom). Place the camera rig at the selected site, 1.7 m above the ground, using `sitePosition` and the local up vector.
  - **Verify:** in the emulator, you stand on Connecting ridge B and can look around; time playback moves the Sun.
