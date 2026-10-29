# Release acceptance matrix

Local implementation evidence was recorded 2026-10-28 in verification.md. “Local verified” means the listed automated fixture/API/browser checks passed, with simulated provider outputs clearly labeled; it does not grant owner acceptance or establish live inference/public deployment. No requirement passes by narrative or screenshot alone.

| Test | Requirement | Observable acceptance | Status |
|---|---|---|---|
| TEST-001 | REQ-001 | Create, reopen, rename and archive a study; versions/results remain inspectable after restart. | Local verified; see RUN-LOCAL-20261028 |
| TEST-002 | REQ-002 | Browser test every major view, keyboard focus, both themes and accessible tabular alternatives; refresh restores selection. | Local verified; see RUN-LOCAL-20261028 |
| TEST-003 | REQ-003 | Demo visitor cannot access owner settings/imports/credentials/private studies; saved/live statuses are explicit. | Local verified; see RUN-LOCAL-20261028 |
| TEST-004 | REQ-004 | Import valid CSV/JSON; reject invalid IDs/types/answers/encodings/nonfinite/oversize with no partial import. | Local verified; see RUN-LOCAL-20261028 |
| TEST-005 | REQ-005 | Attempt overlapping split IDs and mutation of a referenced dataset version; reject both and preserve hashes. | Local verified; see RUN-LOCAL-20261028 |
| TEST-006 | REQ-006 | Compare rendered paired requests; only declared factors differ, neutral role is empty, conversations are independent. | Local verified; see RUN-LOCAL-20261028 |
| TEST-007 | REQ-007 | Calculate matrix size from fixtures; enforce model/role/repetition/concurrency/request limits before calls. | Local verified; see RUN-LOCAL-20261028 |
| TEST-008 | REQ-008 | Change dataset or prompt after freeze; create a new version and leave prior rendered requests/hash unchanged. | Local verified; see RUN-LOCAL-20261028 |
| TEST-009 | REQ-009 | Record real paid-authorized model-list and inference smoke separately; unsupported parameters/model block with no fallback. | Actual model list + funded smoke + cap/reasoning probes verified RUN-LIVE-20261028 |
| TEST-010 | REQ-010 | Kill/restart worker around response persistence; preserve completed attempts and classify uncertain in-flight work. | Local verified; see RUN-LOCAL-20261028 |
| TEST-011 | REQ-011 | Pause/cancel/restart requests under controlled failures; no new dispatch after stop, retries bounded and all attempts retained. | Local verified; see RUN-LOCAL-20261028 |
| TEST-012 | REQ-012 | Inspect success/refusal/invalid/timeout/uncertain records and exports; exact final responses retained without auth material. | Local verified; see RUN-LOCAL-20261028 |
| TEST-013 | REQ-013 | Run independently derived extraction fixtures for labels, decimals, malformed JSON and nonfinite values; exact expected statuses. | Local verified; see RUN-LOCAL-20261028 |
| TEST-014 | REQ-014 | Recompute all denominators/counts manually from a fixed mixed-outcome table and verify pending/uncertain exclusions. | Local verified; see RUN-LOCAL-20261028 |
| TEST-015 | REQ-015 | Hand-compute false-alternative adoption and correct-to-false pairs; report eligibility/exclusions separately. | Local verified; see RUN-LOCAL-20261028 |
| TEST-016 | REQ-016 | Bootstrap a fixed paired clustered table with fixed seed; independently verify repeat grouping and interval/no-interval behavior. | Local verified; see RUN-LOCAL-20261028 |
| TEST-017 | REQ-017 | Click each chart cell through to contributing records, paired responses and excluded rows; zero/missing never conflated. | Local verified; see RUN-LOCAL-20261028 |
| TEST-018 | REQ-018 | Export a known study and independently verify manifest/hash/CSV/report contents; secret and private-host canaries absent. | Local verified; see RUN-LOCAL-20261028 |
| TEST-019 | REQ-019 | Round-trip valid archive; reject traversal/symlink/expansion/hash/schema attacks; imports start no calls and replace no evidence. | Local verified; see RUN-LOCAL-20261028 |
| TEST-020 | REQ-020 | Browser/network/export scans expose no key; reject endpoint SSRF and owner routes in demo; escape HTML/CSV injection fixtures. | Local verified; see RUN-LOCAL-20261028 |
| TEST-021 | REQ-021 | Exercise cost reservation/exhaustion, unknown usage, output/request/time caps; stop new calls and show unresolved cost honestly. | Shared guard/recovery/unknown-cost fixtures + observed real cap/usage verified; invoice not reconciled |
| TEST-022 | REQ-022 | Exceed public visitor/deployment/day/cost quotas; server blocks requests including parallel/spoofed-browser attempts. | Local verified; see RUN-LOCAL-20261028 |
| TEST-023 | REQ-023 | Fresh locked installation and documented local/deployment starts; health/backup/restore/migration tests preserve evidence. | Fresh lock/package + actual live-evidence backup verified; Docker/hosted runtime pending |
| TEST-024 | REQ-024 | Complete scientific/API/recovery/security/browser suites plus separately authorized real provider and deployment smoke records. | 83 Python + 3 simulated / 2 live browser journeys; independent live evaluator; hosted checks pending |
| TEST-025 | REQ-025 | Owner acceptance, working public demo/source/license/README, real sub-three-minute public video, feedback and frozen submission assets. | Local assets/observed feedback/acceptance steps ready; owner/public release pending |

TEST-002 coverage is browser workflow, keyboard focus, theme and narrow-layout smoke coverage, not a claim of an exhaustive accessibility audit. TEST-021 verifies scheduler reservations with controlled providers; real token/billing semantics remain pending. TEST-022 verifies transactional quotas and restricted simulated demo behavior; actual hosted abuse/availability verification remains pending.

Current live evidence supersedes earlier live-pending statements for local integration. Hosted availability, container execution and final owner acceptance remain open; no application test establishes an independently reconciled provider invoice/account hard cap.
