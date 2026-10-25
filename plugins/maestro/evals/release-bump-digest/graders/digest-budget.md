---
type: llm
---
The version-bump git commit body must be a digest of the CHANGELOG `[Unreleased]` section, not a transcription. The section holds twelve `### Added` entries.

PASS if the bump commit body is at most 150 words and contains at most 6 highlight bullets — i.e. it curated the twelve entries into a few highlights plus a pointer to CHANGELOG.md.
FAIL if the bump commit body transcribes all twelve entries (twelve or more bullets, 150+ words), or omits the Highlights/pointer structure entirely.
