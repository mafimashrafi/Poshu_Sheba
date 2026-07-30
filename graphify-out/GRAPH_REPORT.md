# Graph Report - Poshu_Sheba  (2026-07-29)

## Corpus Check
- 31 files · ~180,145 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 345 nodes · 404 edges · 36 communities (29 shown, 7 thin omitted)
- Extraction: 86% EXTRACTED · 13% INFERRED · 1% AMBIGUOUS · INFERRED: 53 edges (avg confidence: 0.83)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_AI Guidance Generation Core|AI Guidance Generation Core]]
- [[_COMMUNITY_Frontend API Client & Auth Dialog|Frontend API Client & Auth Dialog]]
- [[_COMMUNITY_Response Display & Severity Badges|Response Display & Severity Badges]]
- [[_COMMUNITY_PasswordSession Security Utils|Password/Session Security Utils]]
- [[_COMMUNITY_Backend Routers & Data Models|Backend Routers & Data Models]]
- [[_COMMUNITY_Pydantic RequestResponse Schemas|Pydantic Request/Response Schemas]]
- [[_COMMUNITY_Frontend API Client Module|Frontend API Client Module]]
- [[_COMMUNITY_AI + Audio Service Tests|AI + Audio Service Tests]]
- [[_COMMUNITY_Auth & Saved-Response Endpoints|Auth & Saved-Response Endpoints]]
- [[_COMMUNITY_MongoDB Data Access Layer|MongoDB Data Access Layer]]
- [[_COMMUNITY_GemmaGemini Multimodal Pipeline|Gemma/Gemini Multimodal Pipeline]]
- [[_COMMUNITY_Brand Assets & Mascot Images|Brand Assets & Mascot Images]]
- [[_COMMUNITY_Frontend Header Component|Frontend Header Component]]
- [[_COMMUNITY_MongoDB Connection Settings|MongoDB Connection Settings]]
- [[_COMMUNITY_MongoDB Deployment Config|MongoDB Deployment Config]]
- [[_COMMUNITY_UI Design Mockups|UI Design Mockups]]
- [[_COMMUNITY_Walking Cow Mascot Animation|Walking Cow Mascot Animation]]
- [[_COMMUNITY_User Registration Endpoint|User Registration Endpoint]]
- [[_COMMUNITY_Frontend ThemeColor Palette|Frontend Theme/Color Palette]]
- [[_COMMUNITY_Backend App Entrypoint|Backend App Entrypoint]]
- [[_COMMUNITY_Empty Init Module|Empty Init Module]]
- [[_COMMUNITY_Empty Init Module|Empty Init Module]]
- [[_COMMUNITY_Config Module|Config Module]]
- [[_COMMUNITY_vet.ai Visual Identity|vet.ai Visual Identity]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]

## God Nodes (most connected - your core abstractions)
1. `ApiError` - 15 edges
2. `SessionExpiredError` - 10 edges
3. `_detail()` - 10 edges
4. `Poshu Sheba AI — Frontend Documentation` - 10 edges
5. `render_main_content` - 10 edges
6. `_detail` - 10 edges
7. `Poshu Sheba AI (Project)` - 10 edges
8. `require_active_session dependency` - 9 edges
9. `Poshu Sheba AI FastAPI Service` - 9 edges
10. `Poshu Sheba AI — Backend Documentation` - 8 edges

## Surprising Connections (you probably didn't know these)
- `"Gemma 4 Integration" (README-claimed Grounded Generative AI)` --conceptually_related_to--> `Google GenAI Gemini API`  [AMBIGUOUS]
  README.md → BACKEND_DOCUMENTATION.md
- `AI-Is-Not-A-Vet Safety Reminder` --semantically_similar_to--> `Keyword-Matching Grounding Step`  [INFERRED] [semantically similar]
  FRONTEND_DOCUMENTATION.md → BACKEND_DOCUMENTATION.md
- `fastapi==0.139.2 (root requirements.txt)` --shares_data_with--> `Poshu Sheba AI FastAPI Service`  [INFERRED]
  requirements.txt → BACKEND_DOCUMENTATION.md
- `fastapi==0.139.2 (Backend/requirements.txt)` --shares_data_with--> `Poshu Sheba AI FastAPI Service`  [INFERRED]
  Backend/requirements.txt → BACKEND_DOCUMENTATION.md
- `google-genai==2.14.0 (root requirements.txt)` --shares_data_with--> `Google GenAI Gemini API`  [INFERRED]
  requirements.txt → BACKEND_DOCUMENTATION.md

