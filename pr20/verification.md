# PR 20 keyboard regression checks

The original production build reproduced the review: Space on Close left Validation open and started playback. The fixed shared Modal stops keydown propagation at the dialog while preserving native button defaults.

The fixed production build passed Space and Enter activation on Close in Validation, Skyline, and the Artemis III report. In each case the window closed, playback stayed stopped, the timeline time stayed unchanged, and focus returned to the opener. ArrowRight, Shift+ArrowLeft, H, W, A, S, D, Q, E, R, and F were checked inside all three windows. The timeline stayed unchanged and cinema mode stayed off. Tab/Shift+Tab trapping and Escape/focus restoration passed in all three windows.

`after.json` contains 42 recorded observations; 15 additional Tab/Shift+Tab checks asserted focus stayed within the dialog. No console errors were captured. `before.jpg` shows the original Space failure; `after.jpg` shows the closed window and stopped timeline after Space.

Clean `npm ci`, TypeScript checking, all 60 unit tests, production build, and `git diff --check` passed. The existing build chunk warning remains.
