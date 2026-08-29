# Creating a Skill

A skill is the unit of reusable guidance in the `maestro` plugin. This guide covers what skills are for, the exact format they must follow, and the procedure for adding one to the plugin.

## Purpose: what skills are for

Each skill encodes a repeatable development procedure as instructions Claude invokes on demand, namespaced as `/maestro:<name>`:

| Skill | Encodes |
|-------|---------|
| `/maestro:spec` | SDD (spec-first development) methodology + an enforcement hook |
| `/maestro:commit` | Conventional commit format + CHANGELOG maintenance |
| `/maestro:release` | Semver bump + GitHub release |
| `/maestro:claude` | CLAUDE.md authoring conventions |

Skills ship as a plugin instead of copied files for four reasons:

- **Distribution with updates**: one install delivers every skill; fixes reach users via `/plugin update`, gated by the `version` field in `plugin.json`. Copied files never update.
- **Namespacing**: `/maestro:<name>` invocation cannot collide with project files or other plugins.
- **Self-configuring**: each skill ends with a Bootstrap section, so first use in a new project detects missing `{{VARIABLE}}` definitions in that project's CLAUDE.md, appends its own configuration block, and reports what it detected — no manual setup.
- **Optional, never required**: no plugin installed → nothing breaks; the skill is simply unavailable. This is the design principle of the whole plugin (see README "Design: optional, never required").

## Format

### Directory layout

Each skill lives in `plugins/maestro/skills/<name>/`:

```
plugins/maestro/skills/<name>/
├── SKILL.md        # required — frontmatter + instructions
├── scripts/        # optional — executables the skill or a hook runs
├── references/     # optional — auxiliary docs loaded as needed
├── templates/      # optional — file templates the skill writes
```

`spec` uses all three optional directories (`scripts/sdd-reminder.sh`, `references/curation-guide.md`, `templates/spec_template.md`); `commit` is the minimal case — just `SKILL.md`.

### Frontmatter (YAML, required)

```yaml
---
name: <name>
description: <when to use the skill>
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---
```

- `name` — the slash-command suffix (`/maestro:<name>`). Must be unique within the plugin.
- `description` — Claude matches a task to a skill by this text, so phrase it as "when to use" and include trigger phrases. Example from the spec skill: *"Create or modify spec files following project methodology, and drive SDD (spec-first development). Use when writing, editing, or reviewing specs/ files — and BEFORE implementing any feature or behavior change that affects a contract documented in specs/."*
- `allowed-tools` — the tool allowlist for this skill's scope.

### Body conventions

- **Actionable procedures over prose**: decision tables, classification rules, exact commands — e.g. the release skill's semver table.
- **`{{VARIABLE}}` placeholders** for per-project configuration, resolved from the project's CLAUDE.md.
- **Ends with `## Bootstrap (First Use in a New Project)`** — first-use auto-setup: grep the project's CLAUDE.md for the variables, append a configuration block if missing, and report what was detected. Include a degraded mode — never block on missing configuration.
- **Ends with `## Required Configuration`** — a table of every variable the skill consumes.

## Adding a skill: procedure

1. Create `plugins/maestro/skills/<name>/SKILL.md` following the format above.
2. Validate: `claude plugin validate .`
3. Test locally: `claude --plugin-dir plugins/maestro`, then invoke `/maestro:<name>` in-session.
4. Bump `version` in `plugins/maestro/plugin.json` — **mandatory**. `/plugin update` skips unchanged versions, so without a bump no user ever receives the new skill.
5. Add a CHANGELOG `[Unreleased]` entry in the same commit (subsection per change type: Added → Changed → Fixed → Removed → Security → Docs; breaking changes marked `(breaking)`).
6. Commit with `/maestro:commit` (conventional commit + mandatory `Co-Authored-By` line).

Reload behavior: `SKILL.md` changes hot-reload in-session; changes to `hooks/` or `plugin.json` need `/reload-plugins`.

## Evaluating and optimizing a skill

Authoring is the start, not the end. The official `skill-creator` plugin (install: `/plugin install skill-creator@anthropics/claude-plugins-official`) defines the optimization methodology — evaluation-driven, in two lines:

### Line 1: description optimization (trigger accuracy)

The frontmatter `description` is the primary trigger signal, and models tend to under-trigger skills. Optimize it against a trigger eval set:

1. Write ~20 realistic queries: 8–10 that **should** trigger the skill (varied phrasings of the same intent, including cases that never name the skill or its keywords) and 8–10 **near-miss** queries that should NOT trigger (they share keywords or concepts but need something else). Near-misses are the hard part — obviously irrelevant negatives test nothing.
2. Review the set with the user — bad eval queries lead to bad descriptions.
3. Iterate: measure the description's trigger rate on the set (run each query multiple times), propose improvements from the failures, re-test. Hold out part of the set for final selection to avoid overfitting. `skill-creator` ships `scripts/run_loop.py` to automate this loop.

### Line 2: behavioral evaluation (does the skill actually help)

1. Draft 2–3 realistic test prompts.
2. Run each with the skill and without — baseline is "no skill" for a new skill, "old version" for an improvement — and record outputs, assertions, timing, and token usage.
3. Grade assertions and open the HTML reviewer (`eval-viewer/generate_review.py`) for the human to inspect outputs and leave feedback.
4. Improve from the feedback and repeat until the user is satisfied, the feedback is empty, or no meaningful progress.

### Advanced: blind comparison

For "is the new version actually better?" questions, an independent agent judges two outputs without knowing which is which (`agents/comparator.md`) — the human review loop is usually sufficient.

### Improvement principles

- **Generalize from feedback** — the goal is a skill that works across many prompts, not one overfit to the test examples
- **Keep the prompt lean** — remove instructions that aren't pulling their weight
- **Explain the why** behind each instruction instead of piling on rigid MUSTs
- **Bundle repeated work** — if test runs repeatedly reinvent the same helper script, write it once into `scripts/`

## Bundling scripts and hooks (optional)

A skill may ship executable scripts for its own use, or register a hook in `plugins/maestro/hooks/hooks.json`. `spec` does both: `scripts/sdd-reminder.sh` is registered as a PreToolUse hook on `Edit|Write` matching `specs/` paths, resolved via `${CLAUDE_PLUGIN_ROOT}` — no project-side hook configuration needed. Commit hook scripts with the `+x` bit: hooks run them directly, not via `sh`.
