---
name: release
description: Bump the project version and publish a GitHub release in two phases: local (bump, commit, tag) then optional remote (push, GitHub release). Use when releasing a new version — locally or published — and whenever the user asks anything about the release process — which semver bump to pick from the commit history, version bump locations, the release commit message format, tagging and pushing the release, local-only releases, or renaming the CHANGELOG [Unreleased] section — even if they only ask a question rather than request a release.
allowed-tools: Bash, Read, Edit, Grep, Write
---

# Release Skill

Use this skill when bumping the project version and publishing a GitHub release.

The release has two phases: **Phase A — Local** (Steps 0-3: determine, bump, commit, tag) needs no network access and always runs; **Phase B — Remote** (Steps 4-5: push, GitHub release) runs only after an explicit user choice at the gate between the phases. Phase B can also run standalone later, after a local-only release.

## Phase A — Local

### Step 0: Determine Version Number

Review `git log` since the last tag. Classify each commit's conventional commit type into semver:

| Commit Type(s) | Semver | Example |
|---------------|--------|---------|
| `fix:`, `docs:`, `refactor:`, `style:`, `perf:`, `chore:`, `test:`, `ci:`, `build:` | **PATCH** (1.6.1 → 1.6.2) | Bug fix, doc update, internal restructure |
| `feat:` | **MINOR** (1.6.2 → 1.7.0) | New public API, new CLI flag, new feature |
| `feat!:` / `fix!:` or `BREAKING CHANGE` in the commit body | **MAJOR** (1.7.0 → 2.0.0) | Remove public API, change default behavior |

**Rule:** the highest-severity commit wins. If all commits are `docs`/`refactor`/`chore` → PATCH. If any `feat` → MINOR. If any breaking change → MAJOR.

**Concrete check:** before picking a version, look at the `## [Unreleased]` section you're about to rename. If `### Added` is empty (no new features) → PATCH. If any entry is marked `(breaking)` → MAJOR.

### Step 1: Bump Version

Update **all** version locations configured for this project. See the `### Version Bump Locations` table in the `## Maestro Configuration` section of CLAUDE.md for the exact file paths — typical patterns include:

| Pattern | Example File | Field |
|---------|-------------|-------|
| Package init | `{{PACKAGE_NAME}}/__init__.py` | `__version__ = "X.Y.Z"` |
| Project config | `pyproject.toml` | `version = "X.Y.Z"` |
| Version file | `VERSION` | `X.Y.Z` (bare string, no field syntax) |
| Changelog | `CHANGELOG.md` | Rename `## [Unreleased]` → `## [X.Y.Z] - YYYY-MM-DD`, then add a fresh empty `## [Unreleased]` at the top |

The `{{PACKAGE_NAME}}` variable is defined in CLAUDE.md — `none` for projects without a Python package (bare `VERSION` file projects).

**CHANGELOG rename, not rewrite**: the commit skill maintains `## [Unreleased]` on every commit, so the release does not write new entries. Rename the section header and reset it — the section content flows unchanged into the GitHub Release body (Step 5), while the bump commit (Step 2) carries a curated digest of it.

### Step 2: Commit

Use the version bump commit format — the body is a **digest** of the `[X.Y.Z]` section, not a transcription of it (keep it under ~120 words):

```bash
git commit -m "$(cat <<'EOF'
chore: bump version to X.Y.Z

<1-2 sentence theme summary drawn from the section>

Highlights:
- <one curated bullet per line, 3-6 total>

Full release notes: CHANGELOG.md

Co-Authored-By: {{AI_MODEL_NAME}} <{{AI_MODEL_EMAIL}}>
Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
)"
```

**Digest selection rules** (cap the Highlights list at 6 bullets; when more candidates exist, keep the most user-visible):

| Include | Skip |
|---------|------|
| `(breaking)` entries — always | `### Fixed` minutiae |
| New user-facing features (`### Added`) | Internal refactors and optimization details |
| Default-behavior changes (affect existing users) | Recipe transcriptions ("records ... values") |
| 1-2 representative performance numbers | Docs reorganization entries |

The tag points at this commit, so `git log vX.Y.Z -1` shows each release's headlines at a glance; the full section stays in `CHANGELOG.md` and goes verbatim into the GitHub Release body (Step 5).

### Step 3: Tag (Local)

