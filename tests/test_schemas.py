import unittest
from backend.app.schemas.tenant import (
    BrandConfig, AgentConfig, ChatConfig, VoiceConfig, SEOConfig, SocialConfig, TenantFullConfig
)
from backend.app.schemas.chat import ChatRequest, ChatHistoryResponse


class TestPydanticSchemas(unittest.TestCase):
    def test_brand_config_defaults(self):
        brand = BrandConfig(tutor_id="ed_donner")
        self.assertEqual(brand.tutor_id, "ed_donner")
        self.assertEqual(brand.primary_color, "#6366f1")

    def test_tenant_full_config_legacy_dict(self):
        full = TenantFullConfig(
            tutor_id="ed_donner",
            brand=BrandConfig(tutor_id="ed_donner", name="Ed Donner", title="Ed Donner", role="AI Expert"),
            agent=AgentConfig(tutor_id="ed_donner", system_prompt="You are Ed", enabled_tools=["search_courses"]),
            chat=ChatConfig(tutor_id="ed_donner", welcome_message="Hi Ed!", suggested_questions=["Q1"]),
            voice=VoiceConfig(tutor_id="ed_donner"),
            seo=SEOConfig(tutor_id="ed_donner", meta_title="Ed", meta_description="Ed AI"),
            social=SocialConfig(tutor_id="ed_donner", website="https://eddonner.com")
        )
        legacy = full.to_legacy_dict()
        self.assertEqual(legacy["tutor_id"], "ed_donner")
        self.assertEqual(legacy["title"], "Ed Donner")
        self.assertEqual(legacy["welcome_message"], "Hi Ed!")
        self.assertIn("search_courses", legacy["enabled_tools"])

    def test_chat_request_schema(self):
        req = ChatRequest(message="Hello AI", session_id="sess_123")
        self.assertEqual(req.message, "Hello AI")
        self.assertEqual(req.session_id, "sess_123")


if __name__ == "__main__":
    unittest.main()
