# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

claude-skills is a Claude Code plugin marketplace hosting two plugins, distributed via plugin install instead of copied files: `maestro` — reusable development workflow skills (`/maestro:spec`, `/maestro:commit`, `/maestro:release`, `/maestro:claude`); `dataflow` — the dataflow-cv library usage skill (`/dataflow:dataflow-cv`).

## Key Conventions

- **Skills live in** `plugins/<plugin>/skills/<name>/SKILL.md`; each skill ends with "Bootstrap" (first-use config auto-setup) and "Required Configuration" sections
- **Version gates updates**: every user-facing change bumps `version` in `plugins/maestro/plugin.json`, otherwise users never receive the change (`/plugin update` skips unchanged versions)
- **CHANGELOG discipline**: every user-facing commit updates the `[Unreleased]` section in the same commit; subsections are the six Keep a Changelog types in spec order — Added → Changed → Deprecated → Removed → Fixed → Security; `docs:` commits skip CHANGELOG unless user-visible (then `### Changed`); breaking changes marked `(breaking)`
- **Validate before commit**: `claude plugin validate .`
- **Test locally**: `claude --plugin-dir plugins/maestro` loads the plugin without installing
- **Skill development & optimization**: new skills and optimizations follow the evaluation-driven methodology in `docs/creating-a-skill.md` (description trigger optimization + behavioral eval loop, per the official `skill-creator` plugin)
- **Skill changes hot-reload** in-session; changes to `hooks/` or `plugin.json` need `/reload-plugins`

## AI Model Configuration

{{AI_MODEL_NAME}} = DeepSeek-V4-Pro
{{AI_MODEL_EMAIL}} = noreply@deepseek.com

## Release Configuration

This repository has **no repo-level version** — each plugin versions independently and releases separately. Full rules: `docs/release-versioning.md`.

| # | File | Field |
|---|------|-------|
| 1 | `plugins/maestro/plugin.json` | `version = "X.Y.Z"` (bumped when maestro skills change; own sequence) |
| 2 | `plugins/dataflow/plugin.json` | `version = "X.Y.Z"` (mirrors the dataflow-cv version the skill documents; skill-side fixes bump the patch digit) |
| 3 | `CHANGELOG.md` | `## [<plugin>-X.Y.Z] - YYYY-MM-DD` header (same version as the released plugin) |

Release flow (per plugin): bump its `plugin.json` → write its CHANGELOG header → tag `<plugin>-vX.Y.Z` → GitHub Release `<plugin> vX.Y.Z`.

{{REPO_URL}} = https://github.com/zjykzj/claude-skills
