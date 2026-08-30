---
name: dataflow-cv
description: Use the dataflow-cv library (v2.0.0+) — CLI commands (analyse stats/split/filter/partition/sample, convert yolo2coco/yolo2labelme/labelme2yolo/labelme2coco/coco2yolo/coco2labelme, visualize yolo/labelme/coco, evaluate detection/segmentation with --prf1) and Python API (label handlers, 5 analysers, 3 converters, 3 visualizers, 2 evaluators, compute_pr_f1, LogConfig/LogManager). Use when working with dataflow-cv — building dataset pipelines, converting YOLO/LabelMe/COCO annotations, evaluating detections, debugging dataflow-cv errors — and whenever the user asks anything about dataflow-cv — CLI usage, API signatures, metric computation, format conversion rules, or install extras — even if they only ask a question rather than request an action. Do not use for other CV libraries, generic OpenCV usage, or general numpy questions.
allowed-tools: Bash, Read
---

# DataFlow-CV Skill

Reference for operating the dataflow-cv library (v2.0.0+): dataset analysis, format conversion, visualization, and evaluation across YOLO, LabelMe, and COCO annotation formats, via CLI and Python API.

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
| `< 2.0.0` | Warn that this skill documents the 2.0.0 surface; suggest `pip install -U "dataflow-cv>=2.0.0"`. Degraded mode: proceed, but re-verify every flag with `--help` before composing commands. |
| `>= 2.0.0` | Proceed. |

Extras: `[coco]` installs pycocotools — required for `evaluate` and `--do-rle`; `[dev]` = test/lint stack.

## CLI Command Tree

`dataflow-cv <group> <subcommand> [options]`

- `analyse` — `stats` · `split` · `filter` · `partition` · `sample`
- `convert` — `yolo2coco` · `yolo2labelme` · `labelme2yolo` · `labelme2coco` · `coco2yolo` · `coco2labelme`
- `visualize` — `yolo` · `labelme` · `coco`
- `evaluate` — `detection` · `segmentation`

**Hard rule**: `dataflow-cv <group> <subcommand> --help` is the authoritative option list. Run it before composing any command — never hardcode options from memory.

Common options: `--verbose` (enable per-module file logging to `./logs/`), `--log-dir DIR`, `--no-strict` (convert/visualize only; skip invalid annotations), `--display/--no-display` (visualize).

## CLI Workflows

### Analyse

- `stats LABEL_PATH...` — per-class counts; auto-detects format (single `.json` file = COCO; directory of `.txt` = YOLO; directory of `.json` = LabelMe); multiple paths merge; `-R/--recursive`, `--sort-by id|count`, `--descending`, `-c/--class-file`
- `split OUTPUT_DIR -l LABEL_DIR [-i IMAGE_DIR]` — train/val split; `-r/--ratio` (default 0.8), `-s/--seed` 42, `--move` (confirmation prompt). YOLO/LabelMe only.
- `filter LABEL_PATH ORIG_CLASSES NEW_CLASSES OUTPUT_DIR` — keep listed classes, remap class IDs to NEW_CLASSES order
- `partition OUTPUT_DIR -n NUM -l LABEL_DIR [-i IMAGE_DIR]` — N-way split; `--shuffle`, `--seed`, `--move`. YOLO/LabelMe only.
- `sample OUTPUT_DIR -n COUNT -l LABEL_DIR [-i IMAGE_DIR]` — collect N files; `--shuffle` (default) / `--no-shuffle`, `--seed`, `--move`. YOLO/LabelMe only.

YOLO/LabelMe are directories, COCO is a single JSON file — subcommands that need directories reject COCO (check `--help`). Analyse is always non-strict (read-only, lenient).

### Convert

Six directions, source → target as named. Positional args for `yolo2coco`: `IMAGE_DIR LABEL_DIR CLASS_FILE OUTPUT_FILE` (per-file targets take `OUTPUT_DIR`).

- `--prediction` exists **only on `yolo2coco`** — input YOLO lines carry a confidence token (6 tokens detection / even tokens segmentation); output is a plain JSON list of annotation dicts (Variant B, pycocotools `loadRes()`-compatible)
- `--do-rle` (yolo2coco / labelme2coco) needs the `[coco]` extra
- `--no-strict` skips invalid annotations instead of failing

### Visualize

- `visualize yolo IMAGE_DIR LABEL_DIR CLASS_FILE` · `visualize labelme IMAGE_DIR LABEL_DIR` · `visualize coco IMAGE_DIR COCO_FILE`
- `--save DIR` writes rendered images; `--no-display` for headless (pair both)
- Interactive keyboard: `←/↑` prev, `→/↓/Enter/Space` next, `s` snapshot, `h` hints, `q/ESC` quit (window close button may not work — use keyboard)

### Evaluate

- `evaluate detection GT_JSON DT_JSON` — bbox IoU; `evaluate segmentation GT_JSON DT_JSON` — mask IoU
- Two mutually exclusive paths per invocation: mAP/AR via COCOeval (default) or `--prf1` (single-threshold P/R/F1; `--prf1-iou` 0.5, `--prf1-conf` 0.0, `--prf1-method macro|micro`). Run twice to get both.
- Requires `[coco]`. GT = full COCO dict. DT = COCO dict or plain list of annotation dicts; DT annotations must carry `score` and `area`
- `-o/--output FILE` dumps JSON results

## Python API

```python
from dataflow.util import LogConfig, LogManager
log = LogManager(LogConfig(name="job", verbose=True, log_dir=Path("./logs")))

# Handlers (dataflow.label): read() = batch DatasetAnnotations; iter_images() = streaming
from dataflow.label import YoloAnnotationHandler, LabelMeAnnotationHandler, CocoAnnotationHandler
h = YoloAnnotationHandler(label_dir, class_file, image_dir, logger=log.logger)

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
- [*] Strict mode is default: invalid annotations raise; `--no-strict` skips and continues (convert/visualize only — analyse is always non-strict).
- [*] LabelMe images may be absent without warning when the JSON has valid `imageWidth`/`imageHeight`.
- [*] YOLO prediction lines: 6 tokens detection / even tokens segmentation vs 5 / odd for labels.

## Bootstrap (First Use in a New Project)

No configuration — this skill is self-contained; nothing is appended to the project CLAUDE.md. First use = run Step 0; if dataflow-cv is missing, offer the install commands and answer from this document.

## Required Configuration

None. Requirements: `dataflow-cv>=2.0.0` (Step 0); `[coco]` extra only for `evaluate` / `--do-rle`.
