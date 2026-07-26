import unittest
import uuid
from core.workspaces import workspace_manager
from core.rbac import rbac_service, Role
from memory.workspace_memory import workspace_memory
from services.api_keys import api_key_service
from services.audit_logger import audit_logger
from services.dashboard import ceo_dashboard
from services.notifications import notification_service

class TestV42SaaSCore(unittest.TestCase):
    def test_organization_and_workspace_creation(self):
        org = workspace_manager.create_organization(f"Org_{uuid.uuid4().hex[:6]}", "owner_1")
        self.assertTrue(org["success"])
        ws = workspace_manager.create_workspace(org["org"]["id"], "Sales Workspace", "Sales")
        self.assertTrue(ws["success"])

    def test_rbac_permissions(self):
        self.assertTrue(rbac_service.check_permission(Role.OWNER, "delete_workspace"))
        self.assertFalse(rbac_service.check_permission(Role.EMPLOYEE, "delete_workspace"))

    def test_workspace_memory_isolation(self):
        ws_id = f"ws_{uuid.uuid4().hex[:6]}"
        workspace_memory.save_fact(ws_id, "sales_target", "$1M")
        facts = workspace_memory.get_facts(ws_id)
        self.assertGreaterEqual(len(facts), 1)

    def test_api_key_generation_and_validation(self):
        key_res = api_key_service.generate_key("ws_test", "Default Key")
        self.assertTrue(key_res["success"])
        val_res = api_key_service.validate_key(key_res["raw_key"])
        self.assertTrue(val_res["valid"])

    def test_audit_logging(self):
        log_res = audit_logger.log_event("org_1", "ws_1", "actor_1", "USER_INVITED", "Invited user@test.com")
        self.assertTrue(log_res["success"])

    def test_ceo_dashboard_and_notifications(self):
        dash = ceo_dashboard.get_dashboard_summary()
        self.assertEqual(dash["system_status"], "HEALTHY")
        notif = notification_service.send_notification("u_1", "Test", "Message")
        self.assertTrue(notif["success"])

if __name__ == "__main__":
    unittest.main()
