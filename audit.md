# Audit of the seven earlier pull requests

The current upstream `CLAUDE.md` and `REVIEWING.md` were followed: oldest open PR first, updates from main, review-body and inline-comment checks, clean dependency installs, task-specific verification, TypeScript, tests, builds, and required GitHub checks. Changes were pushed to the existing PR branches and documented in their descriptions and review responses. No new feature PR or duplicate task was opened.

| PR | Finding and outcome |
| --- | --- |
| [20](https://github.com/adqm0001/lunar-window/pull/20) | Fixed modal key propagation and native Space/Enter activation. Fix `ea22a5d` passed 60 tests, production keyboard checks, and [CI](https://github.com/adqm0001/lunar-window/actions/runs/43669228859). The maintainer independently verified, approved, and merged it. |
| [21](https://github.com/adqm0001/lunar-window/pull/21) | Fixed palette repainting during playback and native keyboard activation in palette controls. Fix `3ff97cd` passed 60 tests, the production/phone/pending-result checks, the no-recalculation probe, and [CI](https://github.com/adqm0001/lunar-window/actions/runs/43671035741). The maintainer independently verified, approved, and merged it. |
| [22](https://github.com/adqm0001/lunar-window/pull/22) | Already merged; no outstanding review feedback or unresolved inline threads. |
| [23](https://github.com/adqm0001/lunar-window/pull/23) | Already approved and merged; no outstanding review feedback or unresolved inline threads. |
| [24](https://github.com/adqm0001/lunar-window/pull/24) | Fixed unsupported mission windows. Fix `4a20e8b` passed 75 tests, production cutoff checks, the annual layers, the near-end finder, and data checks. Updated with the merged fixes from main at head `0319329`; local checks and [required CI](https://github.com/adqm0001/lunar-window/actions/runs/43672279851) passed again. Maintainer re-review is pending. |
| [25](https://github.com/adqm0001/lunar-window/pull/25) | Already approved and merged; no outstanding review feedback or unresolved inline threads. |
| [71](https://github.com/adqm0001/lunar-window/pull/71) | Already approved and merged; no outstanding review feedback or unresolved inline threads. |

All reported defects in these PRs have fixes and regression evidence. The remaining requested-changes status on PR 24 is the maintainer's earlier review; its required check is successful and the fix response has been posted. The working tree is clean. Commit messages use the user's Git identity without AI attribution or co-author trailers.
