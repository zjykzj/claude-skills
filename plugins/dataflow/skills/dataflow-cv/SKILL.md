---
name: dataflow-cv
description: Use the dataflow-cv library (v3.6.0+) — CLI commands (analyse stats/split/filter/partition/sample (stats --kpts-config), convert yolo2coco/yolo2labelme/labelme2yolo/labelme2coco/coco2yolo/coco2labelme with --pose/--kpts-config/--save-kpts-config, visualize yolo/labelme/coco with --pose/--kpts-config, evaluate detection/segmentation/keypoints with --prf1) and Python API (label handlers with pose keypoints, Keypoints model, 5 analysers, 3 converters, 3 visualizers, 2 evaluators, compute_pr_f1, LogConfig/LogManager). Use when working with dataflow-cv — building dataset pipelines, converting YOLO/LabelMe/COCO annotations, evaluating detections, debugging dataflow-cv errors — and whenever the user asks anything about dataflow-cv — CLI usage, API signatures, metric computation, format conversion rules, or install extras — even if they only ask a question rather than request an action. Do not use for other CV libraries, generic OpenCV usage, or general numpy questions.
allowed-tools: Bash, Read
---

# DataFlow-CV Skill

Reference for operating the dataflow-cv library (v3.6.0+): dataset analysis, format conversion, visualization, and evaluation across YOLO, LabelMe, and COCO annotation formats, via CLI and Python API. Pose (keypoint) support: read/write/convert/visualize/evaluate in all three formats (convert since 3.4.0, evaluate since 3.5.0).

## When to Use

- Building or debugging dataset pipelines that involve dataflow-cv
- Converting YOLO/LabelMe/COCO annotations, including YOLO model prediction files
- Analysing datasets (stats / split / filter / partition / sample)
- Visualizing annotations or evaluating detections/segmentations (mAP or P/R/F1)
- Answering any question about dataflow-cv — usage, formats, metrics, install — question-only requests count

## Step 0: Version Check (Mandatory)

Before executing anything:

```bash
python -c "from importlib.metadata import version; print(version('dataflow-cv'))"
```

| Situation | Action |
|---|---|
| Not installed | Offer install: `pip install dataflow-cv` (add the `[coco]` extra for pycocotools features). Answer from this document; execute nothing. |
| `< 3.6.0` | Warn that this skill documents the 3.6.0 surface; suggest `pip install -U "dataflow-cv>=3.6.0"`. Degraded mode: proceed, but re-verify every flag with `--help` before composing commands. |
| `>= 3.3.0` | Proceed. |

Extras: `[coco]` installs pycocotools — required for `evaluate` and `--do-rle`; `[dev]` = test/lint stack.

## CLI Command Tree

`dataflow-cv <group> <subcommand> [options]`

- `analyse` — `stats` · `split` · `filter` · `partition` · `sample`
- `convert` — `yolo2coco` · `yolo2labelme` · `labelme2yolo` · `labelme2coco` · `coco2yolo` · `coco2labelme`
- `visualize` — `yolo` · `labelme` · `coco`
- `evaluate` — `detection` · `segmentation`

**Hard rule**: `dataflow-cv <group> <subcommand> --help` is the authoritative option list. Run it before composing any command — never hardcode options from memory.

Common options: `--verbose` (enable per-module file logging to `./logs/`), `--log-dir DIR`, `--no-strict` (convert/visualize only; skip invalid annotations), `--display/--no-display` (visualize).

Editable-install alternative to `dataflow-cv`: `python -m dataflow.cli` (3.1.0+; `dataflow/cli/__main__.py` exists).

## CLI Workflows

### Analyse

