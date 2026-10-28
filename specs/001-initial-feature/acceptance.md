# Release acceptance matrix

Every item is PENDING APPLICATION IMPLEMENTATION; foundation checks are recorded separately. No requirement is passed by narrative or a generated screenshot.

| Test | Requirement | Observable acceptance | Status |
|---|---|---|---|
| TEST-001 | REQ-001 | Create, reopen, rename and archive a study; versions/results remain inspectable after restart. | Pending |
| TEST-002 | REQ-002 | Browser test every major view, keyboard focus, both themes and accessible tabular alternatives; refresh restores selection. | Pending |
| TEST-003 | REQ-003 | Demo visitor cannot access owner settings/imports/credentials/private studies; saved/live statuses are explicit. | Pending |
| TEST-004 | REQ-004 | Import valid CSV/JSON; reject invalid IDs/types/answers/encodings/nonfinite/oversize with no partial import. | Pending |
| TEST-005 | REQ-005 | Attempt overlapping split IDs and mutation of a referenced dataset version; reject both and preserve hashes. | Pending |
| TEST-006 | REQ-006 | Compare rendered paired requests; only declared factors differ, neutral role is empty, conversations are independent. | Pending |
| TEST-007 | REQ-007 | Calculate matrix size from fixtures; enforce model/role/repetition/concurrency/request limits before calls. | Pending |
| TEST-008 | REQ-008 | Change dataset or prompt after freeze; create a new version and leave prior rendered requests/hash unchanged. | Pending |
| TEST-009 | REQ-009 | Record real paid-authorized model-list and inference smoke separately; unsupported parameters/model block with no fallback. | Pending |
| TEST-010 | REQ-010 | Kill/restart worker around response persistence; preserve completed attempts and classify uncertain in-flight work. | Pending |
| TEST-011 | REQ-011 | Pause/cancel/restart requests under controlled failures; no new dispatch after stop, retries bounded and all attempts retained. | Pending |
| TEST-012 | REQ-012 | Inspect success/refusal/invalid/timeout/uncertain records and exports; exact final responses retained without auth material. | Pending |
| TEST-013 | REQ-013 | Run independently derived extraction fixtures for labels, decimals, malformed JSON and nonfinite values; exact expected statuses. | Pending |
| TEST-014 | REQ-014 | Recompute all denominators/counts manually from a fixed mixed-outcome table and verify pending/uncertain exclusions. | Pending |
| TEST-015 | REQ-015 | Hand-compute false-alternative adoption and correct-to-false pairs; report eligibility/exclusions separately. | Pending |
| TEST-016 | REQ-016 | Bootstrap a fixed paired clustered table with fixed seed; independently verify repeat grouping and interval/no-interval behavior. | Pending |
| TEST-017 | REQ-017 | Click each chart cell through to contributing records, paired responses and excluded rows; zero/missing never conflated. | Pending |
| TEST-018 | REQ-018 | Export a known study and independently verify manifest/hash/CSV/report contents; secret and private-host canaries absent. | Pending |
| TEST-019 | REQ-019 | Round-trip valid archive; reject traversal/symlink/expansion/hash/schema attacks; imports start no calls and replace no evidence. | Pending |
| TEST-020 | REQ-020 | Browser/network/export scans expose no key; reject endpoint SSRF and owner routes in demo; escape HTML/CSV injection fixtures. | Pending |
| TEST-021 | REQ-021 | Exercise cost reservation/exhaustion, unknown usage, output/request/time caps; stop new calls and show unresolved cost honestly. | Pending |
| TEST-022 | REQ-022 | Exceed public visitor/deployment/day/cost quotas; server blocks requests including parallel/spoofed-browser attempts. | Pending |
| TEST-023 | REQ-023 | Fresh locked installation and documented local/deployment starts; health/backup/restore/migration tests preserve evidence. | Pending |
| TEST-024 | REQ-024 | Complete scientific/API/recovery/security/browser suites plus separately authorized real provider and deployment smoke records. | Pending |
| TEST-025 | REQ-025 | Owner acceptance, working public demo/source/license/README, real sub-three-minute public video, feedback and frozen submission assets. | Pending |
