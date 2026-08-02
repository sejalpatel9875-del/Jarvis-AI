"""
tests/test_v5_3_desktop_assistant.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Comprehensive Unittest Suite for JARVIS Desktop Productivity Assistant (v5.3.0).
"""

import unittest
import os
import tempfile
from core.desktop_permissions import desktop_permissions
from services.desktop_assistant import desktop_assistant
from services.audit_logger import audit_logger


class TestV53DesktopAssistant(unittest.TestCase):
    def test_permission_layer_safe_vs_destructive(self):
        safe_perm = desktop_permissions.evaluate_permission("create_folder")
        self.assertTrue(safe_perm["allowed"])
        self.assertFalse(safe_perm["requires_confirmation"])

        dest_perm = desktop_permissions.evaluate_permission("close_app", {"app_name": "notepad"})
        self.assertFalse(dest_perm["allowed"])
        self.assertTrue(dest_perm["requires_confirmation"])

        confirmed_perm = desktop_permissions.evaluate_permission(
            "close_app", {"app_name": "notepad"}, is_confirmed=True
        )
        self.assertTrue(confirmed_perm["allowed"])

    def test_file_operations_create_rename_move(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 1. Create Folder
            folder_path = os.path.join(tmp_dir, "test_subfolder")
            res_folder = desktop_assistant.execute_desktop_action(
                "create_folder", {"folder_path": folder_path}
            )
            self.assertTrue(res_folder["success"])
            self.assertTrue(os.path.exists(folder_path))

            # 2. Create Dummy File
            src_file = os.path.join(tmp_dir, "sample.txt")
            with open(src_file, "w") as f:
                f.write("Jarvis Desktop Test Data")

            # 3. Rename File
            renamed_file = os.path.join(tmp_dir, "renamed_sample.txt")
            res_rename = desktop_assistant.execute_desktop_action(
                "rename_file", {"old_path": src_file, "new_path": renamed_file}
            )
            self.assertTrue(res_rename["success"])
            self.assertTrue(os.path.exists(renamed_file))

            # 4. Move File
            dst_file = os.path.join(folder_path, "moved_sample.txt")
            res_move = desktop_assistant.execute_desktop_action(
                "move_file", {"src": renamed_file, "dst": dst_file}
            )
            self.assertTrue(res_move["success"])
            self.assertTrue(os.path.exists(dst_file))

    def test_search_files(self):
        res = desktop_assistant.execute_desktop_action(
            "search_files", {"query": "test", "root_dir": "."}
        )
        self.assertTrue(res["success"])
        self.assertIn("matches", res["result"])

    def test_clipboard_manager(self):
        res_set = desktop_assistant.execute_desktop_action(
            "clipboard", {"sub_action": "set", "text": "Jarvis Token 123"}
        )
        self.assertTrue(res_set["success"])
        res_get = desktop_assistant.execute_desktop_action("clipboard", {"sub_action": "get"})
        self.assertEqual(res_get["result"]["text"], "Jarvis Token 123")

    def test_volume_and_screenshot(self):
        res_vol = desktop_assistant.execute_desktop_action(
            "control_volume", {"sub_action": "up", "level": 70}
        )
        self.assertTrue(res_vol["success"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            shot_path = os.path.join(tmp_dir, "test_shot.png")
            res_shot = desktop_assistant.execute_desktop_action(
                "take_screenshot", {"output_path": shot_path}
            )
            self.assertTrue(res_shot["success"])
            self.assertTrue(os.path.exists(shot_path))

    def test_open_apps_and_launchers(self):
        res_browser = desktop_assistant.execute_desktop_action(
            "launch_browser", {"url": "https://example.com"}
        )
        self.assertTrue(res_browser["success"])

        res_vscode = desktop_assistant.execute_desktop_action(
            "open_vscode", {"workspace_path": "."}
        )
        self.assertTrue(res_vscode["success"])

        res_terminal = desktop_assistant.execute_desktop_action(
            "open_terminal", {"working_dir": "."}
        )
        self.assertTrue(res_terminal["success"])

    def test_destructive_close_app_flow(self):
        # Without confirmation -> REQUIRES_CONFIRMATION
        res_unconfirmed = desktop_assistant.execute_desktop_action(
            "close_app", {"app_name": "notepad"}
        )
        self.assertFalse(res_unconfirmed["success"])
        self.assertEqual(res_unconfirmed["status"], "REQUIRES_CONFIRMATION")

        # With confirmation -> COMPLETED
        res_confirmed = desktop_assistant.execute_desktop_action(
            "close_app", {"app_name": "notepad"}, is_confirmed=True
        )
        self.assertTrue(res_confirmed["success"])
        self.assertEqual(res_confirmed["status"], "COMPLETED")

    def test_audit_logs_recorded(self):
        logs = audit_logger.get_logs(limit=10)
        self.assertIsInstance(logs, list)


if __name__ == "__main__":
    unittest.main()
