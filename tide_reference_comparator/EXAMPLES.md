# Comparator examples and limits

## Controlled six-Execution fixture pair

`controlled_0.json`, `controlled_1.json`, and `full_mapping.json` are the
controlled six-Execution, seven-State structures used for the non-native rows
of Table V. They retain:

- 6 Executions;
- 7 States;
- 6 input facts;
- 7 output facts;
- 6 direct handoffs; and
- 13 non-empty reachability answers.

The two files use different opaque identity strings and the same relationship
topology. They are explicit-carrier structures, not additional host
executions. The paper's two retained native runs and their projections remain
in the wider artifact; the comparator begins only after projection.

## Table V controlled cases

- `full_mapping.json` gives complete identity coverage.
- `selected_mapping.json` gives partial identity coverage over both complete
  structures.
- `missing_input.json` omits one mapped input (`Delta I minus`).
- `extra_scoped_input.json` adds one mapped input (`Delta I plus`).
- `missing_output.json` omits one mapped output (`Delta O minus`) and
  leaves its consumed State producerless.
- `mapped_output_target_absent.json` maps an output State identity to an
  identity absent from the target `S`; the map remains assessable and the
  expected output is missing.
- `extra_scoped_output.json` plus
  `full_mapping_with_extra_target_state.json` adds one mapped output (`Delta O
  plus`) while both structures remain valid.
- `invalid_outside_branch.json` adds one producerless input outside the
  complete fixture map, leaving conformance unchanged while target validity
  fails.

Every mutation changes only the supplied map, an explicit carrier, or one
incidence fact, exactly as stated in Table V. None is claimed to be an
observed host defect.

`selected_source.json` is an additional exact-coverage boundary fixture used
by the comparator unit suite with `selected_mapping.json`; it is not a row of
Table V.

## Boundary

This directory contains no native parser, host adapter, workflow runner,
identity matcher, repair rule, provenance completion rule, or cross-history
example. It implements the paper contract and deterministic reporting only.
