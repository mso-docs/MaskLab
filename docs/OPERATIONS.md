# MaskLab operator guide

TASK-003/004/011/012/013; REQ-009–012/020–024. Local setup and simulation are authorized. Paid inference, hosted publication and submission remain separately gated.

## Local topology

Use Python 3.14 and Node 22 with the checked-in locks (see README). SQLite schema version 1 lives at `$MASKLAB_DATA_DIR/masklab.sqlite3`; the default is `artifacts/workspace`. Database blobs retain original uploaded bytes and immutable normalized datasets/protocols. Do not put the workspace, provider credentials or exports in Git. `masklab serve` starts exactly one embedded worker. Alternatively use `serve --external-worker` plus `masklab worker` against the same directory. A nonblocking OS file lock rejects a second worker. Do not delete a live worker lock file or run separate replicas with separate local disks.

The owner binds to 127.0.0.1 by default. Non-loopback owner binding requires `MASKLAB_OWNER_TOKEN` externally configured; enter that token in the browser's session unlock field. It remains in browser memory and is not persisted. TLS is required at a future authenticated hosting boundary; do not expose the owner workspace without it. Direct loopback access without a token is the supported local default. API mutations require same-origin checks plus the custom application header. Host and socket-address checks protect the unconfigured owner view. Do not trust forwarded client-IP headers.

Health: `GET /api/health`. Interactive API docs are disabled to reduce public surface. Local start:

```bash
.venv/bin/python -m masklab serve --port 8000 --data-dir artifacts/workspace
```

Owner ceilings may be lowered with `MASKLAB_MAX_REQUESTS` (default 5000) and `MASKLAB_MAX_CONCURRENCY` (default 4); protocol release ceilings cannot be raised through them.

## Backup and recovery

```bash
.venv/bin/python -m masklab backup --data-dir artifacts/workspace --destination /tmp/masklab-backup.sqlite3
```

The destination must be new. This uses SQLite's online backup API, including committed WAL state. Preserve the private `visitor-secret` alongside a demo workspace backup. Backups contain answer keys/raw outputs and should be private. Stop the server/worker before replacing the database with a verified backup; preserve the old workspace first. Run `PRAGMA integrity_check` with SQLite/Python and `/api/health` after restoration. Reopen a study and compare protocol/blob hashes before proceeding. Schema 1 initialization is additive/idempotent; newer schemas are rejected, never silently downgraded. Future migrations require backup and explicit versioned migration code.

A worker restart takes the exclusive lock and marks all orphaned IN_FLIGHT attempts UNCERTAIN with unresolved cost. Completed evidence stays immutable. It does not replay the unknown request. Pause/cancel prevent new scheduling while allowing up to 65 seconds of in-flight completion. Resume schedules only pending work. Documented connection failures/rate limits may receive one new attempt (two total); read timeouts/ambiguous 5xx are never automatically retried. Export the ledger and reconcile unknown usage with provider logs before any later separately consented recovery action. There is no ambiguous-replay button.

## Credential and paid-call gate — do not enable until authorized

Obtain the key outside Git. Do not paste credentials into study text, protocol JSON, screenshots or logs. The app deliberately does not load `.env` automatically. Configure the process environment through your private service manager/shell. Never put a token in a launch command committed to source.

1. Configure `NEBIUS_API_KEY` server-side and explicitly check the account model list using **Methods & help → Explicitly check account model list**. This is a read-only discovery action, not evidence of inference access.
2. Review the exact available NVIDIA Nemotron ID, supported temperature parameter, output-cap parameter, reasoning/output billing semantics and current prices from the provider. Record these in an **external** JSON file referenced by `MASKLAB_CAPABILITIES_FILE`. No model ID or price is invented by the application.
3. Obtain separate explicit paid-call authorization. Only then set `MASKLAB_APPROVED_SPEND_USD` to the approved total (at most USD10 under this release contract). This application persists known spend plus unresolved reservations across live runs. The scheduling ceiling is not a provider-account hard cap and cannot account for unrelated external usage; reconcile that separately.
4. Start with an explicitly funded one-request access smoke. `POST /api/provider/smoke` accepts `{"model":"<exact account ID>","budget_usd":"<approved small ceiling>"}` with owner authentication and `X-MaskLab-Request: 1`. It uses one bundled arithmetic question, neutral role, absent belief, concurrency one and at most 64 output tokens. It may run against a listed but not-yet-inference-verified model. It still requires reviewed serving/billing semantics, prices, key and paid authorization. The request and every attempt are durable and exportable; unsuccessful/ambiguous evidence is preserved.
5. Inspect the smoke response, actual model metadata, usage/cost, timestamps, request ID and known/unknown serving revision. Record the evidence hash; only after real verification mark that model's external `inference_verified` field true. A successful HTTP model list is insufficient. Do not treat the smoke question as research.
6. Configure an owner study with the exact verified model and reviewed prices. Preview/freeze before scheduling. No endpoint/provider/model substitution is permitted.

External capability-file shape (placeholders are not executable configuration):

```json
{
  "endpoint": "https://api.tokenfactory.nebius.com/v1",
  "output_parameter": "max_tokens",
  "billed_output_includes_reasoning": true,
  "models": {
    "EXACT_ACCOUNT_NVIDIA_NEMOTRON_ID": {
      "inference_verified": false,
      "parameters": ["temperature"],
      "input_price_per_million": "REVIEWED_PRICE",
      "output_price_per_million": "REVIEWED_PRICE"
    }
  }
}
```

The `true` billing assertion and parameter spelling above are examples of required reviewed assertions, **not a claim that serving semantics have been verified**. Supported output parameter values are `max_tokens` and `max_completion_tokens`; unverified reasoning billing blocks inference. The only allowed endpoint is `https://api.tokenfactory.nebius.com/v1`. Endpoint changes require a reviewed code change, never an arbitrary URL proxy.

