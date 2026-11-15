Verification evidence for implementation commit 1b69edb9077b75d7a59c6227f9ab14d968bf9c07.

Task 40: Keyboard handling in windows

Verified in the running Chromium app before opening the pull request:

- Validation, Skyline, and the Artemis III report open from their keyboard
  triggers and put focus on Close.
- Tab and Shift+Tab remain within each window. The completed report's nine
  buttons were checked in both directions, including both boundary wraps.
- The report initially has one button; when GPU results add its action
  buttons, focus stays on Close and the new buttons join the tab sequence.
- Escape and activating Close with Enter close all three windows and return
  focus to their respective opener.
- The report's Go to best spot action still works from the keyboard and
  returns focus to the report opener after closing.
- Backdrop clicks close the window, content clicks keep it open, and the
  mouse close button restores focus.
- Each window has role=dialog, aria-modal=true, and aria-labelledby resolves
  to its visible title.
- No browser console errors were recorded.

There are 42 recorded focus observations in keyboard-checks.json, with no
focus escaping an open window.

The original Validation component was also served from upstream/main at
515b6b0 for comparison. After dismissing the welcome card, it left focus on
the opener, Tab moved to Share view behind the window, and Escape left the
window open. See baseline-checks.json and before.jpg. after-validation.jpg
shows the close button focused after Tab with the completed change.

Repository checks passed:

- TypeScript: tsc --noEmit -p .
- Production build: npm run build. Vite reported the existing large
  three.js chunk warning; the build succeeded.
- Existing tests: npm test, 25 tests across three files passed.
- git diff --check

Checks used the bundled Node 24.22.1 runtime and npm 12.2.2 from the official
npm registry. No source files or tests for other tasks were changed.

