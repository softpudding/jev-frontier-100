# JF100 v0.2: model size × reasoning budget

## Release scope and provenance

This release presents a subset of complete conditions selected after scores
were observed. Every item and all three trials of each retained condition are
included. The published protocol restates the executed setup and selected scope;
it is not the original pre-run document. The original recorded protocol hash
is preserved in data/release_provenance.json. No question, answer or model
response has been edited to improve a result.

## Experiment provenance

This protocol replaces the cancelled v0.1 local-model experiment at the owner's
request. The original 100-item dataset and its SHA-256 remain unchanged.
Conditions were selected after observing v0.1 and an 18-request mechanism probe;
this is an exploratory follow-up, not a blinded preregistration. v0.1 local
results and probe results are excluded from v0.2 scoring.

## Design

Three Qwen3.5 Q8_0 models: 0.8B, 2B, 4B. Each has three conditions:
thinking disabled, thinking budget 512, thinking budget 2048. Each condition
uses 100 items × 3 trials (seeds 101, 202, 303) = 300 requests; total 2,700 local
requests. The existing 300 Jev 1.13.0 requests are reused as a dated reference,
not falsely represented as new API calls. Their request hashes and grades are
verified against the same questions and option rotations.

Within each trial, every local size/budget receives identical question content
and option positions. Trial 2 and 3 rotate positions by one and two respectively.
Seeds and positions vary together across trials; their individual effects cannot
be disentangled. Budget comparisons within a trial hold both fixed.

Only one local model size is loaded at a time. Within each model, all item ×
trial × budget tasks are deterministically shuffled (seed 92026) and dispatched
to 16 continuous-batching slots. Generation is stateless per request; no earlier
answer or grading feedback is supplied. Prefix caching may affect latency.

## Runtime and inputs

Use the installed llama-server binary directly, with the embedded GGUF Jinja
chat template and native reasoning parser. Record binary SHA-256, model blob
SHA-256, model metadata, launch arguments and server properties. This avoids
mixing the old Ollama Go-template path with the new native budget mechanism.
The input messages and final-answer JSON schema are the same as the mechanism
probe and v0.1. Gold labels, rationales and difficulty labels are never sent.

All local conditions explicitly set temperature=1, top_k=20, top_p=0.95,
min_p=0, presence_penalty=1.5, frequency_penalty=0, repeat_penalty=1,
repeat_last_n=64, typical_p=1 and the trial seed. Each slot has a 32,768-token
context. Parameters are identical across sizes and budget conditions except
thinking enablement and generation limits.

Off: enable_thinking=false, reasoning_budget_tokens=0, max_tokens=128.
512/2048: enable_thinking=true, reasoning_budget_tokens=B, max_tokens=B+128.
The backend ends reasoning at the cap and can continue into the final answer.
The 128 is total-generation headroom beyond the reasoning cap, not a separate
answer-only hard cap; early reasoning completion can leave more headroom.

Retokenize returned reasoning for an approximate observed length. Delimiters
and token-boundary normalization can create small differences from internal
budget accounting. Record total generated tokens and actual final answer too.
Reaching the reasoning cap is not an error if a valid answer follows.

## Scoring and inference

Strict JSON answer A–D, exact-match gold. A valid final answer ending normally
is scored even when reasoning hit its cap. Total-generation truncation,
invalid output and infrastructure errors are separately recorded and score
zero in system accuracy; completion rate and valid-answer accuracy accompany
it. Retry one infrastructure failure (network, 429, selected 5xx); never retry
wrong answers, truncation or formatting failures. Local request timeout 600s.
Checkpoint each completed request; resumption never selects among answers.

Use the v0.1 statistical method: 5,000 stratified paired-template bootstrap draws,
seed 92026, 50 pairs stratified across 10 domains. Report paired differences
versus Jev and within-size budget comparisons, without general-IQ or implied
Jev-parameter-size claims. Intervals describe this synthetic template collection.
No multiplicity-adjusted confirmatory claims; comparisons are exploratory.

Report every size/budget condition, domain, difficulty, completion rate, error
category and token usage. Latency is descriptive: shared GPU, interleaved budgets,
caching and variable completion order prevent a controlled speed ranking.
The dataset remains AI-assisted and lacks independent human expert review.

## Full-record retention and confidence analysis

At the owner's request, every new local request retains its exact request body,
all response bodies (including thinking and final content), and returned token
log probabilities with top-5 alternatives. Requests set logprobs=true and
top_logprobs=5. Verify actual token coverage in a preflight rather than assuming
that logprobs only or fully cover the final answer. Raw records remain local
under runs/ and are not silently discarded by compact public export.

Jev's original responses retain its returned confidence. Reused Jev inputs are
reconstructed from the frozen dataset and checked against original request
hashes; they are explicitly marked reconstructed, not captured original bytes.

Token log probability is not automatically a calibrated probability of answer
correctness or directly equivalent to Jev confidence. Keep token boundaries,
raw logprob scale and grammar constraints visible. Any derived answer score
must document token selection/normalization and missing alternatives. Confidence
comparisons should report calibration against correctness (e.g. reliability,
Brier score where a valid probability is defined), with paired-item dependence
and the small exploratory dataset acknowledged.
