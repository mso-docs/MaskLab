# Complete first-release backlog

Foundation/specification completed separately in verification.md. Application tasks below are PLANNED, not implemented. After implementation/spec/profile/source approvals, dependency-ready work may proceed autonomously; no task is permission to spend or publish.

| Task | Requirements | Depends on | Deliverable | State |
|---|---|---|---|---|
| TASK-001 | REQ-001, REQ-005, REQ-008, REQ-010, REQ-012 | none | Core schemas, SQLite versioned store, migrations and immutable evidence contracts. | Planned |
| TASK-002 | REQ-004, REQ-005, REQ-006, REQ-007, REQ-008 | TASK-001 | Validated dataset/split import, protocol renderer/preview/freeze and matrix limits. | Planned |
| TASK-003 | REQ-009, REQ-012, REQ-020, REQ-021 | TASK-001 | Provider adapter, safe credentials/capability checks and fake-provider contract tests; real smoke only with funding. | Planned |
| TASK-004 | REQ-010, REQ-011, REQ-012, REQ-021 | TASK-002,TASK-003 | Durable worker, leases, cancellation/pause/resume, uncertainty and bounded cost/retry accounting. | Planned |
| TASK-005 | REQ-013, REQ-014, REQ-015, REQ-016 | TASK-002 | Versioned deterministic extraction/scoring/paired analysis and independent mathematical fixtures. | Planned |
| TASK-006 | REQ-001, REQ-002, REQ-003 | TASK-001 | Integrated accessible study workspace, appearance, history and useful empty/error states. | Planned |
| TASK-007 | REQ-004, REQ-006, REQ-007, REQ-008 | TASK-002,TASK-006 | Dataset/protocol design interface and full matrix/cost review/freeze journey. | Planned |
| TASK-008 | REQ-010, REQ-011, REQ-012, REQ-017 | TASK-004,TASK-006 | Live run monitor, durable navigation, progress/errors and paired response inspection. | Planned |
| TASK-009 | REQ-014, REQ-015, REQ-016, REQ-017 | TASK-005,TASK-008 | Real results visualizations, denominators, intervals and aggregate-to-evidence drilldown. | Planned |
| TASK-010 | REQ-018, REQ-019, REQ-020 | TASK-001,TASK-005 | Safe portable export/import/reanalysis with original evidence preservation. | Planned |
| TASK-011 | REQ-003, REQ-020, REQ-021, REQ-022 | TASK-004,TASK-008 | Owner access boundaries, public curated demo, quotas, rate limits and abuse controls. | Planned |
| TASK-012 | REQ-002, REQ-018, REQ-019, REQ-020, REQ-023, REQ-024 | TASK-007,TASK-009,TASK-010,TASK-011 | Complete browser/API/security/recovery tests, dependency locks, CI and operator/researcher help. | Planned |
| TASK-013 | REQ-009, REQ-023, REQ-024 | TASK-012 | Authorized real provider smoke and hosted deployment/backup/access verification. | Planned |
| TASK-014 | REQ-025 | TASK-013 | Owner acceptance fixes, accurate README, video/feedback/release assets and authorized submission. | Planned |
