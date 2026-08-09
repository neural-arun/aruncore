import unittest
import httpx
from backend.app.core.api import app


class TestAPIEndpoints(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test"
        )

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_health_endpoint(self):
        res = await self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "ok")

    async def test_config_endpoint_default(self):
        res = await self.client.get("/config")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("frontend_ui_dictionary", data)
        self.assertIn("client_metadata", data)

    async def test_config_endpoint_ed_donner(self):
        res = await self.client.get("/config?tutor=ed_donner")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("tutor_id"), "ed_donner")
        self.assertEqual(data.get("name"), "Ed Donner")

    async def test_chat_history_endpoint(self):
        res = await self.client.get("/chat/history?session_id=test_sess_001")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("session_id"), "test_sess_001")


if __name__ == "__main__":
    unittest.main()
