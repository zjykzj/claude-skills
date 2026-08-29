# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **`sdd-reminder.sh` lacked the executable bit**: plugin hooks run the script directly (no `sh`), so a non-executable script fails with "Permission denied" and can block Edit/Write tool calls. Script is now committed with `+x`.

### Added

- **Initial marketplace with the `workflow` plugin** (breaking): the five skills (spec, dev, commit, release, claude) extracted from DataFlow-CV now ship as one plugin instead of copied files. Skills are invoked namespaced as `/workflow:<skill>`. The SDD enforcement PreToolUse hook is bundled in the plugin and resolved via `${CLAUDE_PLUGIN_ROOT}` — no project-side hook setup.
