# TIDE reference comparator

This directory contains the paper-bounded comparator for finite TIDE
structures. It uses only the Python standard library and has one public
operation:

```python
from comparator import compare

report = compare(K1, K2, execution_map, state_map)
```

The comparator should only be used after native interpretation and occurrence
correspondence have been supplied. It does not read native records, infer or
repair identities, add facts, complete provenance, or choose a comparison
scope.

## Imported representation

Section VII-A represents each finite `K=(I,O)` as JSON-compatible relation
lists:

```json
{
  "I": [["execution", "input_state"]],
  "O": [["execution", "output_state"]]
}
```

`I` and `O` are treated as mathematical sets, serialisation order and duplication does not affect this. Execution and State strings are this artifact declared identities, not values or inferred semantic names.

The two supplied maps are JSON objects whose keys and values encode the
ambient bijections in Equation (8). The comparator checks only that they are a well-formed one-to-one representations. This does not mean every identity needs a corresponding entry.

## What `compare` reports

Every result is a direct report of a paper rule:

- fixed direct-handoff and non-empty reachability answers, Equations (4)-(5);
- validity under unique creation and acyclic ancestry, Equations (6)-(7);
- absent mapped identities under the ambient map, Equation (8);
- mapped carriers and incidence, Equations (9)-(12);
- outside-scope incidence, Equations (13)-(14);
- `I_minus`, `I_plus`, `O_minus`, and `O_plus`, Equations (17)-(18);
- mapped conformance, Equation (16);
- mapped judgment correspondence, Proposition 3 and Equations (20)-(21);
- complete carrier coverage, Equation (19); and
- whole-kernel equality, defined as conformance plus coverage on both sides.

Sorting, counts, and JSON field names are reporting only. They do not alter a
structure, map, validity result, difference set, or conformance result.

## Reproduce the comparator and paper cases

From the artifact root, run the five comparator unit tests:

```bash
python -m unittest tide_reference_comparator.test_comparator -v
```

Then run the nine evaluation-table tests:

```bash
python -m unittest test_examples -v
```

The artifact therefore retains fourteen tests in total: five comparator unit
tests and nine evaluation-table tests.

