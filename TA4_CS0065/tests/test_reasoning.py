"""Behavior checks for inference, similarity, revision, retention, and CLI."""

from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

import ta4_reasoning as ta


class ReasoningTests(unittest.TestCase):
    def setUp(self):
        self.facts = deepcopy(ta.FACTS)
        self.cases = deepcopy(ta.CASE_BASE)

    def test_categories_cover_all_six_facts_once(self):
        keys = [key for group in ta.CATEGORIES.values() for key in group]
        self.assertEqual(len(ta.CATEGORIES), 3)
        self.assertEqual(len(keys), 6)
        self.assertEqual(set(keys), set(self.facts))

    def test_all_rules_evaluated_and_all_matching_actions_returned(self):
        trace, actions = ta.infer(self.facts)
        self.assertEqual(len(trace), 5)
        self.assertEqual([fired for _, fired in trace],
                         [True, True, True, False, True])
        self.assertEqual(len(actions), 4)
        self.assertEqual(self.facts, ta.FACTS)

    def test_no_match(self):
        self.facts.update(temperature=25, humidity=50,
                          is_raining=False, outdoor_activity=False)
        self.assertEqual(ta.infer(self.facts)[1], [])

    def test_rule_boundaries(self):
        self.facts.update(temperature=30, humidity=80, wind_speed=30)
        self.assertIsNone(ta.rule_hot(self.facts))
        self.assertIsNone(ta.rule_humid_heat(self.facts))
        self.assertIsNotNone(ta.rule_wind(self.facts))
        self.facts["temperature"] = 30.1
        self.assertIsNotNone(ta.rule_humid_heat(self.facts))

    def test_exact_match_and_boolean_mismatch(self):
        self.assertEqual(ta.similarity(self.facts, self.facts), 1.0)
        other = deepcopy(self.facts)
        other["is_daytime"] = False
        self.assertAlmostEqual(ta.similarity(self.facts, other), 5 / 6)

    def test_numeric_partial_credit_and_clamping(self):
        other = deepcopy(self.facts)
        other["temperature"] = 22
        self.assertAlmostEqual(ta.similarity(self.facts, other), 5.8 / 6)
        other["temperature"] = -20
        self.assertAlmostEqual(ta.similarity(self.facts, other), 5 / 6)

    def test_retrieval_scores_and_nearest_case(self):
        best, scores = ta.retrieve(self.facts, self.cases)
        self.assertEqual(best, 0)
        self.assertAlmostEqual(scores[0], 0.985)
        self.assertGreater(scores[0], scores[1])
        self.assertGreater(scores[1], scores[2])
        self.assertEqual(len(self.cases), 3)

    def test_tie_chooses_earlier_case(self):
        self.assertEqual(ta.retrieve(self.facts, [self.cases[0]] * 2)[0], 0)

    def test_empty_case_base(self):
        with self.assertRaises(ValueError):
            ta.retrieve(self.facts, [])

    def test_reuse_and_manual_or_unchanged_revision(self):
        proposal = ta.reuse(self.cases[0])
        self.assertEqual(proposal, self.cases[0]["solution"])
        for replacement in (None, "", "  "):
            self.assertEqual(ta.revise(proposal, replacement), proposal)
        self.assertEqual(ta.revise(proposal, "  Use an indoor venue.  "),
                         "Use an indoor venue.")

    def test_retention_stores_copy_and_revised_solution(self):
        ta.retain(self.facts, "Use an indoor venue.", self.cases)
        self.facts["temperature"] = 1
        self.assertEqual(len(self.cases), 4)
        self.assertEqual(self.cases[-1]["problem"]["temperature"], 32)
        self.assertEqual(self.cases[-1]["solution"], "Use an indoor venue.")
        self.assertEqual(ta.retrieve(ta.FACTS, self.cases)[0], 3)

    def test_invalid_facts(self):
        bad_values = {"humidity": (-1, 101, True, float("nan")),
                      "temperature": ("32", float("inf")),
                      "is_raining": (1, "true")}
        for key, values in bad_values.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    bad = {**self.facts, key: value}
                    with self.assertRaises(ValueError):
                        ta.validate_facts(bad)
        with self.assertRaises(ValueError):
            ta.validate_facts({})

    def test_blank_solution_not_retained(self):
        with self.assertRaises(ValueError):
            ta.retain(self.facts, "   ", self.cases)
        self.assertEqual(len(self.cases), 3)

    def test_cli_revision_and_case_export(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "cases.json"
            output = StringIO()
            with redirect_stdout(output):
                result = ta.main(["--mode", "cbr", "--revision", "Stay indoors.",
                                  "--save-cases", str(target)])
            saved = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(result, 0)
            self.assertEqual(len(saved), 4)
            self.assertEqual(saved[-1]["solution"], "Stay indoors.")
            self.assertIn("manually revised", output.getvalue())

    def test_cli_invalid_input_exits_with_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "bad.json"
            target.write_text('{"temperature": 32}', encoding="utf-8")
            output = StringIO()
            with redirect_stderr(output), self.assertRaises(SystemExit) as error:
                ta.main(["--facts", str(target)])
            self.assertEqual(error.exception.code, 2)
            self.assertIn("exactly the six sample keys", output.getvalue())


if __name__ == "__main__":
    unittest.main()