Provider references checked during implementation: [Nebius API schema](https://api.tokenfactory.nebius.com/docs), [official Token Factory cookbook](https://dev.nebius.com/cookbook/beam-reflection-token-factory). Model/account semantics remain pending live review.

## Separate public demo — prepared, not published

Use a different workspace/process with `MASKLAB_MODE=demo`. Curate studies using the owner workspace before starting demo mode. Only public study IDs are visible; no arbitrary import/configuration/provider/owner settings endpoints are writable. Demo execution chooses a curated frozen protocol of at most eight requests. It enforces one active batch per socket-derived visitor, at most three batches per visitor/day, 50 batches/day globally and USD1/day conservative reservations within the separately approved global ceiling. Quotas persist in SQLite transactions and cannot be bypassed by browser cookies or X-Forwarded-For. Behind a reverse proxy all visitors may share the proxy socket identity; this intentionally fails conservatively. A future proxy identity design must be reviewed, not enabled by trusting arbitrary headers.

When quota or live prerequisites fail, saved public runs remain inspectable and are labeled by their actual evidence type. Do not curate simulated records as verified model results. No measured saved example exists until authorized real execution. No arbitrary public model or endpoint selection exists.

The Dockerfile builds the React assets and runs CPU-only FastAPI with a persistent `/workspace` volume and non-root user. Container build/start, TLS/auth proxy, backup storage and public availability through December judging still need environment verification and release authorization. Serverless ephemeral storage is unsupported. Do not deploy by merely building an image.

## Release gates still pending

TASK-013: funded account discovery/access smoke, live capability semantics, real inference and authorized hosted backup/access tests. TASK-014: owner acceptance, actual Nebius/NVIDIA feedback, a public video strictly under three minutes, public source/demo release and submission. Preserve negative findings; freeze submission materials after the official cutoff. No paid calls, publishing, hosting provisioning, commit, push or submission were performed in local implementation.


## Current authorized local integration — 2026-10-28

The operator supplied the private local `.env` and explicitly authorized **USD10 cumulative additional Nebius inference** across all MaskLab workspaces, smoke/retries/experiments. That scoped authorization supersedes the earlier paid-call-pending paragraphs for local development/verification only. Deployment, publication, submission and commits/pushes remain unapproved. Use the [exact acceptance guide](ACCEPTANCE.md) for the configured build.

The local file is now loaded only with `--env-file .env`; the parser treats values as inert strings, allows only known runtime names, never executes/interpolates shell syntax and omits values from errors. The key was not printed or copied into source, archives, logs or frontend. All dotenv copies except `.env.example` are Git-ignored.

`MASKLAB_SPEND_LEDGER` and `MASKLAB_AUTHORIZATION_ID` bind the server/worker to the same persistent additional-spend grant, independent of `MASKLAB_DATA_DIR`. The initialized limit is USD10 and cannot be updated/deleted through the ledger interface. Every paid attempt gets an atomic reservation before dispatch. Known usage settles it; unknown usage keeps the full reservation and halts all new live dispatch. Reservations never expire or reset with a day/process/run/workspace. A cross-database crash before evidence commit is conservative; after evidence commit, recovery settles the recorded known usage. Restored/copied workspaces cannot replay an already-ledgered logical attempt: attempt-history disagreement blocks scheduling pending reconciliation. Never replace the current ledger with an older backup or create a new ledger to recover allowance.

The reviewed model is `nvidia/Nemotron-3_5-Lightning`, input/output list prices USD0.06/USD0.24 per million tokens. The live request profile freezes `temperature`, `response_format=json_object`, `chat_template_kwargs.enable_thinking=false`, `service_tier=default`, one completion and matching `max_tokens`/`max_completion_tokens`. The provider's documented total-completion cap includes reasoning. An isolated thinking-enabled probe used 64/64 completion tokens as reasoning and produced an INVALID truncated final response, which was preserved. Reasoning tokens are counted within completion tokens, never added a second time. Cached input is conservatively estimated at the uncached list price. Exact served-model mismatches fail rather than substituting a model. Revision/tier metadata is unknown if absent; no hidden reasoning text is retained.

The actual verification receipt totals are 669 live attempts, 54,664 input tokens and 5,307 completion tokens (64 reasoning tokens included). Estimated cost USD0.00455352; held USD0; remaining USD9.99544648 at handoff. Provider invoices/account charges/taxes/external usage are not independently reconciled or controlled by this application. No top-up or billing-account setting was changed.

To back up the current shared ledger consistently, with live dispatch stopped, use Python's SQLite online backup API from the configured source to a **new private destination**. Back up the workspace separately with `masklab backup --env-file .env --destination <new-private-file>`. Preserve both current snapshots plus protected capability configuration, but never restore a stale ledger to increase allowance. The live workspace and ledger backups were independently opened and their evidence/charge hashes checked; actual public-host/container recovery remains pending release authorization/environment capability.

Developer scripts `configure_live.py`, `live_verify.py` and the explicit Playwright live configuration are opt-in paid verification tooling; source text does not itself grant spending permission. The configuration script records this specific existing authorization and cannot reset it. Do not run it to obtain more credit. The default `pytest`, browser suite and CI use fakes/isolated ledgers and make no paid calls. `scripts/evaluate_live.py` independently verifies live archive hashes, counts, paired eligibility and usage/cost arithmetic without importing application code. `scripts/verify_secret_boundaries.py` checks the exact private credential against nonignored source, compiled assets, browser artifacts, databases and decompressed export members without printing it or its fingerprint.
