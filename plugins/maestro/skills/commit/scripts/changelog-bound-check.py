#!/usr/bin/env python3
"""CHANGELOG entry bound check — PreToolUse hook payload consumer.

Reads the harness tool-input JSON from stdin. If the edited file is CHANGELOG.md,
scans the incoming bullet lines ("- " entries) against the commit skill's hard bound
(one physical line, <=3 sentences, <=400 characters) and exits 2 when any bullet
exceeds it, naming the offenders on stderr. Exit 0 otherwise — including on parse
errors, so tooling problems never block an edit (fail open).
"""

import json
import sys

MAX_CHARS = 400


def _check() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0  # fail open on malformed input
    tool_input = payload.get('tool_input') or {}
    path = tool_input.get('file_path', '')
    if not path.endswith('CHANGELOG.md'):
        return 0
    # Write carries the whole content; Edit carries the replacement text.
    text = tool_input.get('content') or tool_input.get('new_string') or ''
    offenders = []
    for i, line in enumerate(text.splitlines(), start=1):
        if line.startswith('- ') and len(line) > MAX_CHARS:
            offenders.append('  line %d: %d chars — %.80s…' % (i, len(line), line))
    if not offenders:
        return 0
    print(
        'CHANGELOG entry bound exceeded: %d bullet(s) over %d characters '
        '(bound: one physical line, <=3 sentences, <=%d chars; root cause, '
        'measurements and test names belong in the commit body):'
        % (len(offenders), MAX_CHARS, MAX_CHARS),
        file=sys.stderr,
    )
    print('\n'.join(offenders), file=sys.stderr)
    print(
        'Compress the entry and retry. Essay-length entries already in the file are '
        'pre-4.3.0 legacy output and are not precedent — trim them too.',
        file=sys.stderr,
    )
    return 2


if __name__ == '__main__':
    try:
        sys.exit(_check())
    except Exception:
        sys.exit(0)  # fail open on anything unexpected
