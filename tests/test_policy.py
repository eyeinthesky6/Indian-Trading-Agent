import json
import unittest
from pathlib import Path

from ita.policy import DEFAULT_LEVEL1_POLICY, Level1Policy, load_level1_policy


ROOT = Path(__file__).resolve().parents[1]


class Level1PolicyTests(unittest.TestCase):
    def test_repo_default_policy_matches_embedded_default(self):
        path = ROOT / "policies" / "level1-conservative.json"
        loaded = load_level1_policy(path)
        self.assertEqual(loaded.fingerprint, DEFAULT_LEVEL1_POLICY.fingerprint)
        self.assertEqual(loaded.policy_id, DEFAULT_LEVEL1_POLICY.policy_id)

    def test_unknown_policy_field_is_rejected(self):
        with self.assertRaises(ValueError):
            Level1Policy.from_dict({"name": "x", "version": "1", "typo_threshold": 3})

    def test_policy_fingerprint_changes_when_rule_changes(self):
        stricter = Level1Policy.from_dict({
            "name": "strict-volume",
            "version": "1",
            "min_volume_ratio": 2.0,
        })
        self.assertNotEqual(stricter.fingerprint, DEFAULT_LEVEL1_POLICY.fingerprint)
        self.assertNotEqual(stricter.policy_id, DEFAULT_LEVEL1_POLICY.policy_id)

    def test_policy_dict_is_json_serializable(self):
        payload = DEFAULT_LEVEL1_POLICY.to_dict()
        self.assertIsInstance(json.dumps(payload), str)
        self.assertEqual(payload["target_r_multiples"], [2.0, 3.0])


if __name__ == "__main__":
    unittest.main()
