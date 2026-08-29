# claude-skills

A [Claude Code](https://code.claude.com/docs) plugin marketplace hosting reusable development workflow skills, distributed as plugins instead of copied files.

## Structure

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog (one entry per plugin)
└── plugins/
    └── maestro/                 # Plugin: maestro
        ├── plugin.json           # Manifest (name = skill namespace prefix)
        ├── skills/               # Skills bundled in this plugin
        │   ├── spec/             #   SDD methodology + enforcement hook script
        │   ├── commit/           #   commit format + CHANGELOG maintenance
        │   ├── release/          #   version bump + GitHub release
        │   └── claude/           #   CLAUDE.md authoring, incl. development-command docs
        └── hooks/
            └── hooks.json        # PreToolUse hook: SDD reminder on specs/ edits
```

## Installation

Plugin skills are namespaced by plugin name — `/maestro:spec`, `/maestro:commit`, etc.

**One-time, per machine:**

```bash
claude plugin marketplace add zjykzj/claude-skills
claude plugin install maestro@claude-skills
```

Or in-session: `/plugin marketplace add zjykzj/claude-skills`, then `/plugin install maestro@claude-skills`.

**Per-project enablement:** projects opt in by committing this to their `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "claude-skills": {
      "source": { "source": "github", "repo": "zjykzj/claude-skills" }
    }
  },
  "enabledPlugins": {
    "maestro@claude-skills": true
  }
}
```

On a fresh clone, the marketplace auto-registers once the user trusts the folder; the plugin then reports "not installed" until each user runs the install command once. Nothing breaks meanwhile.

## Design: optional, never required

These skills are **auxiliary tools**. A project develops fine without them:

- No plugin installed → no hooks, no skill invocations, no errors. Project CLAUDE.md rules are self-contained.
- Plugin installed, project not configured → each skill detects missing `{{VARIABLE}}` definitions in CLAUDE.md on first use and appends its own configuration block (see each SKILL.md's "Bootstrap" section).
- Both present → full workflow: SDD hook + skill procedures.

## Maintaining this repo

**Add a skill** to the `maestro` plugin: create `plugins/maestro/skills/<name>/SKILL.md`, then bump `version` in `plugins/maestro/plugin.json`. Users pick it up with `/plugin update`.

**Add a plugin**: create `plugins/<name>/` with its own `plugin.json`, then add an entry to `.claude-plugin/marketplace.json`. Users install it separately — plugin granularity is the unit of per-project enable/disable.

**Skill updates reach users** only after a version bump (plugin.json `version` gates updates).

## Testing locally

```bash
claude plugin validate plugins/maestro          # Manifest/schema check
claude --plugin-dir plugins/maestro             # Load directly without install
```

Run `/reload-plugins` after edits; `SKILL.md` changes hot-reload in-session, but changes to `hooks/` or `plugin.json` need a reload.
