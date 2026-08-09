# 🎓 ArunCore Enterprise Demo Dictionaries (`demos/`)

This directory contains the 238-key enterprise JSON schema dictionaries used to power multi-tenant AI course advisors and digital twins.

---

## 📁 File Inventory

1. **`ed_donner_enterprise_dictionary.json`**:
   - The gold standard enterprise demo dictionary for **Ed Donner** (AI Educator & Course Creator).
   - Contains full course catalog (Udemy AI Engineer Core Track, Agentic Track with MCP, Production MLOps Track), custom Deep Teal theme (`#0d9488`), bio, and system prompt.
   - Live URL: `http://localhost:3000/?tutor=ed_donner`

2. **`general.json`**:
   - The master 238-key JSON schema template used for onboarding new instructors or enterprise clients.

3. **`master_enterprise_dictionary.json`**:
   - Complete dictionary schema reference guide detailing all 238 key specifications.

---

## 🛠️ How to Onboard a New Client

1. Duplicate `demos/general.json` to `demos/<client_id>_enterprise_dictionary.json`.
2. Populate the client's brand colors, course catalog, bio, and custom system prompt.
3. Access the live advisor immediately at `http://localhost:3000/?tutor=<client_id>`. Zero backend code edits required!
