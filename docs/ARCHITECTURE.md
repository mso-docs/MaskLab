# MaskLab architecture

TASK-001–012; REQ-001–024. Architecture implements DES-001–006 in the canonical plan.

```text
React / TypeScript / Vite
    same-origin JSON API, no provider credentials
FastAPI owner or separate restricted demo mode
    authoritative validation, quotas, immutable protocol freeze
SQLite schema 1 + SHA256 evidence blobs + online backups
    studies → datasets / protocols → durable runs → requests → attempts
Single writer/worker guarded by an OS lock
    commit intent → bounded provider dispatch → transactionally persist response
Pure extraction / scoring / question-cluster analysis
    exact raw evidence → versioned scored records → portable ZIP
```

| Module | Responsibility | Trace |
|---|---|---|
| `contracts.py` | Strict versioned schemas, bounded UTF-8 JSON/CSV, split validation, deterministic prompts/matrix | TASK-001/002; REQ-004–008 |
| `store.py` | SQLite transactions, immutable content-addressed evidence, history/idempotency, quota serialization, backup | TASK-001/004/011; REQ-001/005/008/010–012/022–023 |
| `provider.py` | Clearly separate simulation, allowlisted HTTP adapter, reviewed live capability/funding gates, safe metadata | TASK-003; REQ-009/012/020–021 |
| `worker.py` | Exclusive worker, crash uncertainty, bounded concurrency/deadlines/attempts, stop/resume and cost reservations | TASK-004; REQ-010–012/021 |
| `analysis.py` | Versioned exact extraction, honest denominators, paired eligibility, cluster bootstrap and variability | TASK-005/009; REQ-013–017 |
| `portable.py` | Manifest/report/CSV export and bounded inspection-only archive verification/reanalysis | TASK-010; REQ-018–020 |
| `api.py` | Owner/demo boundary, API validation, public visibility, same-origin protection, React serving | TASK-006–012; REQ-001–003/020–023 |
| `frontend/src` | Study/design/monitor/analysis/explorer/help, appearance and routes | TASK-006–009/012; REQ-001–008/010–020 |

Normalized datasets and protocols are canonical JSON with SHA256 identities; original uploaded bytes are separately retained by content hash. Blobs live in private SQLite rather than separate files, allowing evidence and references to commit atomically and simplifying complete online backup. This is a reversible storage implementation choice within the single-volume topology; it introduces no external storage service. No delete API exists for referenced versions/results. SQL triggers reject updates to frozen protocols, datasets, blobs, rendered requests and finalized attempts. Reanalysis adds rows/blobs, never updates originals.

An intent/attempt is persisted IN_FLIGHT before dispatch. On process death, the replacement worker can acquire the lock and mark orphaned attempts UNCERTAIN, keeping cost reservations. It cannot prove whether the provider accepted the request; no automatic replay occurs. Completed outcomes survive. At most one worker schedules up to four requests concurrently, enforcing owner/global reservations in SQLite before each dispatch. Unknown usage is not recorded as zero cost. Output bounds and account capability assertions still require actual live verification; the application bound is not a provider billing guarantee.

The simulated adapter is an explicit provider with a separate model ID and durable evidence-kind flags. It receives rendered messages/settings, not answer keys. It emits fixed strings and controlled refusal, invalid, transient, timeout and unknown-usage cases. These are test outcomes only; no model behavior is simulated credibly or claimed as research. Live and simulated rows are excluded from each other's budget accounting and never aggregated into one run/analysis.

Security uses direct loopback by default, optional bearer-authenticated hosted owner access, same-origin/custom-header writes, inert React text, constrained structured identifiers, no arbitrary URL proxy, narrow metadata retention and safe CSV export. Demo mode blocks owner mutations and private reads, chooses curated protocols server-side and serializes persistent socket-identity/global quotas. It intentionally does not trust forwarded IP/browser cookies. No arbitrary code execution, semantic judge or model-written scientific claim feature exists.

The portable format is fully inert and never extracted. Hashes and deterministic reanalysis verify internal consistency, not the scientific authenticity of untrusted authors. The archive excludes auth material/private connection settings by schema. Scientific text is preserved; users must never paste keys into it. See OPERATIONS.md and RESEARCHER.md for the exact trust boundaries and limits.

Python 3.14/Node 22 are the tested release runtime; hashes/lockfile resolution are checked by a fresh installation. CI is prepared for local correctness/security/browser checks and Gitleaks, with no deployment or paid API call. Docker is a prepared durable-volume topology; this host has no Docker binary, so image build/start remains an explicit environment check, not a claimed success.


Live integration hardening — TASK-013 / REQ-009/020/021/024: `budget.py` now supplies a separate shared SQLite grant/charge ledger across owner/demo workspaces. `runtime.py` adds explicit private dotenv loading with no shell execution. Every attempt reserves before dispatch, settles known usage and halts on unknown usage; there is no expiry/reset/top-up. Replay after a stale workspace restore is blocked by global logical-attempt history. Model-specific controls are bound into the immutable protocol and preflight rejects capability/price drift. The provider validates actual served identity, accounts for reasoning as a completion subset, requests the default service tier and excludes private reasoning text. The UI exposes safe verified model/price presets, cumulative remaining budget and accurate saved/live labels.
