# Preparing the mixed question study

TASK-002/005/007/009/012; REQ-004/005/007/014–017/024. The operator approved preparation of a 150-question study on 2026-10-28. The operator subsequently reviewed and explicitly approved all 150 rows, then authorized development followed by held-out evaluation after freezing choices. Both runs are complete; see [MIXED_STUDY_RESULTS.md](MIXED_STUDY_RESULTS.md). Historical imported snapshots retain their draft wording; the current manifest and CSV record operator approval. SPAR private messages are excluded.

## Prepared data

`data/study-draft-150/` is local and ignored by Git. It contains 38 GSM8K numerical questions, 38 original arithmetic questions, 37 original logic questions, and 37 adapted CMU S10 reading questions. There are 60 development and 90 held-out evaluation IDs. Each CMU question uses a different archived article; articles never cross splits. Generated template families overlap splits, so this is not a test of unseen reasoning families. Public benchmark training exposure is unknown. This convenience sample does not establish representativeness, statistical power or benchmark replication.

Sources: [GSM8K](https://github.com/openai/grade-school-math) at commit `3101c7d5072418e28b9008a6636bde82a006892c` is MIT licensed. [CMU Question–Answer Dataset](https://www.cs.cmu.edu/~ark/QA-data/) S10 is CC BY-SA 3.0, with separate attribution retained; it is not MIT. Only S10 is adapted here. Its questions ask about the supplied historical excerpt, not current facts. The original archive contains duplicates and free-text answers; selected questions were deduplicated and converted to single-choice items with newly authored distractors. Licenses and attribution accompany the dataset and are retained in dataset notes for exports.

The independent checker verified all 38 generated arithmetic answers, all 37 logic answers by exhaustive enumeration, and 25 GSM8K answers by separate arithmetic references. The other 13 GSM8K answers currently rely on upstream labels. All 37 CMU answers passed literal-source checks, which do not establish semantic uniqueness. All 150 rows received explicit operator approval before inference. Mechanical checks are distinct from that approval and do not establish benchmark validity.

## Review and continue

1. Open the local draft study: <http://127.0.0.1:8001/#view=design&study=c00a34d9a3b74ba9bad7e4d46b44d534&run=>. Expand **Full dataset notes, sources and licenses**.
2. Review `data/study-draft-150/review.csv` alongside `manifest.json`. The CSV is a review worksheet, not the app's import schema. Record review decisions and corrections before model execution. Do not alter keys in response to model outcomes.
3. If corrections are needed, preserve this version and import a new `questions.json` dataset version. Re-run independent checks against the corrected data. Freeze the reviewed split and protocol before looking at evaluation outcomes.
4. Proposed matrix: 150 questions × 3 roles × 3 belief frames × 3 repetitions = 4,050 requests. The offline conservative reservation estimate is USD0.69936318 with the reviewed model/price profile and 512 completion-token cap. This is an estimate, not spending or a reservation. Check current pricing, capability profile, shared remaining USD10 grant and preview before starting. Stop if costs cannot be bounded. No top-ups or budget resets.
5. Use development results to test workflow and analysis choices; keep evaluation results separate. Inspect invalid, failed, uncertain and incorrect outcomes. Export each completed run with **Download ZIP**. Report denominators, paired uncertainty, negative findings and sampling limitations.

150 is a starting design, not a definitive target. More distinct reviewed questions improve coverage; repetitions measure variability and cannot replace question diversity. Additional curated questions require further review. Five repetitions of the entire 150×3×3 matrix would exceed the current 5,000-request run limit; three repetitions fit.

## Reproduce preparation

Run from repository root, without loading `.env` or calling a provider:

```bash
.venv/bin/python scripts/fetch_question_source.py
.venv/bin/python scripts/fetch_cmu_source.py
.venv/bin/python scripts/prepare_study_questions.py --questions 150
.venv/bin/python scripts/verify_study_questions.py
```

Fetches download public source data only when absent. Preparation is deterministic and refuses to overwrite differing output or an approved dataset. Reproduce preparation in a fresh workspace to preserve existing review decisions. The curated selection currently supports 20–150 questions; this is not the application dataset limit. `scripts/stage_draft_study.py` stages only a draft study/dataset, never a protocol or run.

## Chart interpretation

Saved results now include correctness bars, repeated-answer consistency, paired differences with existing question-cluster intervals, and a paginated question×condition heatmap. Select a bar, interval or cell to inspect its records. Charts are derived from saved evidence, not new provider requests.

Correctness bars offer all-finalized and valid-only denominators. Missing evidence is distinct from measured zero. Consistency `modal-answer-share-v1` averages the modal valid-answer share equally over questions with at least two valid repetitions; excluded responses remain inspectable. A consistently wrong answer can score 100% consistency. This descriptive view has no confidence interval. Paired differences retain the existing frozen analysis method, use percentage points and omit intervals below five eligible questions. Exploratory comparisons do not establish significance or rankings. Original scoring and frozen protocols are unchanged.
