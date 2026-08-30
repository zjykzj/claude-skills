# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Docs

- **Per-plugin versioning and release rules adopted**: this repository no longer has a repo-level version — each plugin versions independently (`maestro` evolves on its own sequence; `dataflow` mirrors the dataflow-cv version it documents). CHANGELOG headers are plugin-scoped (`## [<plugin>-X.Y.Z]`), tags are plugin-prefixed (`<plugin>-vX.Y.Z`), and GitHub Releases are per plugin. Full rules: `docs/release-versioning.md`.

## [dataflow-2.0.1] - 2026-08-30

### Fixed

- **`dataflow-cv` skill description broke YAML parsing**: the `: ` after `(v2.0.0+)` in the frontmatter description was parsed as a YAML mapping separator by GitHub's frontmatter renderer ("mapping values are not allowed in this context"). Replaced with an em dash; plugin version bumped to 2.0.1.

## [dataflow-2.0.0] - 2026-08-30

### Added

- **`dataflow` plugin with the `dataflow-cv` skill**: CLI command tree (analyse/convert/visualize/evaluate), Python API reference, canonical examples (`assets/test_data/`), and known gotchas for the DataFlow-CV library. Gated on `dataflow-cv>=2.0.0` via a version-check step inside the skill.

## [maestro-3.0.1] - 2026-08-29

### Fixed

- **Skill trigger descriptions optimized for `spec`, `commit`, and `release`**: descriptions now cover question-type requests (workflow, format, classification) instead of only action requests. Evaluated with 20-query trigger eval sets per skill; should-trigger recall improved from 66% → 96% (spec), 45% → 100% (commit), 85% → 100% (release) with zero near-miss regressions. `claude` was already at 100% and is unchanged.
- **Marketplace catalog description listed the removed `dev` skill**: `.claude-plugin/marketplace.json` now matches the plugin manifest's skill list (spec, commit, release, claude).

### Docs

- **Chinese README added**: `README.zh-CN.md` mirrors the English README (structure, installation, design, maintenance, local testing).
- **skill-creator study guide added**: `docs/skill-creator.md` (Chinese) explains the tool's purpose, principles (progressive disclosure, dual-run baselines, quantitative benchmarks, description optimization), and full operating loop, with links to the canonical upstream SKILL.md.
- **docs/ converted to Chinese**: `docs/creating-a-skill.md` translated to Chinese (technical terms, paths, and commands kept in English); docs/ is now uniformly Chinese.
- **Skill creation guide added**: new `docs/creating-a-skill.md` covering the skill format (frontmatter, Bootstrap/Required Configuration sections), its purpose (plugin-distributed, self-configuring, optional), and the add-a-skill procedure (validate, test, version bump, CHANGELOG). README links to it.
- **Skill optimization methodology documented**: `docs/creating-a-skill.md` now covers the evaluation-driven optimization loop (description trigger optimization + with/without behavioral eval) per the official `skill-creator` plugin; README and CLAUDE.md point to it.

## [maestro-3.0.0] - 2026-08-29

### Added

- **Initial marketplace with the `workflow` plugin** (breaking): the five skills (spec, dev, commit, release, claude) now ship as one plugin instead of copied files. Skills are invoked namespaced as `/workflow:<skill>`. The SDD enforcement PreToolUse hook is bundled in the plugin and resolved via `${CLAUDE_PLUGIN_ROOT}` — no project-side hook setup.

### Changed

- **Plugin renamed from `workflow` to `maestro`** (breaking): `workflow` collides with an existing plugin in the community marketplace. The skill namespace prefix changes from `/workflow:` to `/maestro:`. Existing installs must uninstall the old plugin and install `maestro@claude-skills`.

### Fixed

- **`sdd-reminder.sh` lacked the executable bit**: plugin hooks run the script directly (no `sh`), so a non-executable script fails with "Permission denied" and can block Edit/Write tool calls. Script is now committed with `+x`.

### Removed

- **`dev` skill removed from the plugin** (breaking): the generic Python toolchain guidance now lives in the `/maestro:claude` skill, which documents development commands (test/lint/typecheck) directly in each project's CLAUDE.md. Projects that used `/maestro:dev` should move their commands into a self-contained "Development Commands" section in CLAUDE.md.

### Docs

- **Per-project config guidance revised**: the project-level `.claude/settings.json` recipe is now documented as an optional team aid; the recommended path is documenting install steps in the project's CLAUDE.md. Added a CLAUDE.md for this repository (conventions, version-gating rule, AI model configuration).
- **MIT license added**: LICENSE file (copyright zjykzj), the `license` field in `plugin.json`, and a License section in README.md.
- **AI model config updated to `DeepSeek-V4-Pro`**: `{{AI_MODEL_NAME}}` now matches the model powering the session; commit `Co-Authored-By` lines read `DeepSeek-V4-Pro <noreply@deepseek.com>`.
- **Release Configuration section added to CLAUDE.md**: documents the version bump locations (`plugins/maestro/plugin.json`, `CHANGELOG.md`) and `{{REPO_URL}}` consumed by the release skill.
