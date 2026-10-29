# Release preparation — local drafts only

TASK-014 / REQ-025. These assets are prepared for review; none is published or submitted. Full release still requires real evidence, owner acceptance and separately authorized publication. Do not describe simulated measurements as Nemotron results.

## Video storyboard — target 2 minutes 35 seconds

| Time | Picture | Narration / evidence guard |
|---|---|---|
| 0:00–0:15 | MaskLab library and study objective | “MaskLab helps researchers test how an AI's answers change with persona and stated user beliefs. It studies observable behavior, not hidden reasoning.” |
| 0:15–0:40 | Dataset import, development/held-out split, neutral/skeptic/expert roles and belief frames | “Questions and independently checked answers are versioned. Roles and user beliefs vary independently; each trial starts fresh.” |
| 0:40–1:00 | Full matrix preview, exact prompt, model settings, cost ceiling, freeze | “The protocol freezes hashes, prompts, ordering, parameters and budgets before execution. Seeds organize trials; they do not guarantee deterministic responses.” |
| 1:00–1:25 | Durable run monitor and genuine live evidence ledger after authorization | “Requests and attempts are durable. Unknown outcomes remain uncertain, and failures stay visible.” Show a genuine verified live run only after funded integration. If recording before then, prominently say and show SIMULATED DEVELOPMENT throughout. |
| 1:25–1:55 | Condition matrix, paired difference/interval, denominator drilldown | “Every aggregate links to exact records. Correctness includes finalized failures; valid accuracy has a different denominator. Question-cluster intervals keep repetitions together. False-belief adoption alone proves no internal mechanism.” State actual observed values only from the selected export. |
| 1:55–2:20 | Side-by-side responses, raw final text/usage, ZIP export and import | “The evidence bundle carries protocol hashes, attempts, raw final responses, scored records and methods. It can be reopened for inspection without running a model.” |
| 2:20–2:35 | Actual public demo/source links after release authorization | “Built for NVIDIA Nemotron on Nebius Token Factory, with a restricted judge demo and a private owner workspace.” Include only working verified URLs; otherwise label this as an unpublished local prototype recording. |

Recording gate: remove all real secrets, private data/host paths and session tokens. Review every number against the frozen export. Measure duration strictly under 180 seconds. A local rehearsal is not the required public YouTube release. Final recording/upload is pending real evidence and publication authorization.

## Nebius / NVIDIA feedback draft

Observed during local integration: the OpenAI-compatible chat contract fits a narrow HTTPX adapter; model discovery and inference access must be tracked separately. The implementation needs explicit per-model supported sampling parameters, output-cap naming, reasoning/output billing semantics, current prices, request IDs and serving revision metadata to make safe reproducibility/cost claims. Missing revision/usage metadata is represented as unknown.

Documentation reviewed: [API schema](https://api.tokenfactory.nebius.com/docs), [official cookbook](https://dev.nebius.com/cookbook/beam-reflection-token-factory). No account model discovery or real inference has run yet. Do not report latency, reliability, answer quality or actual provider billing from simulation. After funded smoke, append exact model/endpoint, timestamps, serving revision (or unknown), output/usage behavior, request IDs, cost assumptions and preserved failures. Distinguish documented expectations from observed behavior.

## Submission material checklist

| Material | Current state |
|---|---|
| MIT source, setup, methods, architecture, recovery help | Prepared locally; source publication not authorized |
| Automated evidence and simulated workflow | Recorded locally; not research/model evidence |
| Live NVIDIA/Nebius smoke and research export | Pending key, model/semantics review and explicit paid-call authorization |
| Owner acceptance and fixes | Pending operator review |
| Durable judge-accessible demo through December judging | Pending hosting choice/access/spend/publication authorization and verification |
| Public repository/release commit | Pending scoped commit/publication authorization and mandatory clean Gitleaks scan |
| Public YouTube video under three minutes | Storyboard prepared; genuine evidence, recording review and upload pending |
| Specific provider/model feedback | Honest local-integration draft above; measured live feedback pending |
| Export hashes, exact model/config, release commit and final URLs | Fill from actual verified artifacts after gates; never invent |
| External submission | Not authorized; do not submit |

The canonical contract records the owner target Thursday night October 29 Eastern and official cutoff Friday October 30 13:00 Eastern. This document does not independently reverify organizer timing/rules. Verify current official instructions before submission; freeze submitted materials after cutoff as required. No scope reduction is approved by this checklist.


## Observed Nebius / NVIDIA feedback — 2026-10-28 update

The earlier unmeasured draft is historical. Real local integration now validates `nvidia/Nemotron-3_5-Lightning` through the exact configured endpoint. The model was listed among 30 account-visible IDs and the one-request smoke returned the exact selected identity. JSON output with thinking disabled produced complete finite decimal answers; a 648-request synthetic arithmetic matrix completed with 585 correct and 63 incorrect valid responses. These convenience tooling fixtures do not establish general competence, model-family findings or a causal explanation. No answer keys/protocol/scorer were altered to improve results.

The isolated 64-token thinking probe consumed 64 reasoning/completion tokens and returned no valid final answer with a length finish reason; this is retained as INVALID. This demonstrates why total-generation caps and explicit thinking controls matter for short structured-output studies. Reasoning tokens must not be charged twice. The provider returned request IDs and usage, but no serving revision; response service-tier metadata was absent/null and is recorded as unknown. Prices were reviewed at USD0.06 input/USD0.24 output per million tokens. All 669 paid verification attempts cost an estimated USD0.00455352 from returned token usage and list prices; invoices were not independently reconciled. No uncertain charges/retries occurred.

A useful provider improvement would be an authenticated per-model capability/price/revision response: the account model-list record exposed only identity/ownership/time/object fields, requiring separate documentation review and actual bounded inference validation. The local owner and separate eight-call curated demo both passed real browser checks. No public URL/source/video was published, and no hosted availability claim is made.
