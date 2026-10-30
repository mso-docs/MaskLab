# Static guide and judge test build

TASK-014 → REQ-017–020/023–025. Local release candidate prepared at the operator's request. External publication and owner acceptance remain separate gates. This test-build delivery path does not mark the full hosted-demo contract complete or imply an approved scope reduction.

The static page provides nine real condition summaries, exact denominators, question/outcome filters, pagination and raw prompts/responses from the approved completed replication. It makes no inference calls. The downloadable ZIP contains the compiled app wheel, hash-locked dependencies, key-free launcher, import-compatible saved evidence, provenance and separate software/dataset notices.

Python 3.14 and internet for first dependency installation are required. Linux x86-64 is verified; supplied Windows/macOS instructions are unverified. This is not a standalone native executable. The launcher clears inherited provider/budget settings, never loads dotenv, binds loopback and seeds only an inspection import. New judge runs use simulation. Live owner setup requires separate credentials, capabilities and explicit spending configuration.

The saved archive is repackaged from the approved public replication derivative only after checking zero timestamp substitutions and all payload hashes. The standard wrapper explicitly records derivative provenance. Protocol, records, outcomes and analysis are unchanged. Independent evaluation and standard importer validation pass. The original public derivative remains available separately; private databases, originals and spending ledger are excluded. Immutable dataset notes retain their historical DRAFT wording; recorded approval preceded the original live execution.

## Rebuild

```bash
npm run build --prefix frontend
.venv/bin/python -m build --wheel --no-isolation
PYTHONPATH=src .venv/bin/python scripts/build_test_release.py
```

Outputs: `artifacts/release/masklab-test-build.zip`, `SHA256SUMS`, and `pages/`. Only explicitly allowlisted files enter the bundle. Do not rebuild/delete the candidate directory while its isolated server is running.

Browser QA: `node scripts/release/verify_browser.cjs` expects the static preview on 8770 and extracted app on 8771. `node scripts/release/record_walkthrough.cjs --rehearsal` checks the complete eight-scene navigation; omit the flag for the actual timed recording. The recording captures browser content with burned-in English captions and no audio. `scripts/release/finish_video.py` takes a local FFmpeg path, encodes MP4, measures duration and emits review frames, subtitles and narration text. See the handoff and local artifacts for actual evidence and retained failures.

## Publication

The prepared Pages workflow is manual-only. After a separately authorized, clean-scanned commit/push, enable GitHub Actions as the repository's Pages source and run **Publish static judge guide**. It uploads only the generated static directory, including its direct test-build download. No provider calls or automatic GitHub Release creation occur. A compatible GitHub plan/public repository is required; visibility must not change implicitly.

Suggested release tag: `v0.1.0-rc1`; the included wheel package version is explicitly `0.1.0.dev0`. Attach the reviewed ZIP, SHA256SUMS, MP4, SRT, optional narration script and notes from `release/RELEASE_NOTES.md`. The guide links to the release list for video assets. The guide/build are not publicly available until publication actually succeeds. The required public YouTube upload is an additional release step.

Review Git identity/history and tracked host paths before public source release. Verify final public downloads and setup independently. Keep judge access available through December 23 under the currently checked rules. Automated checks do not constitute owner acceptance or hackathon submission.
