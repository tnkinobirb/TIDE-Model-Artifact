"""Tiny unit suite for the TIDE comparator mechanics."""

import contextlib
import io
import json
import unittest
from pathlib import Path

try:  # Support both direct execution and package discovery.
    from .comparator import compare
except ImportError:
    from comparator import compare


K1 = {
    "E": ["p", "c"],
    "S": ["s"],
    "I": [["c", "s"]],
    "O": [["p", "s"]],
}
K2 = {
    "E": ["P", "C"],
    "S": ["S"],
    "I": [["C", "S"]],
    "O": [["P", "S"]],
}
E_MAP = {"p": "P", "c": "C"}
S_MAP = {"s": "S"}
EXAMPLES = Path(__file__).parent / "examples"


def load_example(name):
    """Load one retained JSON boundary fixture."""
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def run(k1=K1, k2=K2, e_map=E_MAP, s_map=S_MAP):
    """Call the comparator without its reporting-only console output."""
    with contextlib.redirect_stdout(io.StringIO()):
        return compare(k1, k2, e_map, s_map)


class ComparatorTests(unittest.TestCase):
    def test_complete_agreement(self):
        """Equations (1)-(25): the smallest complete positive comparison."""
        result = run()
        self.assertEqual(
            (
                result["assessable"],
                result["validity"]["K1"]["valid"],
                result["validity"]["K2"]["valid"],
                result["judgments"]["K1"]["direct_handoffs"],
                result["judgments"]["mapped_correspond"],
                result["conformant"],
                result["identity_coverage"],
                result["complete_agreement"],
            ),
            (True, True, True, [["p", "s", "c"]], True, True,
             {"K1": True, "K2": True}, True),
        )

    def test_scope(self):
        """Equations (7)-(16): unmapped identities and incidence stay outside."""
        k1 = {
            "E": K1["E"] + ["x", "q"],
            "S": K1["S"] + ["u"],
            "I": K1["I"] + [["x", "u"]],
            "O": K1["O"] + [["q", "u"]],
        }
        k2 = {
            "E": K2["E"] + ["X", "Q"],
            "S": K2["S"] + ["U"],
            "I": K2["I"] + [["X", "U"]],
            "O": K2["O"] + [["Q", "U"]],
        }
        result = run(k1, k2)
        self.assertTrue(result["conformant"])
        self.assertEqual(result["identity_coverage"], {"K1": False, "K2": False})
        self.assertEqual(
            result["outside_identities"],
            {
                "K1": {"Executions": ["q", "x"], "States": ["u"]},
                "K2": {"Executions": ["Q", "X"], "States": ["U"]},
            },
        )
        self.assertEqual(
            (result["outside"]["K1"], result["outside"]["K2"]),
            ({"I": [["x", "u"]], "O": [["q", "u"]]},
             {"I": [["X", "U"]], "O": [["Q", "U"]]}),
        )

    def test_missing_mapped_fact(self):
        """Equations (19) and (22): missing incidence is not identity absence."""
        result = run(k2={**K2, "O": []})
        self.assertTrue(result["assessable"])
        self.assertEqual(
            result["mapped_identities_absent"]["K2"]["Executions"],
            [],
        )
        self.assertEqual(result["deltas"]["O_minus"], [["P", "S"]])
        self.assertFalse(result["conformant"])

    def test_mapped_identity_absence_is_separate_from_missing_incidence(self):
        """Equations (11)-(12): map identities may be absent from a carrier."""
        result = run(k2={"E": ["C"], "S": ["S"], "I": [["C", "S"]], "O": []})
        self.assertTrue(result["assessable"])
        self.assertEqual(
            result["mapped_identities_absent"]["K2"]["Executions"],
            ["P"],
        )
        self.assertEqual(result["deltas"]["O_minus"], [["P", "S"]])
        self.assertFalse(result["conformant"])

    def test_validity(self):
        """Equations (4)-(5): validity is reported independently of equality."""
        cycle = {
            "E": ["a", "b"],
            "S": ["s0", "s1"],
            "I": [["a", "s1"], ["b", "s0"]],
            "O": [["a", "s0"], ["b", "s1"]],
        }
        validity = run(cycle, cycle, {"a": "a", "b": "b"},
                       {"s0": "s0", "s1": "s1"})["validity"]["K1"]
        self.assertEqual(
            (validity["unique_creation"], validity["acyclic_ancestry"]),
            (True, False),
        )

    def test_bad_inputs(self):
        """Equations (1) and (6): enforce the structure and map boundaries."""
        with self.assertRaises(ValueError):
            run(k1={"E": [], "S": [], "I": [], "O": [], "extra": []})
        with self.assertRaisesRegex(ValueError, "outside E"):
            run(k1={"E": [], "S": ["s"], "I": [["e", "s"]], "O": []})
        with self.assertRaisesRegex(ValueError, "outside S"):
            run(k1={"E": ["e"], "S": [], "I": [["e", "s"]], "O": []})
        result = run(e_map={"p": "P", "c": "P"})
        self.assertFalse(result["assessable"])
        self.assertIn("Execution map must be one-to-one", result["mapping_errors"])

    def test_explicit_carriers_preserve_empty_answers(self):
        """Proposition 1: represented identities retain determinate empty answers."""
        isolated = {"E": ["idle"], "S": [], "I": [], "O": []}
        result = run(
            isolated,
            {"E": ["IDLE"], "S": [], "I": [], "O": []},
            {"idle": "IDLE"},
            {},
        )
        self.assertEqual(result["validity"]["K1"]["valid"], True)
        self.assertEqual(result["judgments"]["K1"]["direct_handoffs"], [])
        self.assertTrue(result["complete_agreement"])

    def test_declared_producerless_state_is_present_and_invalid(self):
        """Equation (4): semantic validity ranges over every declared State."""
        producerless = {"E": [], "S": ["boundary"], "I": [], "O": []}
        result = run(producerless, producerless, {}, {"boundary": "boundary"})
        self.assertFalse(result["validity"]["K1"]["valid"])
        self.assertEqual(
            result["validity"]["K1"]["producer_count_errors"],
            {"boundary": 0},
        )
        self.assertTrue(result["conformant"])
        self.assertTrue(result["complete_agreement"])

    def test_complete_agreement_requires_exact_map_coverage(self):
        """Equation (23): a strict map superset is not complete coverage."""
        result = run(
            e_map={**E_MAP, "absent": "ABSENT"},
            s_map={**S_MAP, "absent_state": "ABSENT_STATE"},
        )
        self.assertTrue(result["conformant"])
        self.assertEqual(result["identity_coverage"], {"K1": False, "K2": False})
        self.assertFalse(result["complete_agreement"])

    def test_public_operation_and_smaller_source_coverage_boundary(self):
        """Equations (7)-(23): public import and one-sided exact coverage."""
        from tide_reference_comparator import compare as public_compare

        mapping = load_example("selected_mapping.json")
        with contextlib.redirect_stdout(io.StringIO()):
            result = public_compare(
                load_example("selected_source.json"),
                load_example("controlled_1.json"),
                mapping["execution_map"],
                mapping["state_map"],
            )

        self.assertIs(public_compare, compare)
        self.assertTrue(result["conformant"])
        self.assertEqual(result["identity_coverage"], {"K1": True, "K2": False})
        self.assertFalse(result["complete_agreement"])
        self.assertEqual(
            result["outside"]["K2"],
            {
                "I": [["mx2", "ma1"], ["mx3", "ma3"], ["mx5", "ma4"]],
                "O": [["mx0", "ma1"], ["mx2", "ma3"], ["mx5", "ma6"]],
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
