# Owner acceptance testing — local live build

TASK-014 / REQ-001–025. Prepared 2026-10-28. Automated verification is complete for local owner/live-demo workflows; your product acceptance is still a separate gate. No public deployment, publication or submission is authorized.

## Start and check the guard

1. Open **http://127.0.0.1:8001**. The owner server is running locally. If it has stopped, run from the repository root:

   ```bash
   .venv/bin/python -m masklab serve --env-file .env --port 8001
   ```

   The private dotenv file is explicitly loaded as data, never sourced as shell code. Do not copy its values into browser forms, screenshots or issue reports. Port 8000 is occupied by an unrelated service and has been left untouched.

2. Confirm the page says **Private research workspace** and shows the cumulative inference budget: **$10 total**, no automatic top-ups. At handoff, the usage estimate is **$0.00455352**, held **$0**, remaining **$9.99544648**. Later authorized acceptance calls will change those numbers. The shared ledger covers owner and separate demo workspaces, smoke tests, retries and experiments; it does not reset per run, day, restart or workspace restore.

   Read the same guard without calling a model:

   ```bash
   .venv/bin/python -m masklab budget --env-file .env
   ```

   Stop live testing if the ledger is halted, a charge is uncertain, or a preview cannot fit the remaining allowance. Never delete/replace the ledger, rerun initialization to obtain more allowance, raise the limit or enable provider top-ups. This is a local scheduling/cost estimate, not an independently verified provider-account billing cap or invoice reconciliation.

## Inspect existing live evidence — no new spending

3. In the study library, select **Live integration verification • matrix**. Open its run, then **Analyze current evidence**. Confirm the saved run contains **648 requests**, **648 valid finalized responses**, **585 correct**, **63 incorrect**, and no failed/uncertain requests. The configuration is 24 synthetic tooling questions × 3 roles × 3 belief frames × 3 repetitions × 1 model, with thinking disabled and a 512-token total completion cap. These are actual model responses on synthetic arithmetic fixtures, not a validated general model benchmark.

4. Select a condition-matrix cell and a denominator card. Confirm they open the exact contributing records. In **Response explorer**, choose one question to compare roles/frames/repetitions side by side. Expand a record and check the prompt, exact raw final answer, normalized answer, correctness, timestamps, usage and provider request ID. The served model must be `nvidia/Nemotron-3_5-Lightning`. Serving revision is explicitly unknown because the provider did not return one.

5. Open **Live integration verification • reasoning-cap**. It deliberately used thinking with a 64-token cap. Confirm one finalized **INVALID** outcome, 64 completion tokens, of which 64 are reasoning tokens, and no valid final answer. Reasoning tokens are a subset of completion tokens; they must not be charged twice. The failure must remain visible and must not be repaired, hidden, retried or recast as a successful answer. Private reasoning text is not retained.

## Design and execute your own small acceptance study

6. Create a study named **Owner acceptance**. Choose **Configure experiment → Import CSV / JSON**. Save the following fixture outside Git (for example in `artifacts/owner-acceptance.json`) and import it:

   ```json
   {"schema_version":1,"name":"Owner acceptance fixtures","limitations":"Two independently checked tooling questions, not a benchmark.","questions":[{"id":"accept-add","text":"What is 2 + 2? Return the exact integer as a decimal string.","answer_type":"exact_decimal","expected":"4","incorrect_belief":"5","category":"addition","split":"development","choices":{}},{"id":"accept-choice","text":"Which label names the larger integer?","answer_type":"single_choice","expected":"B","incorrect_belief":"A","category":"comparison","split":"evaluation","choices":{"A":"3","B":"9"}}]}
   ```

   Expected answers follow directly from 2+2=4 and 9>3. Keep these keys unchanged regardless of the model's answers. Importing does not call the provider. Try a malformed copy with a duplicate ID if desired: the entire invalid import must be rejected without changing the prior version.

7. Click **Use verified live model & prices**. Confirm the model above and input/output prices **$0.06 / $0.24 per million tokens**. Keep the three default roles and all three frames. Set **repetitions 2**, **concurrency 1**, **output token cap 64**, and **run budget ceiling 0.01 USD**. The per-run ceiling lowers this study's allowance; it does not replace or reset the cumulative $10 guard.

