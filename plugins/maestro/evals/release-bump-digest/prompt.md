---
max_turns: 25
allowed_tools: [Bash, Write, Edit, Skill]
---
The current directory is empty. Set up a minimal project and run a local release (Phase A only):

1. git init; configure the identity (user.name "Eval Bot", user.email eval@example.com).
2. Create VERSION containing `1.0.0`, and a CHANGELOG.md whose `## [Unreleased]` section contains EXACTLY these twelve `### Added` entries (copy them verbatim):
   - **Streaming dataset sampler**: the sampler interleaves shards online with a seeded RNG, removing the startup shuffle stall on multi-shard datasets.
   - **Mixed-precision policy matrix**: `--amp` resolves a per-op dtype policy from the engine, so fp16/fp32 boundary ops no longer need per-model overrides.
   - **Checkpoint warm-start**: `--warm-start` loads optimizer and scheduler state alongside weights, resuming long schedules without the first-epoch lr spike.
   - **Label validation pass**: the loader validates label indices against the class count at scan time, reporting offending files instead of failing mid-epoch.
   - **Augmentation budget**: `--aug-budget` caps the per-image transform count by a cost model, keeping tail images within the p99 batch time.
   - **Triton kernel fallback**: fused kernels fall back to torch ops on unsupported backends automatically, with a one-time warning instead of a crash.
   - **Profiler traces**: `--profile` writes chrome-trace JSON per step with kernel-level annotations, replacing the previous wall-clock-only summary.
   - **Metric aggregation revamp**: AP computation now uses area interpolation everywhere, removing the last float-ordering divergence between eval and training metrics.
   - **Multi-node launcher**: `scripts/launch.py` orchestrates torchrun-style multi-node starts with per-rank log capture and automatic barrier recovery.
   - **Export manifest**: exported artifacts now carry a manifest JSON with input shape, dtype policy and quantization metadata, so downstream serving can validate before loading.
   - **LR finder**: `--lr-find` runs a one-epoch sweep and writes the suggested learning rate plus its loss curve to the run directory.
   - **Gradient checkpointing**: `--grad-checkpoint N` recomputes every Nth block, trading step time for a 40% activation peak reduction.
   Followed by a `## [1.0.0] - 2026-01-01` section with one `### Added` entry: **Initial release**.
3. Commit everything with a plain message, then `git tag v1.0.0`.
4. Now run the local release phase only: determine the next version, bump all version locations, commit the bump, and tag it locally. Stop at the gate — do not push, do not publish a GitHub Release, and do not ask the user how to proceed.

There is no CLAUDE.md and no project configuration anywhere; use degraded-mode fallbacks rather than asking. Actually run the commands.
