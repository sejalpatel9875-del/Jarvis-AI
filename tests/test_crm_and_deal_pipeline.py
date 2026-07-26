"""
Unit tests for crm_engine and deal_pipeline services.
"""

import unittest
import uuid
from services.crm_engine import crm_engine, LeadStatus, CRMEngineService
from services.deal_pipeline import deal_pipeline, DealPipelineService


class TestCRMAndDealPipeline(unittest.TestCase):
    """Test suite for CRM Engine and Deal Pipeline services."""

    def setUp(self):
        self.workspace_id = f"ws_test_{uuid.uuid4().hex[:8]}"

    def test_crm_engine_flow(self):
        # 1. Create Lead
        res = crm_engine.create_lead(
            workspace_id=self.workspace_id,
            name="Alice Corp",
            email="alice@acme.com",
            company="Acme Corp",
            phone="1234567890",
            source="inbound",
        )
        self.assertTrue(res["success"])
        lead = res["lead"]
        lead_id = lead["id"]
        self.assertEqual(lead["workspace_id"], self.workspace_id)
        self.assertEqual(lead["name"], "Alice Corp")
        self.assertEqual(lead["status"], LeadStatus.NEW.value)

        # 2. List Leads
        leads = crm_engine.list_leads(workspace_id=self.workspace_id)
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["id"], lead_id)

        # 3. Update Status
        upd = crm_engine.update_lead_status(lead_id, LeadStatus.QUALIFIED)
        self.assertTrue(upd["success"])
        self.assertEqual(upd["status"], LeadStatus.QUALIFIED.value)

        # 4. List Leads with Status Filter
        qualified_leads = crm_engine.list_leads(workspace_id=self.workspace_id, status=LeadStatus.QUALIFIED)
        self.assertEqual(len(qualified_leads), 1)
        new_leads = crm_engine.list_leads(workspace_id=self.workspace_id, status=LeadStatus.NEW)
        self.assertEqual(len(new_leads), 0)

        # 5. Score Lead
        score_res = crm_engine.score_lead(lead_id)
        self.assertTrue(score_res["success"])
        self.assertGreaterEqual(score_res["score"], 0)
        self.assertLessEqual(score_res["score"], 100)

    def test_deal_pipeline_flow(self):
        # 1. Create Lead for deal
        lead_res = crm_engine.create_lead(
            workspace_id=self.workspace_id,
            name="Bob Enterprise",
            email="bob@enterprise.io",
            company="Enterprise LLC",
        )
        lead_id = lead_res["lead"]["id"]

        # 2. Create Deals
        deal1 = deal_pipeline.create_deal(
            lead_id=lead_id,
            workspace_id=self.workspace_id,
            title="Enterprise Subscription",
            value_usd=50000.0,
            stage="PROSPECTING",
        )
        self.assertTrue(deal1["success"])
        deal1_id = deal1["deal"]["id"]

        deal2 = deal_pipeline.create_deal(
            lead_id=lead_id,
            workspace_id=self.workspace_id,
            title="Consulting Addon",
            value_usd=10000.0,
            stage="QUALIFIED",
        )
        self.assertTrue(deal2["success"])

        # 3. Update Stage
        stage_upd = deal_pipeline.update_deal_stage(deal1_id, "PROPOSAL")
        self.assertTrue(stage_upd["success"])
        self.assertEqual(stage_upd["stage"], "PROPOSAL")

        # 4. Pipeline Summary
        summary = deal_pipeline.get_pipeline_summary(workspace_id=self.workspace_id)
        self.assertTrue(summary["success"])
        self.assertEqual(summary["total_deals"], 2)
        self.assertEqual(summary["total_pipeline_value_usd"], 60000.0)
        self.assertEqual(summary["avg_deal_size_usd"], 30000.0)
        self.assertEqual(summary["deals_by_stage"]["PROPOSAL"], 1)
        self.assertEqual(summary["deals_by_stage"]["QUALIFIED"], 1)


if __name__ == "__main__":
    unittest.main()
