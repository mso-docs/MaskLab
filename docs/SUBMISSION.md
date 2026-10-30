# Submission readiness

Operator authorized source commit/push and the Pages deployment on 2026-10-29, keeping the repository private. GitHub rejected Pages activation with HTTP422 because the current plan does not support Pages for this private repository. No deployment or visibility change occurred. The checked static bundle and private draft release remain available; choose an eligible account plan or separately authorize a public static-only repository to obtain the judge-facing URL.

## Reviewed local assets and private draft — 2026-10-29

TASK-014 / REQ-025: actual captioned app walkthrough recorded and measured at **161.44 seconds (2:41.44)**, MP4/H.264, no spoken audio. Static Pages guide with real saved evidence, direct runnable-test-build download and setup instructions prepared; installed key-free build and browser drilldowns verified. Private unpublished draft release has six uploaded assets: https://github.com/mso-docs/MaskLab/releases/tag/untagged-c11c09cfa8211aed8d17 . See TEST_BUILD_RELEASE.md and current HANDOFF for commands, hashes, failures and limits. Pages is not deployed, source changes are not committed/pushed, release is not published and YouTube is not uploaded. Final release source target must be updated after reviewed commit/push. No repository visibility change or submission performed. Video/test-build uses the earlier COMPLETED replication; later repeat stopped on uncertain provider usage and is excluded.

## Readiness audit — 2026-10-29

TASK-012/013/014 → REQ-020/023–025. Current local source has two commits and real completed Nemotron studies; historical unchecked items below do not mean live inference is still pending. Public hosting, final owner acceptance, public source/video and submission remain unverified release gates.

Official rules rechecked: https://nebiusglobalaihackathon.devpost.com/rules . Deadline remains October 30 at 13:00 Eastern. **Current judging is December 9–23, 2026; plan availability through December 23, superseding the earlier December 1–15 assumption below.** Rules require a working demo/hosted application/test-build URL, public open-source repository, public YouTube demonstration under three minutes, track selection and provider/model feedback. Nebius hosting of the whole app is not required when it calls Token Factory.

Security audit: current nonignored source (136 files) and both commits pass redacted Gitleaks. Exact configured-key scan passes 325 local files plus archive members; independent history check passes 176 blob versions across two commits. `.env` is ignored/untracked and absent from historical tracked paths. This is evidence of no detected credential leak, not a guarantee of no sensitive data. Tracked documentation/configuration contains the local username and absolute host paths; Git author/committer email metadata also needs intentional public identity review. Review/sanitize the public source and history before changing repository visibility; do not rewrite history or ACP policy as part of this audit. Approved public ZIPs contain research questions/responses with separate source-license obligations; timestamp redaction is not general anonymization.

Recording plan: capture only the application window with microphone narration, notifications off and no IDE/terminal/dotenv in frame. Target 2:40: 0:00–0:20 audience/problem; 0:20–0:50 protocol and role×belief matrix; 0:50–1:40 saved real results and denominator drilldown; 1:40–2:15 exact paired responses and export; 2:15–2:40 Nemotron/Token Factory provenance, invalid outcomes/limitations, verified final links. Saved evidence must be labeled as saved; a fresh large run is unnecessary. Local rehearsal can precede hosting. Review the final recording for incidental personal information and measure duration before public upload. No recording or upload was performed by this audit.

Target: Thursday October29, 2026 night, America/New_York. Official cutoff: Friday October30 10:00 Pacific / 13:00 Eastern. Track: Best Apps and Agents. Preserve the submitted version after cutoff per organizer guidance. Plan demo availability through December1–15 judging; no hosting expenditure authorized today.

- [ ] Complete integrated product and owner acceptance tests.
- [ ] Verified real NVIDIA Nemotron inference on Nebius Token Factory.
- [ ] Working judge-accessible hosted demo with bounded live use and explorable saved evidence.
- [ ] Public source, visible MIT license, actual setup/execution instructions and dependency locks.
- [ ] Public YouTube demonstration strictly under three minutes, uploaded with time to spare.
- [ ] Specific model/provider feedback, including observed latency, tool/schema behavior, errors and constraints.
- [ ] Explain ACP scaffold reuse and the new MaskLab work performed during the submission period.
- [ ] Team information/invitations complete if applicable.
- [ ] Gitleaks clean; no private research records, local paths, keys or sensitive feedback published.
- [ ] Freeze release commit, data/protocol/result hashes and submitted assets.
- [ ] Explicit authorization for publication, deployment/hosting spend and submission.

Video draft: 0:00–0:20 research question/audience; 0:20–0:50 define paired roles/beliefs and preview budget; 0:50–1:25 run a bounded real Nemotron experiment and show provider provenance; 1:25–2:15 inspect a real response reversal and denominators/uncertainty; 2:15–2:40 export evidence and explain limitations; 2:40–2:55 sponsor use and conclusion. Replace timing/examples with actual working behavior; never fabricate an outcome to fit the story.
