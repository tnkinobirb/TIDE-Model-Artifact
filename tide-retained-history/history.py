def capture_sources():
    return "source-left-v1", "source-right-v1"


def prepare_left(source_left):
    return "ready-v1"


def prepare_right(source_right):
    return "ready-v1"


def merge(ready_left, ready_right):
    return "merged-v1"


def analyse(merged):
    return "analysis-v1"


def archive(merged):
    return "archive-v1"
