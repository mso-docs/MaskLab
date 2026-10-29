# Foundation verification — 2026-10-27

ACP creation: exit0, project masklab, operation 91bd13a6-45b7-5156-8ab5-e26171d815d3; registered at SPEC_PENDING with empty script/evaluator allowlists and read-only worker policy. Private Gitleaks hooks installed. Registration state does not claim application completion.

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` — exit0, 3 foundation tests passed. These check independent Decimal arithmetic, nonoverlapping stable fixture splits, neutral control and absent spending authorization; they are not application/scientific-result tests.

Python AST and JSON syntax checks passed. Local Markdown links resolved. All25 REQ identifiers appear in acceptance, task and traceability records. Full source was copied to a disposable Git index and scanned with actual Gitleaks: clean, 39 objects. The real project index was left untouched. No model measurements are claimed.

No dependency installation, live provider call, model download, application implementation, worker execution, commit, push, deployment or submission occurred. Dependency resolution, provider account/model/paid-call approval, later publication/hosting and final user acceptance remain future prerequisites.

# RUN-LOCAL-20261028 — credential-independent application verification

Operator authorization on 2026-10-28: full approved local implementation, necessary local development dependencies and clearly labeled simulated provider/failure testing. Paid calls, paid hosting, publication, submission and commit/push remain unapproved. No ACP registry/policy/profile privileges were changed. Work proceeded directly in the IDE session rather than ACP worker dispatch. Foundation-only statements above are historical.

## Actual evidence

Runtime: Python 3.14.4, Node 22.22.1, npm 9.2.0, Linux Ubuntu 26.04. Python/Node dependencies were resolved from their registries with supported scoped tool approvals, and lockfiles were produced from actual resolution. Test/evaluation source links to TASK and REQ identifiers. No provider credential was supplied or printed, no external model inference ran, and no scientific Nemotron result exists.

All paths below are relative to the repository unless stated otherwise. `> ... 2>&1` records both output streams. Commands requiring package registries or local loopback/thread signaling used scoped host approval; the ACP worker sandbox/network policy remained unchanged.

| Exact command | Exit | Result / artifact |
|---|---:|---|
| `python3 -m venv .venv` | 0 | Local development environment |
| `.venv/bin/python -m pip install -r requirements-dev.in` | 0 | Authorized local dependencies resolved/installed after sandbox DNS failure |
| `npm install --prefix frontend` | 0 | Initial frontend install; audit found Vite vulnerability, fixed below |
| `npm install --prefix frontend --save-dev --save-exact vite@7.3.7` | 0 | Patched dependency resolved, package-lock updated |
| `.venv/bin/pip-compile --generate-hashes --output-file requirements.lock requirements.in` | 0 | Hash-locked runtime dependencies |
| `.venv/bin/pip-compile --quiet --allow-unsafe --strip-extras --generate-hashes --output-file requirements-dev.lock requirements-dev.in` | 0 | Complete development lock including build tooling/pip/setuptools |
| `python3 -m venv /tmp/masklab-lock-verification && /tmp/masklab-lock-verification/bin/python -m pip install --require-hashes -r requirements-dev.lock > artifacts/verification/fresh-install.log 2>&1` | 0 | Fresh disposable installation verified all hashes |
| `npm run build --prefix frontend > artifacts/verification/frontend-build.log 2>&1` | 0 | Strict TypeScript check and production React build; no generated assets claimed as measurements |
| `.venv/bin/python -m pytest -q --junitxml=artifacts/verification/pytest.xml > artifacts/verification/pytest.log 2>&1` | 0 | **73 passed**; scientific reference, API, persistence, actual pre/post-response-commit process deaths, recovery, cancellation/pause/resume/draft, cost/retry, import/security/quota checks |
| `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 PLAYWRIGHT_BROWSERS_PATH=/home/asuna/Documents/code/masklab/artifacts/playwright-browsers frontend/node_modules/.bin/playwright install chromium` | 0 | Official Playwright compatibility bundle downloaded to private project artifacts |
| `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 PLAYWRIGHT_BROWSERS_PATH=/home/asuna/Documents/code/masklab/artifacts/playwright-browsers npm test --prefix frontend > artifacts/verification/browser.log 2>&1` | 0 | **3 passed**; owner full workflow, inert text/keyboard/archive, separate restricted simulated demo. JSON/HTML reports, screenshots and export in artifacts/verification |
| `.venv/bin/python scripts/evaluate_release.py artifacts/verification/browser-export.zip > artifacts/verification/independent-evaluation.json` | 0 | Independent evaluator imports no application code; verifies archive hashes and manually specified 216 finalized/valid responses and 9 correct simulated answers |
| `.venv/bin/python -m build --wheel --no-isolation > artifacts/verification/package-build.log 2>&1` | 0 | Built actual wheel with React, brand assets and fixture dataset |
| `/tmp/masklab-lock-verification/bin/python -m pip install --force-reinstall --no-deps dist/*.whl > artifacts/verification/wheel-install.log 2>&1` | 0 | Installed built artifact in fresh environment |
| `cd /tmp && /tmp/masklab-lock-verification/bin/python /home/asuna/Documents/code/masklab/scripts/check_package.py > /home/asuna/Documents/code/masklab/artifacts/verification/package-check.log 2>&1` | 0 | Outside source tree, installed package serves React/brand and loads 24-question fixture |
| `.venv/bin/python -m pip install --no-deps --no-build-isolation -e . > artifacts/verification/editable-install.log 2>&1` | 0 | Development launch entry point installed |
| `.venv/bin/python -m pip check > artifacts/verification/pip-check.log 2>&1` | 0 | No broken dependencies |
| `npm audit --prefix frontend --audit-level=moderate > artifacts/verification/npm-audit.log 2>&1` | 0 | No known npm vulnerabilities |
| `python3 -m venv /tmp/masklab-advisory-check && /tmp/masklab-advisory-check/bin/python -m pip install pip-audit > artifacts/verification/audit-install.log 2>&1 && /tmp/masklab-advisory-check/bin/pip-audit -r requirements.lock --no-deps --disable-pip --format=json --output artifacts/verification/python-audit.json > artifacts/verification/python-audit.log 2>&1` | 0 | No known runtime Python vulnerabilities; disposable audit tooling outside application locks |
| `.venv/bin/python scripts/check_docs.py > artifacts/verification/docs-check.log 2>&1` | 0 | Local document references and all 25 requirement mappings checked |
| `.venv/bin/python scripts/scan_source.py > artifacts/verification/gitleaks.log 2>&1` | 0 | Actual Gitleaks scans copied tracked/nonignored source with redaction; clean; real Git index unchanged. Report artifacts/verification/gitleaks.json |

`artifacts/verification/dependency-licenses.json` records installed direct dependency metadata (MIT/BSD/Apache and NumPy bundled permissive notices); no incompatible direct dependency license was found. Distribution notices must accompany future publication as appropriate. `artifact-hashes.json` records SHA256/size of verification files, screenshots, archives and wheel. These private artifacts are Git-ignored; they are not public research results.

## Independent checks and failure findings

- Scientific expectations are explicit reviewed-fixture calculations: the mixed 12-request table yields 10 finalized, 7 valid, 3 correct, 1 invalid, 1 refusal, 1 failure, 1 uncertain and 1 pending; all-attempt accuracy 3/10, valid accuracy 3/7, adoption 3/4, correct-to-false transition 1/2. A separate cluster-mean bootstrap reference verifies equal question weighting and fixed-seed intervals. A precision regression distinguishes decimal answers beyond 28 digits without context rounding.
- Actual subprocess deaths exit 73 before response persistence and 74 after committed responses. The replacement worker classifies orphaned attempts UNCERTAIN without replay; already committed attempt bodies remain byte-equivalent. These controlled exit codes are expected fixtures, not application test failures.
- Original sandbox Python dependency install failed exit 1 because package-index DNS was unavailable. Supported scoped network approval allowed installation; no policy/registry bypass occurred.
- Initial unrestricted-host Playwright install failed exit 1 because Ubuntu 26.04 has no supported bundle. The explicit Ubuntu 24.04 compatibility bundle works here, but this does not make 26.04 officially supported.
- Sandboxed TestClient stalled before application lifespan while waiting for cross-thread event-loop signaling; a diagnostic `timeout 30 ...` exited 124. The original stalled run was interrupted (130). The same API suite passed with supported scoped host test permission. This was environmental; failed output/diagnostic is retained in the session record. CI is prepared for supported Ubuntu 24.04.
- Initial browser run exited 1 on exact navigation-name targeting because decorative symbols were in accessible names. Symbols are now aria-hidden and all final browser journeys pass. Screenshot/trace failure evidence remains under frontend/test-results only if not overwritten by Playwright's final successful run; final reports are under artifacts/verification.
- Initial npm audit found high Vite advisories (exit 1). Patched Vite 7.3.7 resolves them; final audit is clean. No finding was suppressed.
- Installed Gitleaks uses the older `detect --no-git` interface; probing `gitleaks dir --help` exited 1. Actual final source scans use the supported interface and pass without baselines/suppressions.
- Python suite warnings: upstream Starlette TestClient's HTTPX deprecation and the intentionally constructed duplicate ZIP entry. Neither was hidden or misreported as a failure.
- Port 8000 was already occupied (serve exit 3). The existing service was left untouched. The local owner review server runs on **http://127.0.0.1:8001**, with `PYTHONPATH=src .venv/bin/python -m masklab serve --port 8001 --data-dir artifacts/workspace`; health/asset checks pass and live spending is disabled (artifacts/verification/local-health.json).

## Pending checks / release truth

TASK-001–011 local deliverables and TASK-012's credential-independent suites, locks, packaging and help are implemented. Docker is not installed on this host (`command -v docker`, exit 1), so the prepared image's actual build/start is unverified; no Docker/system privilege escalation was attempted. CI is prepared but was not executed on GitHub. Keyboard/theme/narrow-layout browser smoke coverage is not an exhaustive accessibility audit. The owner's final acceptance remains pending.

TASK-013 needs external credentials, exact available model, reviewed output/sampling/reasoning billing/prices and **separate explicit paid-call authorization** before the durable one-request smoke. Then real inference, model/usage metadata, provider costs and authorized hosted backup/access checks must be recorded. Model discovery is not proof of inference access. A supplied key alone must not enable calls.

TASK-014 needs owner acceptance, real measured feedback, authorized judge hosting/source publication, final sub-three-minute public video and authorized submission. Local README/help/release storyboard/feedback draft are prepared; no live/public URL or scientific finding is invented. Full release TEST-009/023–025 remain open for their external gates. No commit, push, paid call, paid hosting provision, deploy, publish or submission occurred. Gitleaks remains mandatory before every later authorized commit/push.

# RUN-LIVE-20261028 — authorized local live integration

The operator explicitly supplied the local private `.env` key/model and authorized **up to USD10 total additional Nebius inference**, cumulatively across all development/verification runs, smoke tests, retries and experiments. This supersedes earlier live/key/funding-pending statements for local integration only. No grant to publish, deploy, submit, commit/push or modify ACP policy was given or exercised. No key, credential fingerprint or auth header was printed, logged, committed or exported. All dotenv variants except the empty canonical template are ignored by Git.

## Provider facts and actual bounded observations

- Selected/requested/served ID: `nvidia/Nemotron-3_5-Lightning`. Read-only authenticated model discovery listed that exact ID among 30 available IDs; its catalog record exposed identity/ownership/time/object fields, not detailed pricing/capabilities. A subsequent actual inference smoke separately established access.
- Reviewed pricing: **USD0.06 / million input tokens**, **USD0.24 / million output tokens** from the [Nebius model catalog](https://nebius.com/services/token-factory/models/nvidia-nemotron-models-inference). Estimates conservatively charge all input as uncached and all reported completion tokens at the output rate. Provider invoices/account settings/taxes/external usage are not independently reconciled.
- [Official chat API reference](https://docs.tokenfactory.nebius.com/api-reference/inference/create-chat-completion) and the downloaded public OpenAPI schema specify total-generation `max_completion_tokens`, including reasoning; matching `max_tokens` is also supplied. Only one completion is requested, with `store=false`, explicit `temperature`, JSON response format and `service_tier=default` to avoid automatic over-limit tier selection. The exact model-specific thinking control is documented in [Nebius's own verified integration notes](https://github.com/nebius/nebius-physical-ai/blob/main/docs/workbench/token-factory-deprecation-verification.md). Controls are frozen into the protocol; unsupported/changed capability or price assertions block preflight rather than silently altering a run.
- Minimal smoke: one neutral/absent synthetic arithmetic request, output cap 64, thinking disabled. Actual usage **63 input + 7 completion**, reasoning 0; estimated USD0.00000546. Exact selected model matched, JSON parsed correctly. Actual provider request ID and timestamps retained privately.
- Isolated reasoning-cap probe: one request with thinking enabled and output cap 64. Actual usage **63 input + 64 completion, all 64 completion tokens marked reasoning**, finish reason `length`, no valid final answer. This remains **INVALID**, non-correct, with estimated USD0.00001914. No private reasoning text is retained. Reasoning tokens are included once within completion tokens, not added as another 64. The negative/truncated result was not repaired or retried.
- Full default matrix: **24 questions × 3 roles × 3 frames × 3 repetitions × 1 model = 648 requests**, concurrency 2, temperature 0, thinking disabled, total output cap 512. Conservative total reservation USD0.10309518, fixed phase ceiling USD0.50. Actual **53,109 input + 5,103 completion tokens**, zero reasoning, max observed output 9 tokens; estimated USD0.00441126. **648 valid, 585 correct, 63 incorrect**, no failed/uncertain/refused outcomes or retries. These are real responses on synthetic tooling questions, not a representative/validated scientific benchmark or causal interpretation. Answer keys, scorer and protocol were not changed to improve results.
- Real owner browser journey: three additional capped requests, USD0.00001782 estimated. Separate restricted local demo: eight-call saved seed plus eight-call bounded execution, USD0.00004992 estimated each. Both real browser paths passed and retained live/saved labels. The demo was bound to loopback only and stopped when Playwright finished; it was never publicly deployed.
- Provider request IDs, timestamps and usage exist in all live receipts. Serving revision was absent and recorded unknown. Service-tier response metadata was absent/null; it is recorded unknown, not inferred from the requested tier. No silent provider/model fallback occurred.

**Cumulative grant reconciliation at handoff:** 669 attempts; **54,664 input + 5,307 completion tokens**, including 64 reasoning tokens within that completion total. **USD0.00455352 estimated spent; USD0 held; USD9.99544648 remaining; zero uncertain attempts; no automatic top-ups.** This grant is additional to the earlier zero-call foundation/local-simulation stage. Both owner and demo use the same ledger. No unrelated external API usage is claimed accounted for.

## Implemented guard and integration changes

TASK-003/004/012/013 → REQ-009/010–012/020–024. `budget.py` provides one persistent shared additional-spend ledger across workspaces, atomic pre-dispatch per-attempt reservations, immutable grant limit and settled charges, no expiry/reset/top-up, unknown-cost halt and logical-attempt history checks after stale workspace restore/copy. Crash windows across the workspace and budget databases are conservative: missing/uncommitted response evidence keeps the reservation and halts; known committed evidence can settle the existing reservation. Provider preflight rejects a missing grant/ledger or cap outside USD0–10, unsafe endpoint, unverified model access, unsupported parameters and price/capability drift. Unknown usage/tokens exceeding the reviewed bound stop further scheduling. The scheduler remains an application bound, not a provider-account hard cap.

`runtime.py` explicitly loads `.env` only when requested through `--env-file`; it executes/interpolates no shell syntax, exposes no values in errors and allows only recognized runtime fields. The existing key/model were preserved; the scoped grant/capability/ledger references were added privately. The UI now shows safe verified model/price presets, exact frozen provider controls, cumulative spend/held/remaining, and truthful live/saved/simulated provenance. A changed preview hash blocks freezing. Worker-lock acquisition fails startup instead of claiming a healthy embedded scheduler when another worker owns the volume.

No ACP registry/profile/worker sandbox/network settings or Gitleaks hooks were changed. Necessary network/local-test access used supported scoped host approvals. No policy bypass, Git commit or push occurred.

## Exact commands and exits

All paths below are local; `artifacts/live-verification` and private workspaces/ledgers/backups remain ignored by Git. The logs contain sanitized status and permitted metadata only. Live scripts use stable idempotency keys; rerunning a completed named phase does not create another experiment.

| Exact command | Exit | Actual evidence |
|---|---:|---|
| `PYTHONPATH=src .venv/bin/python scripts/discover_provider.py` | 0 | discovery.json plus downloaded public provider.json schema; no inference |
| `PYTHONPATH=src .venv/bin/python scripts/configure_live.py` | 0 | Recorded the already-authorized fixed USD10 grant and reviewed profile; no inference; no key output |
| `PYTHONPATH=src .venv/bin/python scripts/live_verify.py smoke > artifacts/live-verification/smoke.log 2>&1` | 0 | One minimal real request, smoke.json / smoke.zip |
| `PYTHONPATH=src .venv/bin/python scripts/live_verify.py reasoning-cap > artifacts/live-verification/reasoning-cap.log 2>&1` | 0 | One bounded negative/truncated real probe, reasoning-cap.json / reasoning-cap.zip |
| `PYTHONPATH=src .venv/bin/python scripts/live_verify.py matrix > artifacts/live-verification/matrix.log 2>&1` | 0 | Entire 648-request default matrix, matrix.json / matrix.zip |
| `npm run build --prefix frontend > artifacts/live-verification/frontend-build.log 2>&1` | 0 | TypeScript and production React assets |
| `.venv/bin/python -m pytest -q --junitxml=artifacts/live-verification/pytest.xml > artifacts/live-verification/regression.log 2>&1` | 0 | **83 passed**, including shared-budget concurrency, unknown halt, crash windows, grant immutability, stale restore replay prevention, thinking usage and private env parsing |
| `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 PLAYWRIGHT_BROWSERS_PATH=/home/asuna/Documents/code/masklab/artifacts/playwright-browsers npm test --prefix frontend > artifacts/live-verification/browser-simulated.log 2>&1` | 0 | **3 simulated browser journeys passed**, default CI remains non-paid |
| `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 PLAYWRIGHT_BROWSERS_PATH=/home/asuna/Documents/code/masklab/artifacts/playwright-browsers npm test --prefix frontend -- --config playwright.live.config.ts > artifacts/live-verification/browser-live.log 2>&1` | 0 | **2 real browser journeys passed**, live owner + separate local curated demo; browser-live.json, screenshots, browser-live.zip, demo-seed.zip, demo-browser-live.zip |
| `.venv/bin/python scripts/evaluate_live.py artifacts/live-verification/smoke.zip artifacts/live-verification/reasoning-cap.zip artifacts/live-verification/matrix.zip artifacts/live-verification/browser-live.zip artifacts/live-verification/demo-seed.zip artifacts/live-verification/demo-browser-live.zip > artifacts/live-verification/independent-evaluation.json` | 0 | Six archives independently rechecked without importing application code: manifest hashes, counts, valid/incorrect/invalid outcomes, adoption/paired eligibility and token/cost arithmetic |
| `.venv/bin/python scripts/reconcile_live.py artifacts/private/nebius-spend.sqlite3 artifacts/live-verification/smoke.zip artifacts/live-verification/reasoning-cap.zip artifacts/live-verification/matrix.zip artifacts/live-verification/browser-live.zip artifacts/live-verification/demo-seed.zip artifacts/live-verification/demo-browser-live.zip > artifacts/live-verification/ledger-reconciliation.json` | 0 | Independent one-to-one matching of all 669 unique exported attempts to shared ledger charges; exact total estimated cost matches; no provider calls |
| `PYTHONPATH=src .venv/bin/python scripts/check_live_backup.py > artifacts/live-verification/backup-check.log 2>&1` | 0 | Actual live workspace and shared ledger online backups independently opened; integrity, all evidence tables, blob hashes and charges match; zero calls/budget changes |
| `.venv/bin/python -m build --wheel --no-isolation > artifacts/live-verification/package-build.log 2>&1` | 0 | Final wheel includes runtime/guard/client/brand/fixtures |
| `/tmp/masklab-lock-verification/bin/python -m pip install --force-reinstall --no-deps dist/*.whl > artifacts/live-verification/wheel-install.log 2>&1` | 0 | Final wheel installed into previously fresh hash-locked environment |
| `cd /tmp && /tmp/masklab-lock-verification/bin/python /home/asuna/Documents/code/masklab/scripts/check_package.py > /home/asuna/Documents/code/masklab/artifacts/live-verification/package-check.log 2>&1` | 0 | Installed package serves UI/brand/fixtures outside source tree; no inference |
| `PYTHONPATH=src .venv/bin/python scripts/verify_secret_boundaries.py` | 0 | Exact private-key canary check of nonignored source, compiled assets, logs/artifacts, database bytes, decompressed archive/wheel members; no key/fingerprint output |
| `.venv/bin/python scripts/check_docs.py > artifacts/live-verification/docs-check.log 2>&1` | 0 | Local links and all 25 requirement mappings |
| `.venv/bin/python scripts/scan_source.py > artifacts/live-verification/gitleaks.log 2>&1` | 0 | Actual Gitleaks clean, no suppression/baseline; real Git index untouched |
| `PYTHONPATH=src .venv/bin/python -m masklab budget --env-file .env > artifacts/live-verification/budget-final.json` | 0 | Fixed USD10 cumulative grant, 669 attempts, no held/unknown charge, remaining USD9.99544648 |

A final read-only loopback check verified `/api/health`, `/api/config` and `/api/provider/status`: owner healthy, verified profile ready, exact remaining budget unchanged (local-health.json). The final server is running at **http://127.0.0.1:8001** with `.venv/bin/python -m masklab serve --env-file .env --port 8001`. Checking health/model status does not execute inference. `artifact-hashes.json` retains actual SHA256/size evidence, including each live export and final package.

Export hashes: smoke `77dda09f9d5bc82ad3cb696e5f5794a6eb5806ea45f542e259bc2b1a6e37a479`; reasoning probe `4fb6a470454247292c9d3990c3778652a64a9267bf069c4a39d1b8fb4d416e75`; matrix `96e05815da218558711c0e84a96b5206b97ed9fa84d0e43fa46b260ef1a63814`; owner browser `6b27c6461d09bc330651b3fdcbfd8b18d895891c7cbde5f659af96ff89353328`; saved live demo `67fbe8b8021591da9118072de1ae5cd1a5f5df852f1c685ab1aa2cac0424e1dd`; demo execution `e8d9489f0db8631eac3bb6e65f57ecf42784d1315e2d5f945aaf9426bea177d3`.

## Findings, limitations and remaining gates

The initial strengthened-guard regression run exited 1 (77 passed/one failure): an older safety assertion expected a later BUDGET_EXHAUSTED state, whereas the new guard correctly stops immediately at UNCERTAIN_COST. The assertion was updated to the stricter explicitly requested safety contract. No scientific fixture, scoring formula or answer key was changed. The final full suite passes 83 tests. Upstream Starlette HTTPX deprecation and the intentional duplicate-ZIP warning remain visible.

The 64-token reasoning probe is a deliberately preserved negative result, not a verification failure hidden by the parser. The 63 matrix errors and one saved-demo error remain in actual evidence. No invalid response was model-repaired or scored correct.

Container capability checks found no Docker/Podman/Buildah/nerdctl/buildctl binary and no Docker/Podman socket. Therefore the prepared image has not actually been built/run here; no system privilege escalation, paid hosting or deployment was attempted. Earlier dependency audit/lock checks remain applicable because this integration introduced no new application dependencies. CI is prepared but has not been run on a hosted GitHub runner.

Local implementation, funded provider verification, complete default matrix, owner/demo browser verification, private-key boundary checks and actual evidence backups are ready for owner acceptance. Exact steps are in **docs/ACCEPTANCE.md**. TASK-013 retains container/authorized-hosted checks; TASK-014 retains your acceptance and separately authorized public source/demo/video/submission gates. Do not call the public release complete, create public URLs, submit externally, initialize another allowance or increase the budget. Mandatory Gitleaks remains required before every later authorized commit and push.

## RUN-DOWNLOAD-UX-20261028 — TASK-006/010/012; REQ-001/002/018

Prominent browser **Download ZIP** actions replace the previously buried export controls; the same safe export API is reused. Run history supports direct download without opening the monitor. Newly selected studies clear stale run selection. Browser filenames contain the short run ID and need no manually entered path. Existing live Playwright selectors were updated but that paid suite was not rerun for this UI change; the simulated suite covers the same download function without spending.

- `npm run build --prefix frontend > artifacts/live-verification/download-build.log 2>&1` — exit 0; TypeScript + production Vite build.
- `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 PLAYWRIGHT_BROWSERS_PATH=/home/asuna/Documents/code/masklab/artifacts/playwright-browsers npm test --prefix frontend > artifacts/live-verification/download-browser.log 2>&1` — exit 0; 3 passed, including download/history/new-study navigation verification.
- `curl --fail --silent --show-error 'http://127.0.0.1:8001/api/runs/344b98f7814d4c07a9c47ac11af0a0d2/export' --output artifacts/live-verification/download-check.zip && .venv/bin/python scripts/evaluate_live.py artifacts/live-verification/download-check.zip > artifacts/live-verification/download-check.json` — exit 0; saved matrix downloaded and independently validated. No inference request.

All testing/exporting in this change is free of additional paid inference. Credentials remain external; no commit, push, publication or deployment occurred.

## RUN-CHARTS-STUDY-20261028

Scope: TASK-002/005/007/009/012; REQ-004/005/007/014–017/024. Operator-approved preparation of 150 questions and saved-evidence visualizations. No inference or scientific outcomes generated for this draft.

Executed from repository root (browser capture from frontend):

- `npm run build --prefix frontend`: exit 0; artifacts/charts/build.log.
- `npm run test:charts --prefix frontend`: exit 0; artifacts/charts/chart-data-tests.log. Hand-derived checks independently distinguish missing/zero, all-finalized/valid denominators, equal-question modal agreement and drilldown IDs.
- `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 PLAYWRIGHT_BROWSERS_PATH=/home/asuna/Documents/code/masklab/artifacts/playwright-browsers npm test --prefix frontend`: exit 0, 5 simulated journeys; artifacts/charts/browser.log. Includes chart pagination, keyboard interval activation, contributor drilldown and inert draft/license notices.
- `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 PLAYWRIGHT_BROWSERS_PATH=/home/asuna/Documents/code/masklab/artifacts/playwright-browsers node scripts/capture-research-charts.mjs` from frontend: PASS log, six screenshots, zero browser errors. Saved live evidence read only, no run-start requests. Visually inspected dark/light bars, agreement, paired plot, heatmap and draft. Fixed workspace footer appears in element screenshots; wide heatmap scrolls horizontally.
- `.venv/bin/python -m pytest -q --junitxml=artifacts/charts/pytest.xml`: final exit 0 with local socket access, 83 passed, 2 existing warnings; artifacts/charts/pytest-final.log. Initial concurrent build/test attempt failed 3 checks because Vite temporarily removed assets. A subsequent sandbox-restricted attempt stalled at socket-dependent checks and was interrupted (130). Final run follows completed build and passes; no application workaround introduced.
- `.venv/bin/python scripts/prepare_study_questions.py --questions 150`: exit 0; artifacts/charts/dataset-preparation.log. Public source fetches use pinned/rechecked hashes, never inference.
- `.venv/bin/python scripts/verify_study_questions.py`: exit 0; artifacts/charts/dataset-independent-check.json. 75 independently checked generated answers, 25 independent GSM arithmetic references, 13 GSM upstream-only and 37 CMU literal-source checks still require semantic review. All 150 operator reviews PENDING.
- `PYTHONPATH=src .venv/bin/python -m masklab budget --env-file .env`: exit 0; artifacts/charts/budget-final.json. 669 attempts, USD0.00455352 estimated spent, USD0 held, USD9.99544648 remaining; unchanged.
- `.venv/bin/python scripts/check_docs.py`: exit 0; artifacts/charts/docs-check.log, 26 documents.
- `PYTHONPATH=src .venv/bin/python scripts/verify_secret_boundaries.py`: exit 0; artifacts/charts/secret-boundaries.log, 212 files plus archive members checked, including new charts/draft data. Credential content/fingerprint never printed.
- `.venv/bin/python scripts/scan_source.py`: exit 0; artifacts/charts/gitleaks.log, no leaks. Mandatory rescan still required before every future authorized commit/push.
- `git diff --check`: exit 0.

New draft SHA256: `8b7781cc73d74301cfbfbe9823898ab2c3c69c28740dc34a964e8b8113e9902b`; study `c00a34d9a3b74ba9bad7e4d46b44d534`, latest dataset `070ebb7512e14d13b9397894f1acaa53`. 4,050-call plan has offline conservative reservation USD0.69936318, not paid usage. Full source attribution, review steps and limitations: docs/QUESTION_STUDY.md. No deployment/publication/submission/commit/push; container and owner/public release gates unchanged.

## RUN-MIXED-STUDY-AFTERWORK

TASK-007/009/010/012/013 → REQ-004/005/009/014–021/024. Explicit operator authorization: approve all 150 review rows; execute 60 development questions, freeze choices, then 90 held-out questions; existing USD10 cumulative grant unchanged. Timestamp cutoff applies only to pre-17:00 Eastern on the selected day; private originals preserved.

- `.venv/bin/python scripts/run_approved_study.py` with local HTTP access: initial run exit 1 after completed development due to 53 invalid answers, deliberately preserving evaluation gate. artifacts/mixed-study-run.log. No transport failures/uncertain charges. Development review retained strict scoring and unchanged prompts/model controls. Independent evaluator corrected its own malformed-decimal `InvalidOperation` handling; original scorer and outcomes unchanged.
- First resume exit 1, HTTP422 idempotency/protocol mismatch; wrong blob/internal-hash comparison corrected, unused duplicate frozen protocol retained. Zero paid replay. Final resume exit 0; artifacts/mixed-study-evaluation-run.log. Original development run reused; decision persisted in frozen-choices.json before 2,430-call evaluation.
- `PYTHONPATH=src .venv/bin/python -m masklab budget --env-file .env`: exit 0; budget-final.json. 4,719 cumulative attempts, estimated USD0.04656342 spent, USD0 held, USD9.95343658 remaining; no uncertain attempts or automatic top-ups.
- `.venv/bin/python scripts/verify_mixed_run.py`: exit 0; split-ledger-independent.json/log. Actual question IDs disjoint (60/90), shared config and system prompt identical, exactly one attempt per request (4,050), 570,861 input and 32,326 completion tokens, zero reasoning subset, estimated USD0.04200990 additional. Independent per-archive evaluator validates hashes, counts, paired metrics and token/cost caps; development/evaluation-independent.json. Source algorithm imports no application scorer.
- `PYTHONPATH=src .venv/bin/python scripts/report_mixed_run.py`: exit 0; docs/MIXED_STUDY_RESULTS.md and two public derivatives prepared without inference. No publication.
- `npm run build --prefix frontend`: exit 0; artifacts/mixed-study/build.log. `.venv/bin/python -m pytest -q --junitxml=artifacts/mixed-study/pytest.xml` with local sockets: exit 0, 84 passed, 2 existing warnings; pytest.log. Added public redaction boundary test preserves 17:00/later and other-day timestamps and original bytes, including Unix provider times. Targeted rerun after latest redaction changes: exit 0, redaction-test.log.
- `.venv/bin/python scripts/verify_study_questions.py`: exit 0; approved-dataset-check.json. Dataset hash unchanged; operator approval is explicit, not inferred from mechanical checks.
- Approved overwrite guard exercised through subprocess: generator expected exit1, checker exit0; approved-overwrite-guard.json verifies questions/manifest/review hashes unchanged.
- `.venv/bin/python -m compileall -q scripts src/masklab`: exit 0.
- Private SQLite backups after all calls settle: backup/workspace.sqlite3 and backup/spend.sqlite3; integrity checks both `ok`, restored source workspace tables equal; backup/checks.json. No credentials copied.
- Idle server shutdown/restart succeeded after all runs completed; no in-flight calls interrupted. New owner server remains http://127.0.0.1:8001.

Scientific limits: mixed convenience sample, generated template overlap, unknown benchmark exposure, exploratory comparisons. Development and evaluation retained separately. 53/54 invalid answers remain; no protocol/key/scoring changes to improve outcomes. Earlier immutable dataset draft notes are historical; operator approvals are in CSV/manifest and development review. Public copies are explicitly redacted derivatives, not standard-import-compatible original archives. No new hosting/publication/commit/push/submission authorized or performed. Remaining Docker/hosted/operator release gates unchanged.

Final after-work checks:

- `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 PLAYWRIGHT_BROWSERS_PATH=/home/asuna/Documents/code/masklab/artifacts/playwright-browsers node scripts/capture-study-results.mjs` from frontend, local Chromium access: exit0; browser-results-final.log and eight chart screenshots. Full navigation and 180/270 per-condition denominator assertions distinguish development/evaluation. Initial hash-only navigation capture briefly retained prior development state; corrected harness and repeated capture. Fixed workspace footer hidden only in element screenshots to avoid obscuring chart rows. Both saved pages show all four charts with zero browser errors and no inference actions. Evaluation correctness panel visually inspected with correct 270 denominators.
- Public evening-copy inspection: exit0; both derivative manifests have zero timestamp omissions and every original data payload remains byte-identical, preserving post-cutoff timestamps. Old workday public matrix retains redactions. All manifest file hashes verified. Private originals unchanged.
- `.venv/bin/python scripts/scan_source.py`: final exit0, 125 source files, no leaks; gitleaks.log. Earlier false positive on a static idempotency literal was resolved by assigning that non-secret value separately, with no suppression/baseline; actual idempotency unchanged. Mandatory clean rescan remains required before any later authorized commit/push.
- `PYTHONPATH=src .venv/bin/python scripts/verify_secret_boundaries.py`: exit0, 262 files plus archive contents, no exact credential leaks; secret-boundaries-final.log. Includes new public copies/private study evidence/backups. No credential/fingerprint printed.
- `.venv/bin/python scripts/check_docs.py` and `git diff --check`: exit0; docs-check.log.

The final public-copy check initially failed its zero-redactions assertion: regex match count included retained evening timestamps even though payloads correctly preserved them. Corrected the manifest counter to count replacements only; added an exact-count assertion to the boundary regression. Regenerated public copies; independent byte comparison now passes (zero evening redactions, original data payloads identical, hashes verified). Full 84-test regression repeated after this change and passes. No paid calls or scientific output modifications.

## RUN-REPLICATION-V2-PREPARATION

TASK-002/007/012 → REQ-004/005/007/024. Operator requested next iteration and selected broader mixed source curation. No inference authorized by unseen-row approval; preparation only. Existing first-study evidence unchanged.

- `PYTHONPATH=src .venv/bin/python scripts/prepare_replication.py`: exit0, focused 60-question draft; independent text/exhaustive checks exit0. Operator subsequently chose broader scope; focused draft archived unused in app, local files retained. No protocol or run.
- `PYTHONPATH=src .venv/bin/python scripts/prepare_mixed_replication.py`: final exit0; artifacts/replication-v2/mixed-preparation.log. Initial source checks rejected two missing literal spans and one duplicate source question; additional excerpt review replaced an ambiguous oldest-flute item and tightened three contexts. Pre-context draft retained separately, no model outcomes involved. Final data/replication-mixed-150-v2 hash `be3fc0c501455f6c061760816b57b103c6c86c2620d39d1eaa6d018810d1db50`.
- `.venv/bin/python scripts/verify_mixed_replication.py`: exit0; mixed-independent-check.json. 38 arithmetic, 37 exhaustive logic, 12 separately derived GSM references; 26 source-label-only; 37 CMU source-span checks. Exact prior question text/ID/source-question overlap zero; source articles 15 new/22 reused, generated families shared. All 150 operator reviews PENDING. No semantic/source-independent validation claim.
- `.venv/bin/python scripts/stage_replication.py` with local HTTP access: exit0; mixed-staged-study.json. Study `558127eb3544493dbeb7f0311b84e72f`, dataset `ebcb8b02762f4c46aed7623447a78833`, zero protocols/runs/provider calls. Focused draft archived.
- `PYTHONPATH=src .venv/bin/python -m masklab budget --env-file .env`: exit0; budget.json. Unchanged 4,719 cumulative attempts, USD0.04656342 estimated spent, USD0 held, USD9.95343658 remaining. Planned fresh all-evaluation matrix 4,050 calls, offline reservation USD0.70213986; no paid requests or reservation.
- `.venv/bin/python -m compileall -q scripts`: exit0.
- `.venv/bin/python scripts/check_docs.py`: exit0; docs-check.log.
- `.venv/bin/python scripts/scan_source.py`: exit0; 132 source files, no leaks; gitleaks.log. No commit/push, mandatory rescan still required before either authorized action.
- `PYTHONPATH=src .venv/bin/python scripts/verify_secret_boundaries.py`: exit0; 288 files plus archive contents checked, no exact key leak; secret-boundaries.log. New local data/artifacts included; no key/fingerprint printed.
- `git diff --check`: exit0.

Sources/licenses retained (GSM8K MIT; CMU S10 CC BY-SA 3.0), all model controls/scoring unchanged. Review workflow: docs/REPLICATION_V2.md. No publication, deploy, push, commit or submission. Additional row review is the remaining execution gate; previous 150-row approval was not self-extended to this new dataset.

## RUN-LIVE-BROAD-REPLICATION (in progress)

TASK-007/013 → REQ-009/012/021/024. Explicit operator approval of the new broad draft and request to run it on Nebius. No key/question/prompt/scorer changes. Local manifest and all 150 CSV review fields record operator approval, without changing the dataset content hash.

- `.venv/bin/python scripts/verify_mixed_replication.py`: exit0; artifacts/replication-v2/approved-independent-check.json. Same mechanical/source checks, with explicit approved review state.
- `PYTHONPATH=src .venv/bin/python -m masklab budget --env-file .env`: exit0 before execution; 4,719 paid attempts, estimated USD0.04656342 spent, USD9.95343658 remaining, USD0 held, no uncertainty/halt. Same fixed USD10 authorization.
- `PYTHONPATH=src .venv/bin/python scripts/run_live_replication.py`: running, session 36762. Log artifacts/replication-v2/live-run.log. Existing simulation safely paused through normal API, evidence preserved. Live run `adff4b5982dd4112a11c173ba48f3d57`, study `558127eb3544493dbeb7f0311b84e72f`, 4,050 requests, same prior frozen settings, conservative reservation USD0.70213986 < USD2 per-run ceiling < shared remaining grant. Stable idempotency and existing protocol/run lookup prevent duplicate execution.
- Read-only stored receipt inspection confirms `simulation=false`, actual returned model `nvidia/Nemotron-3_5-Lightning`, known input/output/reasoning token usage. At inspection 76 succeeded, two in flight; simulation is PAUSED. These are progress observations, not completed-result claims.
- `.venv/bin/python -m compileall -q scripts/run_live_replication.py scripts/verify_mixed_replication.py`: exit0. `git diff --check`: exit0.

Runner automatically collects complete raw ZIP/analysis, independent hash/scoring/paired-metric/billing checks and final cumulative budget when settled. Those final checks/costs remain pending during active inference. Invalid/negative outcomes are retained. No publication, deployment, commit, push or submission. Do not interrupt in-flight requests or reset the ledger; halt on uncertain costs through the shared guard.

## RUN-LIVE-BROAD-REPLICATION — final and private-push review

Live runner settled successfully, final log artifacts/replication-v2/live-run.log. Raw/analysis/independent/budget artifacts under artifacts/replication-v2/live/. 4,050 scheduled/finalized, 3,900 valid, 2,427 correct, 1,473 incorrect, 150 invalid; zero failed/refused/uncertain/pending. Cost USD0.04329672, 584,460 input + 34,288 output, zero reasoning subset. Cumulative estimated spend USD0.08986014, remaining USD9.91013986, held USD0, 8,769 attempts, no unknown costs/top-ups. Original outcomes and settings unchanged. All source/template/sampling limits retained in docs/REPLICATION_V2_RESULTS.md.

- Independent evaluator from scripts/evaluate_live.py ran on settlement: status PASS; live/independent.json. Counts, paired metrics, hashes, model identity, token caps and prices verified.
- Independent final budget/public-copy check: exit0; live/budget-reconciliation.json. 4,050-attempt and USD0.04329672 exact deltas against pre-run ledger, settled grant with no unknown charges. Every new public data payload byte-identical to private original; all file hashes verified; zero timestamp redactions for this evening run. New public derivative remains distinct from a standard-importable original.
- `gh repo view mso-docs/MaskLab --json nameWithOwner,visibility,url`: exit0, PRIVATE, matching observed origin; read-only verification. No commit, push or remote edit.
- `gitleaks detect --source . --redact --no-banner --report-path artifacts/replication-v2/push-history-scan.json`: exit0, one commit scanned, no leaks; push-history-scan.log.
- `.venv/bin/python scripts/scan_source.py`: exit0; push-source-scan.log, no leaks across tracked and nonignored untracked source. Separate exact-key scan includes new ZIP members/private evidence and checks tracked dotenv exclusions; push-secret-check.log, PASS. No credentials/fingerprints printed.
- `npm run build --prefix frontend`: exit0, push-build.log. `npm run test:charts --prefix frontend`: exit0, push-chart-tests.log.
- `.venv/bin/python -m pytest -q --junitxml=artifacts/replication-v2/push-pytest.xml` with local sockets: exit0, 84 passed / 2 existing warnings; push-pytest.log. No live inference tests included.
- `.venv/bin/python scripts/check_docs.py`: exit0, push-docs-check.log. `git diff --check`: exit0.

README and SECURITY now describe actual implementation status and approved public derivatives; private original datasets/databases/credentials/raw evidence remain excluded. Current source edits are uncommitted/unstaged; these checks do not authorize commits/pushes or bypass mandatory staged/history secret scans. Docker/hosted/public-release gates remain independent of private source-push readiness.

Private-push browser verification initially failed one of five journeys twice: the 216-request monitor reached 206/216 but missed the unchanged 30-second completion deadline. Fresh test-workspace isolation removed reused-state dependence but did not fix the timeout alone. Trace inspection counted 34 full scientific-analysis HTTP requests during approximately 30 seconds of monitoring. The frontend now polls lightweight run status on the monitor, prevents overlapping progress polls, refreshes full analysis on settlement and explicitly on Analyze/Inspect actions. Scientific scoring, worker/provider code and frozen evidence are unchanged. Added an analysis-request-count regression assertion to the existing browser journey; timeouts were not increased and no retries/skips introduced.

Final checks after the fix:

- `npm run build --prefix frontend`: exit0; push-monitor-build.log.
- `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 PLAYWRIGHT_BROWSERS_PATH=/home/asuna/Documents/code/masklab/artifacts/playwright-browsers npm test --prefix frontend`: final exit0, 5 passed in 55 seconds; push-browser-final.log. Full workflow 22.4 seconds, including download/import/reanalysis and the monitor request-count regression. Failed attempts retained in push-browser.log and push-browser-isolated.log.
- New scripts/serve_owner_fixture.py creates a fresh browser-only owner workspace per invocation, retaining each run's artifacts. Prior test/research data is never deleted or reused. Default tests remain simulated and never load `.env`.
- `.venv/bin/python -m compileall -q scripts/serve_owner_fixture.py`: exit0.

All test changes map TASK-006/009/012 → REQ-001/010/014–020/024. Final source/history/key scans and docs/diff checks remain mandatory before a later authorized commit/push; no commit/push occurred here. Private origin visibility verified read-only. Source-ready does not claim hosted/container/public release verification.
