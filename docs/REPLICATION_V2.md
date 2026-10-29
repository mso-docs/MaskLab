# Next iteration: broad mixed replication

TASK-002/007/012 → REQ-004/005/007/024. The operator requested a next iteration and selected a **broader mixed set with more source curation**, superseding the initially proposed focused 60-question draft. The operator explicitly approved the new rows and authorized live Nebius execution. The live run is complete; see [final results](REPLICATION_V2_RESULTS.md). The earlier simulated run is paused and kept separate.

The 150-question draft matches the prior composition: 38 fresh GSM8K questions, 38 fresh arithmetic questions, 37 fresh logic questions and 37 fresh CMU S10 reading questions. There is no exact normalized question-text overlap, no question-ID overlap and no reused GSM8K/CMU source questions with the first study. Generated families/names recur. Among reading sources, 15 articles are new and 22 articles recur with different questions. It is a fresh-question replication, not a source-independent or unseen-template benchmark. Article overlap is retained explicitly in per-question provenance.

All 150 are assigned to evaluation: prompts, roles, belief frames, scoring, model controls, repetition count and analysis stay frozen from the first study, so no new tuning split is needed for this design. Human key/source review occurs before execution and does not use new model outcomes. If prompts or settings are changed, define a new development/evaluation design before running instead of calling this an unchanged replication.

## Review

- [Open the broader draft](http://127.0.0.1:8001/#view=design&study=558127eb3544493dbeb7f0311b84e72f&run=).
- Local worksheet: `data/replication-mixed-150-v2/review.csv`. Review keys, wording, false alternatives, distractors and the supplied archived context. `manifest.json` records provenance and source overlap, including alternative source answers.
- All 150 new rows are explicitly operator-approved. Their original imported snapshot retains historical draft notes; the manifest and review worksheet record the later approval.

Independent checks derive all 38 generated arithmetic answers from displayed text using rational arithmetic and exhaustively check all 37 logic answers. Twelve new GSM8K keys have separate arithmetic derivations; 26 currently rely on upstream labels. Thirty-seven CMU adaptations pass source-answer/article-span checks, which do not establish semantic uniqueness. Agent curation replaced missing-span questions and an ambiguous oldest-flute question, and tightened three weak excerpts before any model execution. Prior draft variants are preserved locally. All rows received explicit operator approval before live execution.

GSM8K is MIT; CMU S10 adaptations remain CC BY-SA 3.0. License notices and attribution accompany the dataset and appear in its notes. Original generated arithmetic/logic is MIT. Public benchmark training exposure is unknown. Report the replication separately; compare category-specific results as well as the mixed aggregate, acknowledging source/template dependence. Do not pool repetitions as independent questions or omit invalid/incorrect findings.

## Proposed execution

150 questions × 3 roles × 3 belief frames × 3 repetitions = **4,050 calls**. Offline conservative reservation: **USD0.70213986**, with the previous profile's USD2 per-run ceiling and existing shared USD10 cumulative grant. This is an estimate, not a reservation or spending. Preflight the current budget/capability profile again before execution; do not reset the ledger or enable top-ups. Live execution now uses the same cumulative grant; see the run monitor and ledger for actual usage.

Reproduce preparation/checks from the repository root:

```bash
PYTHONPATH=src .venv/bin/python scripts/prepare_mixed_replication.py
.venv/bin/python scripts/verify_mixed_replication.py
```

Existing differing output is not overwritten. The unused focused 60-question draft is archived in the app and preserved locally; it has no results. Existing completed studies and their answer keys, protocols and results remain intact.

## Live execution

[Open the live Nebius run](http://127.0.0.1:8001/#view=monitor&study=558127eb3544493dbeb7f0311b84e72f&run=adff4b5982dd4112a11c173ba48f3d57). Run `adff4b5982dd4112a11c173ba48f3d57` schedules 4,050 real requests. Separate simulated run `7b38d704d57244a3a1a51ec2476920da` is paused; its outputs are never live model evidence. Execution and monitoring script: `PYTHONPATH=src .venv/bin/python scripts/run_live_replication.py`. It reuses the same idempotent run, records the ledger baseline, and automatically saves the completed original ZIP, analysis, independent scoring/billing verification and final budget under `artifacts/replication-v2/live/`. Do not restart or replay an uncertain call. Completion, independent checks and final costs are recorded in [REPLICATION_V2_RESULTS.md](REPLICATION_V2_RESULTS.md).
