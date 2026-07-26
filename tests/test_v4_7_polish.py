"""
Unit tests for J.A.R.V.I.S. v4.7 Product Polish & Launch Readiness Platform.
"""

import unittest
import uuid
from services.global_search import global_search
from services.command_palette import command_palette
from services.onboarding_wizard import onboarding_wizard
from services.dashboard import ceo_dashboard

class TestV47ProductPolishPlatform(unittest.TestCase):
    def test_global_search(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        res = global_search.search_all(ws_id, "test")
        self.assertIn("total_matches", res)
        self.assertIn("leads", res)

    def test_command_palette(self):
        cmds = command_palette.get_available_commands("owner")
        self.assertGreaterEqual(len(cmds), 4)
        self.assertIn("shortcut", cmds[0])

    def test_onboarding_wizard(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        status = onboarding_wizard.get_onboarding_status(ws_id)
        self.assertFalse(status["is_finished"])
        comp = onboarding_wizard.complete_onboarding_step(ws_id, "workspace_setup")
        self.assertTrue(comp["success"])

    def test_ceo_dashboard_aggregated_metrics(self):
        dash = ceo_dashboard.get_dashboard_summary()
        self.assertEqual(dash["system_status"], "HEALTHY")
        self.assertIn("total_pipeline_value_usd", dash)

if __name__ == "__main__":
    unittest.main()
