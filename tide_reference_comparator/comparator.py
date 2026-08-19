"""Reference comparator for the TIDE paper's exact-relationship contract.

Traceability legend
-------------------
Eq. (1): candidate structure ``K=(E,S,I,O)``.
Eq. (2)-(3): direct handoff and non-empty directed reachability.
Eq. (4)-(5): unique creation and acyclic ancestry validity.
Eq. (6): supplied ambient one-to-one Execution and State maps.
Eq. (7)-(12): mapped, outside, and absent identity carriers.
Eq. (13)-(16): mapped and outside input/output incidence.
Eq. (17): elementwise pair map.
Eq. (18)-(21): the four mapped difference sets.
Eq. (22): mapped conformance.
Eq. (23): complete agreement across projections.
Prop. 3 / Eq. (24)-(25): mapped handoff and reachability correspondence.

The only public operation is ``compare``. Everything else is either the
declared JSON import boundary or report construction for those paper rules.
The module never interprets native records, discovers occurrence identity,
repairs a structure, extends a map, or changes a supplied fact.
"""

from collections import defaultdict

__all__ = ["compare"]


def _import_structure(candidate, name):
    """Import one finite JSON representation of Eq. (1)."""
    # Eq. (1) admits exactly the two identity carriers and two incidences.
    if (
        not isinstance(candidate, dict)
        or set(candidate) != {"E", "S", "I", "O"}
    ):
        raise ValueError(
            f"{name} must be a JSON object containing exactly E, S, I and O"
        )

    # Import arrays as sets so order and duplicate entries do not change K.
    structure = {"E": set(), "S": set()}
    for carrier, identity_name in (("E", "Execution"), ("S", "State")):
        entries = candidate[carrier]
        if not isinstance(entries, list):
            raise ValueError(f"{name}.{carrier} must be a JSON list")
        for index, identity in enumerate(entries):
            if not isinstance(identity, str) or not identity:
                raise ValueError(
                    f"{name}.{carrier}[{index}] {identity_name} "
                    "must be a non-empty string"
                )
            structure[carrier].add(identity)

    # I and O are sets of ordered Execution-State pairs.
    for relation in ("I", "O"):
        entries = candidate[relation]
        if not isinstance(entries, list):
            raise ValueError(f"{name}.{relation} must be a JSON list")

        # Eq. (1) gives set semantics over Execution-State pairs.
        pairs = set()
        for index, entry in enumerate(entries):
            if not isinstance(entry, list) or len(entry) != 2:
                raise ValueError(
                    f"{name}.{relation}[{index}] must be [execution, state]"
                )
            execution, state = entry

            # Validate identities and import incidence pairs.
            if not isinstance(execution, str) or not execution:
                raise ValueError(
                    f"{name}.{relation}[{index}] Execution must be a non-empty string"
                )
            if not isinstance(state, str) or not state:
                raise ValueError(
                    f"{name}.{relation}[{index}] State must be a non-empty string"
                )
            pairs.add((execution, state))
        structure[relation] = pairs

    # Incidence endpoints must belong to the declared identity carriers.
    for relation in ("I", "O"):
        for execution, state in structure[relation]:
            if execution not in structure["E"]:
                raise ValueError(
                    f"{name}.{relation} references Execution {execution!r} "
                    "outside E"
                )
            if state not in structure["S"]:
                raise ValueError(
                    f"{name}.{relation} references State {state!r} outside S"
                )
    return structure


def _map_errors(mapping, name):
    """Report only failures of the supplied bijection form in Eq. (6)."""
    if not isinstance(mapping, dict):
        return [f"{name} map must be a JSON object"]

    errors = []
    targets = []
    for source, target in mapping.items():
        # Eq. (6) treats endpoints as opaque ambient identities; strings are
        # only this artifact's JSON import representation.
        if not isinstance(source, str) or not source:
            errors.append(f"{name} map source must be a non-empty string")
        if not isinstance(target, str) or not target:
            errors.append(f"{name} map target must be a non-empty string")
        else:
            targets.append(target)

    # Eq. (6) requires one-to-one maps.
    # JSON object keys are unique, so only the entry values need this check.
    if len(set(targets)) != len(targets):
        errors.append(f"{name} map must be one-to-one")
    return errors


def _judgment_sets(inputs, outputs):
    """Derive exactly the fixed judgments in Eq. (2)-(3)."""
    # Eq. (2): one output and one input joined by the identical State.
    handoffs = {
        (producer, state, consumer)
        for producer, state in outputs
        for consumer, consumed_state in inputs
        if state == consumed_state
    }

    # Eq. (3): reachability is the non-empty transitive closure of handoff.
    adjacency = defaultdict(set)
    for producer, _, consumer in handoffs:
        adjacency[producer].add(consumer)

    # Traverse the handoff graph from each incident Execution to derive the
    # non-empty reachability relation in Eq. (3).
    executions = {execution for execution, _ in inputs | outputs}
    reachability = set()
    for start in executions:
        pending = list(adjacency[start])
        visited = set()
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            reachability.add((start, current))
            pending.extend(adjacency[current])
    return handoffs, reachability


