"""
tests/test_v5_8_enterprise_dashboard.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Comprehensive Unittest Suite for JARVIS Enterprise Dashboard (v5.8.0).
"""

import unittest
from services.enterprise_dashboard import enterprise_dashboard


class TestV58EnterpriseDashboard(unittest.TestCase):
    def test_full_telemetry_widget_payload(self):
        telemetry = enterprise_dashboard.get_full_telemetry("default")
        self.assertIn("widgets", telemetry)
        widgets = telemetry["widgets"]

        # Verify all 11 core widgets are present in the payload
        self.assertIn("ai_usage", widgets)
        self.assertIn("automation_status", widgets)
        self.assertIn("task_queue", widgets)
        self.assertIn("notifications", widgets)
        self.assertIn("knowledge_base", widgets)
        self.assertIn("memory_stats", widgets)
        self.assertIn("performance_metrics", widgets)
        self.assertIn("api_health", widgets)
        self.assertIn("user_activity", widgets)
        self.assertIn("workflow_analytics", widgets)
        self.assertIn("revenue_dashboard", widgets)

    def test_report_export_formats(self):
        # 1. Markdown Export
        md_report = enterprise_dashboard.export_report("markdown", "default")
        self.assertIn("Executive Report", md_report)
        self.assertIn("System Health", md_report)

        # 2. CSV Export
        csv_report = enterprise_dashboard.export_report("csv", "default")
        self.assertIn("Metric,Value", csv_report)

        # 3. JSON Export
        json_report = enterprise_dashboard.export_report("json", "default")
        self.assertIn("widgets", json_report)


if __name__ == "__main__":
    unittest.main()