- `stats LABEL_PATH...` — per-class counts; auto-detects format (single `.json` file = COCO; directory of `.txt` = YOLO; directory of `.json` = LabelMe); multiple paths merge; `-R/--recursive`, `--sort-by id|count`, `--descending`, `-c/--class-file`; `--kpts-config` adds a keypoint statistics section (per-class labeled/visible ratios + per-keypoint rates; for YOLO sources it also enables pose-row parsing) (3.6.0)
- `split OUTPUT_DIR -l LABEL_DIR [-i IMAGE_DIR]` — train/val split; `-r/--ratio` (default 0.8), `-s/--seed` 42, `--move` (confirmation prompt). YOLO/LabelMe only.
- `filter LABEL_PATH ORIG_CLASSES NEW_CLASSES OUTPUT_DIR` — keep listed classes, remap class IDs to NEW_CLASSES order. No `--class-file` option (3.1.0: removed — it was a dead no-op; class files are the positional args).
- `partition OUTPUT_DIR -n NUM -l LABEL_DIR [-i IMAGE_DIR]` — N-way split; `--shuffle`, `--seed`, `--move`. YOLO/LabelMe only.
- `sample OUTPUT_DIR -n COUNT -l LABEL_DIR [-i IMAGE_DIR]` — collect N files; `--shuffle` (default) / `--no-shuffle`, `--seed`, `--move`. YOLO/LabelMe only.

YOLO/LabelMe are directories, COCO is a single JSON file — subcommands that need directories reject COCO (check `--help`). Analyse is always non-strict (read-only, lenient).

### Convert

Six directions, source → target as named. Positional args for `yolo2coco`: `IMAGE_DIR LABEL_DIR CLASS_FILE OUTPUT_FILE` (per-file targets take `OUTPUT_DIR`).

- `--prediction` exists **only on `yolo2coco`** — input YOLO lines carry a confidence token (6 tokens detection / even tokens segmentation); output is a plain JSON list of annotation dicts (Variant B, pycocotools `loadRes()`-compatible)
- `--do-rle` (yolo2coco / labelme2coco) needs the `[coco]` extra
- `--save-crowd` (coco2yolo / coco2labelme) writes `iscrowd=1` annotations as ordinary rows/shapes — the default skips them (3.2.0; previously written silently)
- `--no-strict` skips invalid annotations instead of failing
- COCO-source converters (`coco2yolo` / `coco2labelme`) name per-file outputs by the image `file_name` stem — leading zeros kept, subdirectories flattened with a warning, empty `file_name` falls back to the numeric id (3.0.0; previously the numeric image id, breaking)
- **Pose conversion** (3.4.0): `--pose` on all six subcommands converts keypoints; without it, keypoints are dropped with a warning per image. `--kpts-config` feeds COCO category names/skeleton + LabelMe point labels (placeholders when absent); `--save-kpts-config` (coco2yolo / coco2labelme) exports a definition-YAML sidecar. Pose mode skips objects without keypoints and drops segmentation for YOLO targets; `yolo2coco --prediction --pose` writes `keypoints` + `num_keypoints` + `score`.

### Visualize

- `visualize yolo IMAGE_DIR LABEL_DIR CLASS_FILE` · `visualize labelme IMAGE_DIR LABEL_DIR` · `visualize coco IMAGE_DIR COCO_FILE`
- `--save DIR` writes rendered images; `--no-display` for headless (pair both)
- Pose (3.3.0): `visualize yolo --pose --kpts-config KPT_YAML` and `visualize labelme --kpts-config KPT_YAML` render keypoints (v=2 filled green, v=1 hollow orange) + class-color skeleton lines; COCO reads the skeleton from its own categories (no flag needed)
- Interactive keyboard: `←/↑` prev, `→/↓/Enter/Space` next, `s` snapshot, `h` hints, `q/ESC` quit (window close button may not work — use keyboard)

### Evaluate

