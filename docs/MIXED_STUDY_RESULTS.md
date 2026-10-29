# Mixed-question study results

TASK-007/009/013; REQ-004/005/009/014–020/024. Operator approved all 150 question rows and sequential development/evaluation execution. Both runs use live provider measurements, not simulated evidence.

## Results

| Split | Questions | Requests | Correct | Incorrect | Invalid | Finalized correctness | Valid-only accuracy | Estimated USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| development | 60 | 1620 | 1058 | 509 | 53 | 65.31% | 67.52% | 0.01685442 |
| evaluation | 90 | 2430 | 1582 | 794 | 54 | 65.10% | 66.58% | 0.02515548 |

Failure, refusal, uncertainty and pending counts remain explicit in each archive. Invalid and incorrect outcomes remain in the original evidence.

## Methods and limitations

The development decision retained prompts, answer keys, role/frame instructions, output limits, temperature, scoring and analysis unchanged. The decision was persisted before evaluation execution. Development found choice text instead of choice labels, currency-formatted numeric responses and malformed answer objects; those remain invalid under the frozen strict scorer. No retry, rescoring or removal was used to improve outcomes.

The actual 60/90 question ID sets are disjoint. Both splits use three roles, three belief frames and three repetitions per question. Generated template families overlap splits, and public benchmark training exposure is unknown. CMU source articles do not cross splits. This is a mixed convenience study, not a representative benchmark, training run or population-wide model assessment. Paired intervals use the existing question-cluster bootstrap; exploratory multiple comparisons do not establish rankings or internal mechanisms. Report development and evaluation separately.

## Usage and integrity

Additional requests: 4050; input tokens: 570861; completion tokens: 32326; reasoning-token subset: 0. Additional estimated cost: USD0.04200990. Cumulative estimated cost including prior verification: USD0.04656342; remaining grant: USD9.95343658. Costs use reviewed input/output prices; this is not invoice reconciliation. No automatic top-ups or budget increase.

Independent checks verified archive hashes, scores/denominators, paired metrics, usage/costs, split separation, unchanged protocol settings and exactly one attempt per scheduled request. Private original ZIPs and the spending ledger remain outside Git. `public-evidence/` contains explicitly labeled public derivatives; pre-5 p.m. timestamps on the operator-selected day are redacted in textual and numeric provider forms. Private originals remain intact; public derivatives are inspection-only and not standard-import-compatible. Nothing was published, deployed, pushed or submitted.

## Review in the app

- [Development results](http://127.0.0.1:8001/#view=results&study=c00a34d9a3b74ba9bad7e4d46b44d534&run=86f1e67bfebb4254a04a7df484f1ee97) — run `86f1e67bfebb4254a04a7df484f1ee97`.
- [Evaluation results](http://127.0.0.1:8001/#view=results&study=c00a34d9a3b74ba9bad7e4d46b44d534&run=39985e96f2a94011ba717b7808efb324) — run `39985e96f2a94011ba717b7808efb324`.

Open each results page, compare the four chart panels, inspect incorrect and invalid responses, and use **Download ZIP** for the original owner evidence. Public copies are in `public-evidence/`. Source/license and sampling details: [QUESTION_STUDY.md](QUESTION_STUDY.md). Current operator approval is recorded separately; immutable imported dataset notes retain their historical draft wording.
