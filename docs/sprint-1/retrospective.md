# Sprint 1 – Retrospective

Format: **Start / Stop / Continue**, followed by concrete, owned action items for Sprint 2.

## What went well (Continue)
- **Small vertical slices.** Each story was built model → logic → tests on its own branch and
  merged with `--no-ff`; the history reads like the sprint board.
- **Tests alongside code.** 53 tests, including true integration tests against real files and
  the CLI, caught a real design issue early: author lookup had to be case- and
  whitespace-insensitive (`"chinua  ACHEBE"`), otherwise duplicate authors would be created.
- **Validate before storing.** Building the `Book` *before* registering new authors means a
  failed add leaves no orphan data (AC1.4) — a pattern worth re-using for borrowing.
- **CI from day one.** The pipeline was in place before the first feature was merged.

## What didn't go well (Stop / Problems)

| # | Observation | Impact |
|---|---|---|
| P1 | **CI only runs the tests.** No linting/format check and no coverage measurement, so style drift and untested code would not be caught. | Quality gate is weak. |
| P2 | **CI tests a single Python version (3.12)** while the README promises **3.10+**. | A 3.10-incompatible change would ship unnoticed. |
| P3 | **Feature branches were pushed all at once at the end of the sprint.** GitHub does not create push events when more than three branches are pushed together, so CI ran **only on `main`** — feature branches were never validated before merge. | CI feedback arrived after integration instead of before it. |
| P4 | **No logging.** The only diagnostics are `Error: …` messages on stderr; there is no record of what the application did or of unexpected crashes. | Hard to troubleshoot; unexpected exceptions would show a raw traceback. |
| P5 | **Encoding surprise.** The README created with the repository was UTF-16; editing it produced an unreadable file that had to be fixed. JSON written on Windows also used CRLF line endings. | Time lost; risk of broken docs/data. |

## Improvements for Sprint 2 (Start) — action items

| # | Action | Addresses | How we will know it worked |
|---|---|---|---|
| **A1** | Add a **lint job** (`ruff check` + `ruff format --check`) to CI and make the test job depend on it. | P1 | Workflow has a `lint` job; a style error fails the build. |
| **A2** | Measure **coverage** in CI with `pytest-cov` and enforce a **minimum of 90 %**; upload the coverage + JUnit reports as build artifacts. | P1 | Build fails below 90 %; reports downloadable from each run. |
| **A3** | Run tests on a **Python version matrix (3.10, 3.12, 3.13)**. | P2 | Three test jobs per run, all green. |
| **A4** | **Push each branch as soon as it has its first commit** (and again before merging), and only merge when the branch build is green. | P3 | Every Sprint 2 feature branch has its own CI run in the Actions tab. |
| **A5** | Deliver **logging first** in Sprint 2 (part of US-08) so every later story logs its actions from the start. | P4 | Borrow/return/report code logs from its first commit. |
| **A6** | Add an **`.editorconfig`** (UTF-8, LF) and write JSON with explicit `newline="\n"`. | P5 | Files created in Sprint 2 are UTF-8/LF. |
| **A7** | Add a **CLI smoke test** step in CI (`add-book` → `list` → `health`) to prove the packaged app actually runs, not just the unit tests. | P1 | Smoke step visible in every CI run. |

## Sprint 1 metrics

| Metric | Value |
|---|---|
| Velocity | 13 pts |
| Stories done / committed | 3 / 3 |
| Tests | 53 (all passing) |
| Commits (excluding merges) | 18 |
| Escaped defects | 0 |
