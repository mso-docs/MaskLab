# Release traceability

REQ → DES → TASK → TEST. RUN-LOCAL-20261028 now records local automated evidence; live release acceptance remains separately pending.

- REQ-001 → plan.md design/contracts → TASK-001, TASK-006 → TEST-001; evidence pending.
- REQ-002 → plan.md design/contracts → TASK-006, TASK-012 → TEST-002; evidence pending.
- REQ-003 → plan.md design/contracts → TASK-006, TASK-011 → TEST-003; evidence pending.
- REQ-004 → plan.md design/contracts → TASK-002, TASK-007 → TEST-004; evidence pending.
- REQ-005 → plan.md design/contracts → TASK-001, TASK-002 → TEST-005; evidence pending.
- REQ-006 → plan.md design/contracts → TASK-002, TASK-007 → TEST-006; evidence pending.
- REQ-007 → plan.md design/contracts → TASK-002, TASK-007 → TEST-007; evidence pending.
- REQ-008 → plan.md design/contracts → TASK-001, TASK-002, TASK-007 → TEST-008; evidence pending.
- REQ-009 → plan.md design/contracts → TASK-003, TASK-013 → TEST-009; evidence pending.
- REQ-010 → plan.md design/contracts → TASK-001, TASK-004, TASK-008 → TEST-010; evidence pending.
- REQ-011 → plan.md design/contracts → TASK-004, TASK-008 → TEST-011; evidence pending.
- REQ-012 → plan.md design/contracts → TASK-001, TASK-003, TASK-004, TASK-008 → TEST-012; evidence pending.
- REQ-013 → plan.md design/contracts → TASK-005 → TEST-013; evidence pending.
- REQ-014 → plan.md design/contracts → TASK-005, TASK-009 → TEST-014; evidence pending.
- REQ-015 → plan.md design/contracts → TASK-005, TASK-009 → TEST-015; evidence pending.
- REQ-016 → plan.md design/contracts → TASK-005, TASK-009 → TEST-016; evidence pending.
- REQ-017 → plan.md design/contracts → TASK-008, TASK-009 → TEST-017; evidence pending.
- REQ-018 → plan.md design/contracts → TASK-010, TASK-012 → TEST-018; evidence pending.
- REQ-019 → plan.md design/contracts → TASK-010, TASK-012 → TEST-019; evidence pending.
- REQ-020 → plan.md design/contracts → TASK-003, TASK-010, TASK-011, TASK-012 → TEST-020; evidence pending.
- REQ-021 → plan.md design/contracts → TASK-003, TASK-004, TASK-011 → TEST-021; evidence pending.
- REQ-022 → plan.md design/contracts → TASK-011 → TEST-022; evidence pending.
- REQ-023 → plan.md design/contracts → TASK-012, TASK-013 → TEST-023; evidence pending.
- REQ-024 → plan.md design/contracts → TASK-012, TASK-013 → TEST-024; evidence pending.
- REQ-025 → plan.md design/contracts → TASK-014 → TEST-025; evidence pending.


## RUN-LOCAL-20261028 evidence map

| Requirements | Implemented tasks | Executable evidence |
|---|---|---|
| REQ-001/005/008/010/012 | TASK-001/004/006/008 | tests/test_contracts.py, tests/test_worker.py, tests/test_security_api.py, browser researcher journey |
| REQ-004/006/007 | TASK-002/007 | tests/test_contracts.py, browser dataset/protocol/freeze journey |
| REQ-009/020/021 | TASK-003/004 | tests/test_provider.py mocked HTTP contracts, tests/test_worker.py reservations; real smoke pending TASK-013 |
| REQ-013–016 | TASK-005/009 | tests/test_science.py hand-derived mixed table/cluster reference, scripts/evaluate_release.py independent exported-run evaluator |
| REQ-002/003/017 | TASK-006–009/011 | tests/e2e/workspace.spec.ts owner/demo browser journeys, artifacts/verification/browser.json |
| REQ-018–020 | TASK-010/012 | tests/test_security_api.py hash/ZIP/CSRF/auth tests, browser export/import, independent evaluator |
| REQ-022 | TASK-011 | atomic parallel/public quota API tests and separate curated-demo browser journey |
| REQ-023/024 | TASK-012 | fresh hash-locked install, installed-wheel check, actual pre/post-commit crash recovery, Python/browser suites; Docker unavailable and live/hosted verification pending |
| REQ-025 | TASK-014 preparation only | README, docs/RELEASE_PREPARATION.md; owner acceptance/live demo/source/video/submission pending |

Historical “evidence pending” lines above describe the foundation state. Current exact commands, exit codes, limitations and artifact hashes are in verification.md. No simulated outcome is a live model finding.


## RUN-LIVE-20261028

REQ-009/012/020/021/024 → TASK-003/004/013 → TEST-009/012/020/021/024: actual selected-model discovery, one minimal smoke, one bounded reasoning probe, complete 648-request default matrix, 3-call owner browser study and 8+8-call separate local demo. Shared-ledger cumulative use: 669 attempts, 54,664 input and 5,307 completion tokens including 64 reasoning tokens; USD0.00455352 estimated, USD0 held, USD9.99544648 remaining. Independent evaluator verifies all six live archives without application imports. Exact-key boundary scan and actual Gitleaks pass.

REQ-023/024 → TASK-012/013 → TEST-023/024: actual live workspace/ledger online backup, integrity/hash comparison and installed-wheel checks. Docker/hosted execution remains pending environment/release gates. REQ-025 → TASK-014: observed provider feedback and exact owner acceptance guide prepared; acceptance/publication/submission remain open. Full commands/receipt hashes are in verification.md.

2026-10-28 approved mixed-study preparation: TASK-002/005/007/009/012 → REQ-004/005/007/014–017/024. Chart views: frontend/src/{chartData,ResearchCharts}.tsx (helper is .ts), frontend/tests/chart-data.test.mjs, tests/e2e/charts.spec.ts. Public-source preparation and independent checks: scripts/{fetch_question_source,fetch_cmu_source,prepare_study_questions,verify_study_questions}.py; provenance/license/review workflow: docs/QUESTION_STUDY.md. Dataset answer-key approval remains pending; no new scientific run.

After-work mixed study: TASK-007/009/010/012/013 → REQ-004/005/009/014–021/024. Actual live development/evaluation execution, frozen choices and independent verification: scripts/run_approved_study.py, evaluate_live.py, verify_mixed_run.py, report_mixed_run.py; docs/MIXED_STUDY_RESULTS.md; artifacts/mixed-study. Public timestamp boundary: portable.public_redacted_archive, tests/test_public_redaction.py and frontend date display. New results preserve negative/invalid findings; public release remains gated.

Broad replication preparation: TASK-002/007/012 → REQ-004/005/007/024. New source curation, independent key/span/overlap checks and local draft staging: scripts/{prepare_mixed_replication,replication_curations,verify_mixed_replication,stage_replication}.py, docs/REPLICATION_V2.md, artifacts/replication-v2. New operator row review remains pending; no model evidence generated or previous results modified.

Private push-readiness and completed live replication: TASK-006/009/012/013 → REQ-001/009/010/014–024. docs/REPLICATION_V2_RESULTS.md; live independent/cost reconciliation; source/history/key scans. Monitor loadRun/status polling + request-count browser regression and isolated scripts/serve_owner_fixture.py. No scientific scorer/protocol changes; no commit/push/deploy.
