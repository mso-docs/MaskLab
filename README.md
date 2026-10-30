# MaskLab

A local research workbench for measuring how answers change under independent persona and stated-belief conditions.

[Demo and test build](https://mso-docs.github.io/MaskLab/) · [Video walkthrough](https://youtu.be/gmgJFIZNrYs) · [Devpost project](https://devpost.com/software/masklab)

**Current status:** local implementation and live Nebius integration are verified. The selected NVIDIA model completed the default integration matrix plus two 4,050-request mixed-question studies. See the [first study](docs/MIXED_STUDY_RESULTS.md) and [fresh-question replication](docs/REPLICATION_V2_RESULTS.md). Simulated development remains separate from genuine live responses. **These convenience studies are not a validated scientific benchmark.** Owner acceptance, container-runtime verification and public release remain pending. See [verification](specs/001-initial-feature/verification.md) and [handoff](docs/HANDOFF.md).

Create a study → import/version questions → configure roles × belief frames → preview every prompt and cost reservation → freeze → run a durable job → compare paired outcomes → inspect exact responses → export hash-verified evidence.

## Run locally

Tested runtime: Python **3.14**, Node **22**, Linux. The release uses SQLite on a persistent local volume and one worker. No GPU, provider key or spending is required for simulation.

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock
npm ci --prefix frontend
npm run build --prefix frontend
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/python -m masklab serve
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Create a study, choose **Configure experiment**, then **Use synthetic tooling fixtures**. Preview/freeze a protocol and start a **simulated** run. The default 24 × 3 × 3 × 3 matrix contains 648 requests. Smaller matrices are configurable; they are not the product limit. The simulated provider emits a fixed answer string, not a prediction of model behavior. Its outputs remain labeled throughout tables, reports and ZIP exports.

Data is stored under `artifacts/workspace/` by default and ignored by Git. Override with `MASKLAB_DATA_DIR` pointing to a private persistent directory. Private datasets, raw archives, keys and weights stay outside source control. The operator-approved, explicitly labeled derivatives in `public-evidence/` are the sole evidence-sharing exception; their dataset licenses and timestamp policy are retained. The included synthetic fixtures are tooling examples, not a validated benchmark.

For UI development, run the backend with `--external-worker`, start `.venv/bin/python -m masklab worker` separately, and run `npm run dev --prefix frontend`. The Vite loopback dev server proxies `/api` to port 8000. Production serves the compiled React client directly from FastAPI.

## Verify without credentials

```bash
.venv/bin/python -m pytest -q
npm run build --prefix frontend
frontend/node_modules/.bin/playwright install chromium
npm test --prefix frontend
.venv/bin/python scripts/evaluate_release.py artifacts/verification/browser-export.zip
```

Playwright starts a private loopback server using a fresh `artifacts/owner-e2e-*` workspace per invocation; it never makes live calls. On Ubuntu 26.04, the tested compatibility settings are `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64` and `PLAYWRIGHT_BROWSERS_PATH=$PWD/artifacts/playwright-browsers` for both install and test. That OS is not officially supported by this Playwright release. Tests exercise hand-derived mathematical fixtures, API validation, durable recovery after a real process exit, retry/cost uncertainty, malicious ZIPs, quota concurrency and full browser journeys. Passing these checks does not establish live inference or public availability.

## Research and operations

- [Exact owner acceptance steps](docs/ACCEPTANCE.md)
- [Operator setup, backup, recovery and gated live smoke](docs/OPERATIONS.md)
- [Researcher guide and data schema](docs/RESEARCHER.md)
- [Architecture and security boundaries](docs/ARCHITECTURE.md)
- [Full release contract](specs/001-initial-feature/spec.md), [plan](specs/001-initial-feature/plan.md), [tasks](specs/001-initial-feature/tasks.md), [acceptance](specs/001-initial-feature/acceptance.md), [experiment protocol](specs/001-initial-feature/experiments.md), [traceability](specs/001-initial-feature/traceability.md)

## Nebius × NVIDIA

The server adapter targets the allowlisted Nebius Token Factory OpenAI-compatible API. A key alone does not enable spending. Live requests require an explicit approved ceiling, a reviewed capability/price file and the shared cumulative ledger. The operator authorized USD10 additional development/verification spending on 2026-10-28; the initialized grant cannot be raised/reset or automatically topped up. Account discovery does not prove inference access. Serving revision is recorded as unknown if absent. No provider/model fallback occurs. At handoff, 669 live attempts used 54,664 input and 5,307 completion tokens (64 reasoning tokens included), estimated at **USD0.00455352**, leaving **USD9.99544648**, with no uncertain/held cost. These are list-price estimates, not invoice reconciliation. See the [live integration procedure](docs/OPERATIONS.md).

To reopen the configured local owner workspace, explicitly load its private configuration:

```bash
.venv/bin/python -m masklab serve --env-file .env --port 8001
.venv/bin/python -m masklab budget --env-file .env
```

Do not source or print `.env`, delete the spend ledger, initialize a fresh allowance or increase the cap. See [acceptance testing](docs/ACCEPTANCE.md) for saved-evidence inspection without new spending and a small bounded live test.

MaskLab studies observable behavior. It exposes neither activations nor private chain-of-thought. Generated explanations are outputs, not causal evidence. Negative, invalid, refused and uncertain outcomes are preserved. Adoption of a false alternative alone is not proof of sycophancy.

## Release and source protection

MIT licensed. Model/provider/dataset terms remain separate. A deployment Dockerfile and CI checks are prepared; no image has been published and hosting has not been provisioned. Public demo mode is a separate restricted deployment, not an owner workspace exposed publicly. Publication, hosting spend, paid calls and submission require separately scoped authorization. Final product acceptance remains with the owner.

**Gitleaks must pass before every authorized commit and push.** Existing private hooks remain intact. No commit or push is included in this implementation task. Do not bypass hooks, suppress findings or add baselines to hide leaks. See [SECURITY.md](SECURITY.md).
