import unittest
from backend.app.services.tenant_service import TenantService


class TestTenantService(unittest.TestCase):
    def setUp(self):
        self.service = TenantService()

    def test_load_ed_donner_tenant(self):
        config = self.service.load_tenant_config("ed_donner")
        self.assertEqual(config.tutor_id, "ed_donner")
        self.assertEqual(config.brand.name, "Ed Donner")
        self.assertIn("search_courses", config.agent.enabled_tools)

    def test_load_fallback_starter_tenant(self):
        config = self.service.load_tenant_config("non_existent_tenant_999")
        self.assertEqual(config.tutor_id, "tenant_starter")
        self.assertIsNotNone(config.brand.title)


if __name__ == "__main__":
    unittest.main()
