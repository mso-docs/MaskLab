# Architecture and implementation plan

Revision 1.0. The complete release is specified; no application component is implemented today.

## Architecture decisions

DES-001 → REQ-001–003/017: React + TypeScript + Vite browser client; research workspace with study explorer, protocol editor, matrix preview, live monitor, paired-response inspector, results and export views. Semantic accessible controls and CSS design tokens support dark/light themes. Backend APIs are authoritative; no credentials or provider calls from the browser. Build one integrated experience rather than a collection of placeholder screens.
DES-002 → REQ-004–008: Python 3.11+ core with Pydantic schemas and FastAPI, validated JSON/CSV import, deterministic prompt renderer and immutable canonical-JSON protocol hashes. SQLite stores studies, dataset/protocol versions, runs, logical requests, attempts and analysis versions. Evidence blobs are content-addressed private files; database rows reference hashes and relative safe paths. Reference counts prevent deletion of used evidence.
DES-003 → REQ-009–012/021–022: A dedicated single-writer worker claims durable jobs using SQLite transactions/leases. HTTPX invokes the OpenAI-compatible Token Factory chat API with bounded deadlines/concurrency. A provider adapter owns capability checks, error taxonomy, safe metadata and usage extraction. Reconcile IN_FLIGHT rows after a crash as UNCERTAIN; never reuse an attempt ID to hide an additional paid call. Cooperative cancellation stops scheduling and bounds in-flight requests. No automatic fallback model or endpoint.
DES-004 → REQ-013–016: Pure scoring/analysis modules separate extraction, eligibility/denominators, aggregation and question-cluster resampling. Use stdlib Decimal for exact finite numeric answers and NumPy for resampling during implementation. Keep raw response evidence immutable. Unit fixtures include explicit independent mathematical calculations and adversarial missing/error cases. A model cannot judge its own correctness or adjust answer keys.
DES-005 → REQ-018–020/023: Versioned manifest exporter and defensive importer, escaped CSV/HTML text, auth/endpoint allowlisting, owner-loopback defaults and separate restricted demo configuration. ZIP streaming validates expansion limits before materialization. SQLite backups use a consistent snapshot; restoring/merging cannot overwrite verified evidence. Hosted demo runs one backend/worker against persistent storage; initial deployment uses a CPU container, not a rented GPU.
DES-006 → REQ-024–025: Python pytest/API/integration tests, TypeScript UI checks and Playwright browser journeys. A deterministic provider fake tests rate limits/errors/recovery/cost uncertainty; a separately authorized smoke call verifies actual Nebius inference. CI performs checks and Gitleaks, with no deployment or paid inference by default. A deployment smoke verifies judge routes and both saved/live behaviors after authorization.

## Planned interfaces

GET/POST /api/studies; versioned dataset/protocol endpoints; POST protocol preview/freeze; POST run start/pause/resume/cancel; GET run status/events/attempts/results; GET/POST safe export/import. Auth applies to owner endpoints; demo routes apply fixed models/studies and server quotas. Requests use idempotency keys; ambiguous provider acceptance is not represented as exactly-once execution. Structured errors expose actionable codes without provider secrets.

Core contracts: Question(id,type,text,choices,expected,incorrect_belief,category,split); Protocol(version,hash,dataset_hash,split_hash,roles,frames,models,repeats,ordering,parameters,budgets,metric_version); Request(id,rendered_messages,model,trial_key,state); Attempt(id,request_id,ordinal,state,times,provider_ids,usage,cost_state,response_hash,error_code); Score(version,answer_status,normalized,correct,eligibility); Analysis(protocol_hash,scorer_version,seed,counts,paired_summaries,intervals).

All user/model strings are data, never shell commands. No shell/code execution feature or arbitrary provider URL proxy is required. No fake measurements, confidence-as-probability claims, access to hidden reasoning, or unsupported internal-mechanism claims.

## Dependencies and decisions

Chosen stack is recorded to prevent repeated framework decisions. Exact package versions and lockfiles are resolved and verified during the authorized implementation phase; none are downloaded today. Planned backend runtime: FastAPI/Pydantic, HTTPX, NumPy, Uvicorn and existing stdlib SQLite. Frontend: React/TypeScript/Vite; choose a small plotting library only if tabular accessibility and bundle cost justify it. Development: pytest and Playwright. Pin resolved versions and review licenses/security before use. Do not invent a lockfile without resolution.

## Delivery schedule and feasibility

Tuesday October27: ACP creation, complete requirements, architecture, contracts, independent fixtures and implementation work orders. Wednesday: finish persistence/provider/worker/scoring vertical slice early, then complete study/import/configuration and research UI. Thursday: finish integration/security/browser checks, owner acceptance, authorized deployment, recorded video and submission that night. All times America/New_York.

This is an ambitious full release for roughly two implementation days. If the first real bounded experiment is not working by Wednesday afternoon, report the failed task, evidence and schedule impact immediately; do not silently cut requirements. Reuse the chosen components and parallelize only if the operator explicitly authorizes agents. Keep a continuously runnable vertical slice as implementation progresses, but continue until the complete release contract is met.

## True prerequisites to batch

Before real integration: Token Factory credentials provided outside Git, confirmed accessible NVIDIA model, explicit paid-call authorization up to the proposed USD10 cap. Before public release: hosting choice/credentials and cost approval, approved public repository/license ownership, reviewer access, and permission to publish/upload/submit. These are external prerequisites rather than routine coding decisions. All deterministic implementation and fake-provider testing can proceed within separately authorized implementation scope while prerequisites are supplied.
