# Resource budgets and authorization

Today: no installs, paid calls, cloud provisioning, model downloads, application implementation, commits, pushes or submission. ACP execution allowlists remain empty. Future global inference ceiling proposed at USD10 is not approved expenditure yet.

Specified release limits: 500 questions, 8 roles, 3 belief frames, 3 models, 20 repetitions and 5,000 requests/run; reject combinations exceeding the request ceiling. Maximum 4 concurrent calls and 2 attempts/request. Default output cap 512 billed tokens only after verifying provider semantics; ambiguous calls/unknown usage require reconciliation. Proposed request timeout 60 seconds, run scheduling deadline 30 minutes; timeout means partial results, never silently successful completion.

Public demo default: eight calls/batch, one concurrent batch/visitor, 50 batches/deployment/day and USD1/day inside the separately approved global ceiling. Server-side enforcement and abuse resistance are required; these limits do not grant spending authority.

No dedicated GPU is needed for the behavioral API release. Initial CPU deployment target is 2 cores/2 GiB RAM with one SQLite writer and persistent storage; measure actual resource use before choosing a paid hosting tier. Budget caps are conservative application scheduling controls, not guaranteed provider-account billing caps. Track hosting and demo availability through December judging separately.