def _validity_report(structure):
    """Report exactly the semantic-validity conditions in Eq. (4)-(5)."""
    executions, states = structure["E"], structure["S"]

    # Eq. (4): every represented State has exactly one represented producer.
    producers = defaultdict(set)
    for execution, state in structure["O"]:
        producers[state].add(execution)
    producer_counts = {state: len(producers[state]) for state in states}
    unique_creation = all(count == 1 for count in producer_counts.values())

    # Eq. (5): no represented Execution reaches itself.
    _, reachability = _judgment_sets(structure["I"], structure["O"])
    cyclic_executions = sorted(
        execution
        for execution in executions
        if (execution, execution) in reachability
    )
    acyclic_ancestry = not cyclic_executions

    return {
        "valid": unique_creation and acyclic_ancestry,
        "unique_creation": unique_creation,
        "acyclic_ancestry": acyclic_ancestry,
        "producer_count_errors": {
            state: count
            for state, count in sorted(producer_counts.items())
            if count != 1
        },
        "cyclic_executions": cyclic_executions,
    }


def _ordered(values):
    """Convert mathematical sets to deterministic JSON report lists."""
    return [list(value) for value in sorted(values)]


def _judgment_report(structure):
    """Serialize the Eq. (2)-(3) answers."""
    # Eq. (2)-(3) supply the only derived relationship judgments.
    handoffs, reachability = _judgment_sets(structure["I"], structure["O"])
    return {
        "direct_handoffs": _ordered(handoffs),
        "reachability": _ordered(reachability),
    }


def _unassessable_report(k1, k2, mapping_errors):
    """Report a failed map check without performing comparison."""
    # Fixed-K judgments and validity remain reportable before map comparison.
    return {
        "assessable": False,
        "mapping_errors": mapping_errors,
        "validity": {
            "K1": _validity_report(k1),
            "K2": _validity_report(k2),
        },
        "judgments": {
            "K1": _judgment_report(k1),
            "K2": _judgment_report(k2),
        },
        "conformant": None,
        "identity_coverage": {"K1": None, "K2": None},
        "complete_agreement": None,
    }


