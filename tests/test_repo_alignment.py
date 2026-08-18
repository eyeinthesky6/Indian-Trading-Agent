import json
import unittest
from pathlib import Path

from ita.contracts import validate_trade_packet


ROOT = Path(__file__).resolve().parents[1]


class RepoAlignmentTests(unittest.TestCase):
    def test_plugin_marketplace_alignment(self):
        marketplace = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        plugin = json.loads((ROOT / 'plugin/.claude-plugin/plugin.json').read_text())
        self.assertEqual(marketplace['plugins'][0]['name'], plugin['name'])
        self.assertEqual(plugin['name'], 'india-trader')
        self.assertTrue((ROOT / 'plugin/agents/india-trader.md').exists())

    def test_skill_names_match_directories(self):
        skills = list((ROOT / 'plugin/skills').glob('*/SKILL.md'))
        self.assertEqual(len(skills), 11)
        for path in skills:
            text = path.read_text(encoding='utf-8')
            self.assertIn(f'name: {path.parent.name}', text.split('---', 2)[1])

    def test_real_trade_packet_contract(self):
        packet = json.loads((ROOT / 'examples/hdfcbank_real_trade_watch_output_2026-08-10.json').read_text())
        self.assertTrue(validate_trade_packet(packet)['valid'])
        self.assertEqual(packet['status'], 'watch')
        self.assertFalse(packet['execution']['allowed'])


if __name__ == '__main__':
    unittest.main()
