#!/usr/bin/env python3
"""Release bump commit digest check — PreToolUse hook payload consumer.

Reads the harness tool-input JSON from stdin. If the Bash command is a
`git commit` for a version bump (the subject contains "bump version to"), extracts
the heredoc body and blocks (exit 2) when it exceeds the release skill's digest
budget (<=150 words after dropping the subject line and Co-Authored-By trailers),
naming the count on stderr. Exit 0 otherwise — including on parse errors, so
tooling problems never block a commit (fail open).
"""

import json
import re
import sys

MAX_WORDS = 150

_HEREDOC = re.compile(r"<<'EOF'\n(.*?)^EOF$", re.S | re.M)


def _digest_words(command: str):
    """Word count of the bump commit body, or None when unmeasurable."""
    m = _HEREDOC.search(command)
    if not m:
        return None  # not the prescribed heredoc form — nothing to measure
    lines = m.group(1).splitlines()
    if lines and 'bump version to' in lines[0]:
        lines = lines[1:]  # drop the subject line
    body = [line for line in lines if not line.startswith('Co-Authored-By:')]
    return len(' '.join(body).split())


def _check() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0  # fail open on malformed input
    tool_input = payload.get('tool_input') or {}
    command = tool_input.get('command', '')
    if 'git commit' not in command or 'bump version to' not in command:
        return 0
    words = _digest_words(command)
    if words is None or words <= MAX_WORDS:
        return 0
    print(
        'Release bump commit digest bound exceeded: %d words (bound: <=%d). '
        'The bump commit body is a digest — a 1-2 sentence theme summary, 3-6 '
        'curated Highlights bullets and a pointer to CHANGELOG.md — not a '
        'transcription of the [X.Y.Z] section; the full section goes verbatim '
        'into the GitHub Release body.'
        % (words, MAX_WORDS),
        file=sys.stderr,
    )
    print(
        'Compress the Highlights list (<=6 bullets, <=120 words total) and retry.',
        file=sys.stderr,
    )
    return 2


if __name__ == '__main__':
    try:
        sys.exit(_check())
    except Exception:
        sys.exit(0)  # fail open on anything unexpected
