# MaskLab

**A behavioral research workbench for studying how AI answers change under persona and user framing.**

MaskLab's first release will let researchers design paired experiments, run NVIDIA Nemotron through Nebius Token Factory, inspect individual responses, compare measured outcomes, and export reproducible research records.

**Current status:** repository foundation and complete first-release specification. The application, live inference, interface and deployment are not implemented yet. No experiment outcomes are claimed.

## Research questions

- Does assigning an expert or skeptical role improve objective correctness?
- Does stating a false belief move answers toward that belief?
- Which questions are sensitive to framing, and are observed differences stable across repeated trials?

MaskLab studies observable behavior. It does not expose neurons, activations or circuits. Generated explanations are outputs to inspect, not evidence of a model's internal reasoning.

## Planned research workflow

Create a study → import/version questions → define role × belief conditions → preview cost and freeze the protocol → run within approved limits → inspect paired responses and uncertainty → export evidence.

The owner research workspace supports configurable studies. A restricted public demonstration will use curated questions, capped live requests and clearly labeled saved results. It is not a public arbitrary-code execution service.

## Foundation checks — available now

Python 3.11+ is required. From the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q src
```

These verify bundled research fixtures only; they do not verify an application or provider integration. No dependency installation or API key is needed for these checks.

## Application setup — planned

The specified architecture uses a Python/FastAPI backend, SQLite research store and worker, and a React/TypeScript browser workspace. Implementation will add lockfiles, installation/run instructions and a deployment image. No application launch command exists yet.

Copying `.env.example` is optional preparation only; never commit credentials. Configure Token Factory credentials server-side during the separately authorized integration phase. No credentials are needed today.

## Specifications

The sole release authority is [specs/001-initial-feature](specs/001-initial-feature/spec.md): [plan](specs/001-initial-feature/plan.md), [tasks](specs/001-initial-feature/tasks.md), [acceptance](specs/001-initial-feature/acceptance.md), [experiment protocol](specs/001-initial-feature/experiments.md), and [traceability](specs/001-initial-feature/traceability.md).

See [research methodology](research/methodology.md), [dataset provenance](docs/dataset-provenance.md), [security](SECURITY.md), [contributing](CONTRIBUTING.md), [submission checklist](docs/SUBMISSION.md), and [current handoff](docs/HANDOFF.md).

## Nebius × NVIDIA integration

Planned runtime inference uses NVIDIA Nemotron on Nebius Token Factory. A real provider smoke test, available model IDs, endpoint behavior and costs must be recorded before claiming integration. No model weights, API calls or cloud resources are bundled or started by this repository.

This project targets the Best Apps and Agents track. Reused infrastructure: ACP's native ML research scaffold, registration and Gitleaks guards. MaskLab's research engine, scientific evaluation and interface remain new project work.

## Commit and push protection

ACP has installed Gitleaks hooks in private Git metadata on this machine. Every authorized commit requires a clean scan of staged content; every authorized push requires a clean outgoing-history scan. Missing/error/findings block the action. Fresh clones must install the guard through ACP. See SECURITY.md. No commit or publication is included in today's setup.

## License

[MIT](LICENSE). Model, provider and third-party dataset terms remain separate.
