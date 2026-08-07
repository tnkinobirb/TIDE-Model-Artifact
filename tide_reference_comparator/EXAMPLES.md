# Comparator examples and limits

## Controlled six-Execution fixture pair

`controlled_0.json`, `controlled_1.json`, and `full_mapping.json` are the
controlled six-Execution, seven-State structures used for the non-native rows
of Table III. They retain:

- 6 Executions;
- 7 States;
- 6 input facts;
- 7 output facts;
- 6 direct handoffs; and
- 13 non-empty reachability answers.

The two files use different opaque identity strings and the same relationship
topology. They are relation fixtures, not additional host executions. The
paper's two retained native runs and their projections remain in the wider
artifact; the comparator begins only after projection.

## Table III controlled cases

- `full_mapping.json` gives complete carrier coverage.
- `selected_mapping.json` gives partial carrier coverage over both complete
  structures.
- `selected_source.json` gives the smaller-source special case under the same
  mapped-scope rule.
- `missing_input.json` omits one mapped input (`Delta I minus`).
- `extra_scoped_input.json` adds one mapped input (`Delta I plus`).
- `missing_output.json` omits one mapped output (`Delta O minus`) and
  leaves its consumed State producerless.
- `mapped_output_target_absent.json` supplies an output-State endpoint absent
  from the target record; the map remains assessable and the expected output
  is missing.
- `extra_scoped_output.json` plus
  `full_mapping_with_extra_target_state.json` adds one mapped output (`Delta O
  plus`) while both structures remain valid.
- `invalid_outside_branch.json` adds one producerless input outside the
  complete fixture map, leaving conformance unchanged while target validity
  fails.

Every mutation changes only the supplied map, one incidence fact, or the one
added mapped fact and its required identity pair, exactly as stated in Table
III. None is claimed to be an observed host defect.

## Boundary

This directory contains no native parser, host adapter, workflow runner,
identity matcher, repair rule, provenance completion rule, or cross-history
example. It implements the paper contract and deterministic reporting only.
