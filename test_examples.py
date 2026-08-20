"""Regression tests for every evaluation row in Table V of the TIDE paper.

The retained-record test executes ``tide-retained-history/compare.py``.
The controlled tests call the paper's single public comparator operation.
Every assertion corresponds to a result column displayed in Table V; this
file introduces no additional comparison rule.
"""

# Table V is reproduced with the standard-library unittest framework.
import contextlib
import csv
import io
import json
import runpy
import unittest
from pathlib import Path

from tide_reference_comparator.comparator import compare

# Retained native records and controlled fixtures are stored together.
ROOT = Path(__file__).resolve().parent
RETAINED = ROOT / "tide-retained-history"
EXAMPLES = ROOT / "tide_reference_comparator" / "examples"
AUDIT = ROOT / "question-audit"
PAPER = ROOT / "paper" / "TIDE-Paper.tex"

def _load_json(path):
    """Load one retained JSON input used by a Table V comparison."""
    return json.loads(path.read_text(encoding="utf-8"))


def _controlled_result(target_name, mapping_name="full_mapping.json"):
    """Run one controlled Table V fixture through the paper comparator."""
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
    """Execute the retained-history comparison used by Table V's first row."""
    # runpy is required because ``tide-retained-history`` is not a Python
    # package name; executing compare.py also preserves its existing import and
    # input boundary exactly as retained in the artifact.
    with contextlib.redirect_stdout(io.StringIO()):
        namespace = runpy.run_path(str(RETAINED / "compare.py"))
    return namespace["result"]


class PaperEvaluationTableTests(unittest.TestCase):
    """Assert the complete machine-checkable result of every Table V row."""

    def assert_table_row(
        self,
        result,
        *,
        valid,
        delta_i,
        delta_o,
        outside,
        absent,
        conforms,
        complete_agreement,
    ):
        """Match one comparator report to the corresponding Table V cells."""
        # Every Table V case supplies well-formed one-to-one maps.
        self.assertTrue(result["assessable"])

        # Table V column: Semantic validity K1/K2.
        self.assertEqual(
            (
                result["validity"]["K1"]["valid"],
                result["validity"]["K2"]["valid"],
            ),
            valid,
        )

        # Table V columns: Delta I -/+ and Delta O -/+.
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

        # Table V column: Outside I/O K1;K2.
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

        # Table V column: Absent E/S K1;K2.
        self.assertEqual(
            (
                (
                    len(result["mapped_identities_absent"]["K1"]["Executions"]),
                    len(result["mapped_identities_absent"]["K1"]["States"]),
                ),
                (
                    len(result["mapped_identities_absent"]["K2"]["Executions"]),
                    len(result["mapped_identities_absent"]["K2"]["States"]),
                ),
            ),
            absent,
        )

        # Table V columns: Conforms and Complete agreement.
        self.assertEqual(result["conformant"], conforms)
        self.assertEqual(result["complete_agreement"], complete_agreement)

    # Table V row 1: retained Dagster/OpenLineage run records.
    def test_01_dagster_openlineage_run_records(self):
        self.assert_table_row(
            _retained_result(),
            valid=(True, True),
            delta_i=(0, 0),
            delta_o=(0, 0),
            outside=((0, 0), (0, 0)),
            absent=((0, 0), (0, 0)),
            conforms=True,
            complete_agreement=True,
        )

    # Table V row 2: controlled structures, full identity coverage.
    def test_02_controlled_structures_full_identity_coverage(self):
        self.assert_table_row(
            _controlled_result("controlled_1.json"),
            valid=(True, True),
            delta_i=(0, 0),
            delta_o=(0, 0),
            outside=((0, 0), (0, 0)),
            absent=((0, 0), (0, 0)),
            conforms=True,
            complete_agreement=True,
        )

    # Table V row 3: controlled structures, partial identity coverage.
    def test_03_controlled_structures_partial_identity_coverage(self):
        self.assert_table_row(
            _controlled_result("controlled_1.json", "selected_mapping.json"),
            valid=(True, True),
            delta_i=(0, 0),
            delta_o=(0, 0),
            outside=((3, 3), (3, 3)),
            absent=((0, 0), (0, 0)),
            conforms=True,
            complete_agreement=False,
        )

    # Table V row 4: omitted mapped input.
    def test_04_omitted_mapped_input(self):
        self.assert_table_row(
            _controlled_result("missing_input.json"),
            valid=(True, True),
            delta_i=(1, 0),
            delta_o=(0, 0),
            outside=((0, 0), (0, 0)),
            absent=((0, 0), (0, 0)),
            conforms=False,
            complete_agreement=False,
        )

    # Table V row 5: added mapped-scope input.
    def test_05_added_mapped_scope_input(self):
        self.assert_table_row(
            _controlled_result("extra_scoped_input.json"),
            valid=(True, True),
            delta_i=(0, 1),
            delta_o=(0, 0),
            outside=((0, 0), (0, 0)),
            absent=((0, 0), (0, 0)),
            conforms=False,
            complete_agreement=False,
        )

    # Table V row 6: omitted mapped output.
    def test_06_omitted_mapped_output(self):
        self.assert_table_row(
            _controlled_result("missing_output.json"),
            valid=(True, False),
            delta_i=(0, 0),
            delta_o=(1, 0),
            outside=((0, 0), (0, 0)),
            absent=((0, 0), (0, 0)),
            conforms=False,
            complete_agreement=False,
        )

    # Table V row 7: mapped output whose target identity is absent.
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
            absent=((0, 0), (0, 1)),
            conforms=False,
            complete_agreement=False,
        )

    # Table V row 8: added mapped-scope output.
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
            absent=((0, 1), (0, 0)),
            conforms=False,
            complete_agreement=False,
        )

    # Table V row 9: invalid branch outside the supplied map.
    def test_09_invalid_outside_branch(self):
        self.assert_table_row(
            _controlled_result("invalid_outside_branch.json"),
            valid=(True, False),
            delta_i=(0, 0),
            delta_o=(0, 0),
            outside=((0, 0), (1, 0)),
            absent=((0, 0), (0, 0)),
            conforms=True,
            complete_agreement=False,
        )


class PaperAuditWordingTests(unittest.TestCase):
    """Keep the four normalized audit answers identical to the paper."""

    def test_producer_consumer_answer_wording_matches_paper(self):
        expected = {
            "PC1": "Which process occurrence produced a selected data item?",
            "PC2": "Which process occurrences consumed a selected data item?",
            "PC3": "Which exact data items did a process occurrence consume?",
            "PC4": "Which exact data items did a process occurrence produce?",
        }
        with (AUDIT / "producer_consumer_normalisation.csv").open(
            newline="",
            encoding="utf-8",
        ) as stream:
            rows = list(csv.DictReader(stream))

        for form_id, wording in expected.items():
            observed = {
                row["Paper_Exact_Answer_Wording"]
                for row in rows
                if row["Form_ID"] == form_id
            }
            self.assertEqual(observed, {wording})

        paper = PAPER.read_text(encoding="utf-8")
        audit_readme = (AUDIT / "README.md").read_text(encoding="utf-8")
        for wording in expected.values():
            self.assertIn(wording, paper)
            self.assertIn(wording, audit_readme)


# Support direct standard-library reproduction from the artifact root.
if __name__ == "__main__":
    unittest.main(verbosity=2)
