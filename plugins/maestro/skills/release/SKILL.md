---
name: release
description: Bump the project version and publish a GitHub release. Use when releasing a new version, and whenever the user asks anything about the release process — which semver bump to pick from the commit history, version bump locations, the release commit message format, tagging and pushing the release, or renaming the CHANGELOG [Unreleased] section — even if they only ask a question rather than request a release.
allowed-tools: Bash, Read, Edit, Grep
---

# Release Skill

Use this skill when bumping the project version and publishing a GitHub release.

## Step 0: Determine Version Number

Review `git log` since the last tag. Classify each commit's conventional commit type into semver:

| Commit Type(s) | Semver | Example |
|---------------|--------|---------|
| `fix:`, `docs:`, `refactor:`, `style:`, `chore:`, `test:`, `ci:`, `build:` | **PATCH** (1.6.1 → 1.6.2) | Bug fix, doc update, internal restructure |
| `feat:` | **MINOR** (1.6.2 → 1.7.0) | New public API, new CLI flag, new feature |
| `feat!:` or `BREAKING CHANGE` in commit body | **MAJOR** (1.7.0 → 2.0.0) | Remove public API, change default behavior |

**Rule:** the highest-severity commit wins. If all commits are `docs`/`refactor`/`chore` → PATCH. If any `feat` → MINOR. If any breaking change → MAJOR.

**Concrete check:** before picking a version, look at the `## [Unreleased]` section you're about to rename. If `### Added` is empty (no new features) → PATCH. If any entry is marked `(breaking)` → MAJOR.

## Step 1: Bump Version

Update **all** version locations configured for this project. See the `### Version Bump Locations` table in the `## Maestro Configuration` section of CLAUDE.md for the exact file paths — typical patterns include:

| Pattern | Example File | Field |
|---------|-------------|-------|
| Package init | `{{PACKAGE_NAME}}/__init__.py` | `__version__ = "X.Y.Z"` |
| Project config | `pyproject.toml` | `version = "X.Y.Z"` |
| Version file | `VERSION` | `X.Y.Z` (bare string, no field syntax) |
| Changelog | `CHANGELOG.md` | Rename `## [Unreleased]` → `## [X.Y.Z] - YYYY-MM-DD`, then add a fresh empty `## [Unreleased]` at the top |

The `{{PACKAGE_NAME}}` variable is defined in CLAUDE.md — `none` for projects without a Python package (bare `VERSION` file projects).

**CHANGELOG rename, not rewrite**: the commit skill maintains `## [Unreleased]` on every commit, so the release does not write new entries. Rename the section header and reset it — the section content flows unchanged into the version bump commit (Step 2) and the GitHub Release body (Step 5).

## Step 2: Commit

Use the version bump commit format — body **must** include the relevant section from `CHANGELOG.md`:

```bash
git commit -m "$(cat <<'EOF'
chore: bump version to X.Y.Z

<CHANGELOG.md [X.Y.Z] section content, omitting the ### headers>

Co-Authored-By: {{AI_MODEL_NAME}} <{{AI_MODEL_EMAIL}}>
EOF
)"
```

This ensures `git log --oneline --no-decorator` provides enough context to understand each release's contents without opening `CHANGELOG.md`.

## Step 3: Tag

Create an annotated tag with a minimal message:

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
```

## Step 4: Push

```bash
git push && git push --tags
```

## Step 5: Create GitHub Release

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
| `{{AI_MODEL_NAME}}` / `{{AI_MODEL_EMAIL}}` | `Co-Authored-By` line in bump commit | `DeepSeek-V4-Pro` / `noreply@deepseek.com` |
| `{{PACKAGE_NAME}}` | Locate `__init__.py` version field; `none` for projects without a Python package | `dataflow` |
| `{{REPO_URL}}` | CHANGELOG citation link in Release body | `https://github.com/owner/repo` |
| Version bump locations table | Which files carry the version string | `### Version Bump Locations` subsection of `## Maestro Configuration` |
