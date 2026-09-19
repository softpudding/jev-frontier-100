# Data and reproducibility

- `data/items.jsonl`: 100 unchanged questions, answer keys and rationales.
- `data/manifest.json`: dataset fingerprint and design counts.
- `data/release_provenance.json`: original experimental fingerprints and release-scope disclosure.
- `results/v0.2-budget/run_config.json`: the published ten-condition projection of the run configuration.
- `results/v0.2-budget/model_metadata.json`: retained model and backend fingerprints.
- `results/v0.2-budget/outcomes.jsonl`: 3,000 compact scored records, sufficient to recompute accuracy and bootstrap intervals offline.
- `results/v0.2-budget/summary.json`: complete condition, domain, difficulty, difference and confidence-proxy diagnostics.
- `runs/v0.2-budget/*.jsonl`: local full records; never modified when exporting compact data.

## Full records

`request` contains the exact JSON body for Qwen, including input messages, schema,
sampling and budget. `attempts` stores each HTTP result with response body and
latency. `attempts[-1].body.choices[0].message` contains thinking and final output.
`choices[0].logprobs.content` contains emitted token IDs, bytes, logprobs and top-5
alternatives, including thinking tokens. Forced delimiters are backend behavior;
returned probabilities are not proof that the model chose to stop reasoning.

`answer_token_index` points into the last attempt's logprob list. The derived
score is emitted only when the final A/B/C/D character aligns exactly with one
token. Other cases are explicitly missing, not guessed or renormalized.

Jev records contain native response confidence. Their inputs were reconstructed
from frozen items and checked against original hashes; this provenance is recorded
per row. No token logprobs are invented for Jev.

The release exporter selects exactly the ten published conditions, verifies
request hashes and counts, and produces `artifacts/full-records.jsonl.gz` plus a
SHA-256 manifest. This file includes model-generated reasoning and token data,
not model weights, environment variables, API keys or authorization headers.
Raw artifacts are separate from Git. The full 3,000-record archive and SHA-256
manifest are available in the [v0.2.0 release](https://github.com/softpudding/jev-frontier-100/releases/tag/v0.2.0).

For the public raw attachment, absolute local filesystem paths in response
`body.model` routing metadata are replaced with the model blob filename. This
transformation is counted in its manifest; prompts, thinking, final answers and
logprobs are unchanged. Local originals retain the exact original response.
