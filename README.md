# Jev Frontier 100

**Jev scores 77.0%; Qwen3.5 2B with a 2,048-token thinking budget scores 82.0%;
Qwen3.5 4B with the same budget scores 96.7%.** This small benchmark makes Jev's
observed reasoning limits tangible through nine local-model settings.

[中文](README.zh-CN.md) · [All 100 questions](docs/QUESTIONS.md) · [Answers](docs/ANSWERS.md) · [Protocol](docs/PROTOCOL.md)

![Jev versus nine Qwen settings](results/v0.2-budget/comparison.png)

## What the results say

| Thinking budget | Qwen3.5 0.8B | Qwen3.5 2B | Qwen3.5 4B |
|---|---:|---:|---:|
| Off | 38.0% | 48.0% | 56.0% |
| 512 tokens | 39.0% | 59.7% | 78.3% |
| 2,048 tokens | 54.0% | 82.0% | **96.7%** |

**Jev 1.13.0: 77.0%.** Each condition contains 100 questions × 3 trials. All
3,000 retained responses produced valid final answers. No majority vote or
best-of selection is used.

- **Below 4B with sufficient thinking:** 4B/2,048 exceeds Jev by 19.7 percentage
  points; the 95% paired-template bootstrap interval is **+12.7 to +26.7**.
- **Near 2B with sufficient thinking in aggregate:** 2B/2,048 exceeds Jev by
  5.0 points, with an interval of **−2.3 to +12.3**. This supports a descriptive
  comparison, not a statistical proof of equivalence.
- **Budget matters:** 4B with thinking disabled scores 56.0%; at 512 it scores
  78.3%. “Jev is weaker than a 4B model” needs the thinking condition attached.
- **Similar totals do not imply similar skills:** Jev scores well on short code
  semantics and formal logic, while 2B/2,048 is stronger on these relationship
  tracking and algorithm tasks. See [domain results](results/v0.2-budget/RESULTS.md).

This measures performance on a synthetic, English, four-choice task set under
specified interfaces and compute budgets. It does **not** establish a universal
intelligence ceiling, model parameter equivalence, or general coding ability.
The near-ceiling 4B result also exposes the limits of this small dataset.

## The benchmark

100 original AI-assisted questions: ten each in customer service, policy rules,
discourse, formal logic, relations, mathematics, temporal reasoning, code
semantics, algorithms and evidence integration. There are 50 counterfactual
pairs, 60 executable-oracle answers, and 30/40/30 designed easy/medium/hard items.
Difficulty labels have not been independently calibrated. The dataset has not
received independent human expert review.

Qwen uses Q8_0 weights, temperature 1, seeds 101/202/303, and native llama-server
reasoning budgets. Each trial rotates option positions; seeds and positions
therefore vary together. A thinking cap is followed by final-answer generation,
with total generation limited to budget + 128. Jev uses its native Choice API.
All questions, gold answers and completed trial results are unchanged.

The published conditions were selected after observing experimental results.
This is an exploratory release, not a blind preregistration. The release
protocol restates the retained setup; original protocol/config hashes are in
[data/release_provenance.json](data/release_provenance.json). Jev's completed
reference was reused and its reconstructed inputs checked against request hashes.

## Inspect and reproduce

Python 3.10+; grading has no third-party dependencies.

```sh
python -m pip install -e '.[plots]'
python -m unittest discover -s tests -v
# Recompute all published scores, paired intervals and confidence diagnostics offline:
python -m jf100.budget_report v0.2-budget --from-public
python scripts/plot_budget_results.py v0.2-budget
```

To run a fresh experiment, install the Q8_0 Ollama tags used here and a
llama-server build supporting `reasoning_budget_tokens` and token logprobs:

```sh
ollama pull qwen3.5:0.8b
ollama pull qwen3.5:2b-q8_0
ollama pull qwen3.5:4b-q8_0
export JF100_LLAMA_SERVER=/absolute/path/to/llama-server
# Set JEV_KEY in your environment. Never commit it.
python -m jf100 --run-id replication
```

Ollama supplies local model metadata on port 11434; a separate native
llama-server runs on loopback port 11438 with 16 slots and 32K context per slot.
Override `JF100_OLLAMA_URL` or `JF100_LLAMA_PORT` if needed. Only one model size
loads at a time. Repeating the command resumes completed checkpoints. Do not
start two evaluators against the same run directory.

Measured hardware: Apple M5 Max, 128 GiB unified memory. Backend/model hashes and
configuration are in [run_config.json](results/v0.2-budget/run_config.json) and
[model_metadata.json](results/v0.2-budget/model_metadata.json). GPU scheduling,
quantization and backend versions can affect reproducibility. Recorded latency
is descriptive under shared batching, not a controlled speed comparison.

## Inputs, outputs and confidence

[Compact per-request outcomes](results/v0.2-budget/outcomes.jsonl) include grades,
request hashes, token counts, answer-token logprobs/probabilities and Jev
confidence. Every input can be reconstructed from the frozen questions and
trial index. This is sufficient to recompute published accuracy and intervals.

Full request bodies and all response attempts, including thinking, final text,
token IDs, bytes, logprobs and top-5 alternatives, are retained locally in
`runs/`. They are excluded from Git because of size. `scripts/export_raw.py`
creates a compressed, hash-checked release asset without modifying the originals.
See [the data layout](docs/DATA_LAYOUT.md).

The Qwen score is the raw probability of the emitted answer-letter token where
exact alignment is possible. It is **not** normalized over four answer choices
and is not automatically a probability of correctness. Jev's returned confidence
has a different definition. [Reliability plots](results/v0.2-budget/confidence.png)
and Brier scores are exploratory proxy diagnostics; missing alignments and
sample coverage are reported explicitly.

## License and contributions

MIT for original code and questions. Model weights are not distributed.
[Dataset card](docs/DATA_CARD.md) · [Contributing](CONTRIBUTING.md) · [Citation](CITATION.cff).
Report ambiguous questions by item ID; scored question revisions require a new
dataset version. Suggestions for harder, independently reviewed items are welcome.
