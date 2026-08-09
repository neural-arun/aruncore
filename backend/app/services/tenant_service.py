import os
import json
from typing import Optional, Dict, Any
from backend.app.schemas.tenant import (
    BrandConfig, AgentConfig, ChatConfig, VoiceConfig, SEOConfig, SocialConfig, TenantFullConfig
)


class TenantService:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_dir = base_dir
        else:
            self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.tenants_dir = os.path.join(self.base_dir, "tenants")

    def get_tenant_path(self, tutor_id: str) -> str:
        clean_id = (tutor_id or "arun").strip().lower()
        path = os.path.join(self.tenants_dir, clean_id)
        if os.path.exists(path):
            return path
        return os.path.join(self.tenants_dir, "tenant_starter")

    def load_tenant_config(self, tutor_id: Optional[str] = None) -> TenantFullConfig:
        clean_id = (tutor_id or "arun").strip().lower()
        if clean_id in ("arun", "default", "none"):
            clean_id = "tenant_starter"

        tenant_path = self.get_tenant_path(clean_id)
        resolved_id = os.path.basename(tenant_path)
        config_dir = os.path.join(tenant_path, "config")

        # Load split JSON configs
        brand_data = self._read_json(os.path.join(config_dir, "brand.json"), {"tutor_id": resolved_id, "name": "Arun Yadav", "title": "Arun's AI Assistant", "role": "AI Systems Architect • Healthcare & Education", "avatar_url": "/profile_photo.png", "logo_url": "/logo.jpg", "primary_color": "#6366f1", "accent_color": "#818cf8", "theme": "dark", "cta_text": "Consult Arun"})
        agent_data = self._read_json(os.path.join(config_dir, "agent.json"), {"tutor_id": resolved_id, "system_prompt": "You are Arun's AI Assistant.", "temperature": 0.3, "model": "gpt-4o", "enabled_tools": ["search_courses", "book_calendar", "faq_lookup"], "guardrails": []})
        chat_data = self._read_json(os.path.join(config_dir, "chat.json"), {"tutor_id": resolved_id, "welcome_message": "Hi! I'm Arun's AI Assistant.", "suggested_questions": ["What projects has Arun built?", "How can I contact Arun?"]})
        voice_data = self._read_json(os.path.join(config_dir, "voice.json"), {"tutor_id": resolved_id, "voice_id": "alloy", "model": "tts-1", "speed": 1.0})
        seo_data = self._read_json(os.path.join(config_dir, "seo.json"), {"tutor_id": resolved_id, "meta_title": "Arun Core", "meta_description": "AI Platform", "keywords": []})
        social_data = self._read_json(os.path.join(config_dir, "social.json"), {"tutor_id": resolved_id, "website": "https://neuralarun.in"})

        brand_data["tutor_id"] = resolved_id
        agent_data["tutor_id"] = resolved_id
        chat_data["tutor_id"] = resolved_id
        voice_data["tutor_id"] = resolved_id
        seo_data["tutor_id"] = resolved_id
        social_data["tutor_id"] = resolved_id

        return TenantFullConfig(
            tutor_id=resolved_id,
            brand=BrandConfig(**brand_data),
            agent=AgentConfig(**agent_data),
            chat=ChatConfig(**chat_data),
            voice=VoiceConfig(**voice_data),
            seo=SEOConfig(**seo_data),
            social=SocialConfig(**social_data),
        )

    def _read_json(self, filepath: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[TENANT_SERVICE WARNING] Failed to parse {filepath}: {e}")
        return fallback


# Singleton instance helper
tenant_service = TenantService()
