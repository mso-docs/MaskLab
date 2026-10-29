# Complete first-release backlog

Foundation/specification completed separately in verification.md. The operator explicitly authorized the full approved local implementation and dependency installation on 2026-10-28 while obtaining the Nebius key. This supersedes the foundation-only restriction for this direct IDE session. No ACP registry, worker policy, execution profile or source-commit privilege was changed. No task authorizes spending or publication. Local implementation proceeded in dependency order, starting with TASK-001; evidence is in verification.md.

| Task | Requirements | Depends on | Deliverable | State |
|---|---|---|---|---|
| TASK-001 | REQ-001, REQ-005, REQ-008, REQ-010, REQ-012 | none | Core schemas, SQLite versioned store, migrations and immutable evidence contracts. | Local implemented / verified |
| TASK-002 | REQ-004, REQ-005, REQ-006, REQ-007, REQ-008 | TASK-001 | Validated dataset/split import, protocol renderer/preview/freeze and matrix limits. | Local implemented / verified |
| TASK-003 | REQ-009, REQ-012, REQ-020, REQ-021 | TASK-001 | Provider adapter, safe credentials/capability checks and fake-provider contract tests; real smoke only with funding. | Local adapter + actual selected-model smoke verified RUN-LIVE-20261028 |
| TASK-004 | REQ-010, REQ-011, REQ-012, REQ-021 | TASK-002,TASK-003 | Durable worker, leases, cancellation/pause/resume, uncertainty and bounded cost/retry accounting. | Local implemented / verified |
| TASK-005 | REQ-013, REQ-014, REQ-015, REQ-016 | TASK-002 | Versioned deterministic extraction/scoring/paired analysis and independent mathematical fixtures. | Local implemented / verified |
| TASK-006 | REQ-001, REQ-002, REQ-003 | TASK-001 | Integrated accessible study workspace, appearance, history and useful empty/error states. | Local implemented / verified |
| TASK-007 | REQ-004, REQ-006, REQ-007, REQ-008 | TASK-002,TASK-006 | Dataset/protocol design interface and full matrix/cost review/freeze journey. | Local implemented / verified |
| TASK-008 | REQ-010, REQ-011, REQ-012, REQ-017 | TASK-004,TASK-006 | Live run monitor, durable navigation, progress/errors and paired response inspection. | Local implemented / verified |
| TASK-009 | REQ-014, REQ-015, REQ-016, REQ-017 | TASK-005,TASK-008 | Real results visualizations, denominators, intervals and aggregate-to-evidence drilldown. | Local implemented / verified |
| TASK-010 | REQ-018, REQ-019, REQ-020 | TASK-001,TASK-005 | Safe portable export/import/reanalysis with original evidence preservation. | Local implemented / verified |
| TASK-011 | REQ-003, REQ-020, REQ-021, REQ-022 | TASK-004,TASK-008 | Owner access boundaries, public curated demo, quotas, rate limits and abuse controls. | Local implemented / verified |
| TASK-012 | REQ-002, REQ-018, REQ-019, REQ-020, REQ-023, REQ-024 | TASK-007,TASK-009,TASK-010,TASK-011 | Complete browser/API/security/recovery tests, dependency locks, CI and operator/researcher help. | Local automated suites/locks/package/help verified; container engine unavailable |
| TASK-013 | REQ-009, REQ-023, REQ-024 | TASK-012 | Authorized real provider smoke and hosted deployment/backup/access verification. | Live local provider/owner/demo/backup verified; Docker + authorized hosted checks pending |
| TASK-014 | REQ-025 | TASK-013 | Owner acceptance fixes, accurate README, video/feedback/release assets and authorized submission. | Acceptance guide + observed feedback/assets prepared; owner/public release gates pending |

Local implementation includes the full research workflow and separate restricted-demo mode, not only a vertical slice. TASK-013/014 remain release gates. See docs/RELEASE_PREPARATION.md for honest local drafts; no fabricated feedback, live measurements or public URLs are provided.

RUN-LIVE-20261028 records the explicit USD10 cumulative additional inference authorization, 669 actual paid attempts and USD0.00455352 estimated spend. The full 648-request default matrix and real owner/restricted-demo browser paths ran. See docs/ACCEPTANCE.md; synthetic tooling measurements are not benchmark validation. No public deployment/publication/submission/commit/push is included.

2026-10-28 extension within approved TASK-002/005/007/009/012: added saved-evidence charts and operator-approved 150-question draft preparation. Local implementation complete; answer-key/distractor/source semantic review remains an operator gate before execution. No new paid experiment or public release authorized by this preparation approval. Evidence and exact commands: verification.md; review workflow: docs/QUESTION_STUDY.md.
