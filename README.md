# TIDE: A Contract for Comparing Exact Execution Relationships Across Execution Records ~ Supporting Artifact

Within the repo are contained:

- `question-audit` — contains the question audit used to identify and count recurring requirements.
- `paper` — contains the manuscript source, PDF, and exact build instructions.
- `tide-retained-history` — contains the retained Dagster and OpenLineage histories and their comparison.
- `tide_reference_comparator` — contains the TIDE reference comparator and its unit tests.
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
