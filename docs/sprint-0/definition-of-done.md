# Sprint 0 – Definition of Done (DoD)

A backlog item is **Done** only when *all* of the following are true:

### Code
- [ ] Code implements every acceptance criterion of the story.
- [ ] Code follows the agreed structure (`library/` package, one responsibility per module)
      and uses type hints and docstrings on public classes/functions.
- [ ] No debugging `print` statements or commented-out code left behind.

### Testing
- [ ] Unit tests cover the new behaviour, including at least one failure/edge case per AC.
- [ ] Integration tests cover any change touching file persistence or the CLI.
- [ ] The full test-suite passes locally (`pytest`).

### Version control & CI
- [ ] Work was done on a short-lived branch (`feature/US-xx-…`, `ci/…`, `docs/…`) with small,
      descriptive commits (Conventional Commits style: `feat:`, `fix:`, `test:`, `docs:`, `ci:`).
- [ ] The branch is merged into `main` with a merge commit (`--no-ff`) so the story is
      traceable in the history.
- [ ] The CI pipeline on GitHub Actions is **green** for the merged code.

### Documentation
- [ ] README / usage section updated if a command or behaviour changed.
- [ ] The story is marked Done on the sprint board in the sprint review document.

---

## Branching & commit workflow

```
main ──●──────────●───────────────●────────────●──▶   (always releasable, CI green)
        \        / \             /  \         /
         ●──●──●    ●──●──●──●──●    ●──●──●─●
     docs/sprint-0  feature/US-01-…  feature/US-02-…
```

- `main` is the integration branch and must always pass CI.
- One branch per story / enabler, named after the backlog ID.
- Merge with `git merge --no-ff` so each story appears as one merge commit with its work
  commits underneath.
- Sprint completion is marked with an annotated tag (`v0.1.0` = Sprint 1, `v0.2.0` = Sprint 2).
