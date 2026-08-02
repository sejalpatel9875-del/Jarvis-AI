"""
tests/test_v6_0_commercial_release.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Comprehensive Unittest Suite for JARVIS Commercial SaaS Release (v6.0.0).
"""

import unittest
from commercial.subscriptions import subscription_manager, SubscriptionTier
from commercial.feature_flags import feature_flags
from commercial.backups import backup_manager
from commercial.admin_panel import admin_panel


class TestV60CommercialRelease(unittest.TestCase):
    def test_subscription_tiers_and_quota_enforcement(self):
        org_id = "org_free_test"

        # 1. Verify Free Tier default limits
        sub = subscription_manager.get_subscription(org_id)
        self.assertEqual(sub["tier"], SubscriptionTier.FREE)
        self.assertEqual(sub["limits"]["max_api_calls_per_day"], 100)

        # 2. Upgrade to PRO
        up_res = subscription_manager.upgrade_subscription(org_id, SubscriptionTier.PRO)
        self.assertTrue(up_res["success"])
        self.assertEqual(up_res["new_tier"], SubscriptionTier.PRO)
        self.assertEqual(up_res["limits"]["max_api_calls_per_day"], 10000)

        # 3. Test Usage Increment
        self.assertTrue(subscription_manager.increment_and_check_limit(org_id))

    def test_feature_flags_and_killswitches(self):
        org_id = "org_flag_test"

        # On Free tier, mcp_access should be False
        subscription_manager.upgrade_subscription(org_id, SubscriptionTier.FREE)
        self.assertFalse(feature_flags.is_feature_enabled("mcp_access", org_id))

        # On Enterprise tier, mcp_access should be True
        subscription_manager.upgrade_subscription(org_id, SubscriptionTier.ENTERPRISE)
        self.assertTrue(feature_flags.is_feature_enabled("mcp_access", org_id))

        # Test Global Killswitch override
        feature_flags.set_global_killswitch("mcp_access", False)
        self.assertFalse(feature_flags.is_feature_enabled("mcp_access", org_id))

        # Re-enable Global Killswitch
        feature_flags.set_global_killswitch("mcp_access", True)
        self.assertTrue(feature_flags.is_feature_enabled("mcp_access", org_id))

    def test_automated_backups_and_disaster_recovery(self):
        res = backup_manager.create_backup("FULL")
        self.assertTrue(res["success"])
        self.assertIn("backup_id", res["backup"])

        dr_status = backup_manager.get_disaster_recovery_status()
        self.assertEqual(dr_status["disaster_recovery_status"], "HEALTHY")
        self.assertGreaterEqual(dr_status["total_backups_count"], 1)

    def test_super_admin_panel(self):
        org_id = "org_admin_override"
        override_res = admin_panel.override_usage_limit(org_id, 50000)
        self.assertTrue(override_res["success"])
        self.assertEqual(override_res["new_daily_limit"], 50000)

        sus_res = admin_panel.suspend_organization(org_id, "Test Suspension")
        self.assertEqual(sus_res["status"], "SUSPENDED")

        react_res = admin_panel.reactivate_organization(org_id)
        self.assertEqual(react_res["status"], "ACTIVE")


if __name__ == "__main__":
    unittest.main()
