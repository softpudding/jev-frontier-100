# JF100 v0.2 budget experiment

Complete.

| Condition | Completed | Accuracy | Valid completion | Median seconds | Mean generated tokens |
|---|---:|---:|---:|---:|---:|
| jev | 300/300 | 77.0% | 100.0% | 1.3 | — |
| qwen3.5:0.8b / off | 300/300 | 38.0% | 100.0% | 0.7 | 10.2 |
| qwen3.5:0.8b / 512 | 300/300 | 39.0% | 100.0% | 29.5 | 527.1 |
| qwen3.5:0.8b / 2048 | 300/300 | 54.0% | 100.0% | 114.1 | 1955.3 |
| qwen3.5:2b-q8_0 / off | 300/300 | 48.0% | 100.0% | 1.0 | 11.1 |
| qwen3.5:2b-q8_0 / 512 | 300/300 | 59.7% | 100.0% | 38.7 | 515.4 |
| qwen3.5:2b-q8_0 / 2048 | 300/300 | 82.0% | 100.0% | 141.1 | 1635.7 |
| qwen3.5:4b-q8_0 / off | 300/300 | 56.0% | 100.0% | 1.9 | 10.9 |
| qwen3.5:4b-q8_0 / 512 | 300/300 | 78.3% | 100.0% | 72.5 | 511.4 |
| qwen3.5:4b-q8_0 / 2048 | 300/300 | 96.7% | 100.0% | 130.4 | 1153.7 |

Full inputs/outputs and logprobs remain in the local raw run directory. Compact public data excludes raw thinking. Jev is a reused, dated reference. Timing is descriptive under shared-GPU batching. Confidence scores have different semantics; see docs/PROTOCOL.md and summary.json.
