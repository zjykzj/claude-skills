---
type: llm
focus: trace
---
Locate the actual `git commit` command the agent ran (ignore the skill content echoed in Skill tool results).

PASS if that commit message ends with exactly two `Co-Authored-By` trailer lines — a model line and the `Claude Code <noreply@anthropic.com>` line.
FAIL if the commit lacks the two `Co-Authored-By` trailer lines, or has only one.
