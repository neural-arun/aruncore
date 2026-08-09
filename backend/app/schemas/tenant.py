from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BrandConfig(BaseModel):
    tutor_id: str = Field(..., description="Tenant ID matching directory name")
    name: str = Field("Arun Yadav", description="Tenant full name")
    title: str = Field("Arun's AI Assistant", description="Hero assistant title")
    role: str = Field("AI Systems Architect • Healthcare & Education", description="Hero role subtitle")
    subtitle: Optional[str] = None
    avatar_url: str = Field("/profile_photo.png", description="Avatar image URL")
    logo_url: str = Field("/logo.jpg", description="Brand logo URL")
    primary_color: str = Field("#6366f1", description="Primary brand hex color")
    accent_color: str = Field("#818cf8", description="Accent brand hex color")
    theme: str = Field("dark", description="Light or dark theme preference")
    cta_text: str = Field("Consult Arun", description="CTA button label")


class AgentConfig(BaseModel):
    tutor_id: str
    system_prompt: str = Field(..., description="Base system prompt")
    temperature: float = Field(0.3, ge=0.0, le=1.0)
    model: str = Field("gpt-4o", description="LLM model identifier")
    enabled_tools: List[str] = Field(default_factory=list, description="Array of enabled tool names")
    guardrails: List[str] = Field(default_factory=list, description="Safety guardrails")


class ChatConfig(BaseModel):
    tutor_id: str
    welcome_message: str = Field(..., description="Hero card welcome text")
    suggested_questions: List[str] = Field(default_factory=list, description="Chips suggested questions")


class VoiceConfig(BaseModel):
    tutor_id: str
    voice_id: str = Field("alloy", description="TTS voice identifier")
    model: str = Field("tts-1", description="TTS model")
    speed: float = Field(1.0, ge=0.25, le=4.0)


class SEOConfig(BaseModel):
    tutor_id: str
    meta_title: str
    meta_description: str
    keywords: List[str] = Field(default_factory=list)


class SocialConfig(BaseModel):
    tutor_id: str
    website: Optional[str] = None
    linkedin: Optional[str] = None
    udemy: Optional[str] = None
    github: Optional[str] = None
    twitter: Optional[str] = None


class TenantFullConfig(BaseModel):
    tutor_id: str
    brand: BrandConfig
    agent: AgentConfig
    chat: ChatConfig
    voice: VoiceConfig
    seo: SEOConfig
    social: SocialConfig

    def to_legacy_dict(self) -> Dict[str, Any]:
        """Maps split JSON configs back to existing frontend expected dictionary structure (100% backward compatible!)."""
        return {
            "tutor_id": self.tutor_id,
            "title": self.brand.title,
            "subtitle": self.brand.subtitle or self.brand.role,
            "role": self.brand.role,
            "name": self.brand.name,
            "avatar": self.brand.avatar_url,
            "logo": self.brand.logo_url,
            "welcome_message": self.chat.welcome_message,
            "suggested_questions": self.chat.suggested_questions,
            "cta_text": self.brand.cta_text,
            "primary_color": self.brand.primary_color,
            "accent_color": self.brand.accent_color,
            "system_prompt": self.agent.system_prompt,
            "enabled_tools": self.agent.enabled_tools,
            "frontend_ui_dictionary": {
                "header": {
                    "profile_name": self.brand.name,
                    "profile_badge": self.brand.role,
                    "cta_button": {
                        "text": self.brand.cta_text,
                    },
                },
                "sidebar": {
                    "profile_card": {
                        "name": self.brand.name,
                        "title": self.brand.role,
                        "sub_badge": f"{self.brand.name}'s AI Twin",
                    },
                    "contact_button": {
                        "title": self.brand.cta_text,
                        "subtitle": f"Connect directly with {self.brand.name}",
                    },
                },
                "chat_panel": {
                    "hero_card": {
                        "assistant_title": self.brand.title,
                        "role_subtitle": self.brand.role,
                        "welcome_paragraph": self.chat.welcome_message,
                        "cta_button_text": self.brand.cta_text,
                    },
                    "input_bar": {
                        "placeholder": f"Ask {self.brand.name}'s AI Assistant...",
                    },
                    "suggested_questions_section": {
                        "chips": [{"query": q} for q in self.chat.suggested_questions],
                    },
                }
            },
            "client_metadata": {
                "tutor_id": self.tutor_id,
                "avatar_url": self.brand.avatar_url,
                "logo_url": self.brand.logo_url,
            }
        }
