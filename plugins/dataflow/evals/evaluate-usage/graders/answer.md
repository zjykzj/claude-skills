---
type: llm
---
PASS if the response gives the dataflow-cv evaluate detection command form (e.g. `dataflow-cv evaluate detection GT_JSON DT_JSON`) and mentions `--prf1` as the single-threshold P/R/F1 alternative.
FAIL if it invents commands inconsistent with the skill, answers about a different library, or omits the `--prf1` alternative.