- `evaluate detection GT_JSON DT_JSON` — bbox IoU; `evaluate segmentation GT_JSON DT_JSON` — mask IoU; `evaluate keypoints GT_JSON DT_JSON` — OKS (3.5.0), `--kpts-config` supplies per-keypoint sigmas (fallback: COCO 17-keypoint official, then uniform 0.05 + warning)
- Two mutually exclusive paths per invocation: mAP/AR via COCOeval (default) or `--prf1` (single-threshold P/R/F1; `--prf1-iou` 0.5, `--prf1-conf` 0.0 — both must be ∈ [0, 1], `--prf1-method macro|micro`). Run twice to get both.
- Requires `[coco]`. GT = full COCO dict. DT = COCO dict or plain list of annotation dicts; DT annotations must carry `score` and `area`
- `-o/--output FILE` dumps JSON results — mAP path saves `EvaluationResult`; with `--prf1` saves `PRF1Result` (3.1.0+; previously silently ignored)

## Python API

```python
from dataflow.util import LogConfig, LogManager
log = LogManager(LogConfig(name="job", verbose=True, log_dir=Path("./logs")))

# Handlers (dataflow.label): read() = batch DatasetAnnotations; iter_images() = streaming
from dataflow.label import YoloAnnotationHandler, LabelMeAnnotationHandler, CocoAnnotationHandler, Keypoints
h = YoloAnnotationHandler(label_dir, class_file, image_dir, pose=True, logger=log.logger)
# Keypoints: points (native coords) + parallel visibility (0/1/2); count_labeled() -> COCO num_keypoints
# LabelMe pose: point shapes + rectangle sharing group_id; kpts_config YAML orders keypoints

# Analysers (dataflow.analyse): Stats / Split / Filter / Partition / SampleAnalyser
from dataflow.analyse import StatsAnalyser
r = StatsAnalyser(log_config=log).analyse(["labels/"], class_file="classes.txt")

# Converters (dataflow.convert): YoloAndCocoConverter / LabelMeAndYoloConverter / CocoAndLabelMeConverter
from dataflow.convert import YoloAndCocoConverter
YoloAndCocoConverter("yolo", "coco", log_config=log).convert(source_path, target_path, class_file="classes.txt")

# Visualizers (dataflow.visualize): YOLO / LabelMe / COCOVisualizer (kwargs: is_show, is_save, output_dir)

# Evaluators (dataflow.evaluate): DetectionEvaluator / SegmentationEvaluator / compute_pr_f1
from dataflow.evaluate import compute_pr_f1
r = compute_pr_f1(gt_source, dt_source, iou_threshold=0.5, confidence_threshold=0.0,
                  iou_type="bbox", method="macro")  # -> PRF1Result
```

All module constructors accept `log_config: Optional[LogConfig] = None`.

## Canonical Examples

```bash
# Stats (auto-detects format)
dataflow-cv analyse stats images/ labels/ --class-file classes.txt

# Conversion (label)
dataflow-cv convert yolo2coco --verbose images/ yolo_labels/ classes.txt /tmp/out.json

# Conversion (model predictions -> COCO list)
dataflow-cv convert yolo2coco --prediction --verbose images/ yolo_pred/ classes.txt /tmp/pred.json

# Visualization (headless save)
dataflow-cv visualize yolo --no-display --verbose images/ yolo_labels/ classes.txt --save /tmp/viz/

# Evaluation (mAP) and P/R/F1 (separate runs)
dataflow-cv evaluate detection --verbose gt_coco.json dt_coco.json
dataflow-cv evaluate detection --prf1 gt_coco.json dt_coco.json
```

The dataflow-cv repo ships test fixtures under `assets/test_data/` and runnable demos under `samples/` — useful for trying commands.

## Known Gotchas

