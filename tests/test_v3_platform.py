"""
Unit tests for J.A.R.V.I.S. v3.0 Enterprise AI Employee Platform features.
"""

import uuid
import unittest
from core.auth import auth_service
from services.voice_pipeline import voice_pipeline
from tools.registry import tool_registry

class TestV3Platform(unittest.TestCase):
    def test_user_authentication_flow(self):
        """Verify user registration and authentication flow."""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@futureai.io"
        reg_res = auth_service.register_user(unique_email, "Aryan", "secretpass123")
        self.assertTrue(reg_res["success"], f"Registration failed: {reg_res}")

        login_res = auth_service.login_user(unique_email, "secretpass123")
        self.assertTrue(login_res["success"], f"Login failed: {login_res}")
        self.assertIn("token", login_res)

    def test_login_wrong_password(self):
        """Verify login rejects wrong password."""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@futureai.io"
        auth_service.register_user(unique_email, "TestUser", "correctpass")
        login_res = auth_service.login_user(unique_email, "wrongpass")
        self.assertFalse(login_res["success"])

    def test_voice_pipeline_synthesis(self):
        """Verify VoicePipelineService speech synthesis."""
        res = voice_pipeline.synthesize_speech("Hello Boss!")
        self.assertEqual(res["status"], "success")

    def test_voice_pipeline_transcribe(self):
        """Verify VoicePipelineService STT transcription."""
        from unittest.mock import patch, MagicMock
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.json.return_value = {"text": "hello jarvis"}
            mock_post.return_value = mock_response
            
            text = voice_pipeline.transcribe_audio(b"fake_audio_bytes")
            self.assertEqual(text, "hello jarvis")

    def test_v3_real_world_tools_registration(self):
        """Verify GitHubTool, EmailTool, and FileTool execute properly."""
        gh_res = tool_registry.execute("github", action="create_issue", title="Fix Vision OCR")
        self.assertTrue(gh_res.success)
        self.assertIn("created GitHub issue", gh_res.result)

        em_res = tool_registry.execute("email", recipient="boss@futureai.io", subject="Sprint Status")
        self.assertTrue(em_res.success)
        self.assertIn("dispatched email to", em_res.result)

        file_res = tool_registry.execute("file_manager", action="list", path=".")
        self.assertTrue(file_res.success)

if __name__ == "__main__":
    unittest.main()
