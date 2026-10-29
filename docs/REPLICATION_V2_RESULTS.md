# Broad replication results

TASK-007/013 → REQ-009/012/014–021/024. Live Nebius run `adff4b5982dd4112a11c173ba48f3d57`, separate from the paused simulated run. The operator approved all 150 new questions and explicitly authorized live execution. No prompts, keys or scoring rules were changed.

| Outcome | Count |
|---|---:|
| Scheduled/finalized | 4,050 |
| Correct | 2,427 |
| Incorrect | 1,473 |
| Invalid | 150 |
| Failed/refused/uncertain/pending | 0 |

Finalized correctness: **59.93%**. Valid-only accuracy: **62.23%** (2,427/3,900). Invalids remain non-correct finalized outcomes. No retry or rescoring was used to improve findings.

Usage: 584,460 input + 34,288 completion tokens; reasoning subset 0. Estimated run cost **USD0.04329672**. Cumulative grant: USD0.08986014 estimated spent, USD9.91013986 remaining, USD0 held, no uncertain charges or top-ups. Estimates use the reviewed prices, not provider invoice reconciliation.

Independent archive evaluation verified hashes, counts, paired metrics, returned model identity, token caps and cost calculations. The exact budget delta reconciles to 4,050 additional attempts and the reported run cost.

[Open results and charts](http://127.0.0.1:8001/#view=results&study=558127eb3544493dbeb7f0311b84e72f&run=adff4b5982dd4112a11c173ba48f3d57). Inspect invalid/incorrect responses and use **Download ZIP** for the original evidence. The private original is `artifacts/replication-v2/live/original.zip`; the approved public derivative is `public-evidence/replication-v2-redacted.zip`. The derivative retains all evening data payloads unchanged, has neutral ZIP metadata and an explicit derivative manifest; it is inspection-only, not standard-import-compatible. Private originals and ledger remain outside Git.

This is a fresh-question convenience replication with the same model/settings, not training or a representative benchmark. There are 15 new and 22 reused CMU articles, shared generated template families and unknown public benchmark exposure. Different question difficulty means the aggregate difference from the first study is not evidence that the model improved or deteriorated. Multiple comparisons remain exploratory; adoption does not establish an internal causal mechanism. See [design and sources](REPLICATION_V2.md) and [first-study results](MIXED_STUDY_RESULTS.md).

Nothing was committed, pushed, published, deployed or submitted by this verification.