## Hyperedges (group relationships)
- **Session-State Navigation Routing** — sidebar_render_sidebar, header_render_header, saved_panel_render_saved_panel, app_render_main_content [INFERRED 0.85]
- **Login/Registration Flow** — app_login_dialog, api_client_login, api_client_register, api_client_apierror [EXTRACTED 1.00]
- **AI Response Generation and Severity Flow** — app_render_main_content, api_client_generate, badges_classify_severity, badges_render_severity_badge [EXTRACTED 1.00]
- **Module-level Singleton Resource Initialization** — ai_client, audio_whisper_model, mongodb_lifespan [INFERRED 0.75]
- **Bearer Token Session Authentication Flow** — auth_login, responses_require_active_session, security_hash_session_token [INFERRED 0.85]
- **Multimodal Vet Guidance Generation Pipeline** — generate_generate, audio_transcribe_audio, ai_match_knowledge_base, ai_generate_guidance [INFERRED 0.85]
- **Grounded AI Response Generation Pipeline** — backend_documentation_generate_endpoint, backend_documentation_disease_knowledge_base, backend_documentation_gemini_api, backend_documentation_keyword_grounding [EXTRACTED 1.00]
- **Audio Transcription Pipeline** — backend_documentation_generate_endpoint, backend_documentation_ffmpeg, backend_documentation_whisper, backend_documentation_audio_service [EXTRACTED 1.00]
- **Account Authentication & Session Lifecycle** — backend_documentation_register_endpoint, backend_documentation_login_endpoint, backend_documentation_security_py, backend_documentation_sessions_collection [EXTRACTED 1.00]

## Communities (36 total, 7 thin omitted)

### Community 0 - "AI Guidance Generation Core"
Cohesion: 0.12
Nodes (30): _detail, ApiError, delete_account, generate, get_profile, get_saved_responses, login, register (+22 more)

### Community 1 - "Frontend API Client & Auth Dialog"
Cohesion: 0.1
Nodes (21): classify_severity(), get_severity_accent(), Severity/urgency badge shown next to AI answers.  Classification is a lightweigh, Return 'mild', 'monitor', or 'urgent' based on keywords in the response., Return the accent color for the given severity level (e.g. for a card border)., Return an inline-styled HTML chip for the given severity level., render_severity_badge(), _format_timestamp() (+13 more)

### Community 2 - "Response Display & Severity Badges"
Cohesion: 0.09
Nodes (21): hash_password(), hash_session_token(), Password and session-token hashing utilities., Return a salted scrypt password hash suitable for database storage., Hash a login password with the stored salt and compare safely., Store only a one-way hash of each random bearer token., verify_password(), delete_account() (+13 more)