def compare(k1_candidate, k2_candidate, execution_map, state_map):
    """Apply the paper contract and return its results as one report."""
    # Import JSON representation of the TIDE Model
    k1 = _import_structure(k1_candidate, "K1")
    k2 = _import_structure(k2_candidate, "K2")

    # Eq. (6): check representation and one-to-one form.
    mapping_errors = [
        *_map_errors(execution_map, "Execution"),
        *_map_errors(state_map, "State"),
    ]
    # An invalid map makes comparison unassessable, but fixed-K validity and
    # judgments remain reportable.
    if mapping_errors:
        report = _unassessable_report(k1, k2, mapping_errors)
        print_report(report)
        return report

    # Eq. (1): each record supplies its represented identity carriers.
    e1, s1 = k1["E"], k1["S"]
    e2, s2 = k2["E"], k2["S"]

    # Eq. (6): the supplied domains and ranges define ambient map scope.
    d_e = set(execution_map)
    r_e = set(execution_map.values())
    d_s = set(state_map)
    r_s = set(state_map.values())

    # Eq. (7)-(8): mapped identities present in each representation.
    e1_m, e2_m = e1 & d_e, e2 & r_e
    s1_m, s2_m = s1 & d_s, s2 & r_s

    # Eq. (13)-(14): mapped input and output incidence.
    i1_m = {(e, s) for e, s in k1["I"] if e in e1_m and s in s1_m}
    o1_m = {(e, s) for e, s in k1["O"] if e in e1_m and s in s1_m}
    i2_m = {(e, s) for e, s in k2["I"] if e in e2_m and s in s2_m}
    o2_m = {(e, s) for e, s in k2["O"] if e in e2_m and s in s2_m}

    # Eq. (15)-(16): retain, but do not compare, outside-scope incidence.
    i1_out, o1_out = k1["I"] - i1_m, k1["O"] - o1_m
    i2_out, o2_out = k2["I"] - i2_m, k2["O"] - o2_m

    # Eq. (17): extend the supplied identity maps elementwise to incidence.
    f_i1_m = {(execution_map[e], state_map[s]) for e, s in i1_m}
    f_o1_m = {(execution_map[e], state_map[s]) for e, s in o1_m}

    # Eq. (18)-(21): preservation and reflection differences.
    delta_i_minus = f_i1_m - i2_m
    delta_i_plus = i2_m - f_i1_m
    delta_o_minus = f_o1_m - o2_m
    delta_o_plus = o2_m - f_o1_m

    # Eq. (22): conformance holds exactly when all four differences are empty.
    conformant = not any(
        (delta_i_minus, delta_i_plus, delta_o_minus, delta_o_plus)
    )

    # Prop. 3 / Eq. (24)-(25): report mapped judgment correspondence.
    h1_m, r1_m = _judgment_sets(i1_m, o1_m)
    h2_m, r2_m = _judgment_sets(i2_m, o2_m)
    f_h1_m = {
        (execution_map[producer], state_map[state], execution_map[consumer])
        for producer, state, consumer in h1_m
    }
    f_r1_m = {
        (execution_map[source], execution_map[target])
        for source, target in r1_m
    }

    # Eq. (23): complete coverage is exact identity equality on both sides.
    k1_covered = e1 == d_e and s1 == d_s
    k2_covered = e2 == r_e and s2 == r_s

    # Eq. (23): complete agreement is conformance plus exact coverage.
    complete_agreement = conformant and k1_covered and k2_covered

    # Assemble the comparison results without changing the supplied inputs.
    report = {
        "assessable": True,
        "mapping_errors": [],
        "validity": {
            "K1": _validity_report(k1),
            "K2": _validity_report(k2),
        },
        "judgments": {
            "K1": _judgment_report(k1),
            "K2": _judgment_report(k2),
            "mapped_correspond": f_h1_m == h2_m and f_r1_m == r2_m,
            "mapped_differences": {
                "handoffs_missing": _ordered(f_h1_m - h2_m),
                "handoffs_unsupported": _ordered(h2_m - f_h1_m),
                "reachability_missing": _ordered(f_r1_m - r2_m),
                "reachability_unsupported": _ordered(r2_m - f_r1_m),
            },
        },
        "mapped_scope": {
            "K1": {"Executions": sorted(e1_m), "States": sorted(s1_m)},
            "K2": {"Executions": sorted(e2_m), "States": sorted(s2_m)},
        },
        "outside_identities": {
            "K1": {
                "Executions": sorted(e1 - d_e),
                "States": sorted(s1 - d_s),
            },
            "K2": {
                "Executions": sorted(e2 - r_e),
                "States": sorted(s2 - r_s),
            },
        },
        "mapped_identities_absent": {
            "K1": {
                "Executions": sorted(d_e - e1),
                "States": sorted(d_s - s1),
            },
            "K2": {
                "Executions": sorted(r_e - e2),
                "States": sorted(r_s - s2),
            },
        },
        "deltas": {
            "I_minus": _ordered(delta_i_minus),
            "I_plus": _ordered(delta_i_plus),
            "O_minus": _ordered(delta_o_minus),
            "O_plus": _ordered(delta_o_plus),
        },
        "preservation": {
            "I": not delta_i_minus,
            "O": not delta_o_minus,
        },
        "reflection": {
            "I": not delta_i_plus,
            "O": not delta_o_plus,
        },
        "outside": {
            "K1": {"I": _ordered(i1_out), "O": _ordered(o1_out)},
            "K2": {"I": _ordered(i2_out), "O": _ordered(o2_out)},
        },
        "conformant": conformant,
        "identity_coverage": {"K1": k1_covered, "K2": k2_covered},
        "complete_agreement": complete_agreement,
    }
    print_report(report)
    return report
    

# Report visualisation
def print_report(report):
    print("\nAssessable:", report["assessable"])
    print("Mapping errors:", len(report["mapping_errors"]))

    for name, validity in report["validity"].items():
        print(f"{name} valid:", validity["valid"])

    for name in ("K1", "K2"):
        judgment = report["judgments"][name]
        print(
            f"{name} judgment:",
            len(judgment["direct_handoffs"]), "handoffs,",
            len(judgment["reachability"]), "reachable pairs"
        )

    # No mapped-scope comparison fields exist when the supplied maps fail
    # Eq. (6); the fixed-K information above is still a complete report.
    if not report["assessable"]:
        print("Conformant:", report["conformant"])
        print("Identity coverage:", report["identity_coverage"])
        print("Complete agreement:", report["complete_agreement"])
        return

    print("Mapped correspond:", report["judgments"]["mapped_correspond"])

    for name in ("K1", "K2"):
        scope = report["mapped_scope"][name]
        print(
            f"{name} mapped scope:",
            len(scope["Executions"]), "executions,",
            len(scope["States"]), "states"
        )

    for name in ("K1", "K2"):
        absent = report["mapped_identities_absent"][name]
        print(
            f"{name} absent identities:",
            len(absent["Executions"]), "executions,",
            len(absent["States"]), "states"
        )

    print("Deltas:", {
        name: len(values)
        for name, values in report["deltas"].items()
    })

    print("Preservation:", report["preservation"])
    print("Reflection:", report["reflection"])

    for name in ("K1", "K2"):
        outside = report["outside"][name]
        print(
            f"{name} outside:",
            len(outside["I"]), "inputs,",
            len(outside["O"]), "outputs"
        )

    print("Conformant:", report["conformant"])
    print("Identity coverage:", report["identity_coverage"])
    print("Complete agreement:", report["complete_agreement"])
