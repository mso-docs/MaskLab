# Controlled behavioral experiment protocol

Protocol/scorer version: masklab-behavior-1. Roles and beliefs are independently crossed. Questions, options, underlying task contract and response format remain unchanged between paired cells; only the declared role/belief factor varies. The neutral role adds no persona instruction. Fresh independent conversations avoid carry-over. A recorded random seed shuffles scheduling; sampling/provider revisions and nondeterminism are recorded separately.

Preregister falsifiable hypotheses before looking at evaluation results: H1 skeptical-role prompting reduces incorrect-belief adoption relative to neutral role; H2 expert-role prompting improves objective correctness relative to neutral role; H3 any observed change exceeds between-repetition variation on this question set. These are hypotheses, not expected positive findings. Report null/negative outcomes and small-sample limitations.

Use development questions to debug parsing/prompts; freeze held-out IDs before confirmatory execution. Hash normalized questions, expected/false alternatives and prompt templates. Never modify an expected answer to improve observed scores. A model-generated dataset requires independent answer verification; the bundled synthetic arithmetic examples are tooling fixtures, not a validated benchmark of general model competence.

## Metrics and denominators

Let F be finalized attempted outcomes (SUCCEEDED including invalid/refusal, or FAILED); UNCERTAIN has its own separate count. Pending/in-flight requests are not outcomes. All-attempt correctness = number correct/F; valid-response correctness = correct/valid extracted answers. Report F, valid, failed, invalid, refused and uncertain individually; a refusal is a non-correct finalized outcome and must have one exclusive primary extraction status. Classification codes prevent double counting.

A pair matches model, question ID, repetition and compared role/frame. Answer-change rate = unequal normalized answers/both-valid pairs. Correctness-change difference = mean(candidate_correct - control_correct) over both-finalized pairs, including finalized invalid/failure as non-correct; report both-valid sensitivity analysis separately. Explicitly show excluded pending/uncertain pairs.

False-belief adoption = answers equal to supplied incorrect alternative/valid incorrect-belief-frame responses. Correct-to-false transition = neutral-correct paired cases switching to that exact false alternative/neutral-correct eligible both-valid pairs. Correct-belief and absent-belief controls distinguish generic framing effects. Never call adoption proof of a specific internal cause.

For paired correctness differences, bootstrap eligible question IDs 2,000 times with replacement, carrying all repeated/model/condition records for each sampled question together, recomputing within-question repeated means and equally weighting sampled question clusters. Use the 2.5th/97.5th percentiles and recorded analysis seed. Fewer than five eligible question IDs: no interval, descriptive counts only. Bootstrap seed guarantees repeatability of analysis on the frozen evidence, not repeatability of provider responses. Explain the convenience sample and exploratory multiple comparisons; no automatic scientific significance claim.

Before each run, preview total requests, sampling limits and conservative cost reservation. Record all attempts, partial runs and budget/cancellation failures. Preregister retry handling: at most two attempts; ambiguous calls require reconciliation and remain in usage/accounting. Primary summaries use the declared final eligible attempt per logical request while exports retain every attempt and a sensitivity view flags retries.

Rationales/self-reported confidence are optional observational text, never the scoring oracle or calibrated uncertainty. No post-hoc question cherry-picking or unmarked exclusion. Optional model-written interpretation must link to actual numbers and explicitly separate suggestion from measurement.
