#!/bin/bash
# Release bump commit digest enforcement — invoked by the PreToolUse hook on Bash calls.
# Thin wrapper: pipes the harness's stdin JSON payload into digest-check.py,
# which blocks (exit 2) when a `git commit` version-bump body exceeds the release
# skill's 150-word digest budget, reporting the count on stderr.
#
# Requirements: python3
#
# Ships with the maestro plugin: registered in hooks/hooks.json and resolved via
# ${CLAUDE_PLUGIN_ROOT}. No project-side hook configuration needed. cwd-independent —
# the payload arrives on stdin. Fails open (exit 0) on tooling errors, so a broken
# environment never blocks a commit.

exec python3 "$(dirname "$0")/digest-check.py"
