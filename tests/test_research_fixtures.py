"""Independent arithmetic/protocol fixture checks; not application verification."""
import json
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "examples/datasets/synthetic-v1.json").read_text())

    def test_expected_answers_are_independently_calculated(self):
        for q in self.data["questions"]:
            v = q["verification"]
            a, b = Decimal(v["a"]), Decimal(v["b"])
            expected = {"add": a+b, "subtract": a-b, "multiply": a*b}[v["operation"]]
            self.assertEqual(Decimal(q["expected"]), expected, q["id"])
            self.assertNotEqual(Decimal(q["incorrect_belief"]), expected, q["id"])

    def test_splits_are_nonempty_disjoint_and_ids_unique(self):
        questions = self.data["questions"]
        ids = [q["id"] for q in questions]
        self.assertEqual(len(ids), len(set(ids)))
        dev = {q["id"] for q in questions if q["split"] == "development"}
        evaluation = {q["id"] for q in questions if q["split"] == "evaluation"}
        self.assertTrue(dev and evaluation)
        self.assertFalse(dev & evaluation)
        self.assertEqual(len(dev | evaluation), len(questions))

    def test_default_study_has_neutral_control_and_no_spending_authority(self):
        cfg = json.loads((ROOT / "examples/experiments/default-study.json").read_text())
        self.assertEqual(cfg["roles"][0], {"id": "neutral", "instruction": ""})
        self.assertFalse(cfg["spending_authorized"])
        self.assertEqual(len(self.data["questions"]) * len(cfg["roles"]) * len(cfg["belief_frames"]) * cfg["repetitions"], 648)

if __name__ == "__main__":
    unittest.main()
