# GitHub Studio Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development; user delegates all execution choices.

**Goal:** Deliver an original evidence-based GitHub portfolio and resumable operations workspace.
**Architecture:** JSON desired state + Python stdlib gh runner; profile sources and public-only research live beside the tooling. Existing profile contents publish directly after review; denied actions remain explicit.
**Tech Stack:** Python3 standard library, Git/GitHub CLI, Markdown, SVG.
**Spec:** docs/superpowers/specs/2026-10-25-github-studio-design.md

## Global Constraints
- No user questions; continue authorized work; blocked operations persist.
- Only public repository facts enter public files. No secrets or private repository names.
- Account hrniux and host github.com; allowlisted operations, no arbitrary shell.
- Write only under apply; validate before mutations; verify writes by reading.
- Never claim blocked/manual/failed actions succeeded; never imply draft PR merged.
- No schedules, repository deletion/rename/visibility changes, broad existing-license changes.

## Review Focus
- Changed config must not be skipped because a previous payload was applied.
- Denied writes and partial runs must resume without losing state.
- Wrong account/owner or unknown kind must cause no mutation.
- Read-back mismatch must fail; private facts must not leak into public reports.
- Missing pin API remains manual; no invented pin implementation.

### Task 1: Operations engine (agent)
Files: studio/__init__.py, studio/operations.py, scripts/studio.py, tests/test_operations.py.
Interfaces: config/operations.json as in spec; .local/state.json for persisted statuses.
- [ ] Read spec and write behavioral tests first; observe missing engine fail.
- [ ] Implement validated plan/status/apply and bounded gh adapter, atomic state, read-back, retry-blocked.
- [ ] Run full unittest suite, smoke plan with controller configuration; save report. Do not mutate real API or commit shared files.

### Task 2: Profile identity and source (agent)
Files: profile/README.md, profile/assets/github-studio/{hero-light,hero-dark}.svg.
- [ ] Original accessible restrained profile; 3 key projects and compact auxiliary links.
- [ ] Link only existing public pages; mark draft PR #2 truthfully. SVG has no script/foreignObject/network resources.
- [ ] Validate XML and referenced assets; save report. No remote writes, no shared git commits.

### Task 3: Research, configuration and execution (controller)
Files: config/*.json, docs/{RESEARCH,PORTFOLIO_STRATEGY,OPERATIONS}.md, reports/*.json, README.md, LICENSE, CONTRIBUTING.md.
- [ ] Capture verified public snapshot and source references.
- [ ] Write desired public metadata and queue denied create/Star plus manual pins.
- [ ] Review source/profile, apply supported changes and preserve accurate results.
- [ ] Repair two documentation issues in isolated clones; verify linked commits.
- [ ] Test integrated project, publish backup branch and profile; attempt metadata/Bio; archive source/results and report.

### Task 4: Final review and delivery
- [ ] Fresh code/content review with complete diff and tests.
- [ ] Fix important findings, rerun affected checks and verify actual remote results.
- [ ] Publish final source/results; keep pending jobs ready for future permission.
