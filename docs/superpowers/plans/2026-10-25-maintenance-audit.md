# GitHub Studio maintenance audit implementation plan

> **For agentic workers:** Use superpowers:subagent-driven-development; user has delegated all execution choices.

**Goal:** Make portfolio maintenance auditable and recoverable, and make project verification easier.
**Architecture:** Extend existing CLI with a read-only audit module; harden state/path validation; preserve desired configuration and resume checkpoint. Update human-facing entry points using current main facts.
**Tech Stack:** Python stdlib, Git/GitHub CLI, Markdown.
**Spec:** docs/superpowers/specs/2026-10-25-maintenance-audit-design.md

## Global Constraints
- No questions, no denied write retries, no credentials/private repository facts in public artifacts.
- Audit is read-only and never modifies checkpoint; all remote repositories must be public and canonical identity checked.
- Metadata state history and current audit observations remain separate.
- Validate file path aliases before API/filesystem mutations.
- No Java business changes, no PR#2 merge, no schedules.

## Review Focus
- Blocked local checkpoint may already match remote.
- State corruption must not crash or trigger API calls.
- Symlink/hardlink report aliases must not clobber config/checkpoint.
- Failed reads must not become missing or successful completion.
- Docs must give actual main commands and expected scenario outputs.

### Task 1: Audit and recovery reliability (agent)
Files studio/audit.py(optional),studio/operations.py,scripts/studio.py,tests/test_audit.py,tests/test_operations.py
- [ ] Add failing behavioral tests for requirements and observe RED.
- [ ] Implement read-only observations, strict state validation and path guards.
- [ ] Run complete unittest suite and plan/status with actual config, record commands/results. No remote writes or commits.

### Task 2: Verification entrances (content agents/controller)
Files profile/README.md and external underwriting README+three existing docs.
- [ ] Add literal expected scenarios, existing main scripts and prerequisites.
- [ ] Synchronize Wrapper commands and validate source/relative links. No business changes.

### Task 3: Integrated evidence and publication (controller)
- [ ] Run fresh read-only audit with existing portable checkpoint and show unchanged hash.
- [ ] Publish sanitized report and truthful docs/results, then fresh review.
- [ ] Push project backup branch and edited profile/docs with read-back verification; archive verified source/evidence.