### Community 3 - "Password/Session Security Utils"
Cohesion: 0.09
Nodes (22): API reference, code:json ({), code:block11 (------WebKitFormBoundaryXXXX), code:http (Authorization: Bearer <access_token>), code:json ({"response":"Text of the generated response"}), code:json ({"message":"Response saved successfully","response_id":"..."), code:http (Authorization: Bearer <access_token>), code:json ({) (+14 more)

### Community 4 - "Backend Routers & Data Models"
Cohesion: 0.09
Nodes (21): 🩺 পশু সেবা AI (Poshu Sheba AI), code:bash (# ক্লোন করুন), code:bash (cp .env.example .env), code:env (MONGODB_URI=mongodb+srv://your_username:your_password@cluste), code:bash (cd Backend), code:bash (cd Frontend), code:bash ($env:PYTHONIOENCODING="utf-8"; .\venv\Scripts\python Backend), code:bash (git checkout -b feature/your-feature-name) (+13 more)

### Community 5 - "Pydantic Request/Response Schemas"
Cohesion: 0.1
Nodes (22): Backend/core/config.py, Missing CORS Configuration, Poshu Sheba AI FastAPI Service, MongoDB Deployment (Backend), Backend/db/mongodb.py, fastapi==0.139.2 (Backend/requirements.txt), pymongo==4.15.5 (Backend/requirements.txt), Bengali-First Design Principle (+14 more)

### Community 6 - "Frontend API Client Module"
Cohesion: 0.25
Nodes (17): ApiError, delete_account(), _detail(), generate(), get_profile(), get_saved_responses(), login(), Thin wrapper around the Poshu Sheba AI FastAPI backend.  Every function raises A (+9 more)

### Community 7 - "AI + Audio Service Tests"
Cohesion: 0.13
Nodes (8): BaseModel, Pydantic request models for saving generated responses., SaveResponseRequest, FarmEntry, LoginRequest, ProfileUpdateRequest, Pydantic request models for user registration and login., UserRegisterRequest

### Community 8 - "Auth & Saved-Response Endpoints"
Cohesion: 0.14
Nodes (18): Backend/routers/auth.py, POST /login, Backend/main.py (FastAPI App Factory), POST /register, Backend/models/response.py (SaveResponseRequest), Backend/routers/responses.py, POST /save-response, MongoDB saved_responses Collection (+10 more)

### Community 9 - "MongoDB Data Access Layer"
Cohesion: 0.15
Nodes (12): Exception, generate(), Generate preliminary veterinary support guidance., generate_guidance(), match_knowledge_base(), AudioConversionError, _convert_to_wav(), Raised when ffmpeg fails to convert the uploaded audio to WAV. (+4 more)

### Community 10 - "Gemma/Gemini Multimodal Pipeline"
Cohesion: 0.12
Nodes (17): delete_account endpoint, get_profile endpoint, login endpoint, logout endpoint, update_profile endpoint, upload_profile_picture endpoint, get_user_saved_responses, save_user_response (+9 more)

### Community 11 - "Brand Assets & Mascot Images"
Cohesion: 0.17
Nodes (17): Backend/services/ai.py (Gemini client wrapper), animal_type Field Filter (cow/goat/chicken/duck), Backend/services/audio.py, Backend/data/disease_knowledge_base.json, FFmpeg Audio Conversion, Google GenAI Gemini API, POST /generate, Backend/routers/generate.py (+9 more)

### Community 12 - "Frontend Header Component"
Cohesion: 0.14
Nodes (12): get_user_saved_responses(), Store a generated response (and the prompt that produced it) under the     authe, Return a user's saved responses, most recently saved first., save_user_response(), delete_saved_response(), get_saved_responses(), Return the active session represented by a Bearer access token., Save a generated response for the phone number associated with the login. (+4 more)

### Community 13 - "MongoDB Connection Settings"
Cohesion: 0.13
Nodes (14): Application experience, Ask a question, code:text (Home), Content and safety principles, Create an account and sign in, Overview, Poshu Sheba AI — Frontend Documentation, Privacy and session behaviour (+6 more)

### Community 14 - "MongoDB Deployment Config"
Cohesion: 0.15
Nodes (13): genai.Client instance (Gemini/Gemma API client), generate_guidance (Gemma prompt + response), KNOWLEDGE_BASE curated disease dataset, match_knowledge_base (keyword/symptom matcher), _convert_to_wav (ffmpeg conversion), transcribe_audio (public audio pipeline entrypoint), _transcribe_wav (Whisper transcription), _whisper_model (faster-whisper 'small' CPU int8) (+5 more)

### Community 15 - "UI Design Mockups"
Cohesion: 0.18
Nodes (10): code:text (Client request), code:env (MONGODB_URI=<your MongoDB connection string>), code:bash (uvicorn main:app --reload), Deployment considerations, Errors and operational behaviour, Overview, Persistence and security, Poshu Sheba AI — Backend Documentation (+2 more)

### Community 16 - "Walking Cow Mascot Animation"
Cohesion: 0.6
Nodes (5): Cow Walk Animation Sprite Sheet (Small), Poshu Sheba AI (vet.ai) Web App UI Screenshot, Cow Walk Animation Doodle Sprite Sheet (Large), vet.ai Cow Head Mascot Icon, vet.ai Full Logo with Wordmark and Tagline

### Community 17 - "User Registration Endpoint"
Cohesion: 0.67
Nodes (3): _mask_phone(), Top header: brand lockup and account menu., render_header()

### Community 18 - "Frontend Theme/Color Palette"
Cohesion: 0.5
Nodes (4): MONGODB_DB setting, MONGODB_URI setting, FastAPI app instance, lifespan() FastAPI DB startup/shutdown

### Community 19 - "Backend App Entrypoint"
Cohesion: 0.83
Nodes (4): Poshu Sheba AI Home Screen (Bengali), AI Response Screen with Save Action, Login Required Modal (Saved Data Gate), Log In Screen Placeholder

### Community 21 - "Empty Init Module"
Cohesion: 0.67
Nodes (3): register_user endpoint, hash_password (scrypt), UserRegisterRequest model

## Ambiguous Edges - Review These
- `"Gemma 4 Integration" (README-claimed Grounded Generative AI)` → `Google GenAI Gemini API`  [AMBIGUOUS]
  README.md · relation: conceptually_related_to
- `AI Response Screen with Save Action` → `Login Required Modal (Saved Data Gate)`  [AMBIGUOUS]
  Design/2.png · relation: semantically_similar_to
- `Cow Walk Animation Sprite Sheet (Small)` → `Poshu Sheba AI (vet.ai) Web App UI Screenshot`  [AMBIGUOUS]
  logo/design.png · relation: conceptually_related_to

## Knowledge Gaps
- **129 isolated node(s):** `Single source of truth for the vet.ai color palette.  Every color used in the fr`, `Small inline SVG icon set (feather-style outline icons) used across the UI.  Kep`, `Return an inline <svg> string for the given icon name.`, `Thin wrapper around the Poshu Sheba AI FastAPI backend.  Every function raises A`, `Carries a Bangla message safe to show directly to the user.` (+124 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `"Gemma 4 Integration" (README-claimed Grounded Generative AI)` and `Google GenAI Gemini API`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `AI Response Screen with Save Action` and `Login Required Modal (Saved Data Gate)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `Cow Walk Animation Sprite Sheet (Small)` and `Poshu Sheba AI (vet.ai) Web App UI Screenshot`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Poshu Sheba AI FastAPI Service` connect `Pydantic Request/Response Schemas` to `Brand Assets & Mascot Images`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `Backend/main.py (FastAPI App Factory)` connect `Auth & Saved-Response Endpoints` to `Brand Assets & Mascot Images`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `Backend/routers/generate.py` connect `Brand Assets & Mascot Images` to `Auth & Saved-Response Endpoints`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `render_main_content` (e.g. with `render_saved_panel` and `render_sidebar`) actually correct?**
  _`render_main_content` has 3 INFERRED edges - model-reasoned connections that need verification._