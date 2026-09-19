# Dataset card: JF100 v0.1

## Purpose and intended use

A transparent, small diagnostic set for the empirical task boundary of Jev
1.13.0 relative to thinking language models. Suitable for reproducible probing,
error analysis and teaching evaluation methodology. Not a psychometric IQ test,
not a comprehensive coding benchmark, and not evidence of a model's latent
parameter count. Do not use it alone for high-stakes deployment decisions.

## Composition

100 English multiple-choice text items in ten equally weighted domains. Fifty
template pairs introduce a decisive counterfactual variation. Some variants
also differ in option labels, numerical distractors or semantically irrelevant
ordering; the pairs are related probes, not perfectly isolated causal
experiments. Difficulty labels are a priori design judgments, not empirical
item-response calibration. There are only five template clusters per domain.

Four answer labels are balanced globally, not necessarily within every domain
or difficulty cell. Uniform random-label accuracy is 25%, but elimination of
obviously incompatible alternatives can yield a stronger guessing baseline.
Some tasks encode binary or ordinal judgments into the common four-option
interface. Thus domain chance-adjusted difficulty is not interchangeable.

## Creation and validation

Original synthetic tasks authored with AI assistance, informed by TypeSafe's
public use cases/known limitations and earlier local exploratory tests. No
third-party benchmark questions or user-private data were imported. This does
not prove freedom from familiar patterns or training contamination. Examples
of aliases, closures and elementary logic are widely known problem families.

Each row records domain, pair, difficulty, language, state, question, options,
gold label, explanation, oracle type, tags and provenance. Sixty answers are
computed by deterministic local oracles; forty semantic/rule answers are
explicitly authored. Tests include separately hand-derived numeric anchors,
code execution, independent graph walks, option rotations, answer non-leakage,
duplicate detection and aggregation invariants.

Initial construction review corrected two paired templates whose original
variants accidentally had identical answer meanings (calendar and LRU). These
were fixed **before scored runs**. The first frozen version is identified by
the committed data manifest. There are no scored-data corrections so far.

No independent human expert review or inter-rater agreement study has been
completed. This limitation cannot be removed by automated tests alone. A future
reviewed release must record reviewers, disputes and adjudication, and increment
the dataset version if any scored question or answer changes.

## Distribution and contamination

MIT license for the original code and data. Public answers make contamination
possible after release; new models may have trained on the released test.
The release includes original questions and compact outcomes. Neither external model weights
nor private API keys are included. Generated raw thinking remains in ignored
local run directories; compact outcomes are sufficient to recompute accuracy.

## Known scope gaps

No multimodal, interactive tool-use, external knowledge retrieval, multilingual,
long-horizon agent, proof-generation or open-ended synthesis assessment.
No official population-based notion of intelligence is estimated. Long-context
items contain synthetic structured distractors rather than natural books or
entire repositories. Code is short, self-contained Python. A high score may
indicate saturation of this diagnostic set, not a measured ceiling.
