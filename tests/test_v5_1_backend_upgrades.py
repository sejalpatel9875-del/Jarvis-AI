import unittest
from fastapi.testclient import TestClient
from api.main import app
from core.auth import auth_service
import uuid

class TestV51BackendUpgrades(unittest.TestCase):
    """Comprehensively validates backend architecture: JWT refresh, teams, rate limiters."""

    def setUp(self):
        self.client = TestClient(app)

    def test_health_and_status(self):
        # Health Endpoint
        res = self.client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")

        # Status Endpoint
        res_status = self.client.get("/api/v1/status")
        self.assertEqual(res_status.status_code, 200)
        self.assertEqual(res_status.json()["system_status"], "online")

    def test_token_refresh(self):
        # 1. Register and login
        email = f"test_{uuid.uuid4().hex[:6]}@example.com"
        password = "Password123"
        auth_service.register_user(email, "Tester", password)
        login_res = auth_service.login_user(email, password)
        self.assertTrue(login_res["success"])
        refresh_token = login_res["refresh_token"]

        # 2. Call refresh endpoint
        res = self.client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        self.assertEqual(res.status_code, 200)
        new_tokens = res.json()
        self.assertIn("access_token", new_tokens)
        self.assertIn("refresh_token", new_tokens)

        # 3. Call with invalid refresh token
        res_bad = self.client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid_refresh_jwt"})
        self.assertEqual(res_bad.status_code, 401)

    def test_teams_crud(self):
        ws_id = f"ws_test_{uuid.uuid4().hex[:6]}"
        team_name = "Core Backend Engineers"
        
        # 1. Create Team
        res_create = self.client.post("/api/v1/teams", json={"workspace_id": ws_id, "name": team_name})
        self.assertEqual(res_create.status_code, 200)
        data = res_create.json()
        self.assertTrue(data["success"])
        team_id = data["team"]["id"]

        # 2. List Teams
        res_list = self.client.get(f"/api/v1/teams?workspace_id={ws_id}")
        self.assertEqual(res_list.status_code, 200)
        teams = res_list.json()["teams"]
        self.assertTrue(any(t["id"] == team_id for t in teams))

        # 3. Add Team Member
        res_member = self.client.post("/api/v1/teams/members", json={
            "team_id": team_id,
            "user_id": "user_rahul",
            "role": "lead"
        })
        self.assertEqual(res_member.status_code, 200)
        mem_data = res_member.json()
        self.assertTrue(mem_data["success"])
        self.assertEqual(mem_data["member"]["role"], "lead")

    def test_login_rate_limiting(self):
        # Rapidly attempt authentication logins to trigger rate limiting
        # Limits are 5 requests per window_seconds (60)
        for _ in range(7):
            res = self.client.post("/auth/login", data={"username": "user", "password": "bad"})
        
        # Expect rate-limited response
        self.assertEqual(res.status_code, 429)
        self.assertIn("Too Many Requests", res.json()["error"])

if __name__ == "__main__":
    unittest.main()
