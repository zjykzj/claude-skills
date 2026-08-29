# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0] - 2026-08-29

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
