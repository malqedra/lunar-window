# Shared landing-result fix verification

Issue: https://github.com/adqm0001/lunar-window/issues/152

The selected finder candidate is encoded using the existing named-point format. The source page keeps its original finder and custom-point state. If 20 custom points already exist, the shared link keeps the newest 19 plus the selected result, matching the application's existing point limit.

The recipient restores the selected result's name and coordinates at the existing four-decimal precision. Score/survival overlays require computation as before; supported layers and the existing camera/time/view/range parameters continue to restore.

Checked on 15 November 2026 in production builds served locally, Chromium on Windows:

- Before: the old result ID from issue #152 opens Connecting ridge B in the unmodified main build (6dc67b8; its sharing implementation is unchanged in this branch's base 467e9f5).
- After: a generated first-result link opens Best spot #1, with the same time and camera coordinates. See before-wrong-site.jpg and after-restored-result.jpg, both 1280×720.
- Another generated link opens Best spot #2 while retaining an existing point named Shared point 100%, A;B and the Sun layer. The clipboard content matched the generated address-bar link once the copy operation completed.
- At 375×812, the recipient's Site tab shows Best spot #2 with the expected coordinates and Sun layer. Phone testing here means viewport testing, not physical mobile/Safari verification.
- No console errors in the three fixed-build pages used for these checks.
- Six regression tests exercise real encode/parse/restore/store selection, replacing only the GPU point-horizon lookup. Four failed against the original implementation. They cover first/second result, sharing a restored point again, nonmutating source state, mixed points and punctuation, a full point list, and unchanged built-in/custom selection.
- Full suite: 105 tests passed. TypeScript and production build passed; Vite reports its existing large three.js chunk advisory.

Screenshots and browser-results.json are alongside this file. No physics or renderer changes are included.
