"""
Unit tests for J.A.R.V.I.S. v4.5 Enterprise CRM & Lead Workspace Platform.
"""

import unittest
import uuid
from services.crm_engine import crm_engine, LeadStatus
from services.deal_pipeline import deal_pipeline
from services.lead_ai_assistant import lead_ai_assistant

class TestV45CRMPlatform(unittest.TestCase):
    def test_create_and_list_leads(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        res = crm_engine.create_lead(ws_id, "Jane Doe", "jane@acme.com", "Acme Corp")
        self.assertTrue(res["success"])
        leads = crm_engine.list_leads(ws_id)
        self.assertEqual(len(leads), 1)

    def test_lead_scoring_and_status_update(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        res = crm_engine.create_lead(ws_id, "Bob Smith", "bob@enterprise.com", "Enterprise AI")
        lead_id = res["lead"]["id"]
        score_res = crm_engine.score_lead(lead_id)
        self.assertGreaterEqual(score_res["score"], 50)
        up_res = crm_engine.update_lead_status(lead_id, LeadStatus.QUALIFIED)
        self.assertTrue(up_res["success"])

    def test_deal_pipeline_and_summary(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        d_res = deal_pipeline.create_deal(1, ws_id, "Enterprise License", 50000.0)
        self.assertTrue(d_res["success"])
        summary = deal_pipeline.get_pipeline_summary(ws_id)
        self.assertEqual(summary["total_deals"], 1)
        self.assertEqual(summary["total_pipeline_value_usd"], 50000.0)

    def test_ai_sales_copilot(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        l_res = crm_engine.create_lead(ws_id, "Alice Tech", "alice@tech.org")
        lead_id = l_res["lead"]["id"]
        
        summ = lead_ai_assistant.generate_lead_summary(lead_id)
        self.assertIn("executive_summary", summ)
        
        email = lead_ai_assistant.draft_followup_email(lead_id)
        self.assertIn("subject", email)
        self.assertIn("email_body", email)

        notes = lead_ai_assistant.generate_meeting_notes(lead_id, "Discussed API licensing and team onboarding.")
        self.assertIn("action_items", notes)

if __name__ == "__main__":
    unittest.main()
