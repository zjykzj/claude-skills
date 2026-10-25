# claude-skills

A [Claude Code](https://code.claude.com/docs) plugin marketplace hosting reusable development workflow skills, distributed as plugins instead of copied files.

## Structure

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog (one entry per plugin)
├── .github/
│   └── workflows/
│       └── plugin-eval.yml        # CI: plugin validate + eval on push
├── docs/                          # Guides: skill creation, releases, installation, skill-creator
├── plugins/
│   ├── maestro/                 # Plugin: maestro
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json       # Manifest (name = skill namespace prefix)
│   │   ├── skills/               # Skills bundled in this plugin
│   │   │   ├── spec/             #   SDD methodology + enforcement hook script
│   │   │   ├── commit/           #   commit format + CHANGELOG maintenance
│   │   │   ├── release/          #   version bump + GitHub release
│   │   │   └── claude/           #   CLAUDE.md authoring, incl. development-command docs
│   │   ├── evals/                # Plugin eval suites (claude plugin eval)
│   │   └── hooks/
│   │       └── hooks.json        # PreToolUse hook: SDD reminder on specs/ edits
│   └── dataflow/                # Plugin: dataflow (version mirrors dataflow-cv)
│       ├── .claude-plugin/
│       │   └── plugin.json       # Manifest (name = skill namespace prefix)
│       ├── skills/
│       │   └── dataflow-cv/      #   dataflow-cv library usage skill
│       └── evals/                # Plugin eval suites (claude plugin eval)
└── README.md / README.zh-CN.md   # Bilingual READMEs, kept in sync
```

## Installation

Plugin skills are namespaced by plugin name — `/maestro:spec`, `/maestro:commit`, `/dataflow:dataflow-cv`, etc.

**One-time, per machine:**

```bash
claude plugin marketplace add zjykzj/claude-skills
claude plugin install maestro@claude-skills
claude plugin install dataflow@claude-skills
```

Or in-session: `/plugin marketplace add zjykzj/claude-skills`, then `/plugin install maestro@claude-skills` (or `dataflow@claude-skills`).

**Per-project config (optional):** the install above is per-machine and applies to every project — no per-project config is required. Two optional aids exist:

- **CLAUDE.md**: document the install command in the project's CLAUDE.md so contributors find it. This is the recommended approach.
- **Team repos**: committing `.claude/settings.json` with `extraKnownMarketplaces` + `enabledPlugins` auto-registers the marketplace for clones (after workspace trust) and signals plugin use — installation still requires each user to run the install command once.

Neither is needed for the plugin to work; nothing breaks when the plugin is absent.

## Design: optional, never required

These skills are **auxiliary tools**. A project develops fine without them:

- No plugin installed → no hooks, no skill invocations, no errors. Project CLAUDE.md rules are self-contained.
- Plugin installed, project not configured → each skill detects missing `{{VARIABLE}}` definitions in CLAUDE.md on first use and appends its own configuration block (see each SKILL.md's "Bootstrap" section).
- Both present → full workflow: SDD hook + skill procedures.

## Maintaining this repo

**Add a skill** to the `maestro` plugin: create `plugins/maestro/skills/<name>/SKILL.md`, then bump `version` in `plugins/maestro/.claude-plugin/plugin.json`. Users pick it up with `/plugin update`. See [docs/creating-a-skill.md](docs/creating-a-skill.md) for the skill format and full procedure.

**Develop or optimize a skill** evaluation-driven: description trigger optimization plus a with/without behavioral eval loop, per the official `skill-creator` plugin (`/plugin install skill-creator@anthropics/claude-plugins-official`). Full methodology in [docs/creating-a-skill.md](docs/creating-a-skill.md).

**Run skill evals**: suites live in `plugins/<plugin>/evals/` — run `claude plugin eval plugins/<plugin>` locally (each case is a billed model call). CI (`.github/workflows/plugin-eval.yml`) runs `claude plugin validate` + `claude plugin eval` on push to `plugins/**` (the eval job needs the `ANTHROPIC_API_KEY` repo secret).

**Add a plugin**: create `plugins/<name>/` with its own `.claude-plugin/plugin.json`, then add an entry to `.claude-plugin/marketplace.json`. Users install it separately — plugin granularity is the unit of per-project enable/disable.

**Release a plugin**: per-plugin versioning — each plugin bumps, tags (`<plugin>--vX.Y.Z`), and releases separately; see [docs/release-versioning.md](docs/release-versioning.md).

**Install / update / query plugins**: how `plugin@marketplace` resolves (marketplace HEAD + `plugin.json` version, not GitHub Releases) and the full command surface; see [docs/plugin-installation.md](docs/plugin-installation.md).

**Skill updates reach users** only after a version bump (plugin.json `version` gates updates).

## Testing locally

```bash
claude plugin validate plugins/maestro          # Manifest/schema check
claude plugin eval plugins/maestro              # Run the plugin's eval suites (billed model calls)
claude --plugin-dir plugins/maestro             # Load directly without install
```

Run `/reload-plugins` after edits; `SKILL.md` changes hot-reload in-session, but changes to `hooks/` or `plugin.json` need a reload. Eval results land in `plugins/<plugin>/evals/results/` (gitignored).

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 zjykzj.
