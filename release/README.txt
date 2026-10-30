MASKLAB — JUDGE TEST BUILD • release candidate 0.1.0-rc1
TASK-014 / REQ-018/020/023/025

A local browser application, not a standalone native executable.
Requires Python 3.14, pip, and internet for first dependency installation.
Linux x86-64 is the verified platform. Windows/macOS commands are supplied but unverified.
No Node, GPU, API key, Docker or paid inference is needed for this test build.

1. Extract the entire ZIP into a writable folder.
2. Open a terminal in that folder.

Linux/macOS:
  python3.14 -m venv .venv
  .venv/bin/python -m pip install --require-hashes -r requirements.lock
  .venv/bin/python -m pip install --no-deps masklab-0.1.0.dev0-py3-none-any.whl
  .venv/bin/python run.py

Windows PowerShell (Python 3.14 must be installed):
  py -3.14 -m venv .venv
  .\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements.lock
  .\.venv\Scripts\python.exe -m pip install --no-deps masklab-0.1.0.dev0-py3-none-any.whl
  .\.venv\Scripts\python.exe run.py

Open http://127.0.0.1:8000. If busy, use run.py --port 8080.
Stop with Ctrl+C. Re-run the last command to reopen your workspace.

SAVED REAL RESULTS (no inference):
Studies → Portable evidence → saved-public-replication.
Inspect 150 questions × 3 roles × 3 belief frames × 3 repetitions = 4,050 responses.
This saved live run has 2,427 correct, 1,473 incorrect and 150 invalid results.
Correctness is 59.93% (2,427/4,050); valid-only accuracy 62.23% (2,427/3,900).
Click a chart to inspect its contributors; select a question to compare responses.
The import-compatible saved-evidence.zip is repackaged from an approved public derivative
with ZERO timestamp substitutions; protocol/records/scores are unchanged. BUILD.json records
provenance and SHA256. This is saved evidence, not a fresh model run.

TRY THE FULL WORKFLOW (SIMULATED ONLY):
Create a study → Configure experiment → Use synthetic tooling fixtures → set repetitions 1
→ Preview complete matrix → Freeze immutable protocol → Start simulated run.
Then inspect charts/response records, Download ZIP and import the resulting archive.
Simulation tests the app; it is not Nemotron research evidence.
The launcher clears inherited provider/budget variables and never loads .env.
Running live experiments requires the separately documented owner setup, your own credentials
and explicit spending configuration. Never share API keys or copy private databases.

LIMITATIONS AND LICENSES:
Convenience-sample behavioral measurements, not a validated or representative benchmark.
Invalids are retained as non-correct. Shared templates and some source articles recur.
Observed answer changes do not reveal internal reasoning or establish a causal mechanism.
Software is MIT. GSM8K material retains OpenAI MIT notice; adapted CMU S10 material is
CC BY-SA 3.0 and is not relicensed MIT. See DATA-NOTICES.txt and the evidence dataset.
No paid service or ongoing host is needed to inspect this build.
