# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

claude-skills is a Claude Code plugin marketplace hosting the `maestro` plugin — reusable development workflow skills (`/maestro:spec`, `/maestro:commit`, `/maestro:release`, `/maestro:claude`) distributed via plugin install instead of copied files.

## Key Conventions

- **Skills live in** `plugins/maestro/skills/<name>/SKILL.md`; each skill ends with "Bootstrap" (first-use config auto-setup) and "Required Configuration" sections
- **Version gates updates**: every user-facing change bumps `version` in `plugins/maestro/plugin.json`, otherwise users never receive the change (`/plugin update` skips unchanged versions)
- **CHANGELOG discipline**: every user-facing commit updates the `[Unreleased]` section in the same commit; subsections ordered Added → Changed → Fixed → Removed → Security → Docs; breaking changes marked `(breaking)`
- **Validate before commit**: `claude plugin validate .`
- **Test locally**: `claude --plugin-dir plugins/maestro` loads the plugin without installing
- **Skill changes hot-reload** in-session; changes to `hooks/` or `plugin.json` need `/reload-plugins`

## AI Model Configuration

{{AI_MODEL_NAME}} = DeepSeek-V4.0
{{AI_MODEL_EMAIL}} = noreply@deepseek.com
