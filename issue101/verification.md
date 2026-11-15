# Slow High-quality playback guidance

Issue [#101](https://github.com/adqm0001/lunar-window/issues/101) accepts clear guidance toward a suitable quality mode when High playback stays slow. This change implements that option. It does not claim an Iris Xe frame-rate improvement; the reported Iris Xe configuration was not independently reproduced.

The app observes actual draw-frame timestamps from `MoonScene.loop` while High quality is playing in a visible tab. It ignores six seconds of startup, then evaluates eight-second windows. A window is slow below 15 rendered FPS or after at least three gaps of 250 ms or longer. An epsilon avoids a float-rounding false positive at exactly 15 FPS.

The prompt offers **Use Balanced** and **Keep High**. Choosing Balanced uses the existing quality setting; Keep High dismisses the prompt for the current playback session. Pause, quality changes and hidden/visible transitions reset the observation window. Healthy windows clear the slow result. Cinema mode hides the prompt. The phone layout reserves space for camera height controls and the bottom navigation.

## Verification

- Clean `npm ci`, TypeScript, all 96 tests, production build and whitespace checks pass. The existing three.js bundle-size warning remains.
- Fifteen tests cover smooth 15/20/30/60/120 FPS, reported-style 7/11 FPS and 14 FPS, startup and full-window timing, repeated stalls despite a higher mean FPS, one isolated stall, recovery, reset after a long pause/hidden period, unsubscribe and stale StrictMode cleanup.
- Browser checks use controlled frame histories fed into the real monitor through the real rendered-frame listener, with controlled document visibility. The browser animation API is intact; the scene is also stepped manually for hidden-tab screenshots as in ARCHITECTURE.md. These checks prove the notice and controls, not the original physical GPU stall.
- At 1600×900: slow High playback displays one status prompt. Space on Keep High dismisses it while quality remains High and playback continues. Dismissal survives additional slow windows. A new playback session can show guidance again. Enter on Use Balanced changes quality and leaves playback running. Balanced and paused states do not show a prompt. A healthy history clears it. Hidden/visible transitions reset it. Cinema mode hides it.
- At 375×812: the text and actions fit with no page overflow. Both actions receive pointer input. Space on Use Balanced changes quality without pausing. The camera up/down controls remain reachable beside the prompt.
- Controlled cases captured no uncaught errors or unhandled rejections. The normal production app is also checked separately, without the controlled-history harness.
- Production smoke check: the 3D canvas loads, High and 6 h/s playback run and advance the displayed date, Pause returns to Play, no QA controls are present, and no console errors are captured (`production-smoke.json`, `production.jpg`).

The JSON snapshots record state, decisions, action hit testing, dimensions and errors. Before/after screenshots show the existing High controls and the new prompt; they are UI evidence, not FPS measurements.

## Reproduction

From the repository's parent workspace, the included `issue101-server.mjs` and `issue101-browser.mjs` scripts can serve the current app and the baseline at `13d45a9`. The scripts assume they are in `work/` beside `../outputs/lunar-window`; adjust the paths if using a different checkout. They require the app's npm dependencies.

```sh
node work/issue101-server.mjs --before  # localhost:5201
node work/issue101-server.mjs           # localhost:5200
```

Open either page at Connecting ridge B, choose High and Play, then use the clearly labelled QA controls to feed slow/healthy histories or change visibility. Save results writes JSON beside this record. The baseline has no prompt or monitor. The QA controls are not committed to the app.

GPU timing uses `EXT_disjoint_timer_query_webgl2`, a fixed 1600×900 drawing buffer at pixel ratio 1, High quality, the same paused time and camera, 60 warm-up frames and 14 measured composer renders. The dedicated `before-1600-gpu.json` / `after-1600-gpu.json` timing records include all samples. UI snapshots may carry timing data from their earlier session; only the dedicated timing records are used for comparison. An early un-warmed comparison was discarded because the quality change and terrain refinement had not settled.

The settled local GPU medians are **6.2433 ms before / 5.4241 ms after**, with no added GPU cost observed in this sample. This is an overhead check, not evidence of an Iris Xe rendering-speed improvement. The shaders and terrain detail settings are unchanged.

The deferred WebXR changes are kept separately in the local Git stash and `work/task61-deferred.patch`. Task 61 was closed by the maintainer for the hackathon deadline; no WebXR code or dependencies are included in this PR.
