# Contributing

Read AGENTS.md and the canonical release specification before changes. Link changes to REQ/TASK/TEST identifiers. Preserve immutable protocols, original response evidence and negative findings. Scientific metric changes require a new version and comparison with the previous scoring definition.

Use small independently verifiable changes. Current checks: `python3 -m unittest discover -s tests -v` and `python3 -m compileall -q src`. Implementation must add actual API/UI/worker tests and reproducible dependency locks before release; fixture checks alone are insufficient.

Do not use production secrets or private participant data in examples. Construct synthetic credential-shaped canaries only in disposable scanner tests. Do not silently disable failing tests, change answer keys to match outputs, or alter a frozen protocol.

Gitleaks must pass before every authorized commit/push. Publishing, spending, permission expansion and external submission need their own authorization. Report security problems privately to the repository owner; do not include secret values in an issue.
