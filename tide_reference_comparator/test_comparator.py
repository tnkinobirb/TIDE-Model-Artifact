"""Tiny unit suite for the TIDE comparator mechanics."""

import contextlib
import io
import unittest

try:  # Support both direct execution and package discovery.
    from .comparator import compare
except ImportError:
    from comparator import compare


K1 = {"I": [["c", "s"]], "O": [["p", "s"]]}
K2 = {"I": [["C", "S"]], "O": [["P", "S"]]}
E_MAP = {"p": "P", "c": "C"}
S_MAP = {"s": "S"}


def run(k1=K1, k2=K2, e_map=E_MAP, s_map=S_MAP):
    """Call the comparator without its reporting-only console output."""
    with contextlib.redirect_stdout(io.StringIO()):
        return compare(k1, k2, e_map, s_map)


class ComparatorTests(unittest.TestCase):
    def test_equal_kernels(self):
        """Equations (4)-(21): the smallest complete positive comparison."""
        result = run()
        self.assertEqual(
            (
                result["assessable"],
                result["validity"]["K1"]["valid"],
                result["validity"]["K2"]["valid"],
                result["judgments"]["K1"]["direct_handoffs"],
                result["judgments"]["mapped_correspond"],
                result["conformant"],
                result["carrier_coverage"],
                result["whole_kernel_equal"],
            ),
            (True, True, True, [["p", "s", "c"]], True, True,
             {"K1": True, "K2": True}, True),
        )

    def test_scope(self):
        """Equations (9)-(14): unmapped incidence is only reported outside."""
        k1 = {"I": K1["I"] + [["x", "u"]], "O": K1["O"] + [["q", "u"]]}
        k2 = {"I": K2["I"] + [["X", "U"]], "O": K2["O"] + [["Q", "U"]]}
        result = run(k1, k2)
        self.assertTrue(result["conformant"])
        self.assertEqual(result["carrier_coverage"], {"K1": False, "K2": False})
        self.assertEqual(
            (result["outside"]["K1"], result["outside"]["K2"]),
            ({"I": [["x", "u"]], "O": [["q", "u"]]},
             {"I": [["X", "U"]], "O": [["Q", "U"]]}),
        )

    def test_missing_mapped_fact(self):
        """Equations (8), (16), and (18): absence is evidence, not map failure."""
        result = run(k2={"I": [["C", "S"]], "O": []})
        self.assertTrue(result["assessable"])
        self.assertEqual(result["mapped_identities_absent"]["K2"]["Executions"], ["P"])
        self.assertEqual(result["deltas"]["O_minus"], [["P", "S"]])
        self.assertFalse(result["conformant"])

    def test_validity(self):
        """Equations (6)-(7): validity is reported independently of equality."""
        cycle = {
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
        """Equation (1) and Equation (8): enforce only the import/map boundary."""
        with self.assertRaises(ValueError):
            run(k1={"I": [], "O": [], "extra": []})
        result = run(e_map={"p": "P", "c": "P"})
        self.assertFalse(result["assessable"])
        self.assertIn("Execution map must be one-to-one", result["mapping_errors"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
