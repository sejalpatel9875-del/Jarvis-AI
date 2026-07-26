"""
Unit tests for LeadAIAssistantService.
"""

import unittest
from services.crm_engine import crm_engine
from services.lead_ai_assistant import LeadAIAssistantService, lead_ai_assistant


class TestLeadAIAssistantService(unittest.TestCase):
    """Test suite for LeadAIAssistantService."""

    def test_singleton_instance(self):
        """Verify lead_ai_assistant singleton instance exists."""
        self.assertIsInstance(lead_ai_assistant, LeadAIAssistantService)

    def test_generate_lead_summary_existing_lead(self):
        """Verify generate_lead_summary returns expected dict structure for an existing lead."""
        create_res = crm_engine.create_lead(
            workspace_id="test_ws_lead_ai",
            name="Alice Smith",
            email="alice@acmecorp.com",
            company="Acme Corp",
            phone="123-456-7890",
            source="inbound",
        )
        self.assertTrue(create_res["success"])
        lead_id = create_res["lead"]["id"]

        summary_res = lead_ai_assistant.generate_lead_summary(lead_id)
        self.assertIn("lead_id", summary_res)
        self.assertIn("executive_summary", summary_res)
        self.assertIn("company_profile", summary_res)
        self.assertIn("intent_signals", summary_res)

        self.assertEqual(summary_res["lead_id"], lead_id)
        self.assertIn("Alice Smith", summary_res["executive_summary"])
        self.assertIn("Acme Corp", summary_res["company_profile"])
        self.assertIsInstance(summary_res["intent_signals"], list)
        self.assertTrue(len(summary_res["intent_signals"]) > 0)

    def test_generate_lead_summary_nonexistent_lead(self):
        """Verify generate_lead_summary handles non-existent lead IDs gracefully."""
        res = lead_ai_assistant.generate_lead_summary("non_existent_lead_999")
        self.assertEqual(res["lead_id"], "non_existent_lead_999")
        self.assertIn("executive_summary", res)
        self.assertIn("company_profile", res)
        self.assertIn("intent_signals", res)
        self.assertIsInstance(res["intent_signals"], list)

    def test_draft_followup_email(self):
        """Verify draft_followup_email produces subject and email_body for various tones."""
        create_res = crm_engine.create_lead(
            workspace_id="test_ws_lead_ai",
            name="Bob Johnson",
            email="bob@techinnovations.io",
            company="Tech Innovations Inc",
        )
        self.assertTrue(create_res["success"])
        lead_id = create_res["lead"]["id"]

        for tone in ["professional", "casual", "urgent", "persuasive"]:
            email_res = lead_ai_assistant.draft_followup_email(lead_id, tone=tone)
            self.assertIn("subject", email_res)
            self.assertIn("email_body", email_res)
            self.assertTrue(len(email_res["subject"]) > 0)
            self.assertTrue(len(email_res["email_body"]) > 0)

    def test_generate_meeting_notes(self):
        """Verify generate_meeting_notes parses transcript into summary, action_items, key_decisions."""
        transcript = (
            "Alice: Let's discuss the product demo timeline for Acme Corp.\n"
            "Bob: We agreed to schedule the product demo for next Tuesday.\n"
            "Alice: Great. Action item: Bob will prepare the slide deck by Friday.\n"
            "Bob: Todo: Send calendar invitation to all stakeholders."
        )

        res = lead_ai_assistant.generate_meeting_notes("lead_123", transcript)
        self.assertIn("summary", res)
        self.assertIn("action_items", res)
        self.assertIn("key_decisions", res)

        self.assertIsInstance(res["action_items"], list)
        self.assertIsInstance(res["key_decisions"], list)
        self.assertTrue(len(res["action_items"]) > 0)
        self.assertTrue(len(res["key_decisions"]) > 0)


if __name__ == "__main__":
    unittest.main()
