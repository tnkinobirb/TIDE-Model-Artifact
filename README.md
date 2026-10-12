# TIDE: A Contract for Comparing Exact Execution Relationships Across Execution Records | Supporting Artifact

This repo contains a research paper and it's supporting artifact. The research paper defines a formal model for representing and comparing recorded execution relationships. 

Contained within are:

- `paper/` — contains the PDF and `.tex` source.
- `question-audit/` — contains the question audit used to identify and count recurring requirements.
- `tide-retained-history/` — contains the retained Dagster and OpenLineage histories and their comparison.
- `tide_reference_comparator/` — contains the TIDE reference comparator and its unit tests.
- `test_examples.py` — tests and runs the comparisons outlined in Section VII.

All tests can be run with:

```bash
python -m unittest discover -v
```

`test_examples.py` can be run with:

```bash
python -m unittest test_examples -v
```

`test_comparator.py` can be run with:

```bash
python -m unittest tide_reference_comparator.test_comparator -v
```
