# 🏢 Multi-Tenant Configuration Architecture (`tenants/`)

> **Architecture Rule:** All raw assets, tenant PDFs, and split JSON configurations live outside the core code repository.

---

## 📁 Multi-Tenant Directory Structure

```text
tenants/
├── ed_donner/
│   └── config/
│       ├── agent.json         # Agent settings, LLM parameters, & enabled_tools list
│       ├── brand.json         # Theme design tokens & accent colors
│       ├── chat.json          # Welcome message, role subtitle, & suggested questions
│       ├── seo.json           # Title tags, meta descriptions, & canonical URLs
│       ├── social.json        # Social media links (LinkedIn, Twitter, GitHub, YouTube)
│       └── voice.json         # Voice persona audio settings & TTS voice ID
└── tenant_starter/            # Starter template for new multi-tenant deployments
```

---

## 🔒 Golden Rule #7: ZERO Backend Client `if` Statements
- All tenant branding, prompts, tools, and social links are resolved dynamically by `TenantService` in [`backend/app/services/tenant_service.py`](file:///home/arun/projects/profile/backend/app/services/tenant_service.py).
- Python code contains ZERO `if client == "ed":` or `if tenant_id == "hitesh":` statements!
