import json
from datetime import datetime, timezone
from pathlib import Path

from openlineage.client import OpenLineageClient
from openlineage.client.event_v2 import (
    InputDataset,
    Job,
    OutputDataset,
    Run,
    RunEvent,
    RunState,
)
from openlineage.client.serde import Serde
from openlineage.client.transport import Transport

import history


HERE = Path(__file__).parent
NAMESPACE = "tide-retained-history"
PRODUCER = "https://github.com/tnkinobirb/TIDE-Model-Artifact"
RUN_IDS = {
    "capture_sources": "10000000-0000-4000-8000-000000000001",
    "prepare_left": "10000000-0000-4000-8000-000000000002",
    "prepare_right": "10000000-0000-4000-8000-000000000003",
    "merge": "10000000-0000-4000-8000-000000000004",
    "analyse": "10000000-0000-4000-8000-000000000005",
    "archive": "10000000-0000-4000-8000-000000000006",
}
# OpenLineage configuration
class RecordHere(Transport):
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


records = RecordHere()
client = OpenLineageClient(transport=records)

# record event
def record(execution, inputs, outputs):
    client.emit(RunEvent(
        eventType=RunState.COMPLETE,
        eventTime=datetime.now(timezone.utc).isoformat(),
        run=Run(runId=RUN_IDS[execution]),
        job=Job(namespace=NAMESPACE, name=execution),
        producer=PRODUCER,
        inputs=[InputDataset(NAMESPACE, item) for item in inputs],
        outputs=[OutputDataset(NAMESPACE, item) for item in outputs],
    ))

# execute the workflow defined in history.py
# record the workflow as openlineage events
source_left, source_right = history.capture_sources()
record("capture_sources", [], ["source_left", "source_right"])

ready_left = history.prepare_left(source_left)
record("prepare_left", ["source_left"], ["ready_left"])

ready_right = history.prepare_right(source_right)
record("prepare_right", ["source_right"], ["ready_right"])

merged = history.merge(ready_left, ready_right)
record("merge", ["ready_left", "ready_right"], ["merged"])

analysis = history.analyse(merged)
record("analyse", ["merged"], ["analysis"])

archive_record = history.archive(merged)
record("archive", ["merged"], ["archive_record"])


# preserve the OpenLineage RunEvents.
(HERE / "openlineage.run-events.raw.jsonl").write_text(
    "\n".join(Serde.to_json(event) for event in records.events) + "\n",
    encoding="utf-8",
)

# derive the TIDE model 

# naming helpers
def execution(event):
    return f"openlineage:run:{event.run.runId}"

def state(dataset):
    return f"openlineage:dataset:{dataset.namespace}/{dataset.name}"

# TIDE structure
model = {"I": [], "O": []}

for event in records.events:
    # project (e, s) input and output occurrences
    model["I"].extend([execution(event), state(item)] for item in event.inputs)
    model["O"].extend([execution(event), state(item)] for item in event.outputs)

# sort the lists
for relation in model.values():
    relation.sort()

# export the TIDE model as json
(HERE / "openlineage.tide.json").write_text(
    json.dumps(model, indent=2) + "\n",
    encoding="utf-8",
)
