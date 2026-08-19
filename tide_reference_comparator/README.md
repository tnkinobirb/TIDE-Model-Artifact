# TIDE reference comparator

This directory contains the paper-bounded comparator for finite TIDE
structures. It uses only the Python standard library and has one public
operation:

```python
from tide_reference_comparator import compare

report = compare(K1, K2, execution_map, state_map)
```

The comparator should only be used after native interpretation and occurrence
correspondence have been supplied. It does not read native records, infer or
repair identities, add facts, complete provenance, or choose a comparison
scope.

## Imported representation

The retained artifact represents each finite `K=(E,S,I,O)` as
JSON-compatible set lists:

```json
{
  "E": ["execution"],
  "S": ["input_state", "output_state"],
  "I": [["execution", "input_state"]],
  "O": [["execution", "output_state"]]
}
```

`E`, `S`, `I`, and `O` are treated as mathematical sets, so serialisation
order and duplication do not affect them. `E` and `S` are authoritative:
every incidence endpoint must belong to its declared carrier, while declared
identities need not occur in incidence. Execution and State strings are the
artifact's declared identities, not values or inferred semantic names.

The two supplied maps are JSON objects whose keys and values encode the
supplied bijections between selected identity subsets in Equation (6). The
comparator checks only that they are well-formed one-to-one representations.
This does not mean every identity needs a corresponding entry.

## What `compare` reports

Every result is a direct report of a paper rule:

- fixed direct-handoff and non-empty reachability answers, Equations (2)-(3);
- validity under unique creation and acyclic ancestry, Equations (4)-(5);
- mapped, outside, and absent identities, Equations (7)-(12);
- mapped and outside incidence, Equations (13)-(16);
- `I_minus`, `I_plus`, `O_minus`, and `O_plus`, Equations (18)-(21);
- mapped conformance, Equation (22);
- mapped judgment correspondence, Proposition 3 and Equations (24)-(25);
- exact map coverage and complete agreement, Equation (23).

Sorting, counts, and JSON field names are reporting only. They do not alter a
structure, map, validity result, difference set, or conformance result.

## Reproduce the comparator and paper cases

From the artifact root, run the ten comparator unit tests:

```bash
python -m unittest tide_reference_comparator.test_comparator -v
```

Then run the nine evaluation-table tests and the paper/audit wording check:

```bash
python -m unittest test_examples -v
```

The artifact therefore retains twenty tests in total: ten comparator unit
tests, nine evaluation-table tests, and one paper/audit consistency test.
