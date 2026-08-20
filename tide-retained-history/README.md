# Executed retained history

Both scripts execute the same six functions from `history.py`. Their function
bodies are framework-independent and shared unchanged.

| Execution | Input State(s) | Output State(s) |
|---|---|---|
| `capture_sources` | none | `source_left`, `source_right` |
| `prepare_left` | `source_left` | `ready_left` |
| `prepare_right` | `source_right` | `ready_right` |
| `merge` | `ready_left`, `ready_right` | `merged` |
| `analyse` | `merged` | `analysis` |
| `archive` | `merged` | `archive_record` |

`ready_left` and `ready_right` both have the value `"ready-v1"`, but remain
distinct State occurrences. The `merged` occurrence is consumed twice.

`run_dagster.py` adapts the functions to Dagster ops and executes the graph. It
retains the complete returned `DagsterEvent` stream in
`dagster.events.raw.json`, then derives the Execution carrier from selected
step occurrences and the State carrier and incidence from native
`STEP_OUTPUT` and `LOADED_INPUT` events.

`run_openlineage.py` executes the same functions and uses the OpenLineage client
to emit native `COMPLETE` RunEvents. It retains those events in
`openlineage.run-events.raw.jsonl`, then derives the Execution carrier from Run
occurrences and the State carrier and incidence from their input and output
datasets. `mapping.json` supplies the correspondence; it is not inferred.

Dagster records include process-local fields such as the PID, and OpenLineage
records contain execution timestamps, so raw-file hashes may change between
runs. The `E`/`S`/`I`/`O` projections remain deterministic.

From the parent directory:

```bash
python -m pip install dagster==1.13.16 openlineage-python==1.52.0
python tide-retained-history/run_dagster.py
python tide-retained-history/run_openlineage.py
python tide-retained-history/compare.py
```

Expected result:

Each projection has 6 Executions, 7 States, 6 input facts, 7 output facts,
6 direct handoffs, and 13 non-empty reachability answers.
