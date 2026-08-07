"""Regression tests for every evaluation row in Table III of the TIDE paper.

The retained-record test executes ``tide-retained-history/compare.py``.
The controlled tests call the paper's single public comparator operation.
Every assertion corresponds to a result column displayed in Table III; this
file introduces no additional comparison rule.
"""

# Table III is reproduced with the standard-library unittest framework.
import contextlib
import io
import json
import runpy
import unittest
from pathlib import Path

from tide_reference_comparator.comparator import compare

# Section VII-D retains the native records and controlled fixtures together.
ROOT = Path(__file__).resolve().parent
RETAINED = ROOT / "tide-retained-history"
EXAMPLES = ROOT / "tide_reference_comparator" / "examples"

def _load_json(path):
    """Load one retained JSON input used by a Table III comparison."""
    return json.loads(path.read_text(encoding="utf-8"))


def _controlled_result(target_name, mapping_name="full_mapping.json"):
    """Run one controlled Table III fixture through the paper comparator."""
    mapping = _load_json(EXAMPLES / mapping_name)
    # Comparator console output is reporting only and is suppressed in tests.
    with contextlib.redirect_stdout(io.StringIO()):
        return compare(
            _load_json(EXAMPLES / "controlled_0.json"),
            _load_json(EXAMPLES / target_name),
            mapping["execution_map"],
            mapping["state_map"],
        )


def _retained_result():
    """Execute the retained-history comparison used by Table III's first row."""
    # runpy is required because ``tide-retained-history`` is not a Python
    # package name; executing compare.py also preserves its existing import and
    # input boundary exactly as retained in the artifact.
    with contextlib.redirect_stdout(io.StringIO()):
        namespace = runpy.run_path(str(RETAINED / "compare.py"))
    return namespace["result"]


class PaperEvaluationTableTests(unittest.TestCase):
    """Assert the complete machine-checkable result of every Table III row."""

    def assert_table_row(
        self,
        result,
        *,
        valid,
        delta_i,
        delta_o,
        outside,
        conforms,
        whole_equal,
    ):
        """Match one comparator report to the corresponding Table III cells."""
        # Every Table III case supplies well-formed one-to-one maps.
        self.assertTrue(result["assessable"])

        # Table III column: Valid K1/K2.
        self.assertEqual(
            (
                result["validity"]["K1"]["valid"],
                result["validity"]["K2"]["valid"],
            ),
            valid,
        )

        # Table III columns: Delta I -/+ and Delta O -/+.
        self.assertEqual(
            (
                len(result["deltas"]["I_minus"]),
                len(result["deltas"]["I_plus"]),
            ),
            delta_i,
        )
        self.assertEqual(
            (
                len(result["deltas"]["O_minus"]),
                len(result["deltas"]["O_plus"]),
            ),
            delta_o,
        )

        # Table III column: Outside I/O K1;K2.
        self.assertEqual(
            (
                (
                    len(result["outside"]["K1"]["I"]),
                    len(result["outside"]["K1"]["O"]),
                ),
                (
                    len(result["outside"]["K2"]["I"]),
                    len(result["outside"]["K2"]["O"]),
                ),
            ),
            outside,
        )

        # Table III columns: Conforms and Whole equal.
        self.assertEqual(result["conformant"], conforms)
        self.assertEqual(result["whole_kernel_equal"], whole_equal)

    # Table III row 1: retained Dagster/OpenLineage run records.
    def test_01_dagster_openlineage_run_records(self):
        self.assert_table_row(
            _retained_result(),
            valid=(True, True),
            delta_i=(0, 0),
            delta_o=(0, 0),
            outside=((0, 0), (0, 0)),
            conforms=True,
            whole_equal=True,
        )

    # Table III row 2: controlled structures, full carrier coverage.
    def test_02_controlled_structures_full_carrier_coverage(self):
        self.assert_table_row(
            _controlled_result("controlled_1.json"),
            valid=(True, True),
            delta_i=(0, 0),
            delta_o=(0, 0),
            outside=((0, 0), (0, 0)),
            conforms=True,
            whole_equal=True,
        )

    # Table III row 3: controlled structures, partial carrier coverage.
    def test_03_controlled_structures_partial_carrier_coverage(self):
        self.assert_table_row(
            _controlled_result("controlled_1.json", "selected_mapping.json"),
            valid=(True, True),
            delta_i=(0, 0),
            delta_o=(0, 0),
            outside=((3, 3), (3, 3)),
            conforms=True,
            whole_equal=False,
        )

    # Table III row 4: omitted mapped input.
    def test_04_omitted_mapped_input(self):
        self.assert_table_row(
            _controlled_result("missing_input.json"),
            valid=(True, True),
            delta_i=(1, 0),
            delta_o=(0, 0),
            outside=((0, 0), (0, 0)),
            conforms=False,
            whole_equal=False,
        )

    # Table III row 5: added mapped-scope input.
    def test_05_added_mapped_scope_input(self):
        self.assert_table_row(
            _controlled_result("extra_scoped_input.json"),
            valid=(True, True),
            delta_i=(0, 1),
            delta_o=(0, 0),
            outside=((0, 0), (0, 0)),
            conforms=False,
            whole_equal=False,
        )

    # Table III row 6: omitted mapped output.
    def test_06_omitted_mapped_output(self):
        self.assert_table_row(
            _controlled_result("missing_output.json"),
            valid=(True, False),
            delta_i=(0, 0),
            delta_o=(1, 0),
            outside=((0, 0), (0, 0)),
            conforms=False,
            whole_equal=False,
        )

    # Table III row 7: mapped output whose target identity is absent.
    def test_07_mapped_output_target_identity_absent(self):
        self.assert_table_row(
            _controlled_result(
                "controlled_1.json",
                "mapped_output_target_absent.json",
            ),
            valid=(True, True),
            delta_i=(0, 0),
            delta_o=(1, 0),
            outside=((0, 0), (0, 1)),
            conforms=False,
            whole_equal=False,
        )

    # Table III row 8: added mapped-scope output.
    def test_08_added_mapped_scope_output(self):
        self.assert_table_row(
            _controlled_result(
                "extra_scoped_output.json",
                "full_mapping_with_extra_target_state.json",
            ),
            valid=(True, True),
            delta_i=(0, 0),
            delta_o=(0, 1),
            outside=((0, 0), (0, 0)),
            conforms=False,
            whole_equal=False,
        )

    # Table III row 9: invalid branch outside the supplied map.
    def test_09_invalid_outside_branch(self):
        self.assert_table_row(
            _controlled_result("invalid_outside_branch.json"),
            valid=(True, False),
            delta_i=(0, 0),
            delta_o=(0, 0),
            outside=((0, 0), (1, 0)),
            conforms=True,
            whole_equal=False,
        )


# Section VII-D permits direct standard-library reproduction from artifact root.
if __name__ == "__main__":
    unittest.main(verbosity=2)
