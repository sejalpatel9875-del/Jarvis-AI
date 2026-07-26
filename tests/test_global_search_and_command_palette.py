"""
Unit tests for GlobalSearchEngine and CommandPaletteService.
"""

import unittest
import uuid
from services.global_search import global_search, GlobalSearchEngine
from services.command_palette import command_palette, CommandPaletteService
from services.crm_engine import crm_engine
from services.deal_pipeline import deal_pipeline
from services.automation_engine import automation_engine
from services.activity_feed import activity_feed


class TestGlobalSearchAndCommandPalette(unittest.TestCase):
    """Test suite for Global Search and Command Palette services."""

    def setUp(self):
        self.workspace_id = f"ws_test_{uuid.uuid4().hex[:8]}"

    def test_global_search_flow(self):
        # 1. Populate workspace items
        crm_engine.create_lead(
            workspace_id=self.workspace_id,
            name="Apex Cybernetics",
            email="contact@apexcyber.com",
            company="Apex Cybernetics"
        )
        deal_pipeline.create_deal(
            lead_id=1,
            workspace_id=self.workspace_id,
            title="Apex Enterprise Software Licensing",
            value_usd=75000.0
        )
        automation_engine.create_workflow(
            workspace_id=self.workspace_id,
            name="Apex Auto Onboarding",
            trigger_type="document_uploaded",
            action_type="send_email"
        )
        activity_feed.log_activity(
            workspace_id=self.workspace_id,
            actor_name="Apex System Agent",
            action="Apex Pipeline Initiated"
        )

        # 2. Search with empty query -> returns all items
        res_all = global_search.search_all(workspace_id=self.workspace_id, query="")
        self.assertEqual(res_all["workspace_id"], self.workspace_id)
        self.assertEqual(res_all["query"], "")
        self.assertGreaterEqual(len(res_all["leads"]), 1)
        self.assertGreaterEqual(len(res_all["deals"]), 1)
        self.assertGreaterEqual(len(res_all["workflows"]), 1)
        self.assertGreaterEqual(len(res_all["activity_feed"]), 1)
        self.assertEqual(
            res_all["total_matches"],
            len(res_all["leads"]) + len(res_all["deals"]) + len(res_all["workflows"]) + len(res_all["activity_feed"])
        )

        # 3. Search with specific keyword match ("Apex")
        res_apex = global_search.search_all(workspace_id=self.workspace_id, query="Apex")
        self.assertEqual(res_apex["query"], "Apex")
        self.assertGreaterEqual(res_apex["total_matches"], 4)
        self.assertTrue(any("Apex" in lead["name"] for lead in res_apex["leads"]))
        self.assertTrue(any("Apex" in deal["title"] for deal in res_apex["deals"]))
        self.assertTrue(any("Apex" in wf["name"] for wf in res_apex["workflows"]))
        self.assertTrue(any("Apex" in act["action"] for act in res_apex["activity_feed"]))

        # 4. Search with non-matching query ("NonExistentXYZ")
        res_none = global_search.search_all(workspace_id=self.workspace_id, query="NonExistentXYZ")
        self.assertEqual(res_none["total_matches"], 0)
        self.assertEqual(len(res_none["leads"]), 0)
        self.assertEqual(len(res_none["deals"]), 0)
        self.assertEqual(len(res_none["workflows"]), 0)
        self.assertEqual(len(res_none["activity_feed"]), 0)

    def test_command_palette_available_commands(self):
        # 1. Owner role -> all commands
        owner_cmds = command_palette.get_available_commands(role="owner")
        cmd_ids = [cmd["id"] for cmd in owner_cmds]
        self.assertIn("global_search", cmd_ids)
        self.assertIn("create_lead", cmd_ids)
        self.assertIn("upload_document", cmd_ids)
        self.assertIn("run_workflow", cmd_ids)
        self.assertIn("manage_api_keys", cmd_ids)

        # Verify command structure
        for cmd in owner_cmds:
            self.assertIn("id", cmd)
            self.assertIn("title", cmd)
            self.assertIn("shortcut", cmd)
            self.assertIn("category", cmd)
            self.assertIn("action", cmd)

        # 2. Viewer role -> restricted commands
        viewer_cmds = command_palette.get_available_commands(role="viewer")
        viewer_cmd_ids = [cmd["id"] for cmd in viewer_cmds]
        self.assertIn("global_search", viewer_cmd_ids)
        self.assertNotIn("create_lead", viewer_cmd_ids)
        self.assertNotIn("manage_api_keys", viewer_cmd_ids)

        # 3. Default role parameter (owner)
        default_cmds = command_palette.get_available_commands()
        self.assertEqual(len(default_cmds), len(owner_cmds))


if __name__ == "__main__":
    unittest.main()