Create an annotated tag locally with a minimal message — do not push:

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
```

In plugin-marketplace repos with per-plugin versioning (like this one), use the tool-native tag instead: `claude plugin tag plugins/<plugin>` (without `--push`) — it generates the `<plugin>--vX.Y.Z` format and validates the manifest.

## Gate: Local or Remote?

After Phase A completes, **always pause and ask the user how to proceed** — regardless of permission mode (including auto/acceptEdits). Pushing and publishing are outward-facing and hard to reverse, and the user's environment may be offline; the local phase must never auto-continue into remote actions. Use AskUserQuestion:

| Option | Action |
|--------|--------|
| Push and publish | Run Phase B, Steps 4-5 |
| Push only | Run Step 4, skip Step 5 |
| Local only | Stop here — Phase B can run later from the gate |

**Phase B runs standalone**: if the bump commit and tag already exist from a previous local-only release, skip Phase A and start directly at the gate.

## Phase B — Remote

Runs only for "Push and publish" or "Push only".

### Step 4: Push

```bash
git push && git push --tags
```

For plugin-marketplace repos that tagged with `claude plugin tag plugins/<plugin>` in Step 3, the tag already exists locally, so re-running the command with `--push` fails with "Tag ... already exists locally". Push the tag with the exact command the tagger prints instead: `git push origin refs/tags/<plugin>--vX.Y.Z` (or `git push --tags`; `--force` is only for moving a wrongly-placed tag). If the push fails (e.g. no network), Phase A's work stays intact — retry Phase B later.

### Step 5: Create GitHub Release

Go to the repository's Releases page, select tag `vX.Y.Z`, and fill in:

| Field | Content |
|-------|---------|
| **Title** | `vX.Y.Z: <one-line summary>` — draw the key theme(s) from the CHANGELOG entries. Keep it concise (~5-10 words). Examples: `v1.5.0: Industry-Standard Label Positioning`, `v1.6.1: Specs Purge & Code-Spec Compliance` |
| **Body** | CHANGELOG.md `[X.Y.Z]` section content, with citation link appended at the end |

Body template:

```markdown
<CHANGELOG.md [X.Y.Z] section content, including ### Added/Changed/Deprecated/Removed/Fixed/Security headings>

---

*See [CHANGELOG.md]({{REPO_URL}}/blob/main/CHANGELOG.md) for the full change history.*
```

**Rationale**: Full changelog content on the Release page lets readers see all changes without navigating away. The citation link at the bottom serves as an attribution reference.

## Bootstrap (First Use in a New Project)

Configuration lives in the unified `## Maestro Configuration` section of the project's CLAUDE.md, shared with the other maestro skills. On first use in a project:

1. Grep CLAUDE.md for `## Maestro Configuration` and for `{{AI_MODEL_NAME}}`, `{{AI_MODEL_EMAIL}}`, `{{PACKAGE_NAME}}`, `{{REPO_URL}}` definition lines and the `### Version Bump Locations` table.
2. If the section or the lines are missing, add what's missing — create the section at the end of CLAUDE.md containing just the lines below, or append the lines inside an existing section (table last). If CLAUDE.md does not exist, create it with just this section. In either case, detect what you can from the project: `git remote get-url origin` for the repo URL; `pyproject.toml` with a package directory → `{{PACKAGE_NAME}} = <package>`, otherwise `{{PACKAGE_NAME}} = none`; `grep -rn 'X.Y.Z' pyproject.toml <package>/` or a bare `VERSION` file for version locations. Ask the user for `{{AI_MODEL_NAME}}` / `{{AI_MODEL_EMAIL}}` rather than guessing, and tell the user what was detected.
3. If the lines are present — inside or outside the section (legacy `## Release Configuration` format) — use the existing values unchanged. If they sit outside the section, tell the user to merge them into `## Maestro Configuration`.

```markdown
{{AI_MODEL_NAME}} = <model-name>
{{AI_MODEL_EMAIL}} = <model-email>
{{REPO_URL}} = <repo-url>
{{PACKAGE_NAME}} = <package-name|none>

### Version Bump Locations

| # | File | Field |
|---|------|-------|
| 1 | `pyproject.toml` | `version = "X.Y.Z"` |
| 2 | `<package>/__init__.py` | `__version__ = "X.Y.Z"` |
| 3 | `CHANGELOG.md` | `## [X.Y.Z] - YYYY-MM-DD` section header |
```

**Degraded mode**: if configuration cannot be added, use the detected values per-invocation and state them in the output. Never block the release over missing configuration.

## Required Configuration

Defined in the project's CLAUDE.md, `## Maestro Configuration` section (unified with the other maestro skills — shared variables are defined once at the section top):

| Item | Purpose | Example |
|------|---------|---------|
| `{{AI_MODEL_NAME}}` / `{{AI_MODEL_EMAIL}}` | `Co-Authored-By` model line in bump commit; the agent-tool line is fixed to `Claude Code <noreply@anthropic.com>` | `DeepSeek-V4-Pro` / `noreply@deepseek.com` |
| `{{PACKAGE_NAME}}` | Locate `__init__.py` version field; `none` for projects without a Python package | `dataflow` |
| `{{REPO_URL}}` | CHANGELOG citation link in Release body | `https://github.com/owner/repo` |
| Version bump locations table | Which files carry the version string | `### Version Bump Locations` subsection of `## Maestro Configuration` |
