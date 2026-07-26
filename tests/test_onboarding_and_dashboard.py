"""
Unit tests for J.A.R.V.I.S. Onboarding Wizard and CEO Dashboard Services.
"""

import unittest
import uuid
import memory.database as db
from services.onboarding_wizard import onboarding_wizard, OnboardingWizardService
from services.dashboard import ceo_dashboard, CEODashboardService
from services.crm_engine import crm_engine
from services.deal_pipeline import deal_pipeline
from services.automation_engine import automation_engine, WorkflowTrigger, WorkflowAction
from services.activity_feed import activity_feed


class TestOnboardingWizardAndDashboard(unittest.TestCase):
    def test_onboarding_wizard_lifecycle(self):
        ws_id = f"ws_test_{uuid.uuid4().hex[:6]}"
        
        # Initial status
        status = onboarding_wizard.get_onboarding_status(ws_id)
        self.assertTrue(status["success"])
        self.assertEqual(status["workspace_id"], ws_id)
        self.assertEqual(status["current_step"], "workspace_setup")
        self.assertEqual(status["completed_steps"], [])
        self.assertFalse(status["is_finished"])

        # Complete step 1
        res1 = onboarding_wizard.complete_onboarding_step(ws_id, "workspace_setup")
        self.assertTrue(res1["success"])
        self.assertEqual(res1["current_step"], "team_invite")
        self.assertIn("workspace_setup", res1["completed_steps"])
        self.assertFalse(res1["is_finished"])

        # Complete step 2
        res2 = onboarding_wizard.complete_onboarding_step(ws_id, "team_invite")
        self.assertEqual(res2["current_step"], "ai_configuration")

        # Complete step 3
        res3 = onboarding_wizard.complete_onboarding_step(ws_id, "ai_configuration")
        self.assertEqual(res3["current_step"], "sample_data")

        # Complete step 4 (final step)
        res4 = onboarding_wizard.complete_onboarding_step(ws_id, "sample_data")
        self.assertEqual(res4["current_step"], "completed")
        self.assertTrue(res4["is_finished"])

        # Verify status retrieval reflects completed state
        final_status = onboarding_wizard.get_onboarding_status(ws_id)
        self.assertTrue(final_status["is_finished"])
        self.assertEqual(final_status["current_step"], "completed")

    def test_ceo_dashboard_summary_aggregation(self):
        ws_id = f"ws_dash_{uuid.uuid4().hex[:6]}"

        # Seed CRM lead
        crm_engine.create_lead(ws_id, "Alice Test", "alice@example.com", "Acme Inc")

        # Seed deal
        deal_pipeline.create_deal(1, ws_id, "Test Enterprise Deal", 25000.0)

        # Seed automation workflow
        automation_engine.create_workflow(
            ws_id, "Auto Report", WorkflowTrigger.DOCUMENT_UPLOADED, WorkflowAction.GENERATE_REPORT
        )

        # Seed activity feed item
        activity_feed.log_activity(ws_id, "AdminUser", "UPDATED_SETTINGS", "Updated workspace settings")

        summary = ceo_dashboard.get_dashboard_summary(workspace_id=ws_id)

        self.assertIn("total_organizations", summary)
        self.assertIn("total_workspaces", summary)
        self.assertIn("total_leads", summary)
        self.assertIn("total_pipeline_value_usd", summary)
        self.assertIn("active_workflows", summary)
        self.assertIn("pending_tasks", summary)
        self.assertIn("knowledge_files", summary)
        self.assertEqual(summary["system_status"], "HEALTHY")

        self.assertGreaterEqual(summary["total_leads"], 1)
        self.assertGreaterEqual(summary["total_pipeline_value_usd"], 25000.0)
        self.assertGreaterEqual(summary["active_workflows"], 1)


if __name__ == "__main__":
    unittest.main()
