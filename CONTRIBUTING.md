# Contributing

Use item IDs in every correction. Explain the ambiguity or alternate answer and
supply a reproducible oracle when possible. Do not silently patch scored v0.1
data. File a documented erratum and increment the dataset version before a new
run. Do not optimize prompts on test-set answers and report that result as the
original protocol. Distinguish ablations from primary runs.

New tasks should have one uniquely defensible answer, plausible distractors,
explicit semantics, original provenance, and difficulty justified by required
operations. Add a counterfactual pair and an executable oracle when practical.
Human review by a second independent reviewer is encouraged and should be
attributed accurately. Do not claim AI-assisted review is independent human
validation.

Never commit API keys or private examples. Public release should include frozen
items, run configuration, model digests, per-item compact outcomes and the
aggregation code. Raw model thinking is optional; do not make reproducibility
of accuracy depend on disclosing it.

`docs/ci-template.yml` is a GitHub Actions template for offline validation. This
release does not install an active workflow; publishing credentials did not
include the workflow scope. The release's tests were run locally. A maintainer
with workflow permissions can install the template under `.github/workflows/`.