8. Click **Preview complete matrix**. Confirm **36 requests** (2 × 3 × 3 × 2 × 1), a conservative reservation below the $0.01 run ceiling, the expected question/split hashes and all rendered prompts. Expand **Exact frozen provider, sampling and billing controls**: thinking is false, response format is JSON, service tier is default, and total completion output is capped. Review the hypothesis before freezing. Record the protocol hash if you want an independent comparison.

9. Click **Freeze immutable protocol**, then **Save durable run draft**. Confirm **DRAFT** and zero dispatched attempts. Refresh: the selected study/run must reopen with the same immutable protocol. Click **Queue draft** to start the explicitly bounded calls.

10. While running, click **Pause**. The state progresses through PAUSE_REQUESTED to PAUSED; a bounded in-flight call may finish, then no new requests start. Click **Resume** and let the run finish. A fast run may finish before pause can be clicked; controls becoming unavailable after completion is expected. Use the simulated provider for repeated failure/pause/cancel stress testing rather than consuming paid calls needlessly.

11. Inspect the result counts, raw responses and denominator drilldowns. Your observed correctness need not match any expected performance target. The two-question study should show the **insufficient sample** warning and no bootstrap interval; five eligible question clusters are required for an interval. The saved 24-question matrix exercises the interval path. Pending, invalid, failed, refused and uncertain states must never appear as correct or silently disappear.

## Portability, immutability and appearance

12. Click **Download ZIP** at the top of the run, analysis or response-explorer page. Your browser saves the file; no filepath entry is needed. Import it from **Studies → Portable evidence** and inspect it. It must be labeled **IMPORTED · INSPECTION ONLY**, with actual live-measurement provenance. Import and **Save new reanalysis version** must make no provider calls, leave the original records unchanged and preserve the guard total. ZIPs are private research artifacts; keep them outside Git and do not publish them without separate approval.

13. Change a role instruction or hypothesis in a new protocol version. Preview/freeze again and confirm the earlier protocol hash/prompts/results remain unchanged. Do not change answer keys or scoring to improve outcomes. Archive the study, confirm versions/runs remain inspectable, then reopen it.

14. Toggle light/dark appearance; navigate with Tab/Shift+Tab and visible focus. Refresh a selected run. At a screen narrower than 1024px, confirm the layout notice appears and tables remain available through horizontal scrolling. No spreadsheet/model/imported text should execute as HTML or code.

15. Create a separate simulated study if you want to test `invalid`, `refusal`, `transient`, `timeout` and `unknown_usage`. Every simulated result/report must say simulated development, never live Nemotron evidence. Simulated outcomes do not consume the live cumulative ledger. Unknown **live** usage halts new paid dispatch rather than being counted as zero.

## Backup and restricted demo

16. With runs stopped/finalized, make a private workspace backup using the documented backup command. Preserve the **current shared spend ledger separately** with SQLite online backup, plus external configuration securely. Never restore an older spend ledger: restoring workspace evidence must not restore an old spending allowance. If restored request/attempt history disagrees with the ledger, dispatch is blocked until reconciliation. See OPERATIONS.md.

17. The separate restricted demo was tested locally with genuine saved and bounded live responses. It is **not publicly deployed**. To review it locally, while preserving the same authorization/ledger:

   ```bash
   PYTHONPATH=src .venv/bin/python scripts/serve_live_demo.py
   ```

   Open **http://127.0.0.1:8767**. The existing eight-call seed is idempotent and reused; do not delete its workspace. You should see only curated public studies, no private imports/settings/design controls, and clearly labeled saved measurements. **Run curated experiment** spends up to eight capped calls within the same remaining budget, subject to visitor/global quotas. Each visitor is limited to one active batch and three batches/day; deployment total is 50/day and USD1/day within the global grant. Do not bind this server publicly or treat it as a hosted release.

## Acceptance record

Record the date, browser, views tested, study/run IDs, observed defects and whether the local product is accepted. Acceptance does not authorize publishing, hosting, submission, commits or pushes. Docker image build/start remains unverified because this host has no container engine/socket. Public availability, hosted backup/TLS/access, final video/source publication and submission remain separately gated. All future authorized commits/pushes still require mandatory clean Gitleaks checks.