- [!] Coordinate semantics depend on format: YOLO = center + normalized [0,1]; LabelMe/COCO = top-left + absolute pixels. Same `BoundingBox` class, different meaning — check `DatasetAnnotations.format`.
- [!] `--prediction` exists only on `yolo2coco`; output is a plain JSON list (Variant B) with `score`, no `id` field.
- [!] DT predictions require `score` in every annotation; `area` is required by COCOeval — fill as `bbox.width * bbox.height`.
- [!] RLE counts are latin-1 bytes — never utf-8 when round-tripping byte↔string.
- [*] `--prf1` and mAP are mutually exclusive per run — run twice to get both metrics.
- [*] `--move` (split/partition/sample) prompts for confirmation before relocating files.
- [*] Exit codes: 0 success, 2 input error (bad paths/params), 4 runtime API failure.
- [*] `--verbose` gates file logs (`./logs/`); console output is `click.echo`.
- [*] Convert logs an `Output layout:` summary after every conversion (3.0.0+).
- [*] Strict mode is default: invalid annotations raise; `--no-strict` skips and continues (convert/visualize only — analyse is always non-strict). Exception: **image errors always skip with a warning in both modes** (3.1.0) — one corrupt image never fails the whole dataset.
- [*] `CocoAnnotationHandler(do_rle=None)` auto-detects output format from the source on read; explicit `True`/`False` disable auto-detection (3.1.0 — `do_rle=False` previously still auto-switched to RLE for RLE sources).
- [*] Verbose per-class P/R/F1 come from the single max-F1 operating point (3.1.0 — previously an unreachable max-P + max-R combination).
- [*] Analyse never raises for data issues — missing paths return an error result (3.1.0 — `image_dir` previously raised `FileNotFoundError`).
- [!] `iscrowd=1` (crowd) annotations are **skipped by default** on `coco2yolo` / `coco2labelme`; `--save-crowd` restores writing them as ordinary rows/shapes (3.2.0, breaking default).
- [*] Multi-segment COCO polygons (and all RLE contours) are merged into **one outline** at read time — rasterizing the output reproduces the source union; single-segment output stays bit-identical (3.2.0; previously concatenated, fabricating mask area).
- [*] LabelMe images may be absent without warning when the JSON has valid `imageWidth`/`imageHeight`.
- [*] YOLO prediction lines: 6 tokens detection / even tokens segmentation vs 5 / odd for labels.
- [!] YOLO pose mode is **explicit** (`pose=True` / `--pose`) — a 5+3k pose row can collide with segmentation token counts; k is fixed per dataset (3.3.0).
- [*] LabelMe pose convention (3.3.0): one instance = `point` shapes (keypoint-name labels) + a `rectangle` (class + bbox) sharing a `group_id`; the rectangle is required; a `point` without `group_id` is a parse error.
- [*] Keypoint-definition YAML (3.3.0): `keypoints` global list / `classes` per-class (X-AnyLabeling compatible) + optional `skeleton`/`sigmas`; v=0 keypoints are stored at (0, 0) and COCO `num_keypoints` is recomputed on write.
- [*] Pose conversion rules (3.4.0): pose mode enforces a dataset-wide k (first object sets it); COCO→LabelMe degrades v=1 to v=2 with a warning; `--save-kpts-config` sidecars filter out-of-range skeleton edges (the official COCO person skeleton contains index 17 for 17 keypoints).
- [*] Keypoint evaluation (3.5.0): pycocotools yields **10** stats for `iouType='keypoints'` (no small scale, maxDets=20) — `EvaluationMetrics.ar_max_20` carries the AR and the 12-metric slots stay -1.0; `compute_pr_f1(iou_type='keypoints')` treats the IoU threshold as the OKS threshold.
- [*] Keypoint statistics (3.6.0): `analyse stats --kpts-config` reports per-keypoint labeling rates — for YOLO sources the flag is required to parse pose rows at all; k consistency across objects/paths is enforced (mixed-k datasets are an error).

## Bootstrap (First Use in a New Project)

No configuration — this skill is self-contained; nothing is appended to the project CLAUDE.md. First use = run Step 0; if dataflow-cv is missing, offer the install commands and answer from this document.

## Required Configuration

None. Requirements: `dataflow-cv>=3.6.0` (Step 0); `[coco]` extra only for `evaluate` / `--do-rle`.
