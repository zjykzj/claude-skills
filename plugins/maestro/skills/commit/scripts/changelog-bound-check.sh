#!/bin/bash
# CHANGELOG entry bound enforcement — invoked by the PreToolUse hook on CHANGELOG.md edits.
# Thin wrapper: pipes the harness's stdin JSON payload into changelog-bound-check.py,
# which blocks (exit 2) when an incoming bullet exceeds the commit skill's hard bound
# (one physical line, <=3 sentences, <=400 characters), naming the offenders on stderr.
#
# Requirements: python3
#
# Ships with the maestro plugin: registered in hooks/hooks.json and resolved via
# ${CLAUDE_PLUGIN_ROOT}. No project-side hook configuration needed. cwd-independent —
# the payload arrives on stdin. Fails open (exit 0) on tooling errors, so a broken
# environment never blocks an edit.

exec python3 "$(dirname "$0")/changelog-bound-check.py"
