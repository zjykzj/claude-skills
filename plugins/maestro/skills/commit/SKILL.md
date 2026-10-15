---
name: commit
description: Create git commits following project conventions. Use when committing code or preparing a commit message, and whenever the user asks anything about commit conventions — the commit message format, Conventional Commit type classification, the mandatory Co-Authored-By lines, or CHANGELOG maintenance rules (subsections, breaking-change marking, what to skip) — even if they only ask a question rather than request a commit.
allowed-tools: Bash, Read, Edit, Write
---

# Git Commit Skill

Use this skill whenever committing code to the repository.

## Commit Message Format

All commits must use the following heredoc format:

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <subject>

<body if needed>

Co-Authored-By: {{AI_MODEL_NAME}} <{{AI_MODEL_EMAIL}}>
Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
)"
```

The two `Co-Authored-By` lines are **mandatory** for all commits: the AI model (`{{AI_MODEL_NAME}} <{{AI_MODEL_EMAIL}}>`, configured per-project in the `## Maestro Configuration` section of CLAUDE.md) and the agent tool (`Claude Code <noreply@anthropic.com>`, fixed — the plugin only runs inside Claude Code).

## Conventional Commit Types

| Type | Description |
|------|------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `build` | Build system or external dependencies |
| `test` | Adding missing tests or correcting existing tests |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `style` | Changes that do not affect the meaning of the code (white-space, formatting, etc.) |
| `perf` | Code change that improves performance |
| `ci` | Changes to CI configuration files and scripts |
| `chore` | Other changes that don't modify src or test files |

## CHANGELOG Maintenance

User-facing commits **must** also update `CHANGELOG.md`. If `CHANGELOG.md` does not exist, create it first with the standard header and an empty `[Unreleased]` section:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
```

If the file exists but has no `[Unreleased]` section, create it above the most recent `## [X.Y.Z]` section. One decision table covers every commit type:

| Commit Type | CHANGELOG Entry |
|-------------|-----------------|
| `feat` | `### Added`; removing features/APIs → `### Removed` |
| `fix` | `### Fixed`; security fix → `### Security` |
| Deprecation (any commit type marking a feature/API as deprecated) | `### Deprecated` |
| `chore` / `refactor` / `perf` / `docs` — user-visible only | `### Changed` |
| `test` / `ci` / `build` / `style`; anything with no user-visible difference | none — skip |

Rule of thumb: **no user-visible difference → no entry**. This covers pure-internal refactors, doc-only edits, version bump commits (the release skill renames the `[Unreleased]` section at release time) and commits that only modify `CHANGELOG.md`.

**Entry format, bounded**: `- **Bold summary**: description.` — one physical line, at most ~3 sentences, ≤400 characters, covering **what changed** and **why it matters to the user**. Root cause, measurements, test names and trade-offs belong in the commit body, never here. One entry per logical change; closely related changes may share one entry. Follow the existing *format*, not the existing *length*. Order subsections Added → Changed → Deprecated → Removed → Fixed → Security — the Keep a Changelog spec's six section types, in spec order. The bound is mechanically enforced by the plugin's PreToolUse hook (`skills/commit/scripts/changelog-bound-check.sh`, blocks overlong entries on every CHANGELOG.md edit) — if it blocks, compress the entry and retry.

**Legacy entries are not precedent**: essay-length entries already in the file predate this bound — usually written by a stale pre-4.3.0 plugin snapshot (tell the user `/plugin update` may be due). Never match their length; trim them opportunistically when touching the file.

**Breaking changes** (`feat!` / `fix!` / `BREAKING CHANGE` in the commit body, or any change that breaks users regardless of type) **must** be explicitly marked: append `(breaking)` to the entry, e.g. `- **Async is one deployment shape** (breaking): ...`. The release skill reads these markers to decide the MAJOR version bump.

The CHANGELOG edit is part of the **same commit** as the code change — never a separate commit.

## Procedure

1. Review the diff to determine the appropriate type and scope
2. Write a concise subject line (imperative mood, ≤50 chars)
3. Write the commit body if the change needs explanation — engineering detail (root cause, measurements, trade-offs, test names) lives here
4. Derive the CHANGELOG entry from the body — the user-facing summary of the same change, bounded as above; do not duplicate the body (see CHANGELOG Maintenance)
5. Append the two `Co-Authored-By` lines — AI model first, then agent tool
6. Verify the CHANGELOG entry stays within the bound (one physical line, ≤3 sentences, ≤400 characters) — the changelog-bound hook already blocks violations on Edit/Write, but re-check the final diff before staging
7. Stage the CHANGELOG edit together with the code changes and execute the commit command

## Bootstrap (First Use in a New Project)

Configuration lives in the unified `## Maestro Configuration` section of the project's CLAUDE.md, shared with the other maestro skills. On first use in a project:

1. Grep CLAUDE.md for `## Maestro Configuration` and for `{{AI_MODEL_NAME}}` / `{{AI_MODEL_EMAIL}}` definition lines.
2. If the section or the lines are missing, add what's missing — create the section at the end of CLAUDE.md containing just the lines below, or append the lines inside an existing section. If CLAUDE.md does not exist, create it with just this section. In either case, ask the user for the values rather than guessing.
3. If the lines are present — inside or outside the section (legacy `## AI Model Configuration` format) — use the existing values unchanged. If they sit outside the section, tell the user to merge them into `## Maestro Configuration`.

```markdown
{{AI_MODEL_NAME}} = <model-name>
{{AI_MODEL_EMAIL}} = <model-email>
```

**Degraded mode**: if configuration cannot be added (user declines, no CLAUDE.md), proceed using `Claude <noreply@anthropic.com>` for the model line (the agent-tool line is fixed) and tell the user what was assumed. Never fail the commit over missing configuration.

## Required Configuration

Defined in the project's CLAUDE.md, `## Maestro Configuration` section (unified with the other maestro skills — shared variables are defined once at the section top):

| Variable | Purpose | Example |
|----------|---------|---------|
| `{{AI_MODEL_NAME}}` | `Co-Authored-By` model name | `DeepSeek-V4-Pro` |
| `{{AI_MODEL_EMAIL}}` | `Co-Authored-By` model email | `noreply@deepseek.com` |
