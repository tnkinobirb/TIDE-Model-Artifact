import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from tide_reference_comparator import compare

def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))



dagster = load("dagster.tide.json")
openlineage = load("openlineage.tide.json")
mapping = load("mapping.json")

result = compare(dagster, openlineage, mapping["execution_map"], mapping["state_map"])
