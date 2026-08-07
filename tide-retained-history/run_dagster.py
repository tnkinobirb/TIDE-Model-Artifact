import json
from pathlib import Path

import dagster as dg
from dagster._serdes import serialize_value

import history


RUN_ID = "00000000-0000-4000-8000-000000000001"
HERE = Path(__file__).parent

# Declare dagster workflow based on history.py

@dg.op(
    name="capture_sources",
    out={"source_left": dg.Out(), "source_right": dg.Out()},
)
def capture_sources_op():
    return history.capture_sources()


@dg.op(name="prepare_left")
def prepare_left_op(source_left):
    return history.prepare_left(source_left)


@dg.op(name="prepare_right")
def prepare_right_op(source_right):
    return history.prepare_right(source_right)


@dg.op(name="merge")
def merge_op(ready_left, ready_right):
    return history.merge(ready_left, ready_right)


@dg.op(name="analyse")
def analyse_op(merged):
    return history.analyse(merged)


@dg.op(name="archive")
def archive_op(merged):
    return history.archive(merged)


@dg.job
def workflow():
    source_left, source_right = capture_sources_op()
    ready_left = prepare_left_op(source_left)
    ready_right = prepare_right_op(source_right)
    merged = merge_op(ready_left, ready_right)
    analyse_op(merged)
    archive_op(merged)

# run the workflow
result = workflow.execute_in_process(run_id=RUN_ID)

# preserve the DagsterEvents.
raw_events = [json.loads(serialize_value(event)) for event in result.all_events]
(HERE / "dagster.events.raw.json").write_text(
    json.dumps(
        {
            "format": "DagsterEvent serialized with dagster._serdes.serialize_value",
            "dagster_version": dg.__version__,
            "run_id": RUN_ID,
            "events": raw_events,
        },
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


# derive the TIDE projection

# identity naming helpers
def execution(step):
    return f"dagster:run:{RUN_ID}:step:{step}"

def state(step, output):
    return f"dagster:run:{RUN_ID}:step:{step}:output:{output}"

# TIDE Structure - lists may contain duplicates, but are treated as one occurrence. 
model = {"I": [], "O": []}

# dor all dagster events
for event in result.all_events:
    # project (e, s) output occurrences.
    if event.event_type_value == "STEP_OUTPUT":
        output_name = event.event_specific_data.output_name
        model["O"].append([execution(event.step_key), state(event.step_key, output_name)])

    #  project (e, s) input occurrences.
    if event.event_type_value == "LOADED_INPUT":
        loaded = event.event_specific_data
        model["I"].append([
            execution(event.step_key),
            state(loaded.upstream_step_key, loaded.upstream_output_name),
        ])

# sort occurrences
for relation in model.values():
    relation.sort()

# export the TIDE model as json
(HERE / "dagster.tide.json").write_text(
    json.dumps(model, indent=2) + "\n",
    encoding="utf-8",
)
