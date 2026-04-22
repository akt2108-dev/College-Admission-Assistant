# HBTU Counselling Assistant Chatbot - Project Report

## 1. Executive Summary

The HBTU Counselling Assistant Chatbot is a web-based admission guidance system for Harcourt Butler Technical University (HBTU), Kanpur. The project combines:

- Historical B.Tech ORCR data processing (2023-2025)
- Seat matrix lookup for 2025
- Rule-based intent routing for counselling support
- Multi-turn branch prediction workflow (rank, category, quota)
- An MBA admission knowledge module (2026-27)
- An LLM fallback layer for conversational handling
- Non-blocking user query logging in PostgreSQL (with intent + session tracking)
- Clickable, styled hyperlink rendering in chat responses
- Improved intent disambiguation to reduce false counselling triggers

After reviewing the full repository, this report documents the current implementation as it exists in code, including runtime behavior, architecture, strengths, and limitations.

---

## 2. Problem Statement

Students and parents often struggle to navigate admission counselling due to fragmented information across portals, brochures, and notices. This project addresses that problem by providing a single conversational interface for:

- Branch prediction using historical cutoffs
- Seat availability by branch and year
- Counselling process explanations (rounds, fee, documents, freeze/float/withdraw)
- MBA admission Q&A

---

## 3. Scope and Coverage

### In Scope

- HBTU admissions support via chat interface
- B.Tech branch prediction and seat queries
- B.Tech counselling guidance (brochure-based)
- MBA admission guidance module
- FastAPI backend + PostgreSQL integration
- Single-page frontend UI in plain HTML/CSS/JS

### Out of Scope

- Real-time integration with official counselling portal APIs
- Automated fee/date synchronization from official websites
- Native mobile apps
- User authentication and role-based access

---

## 4. Repository Review Summary

### Core Backend Files

- backend/main.py
  - Main FastAPI app
  - Intent routing
  - Prediction, seats, counselling, MBA, and AI fallback flows
  - Async /chat flow with background query logging
- backend/db.py
  - PostgreSQL connection pooling
  - Query helpers
  - Conversation memory persistence
  - Auto-created user_queries table + async logging helper
- backend/mba_knowledge.py
  - MBA knowledge base and keyword-intent detector
- backend/ai_brain.py
  - Groq LLM fallback (llama-3.3-70b-versatile)
  - Strict prompt governance for canonical HBTU links and administrative roles
- backend/utils.py
  - Category builder helper

### Frontend

- backend/frontend/index.html
  - Complete UI and client logic in one page
  - Rich cards, chips, typing indicator, streaming typewriter effect
  - Safe URL linkification with dedicated link styling
- backend/frontend/config.js
  - Runtime API base configuration
- backend/frontend/images/hbtumitr-logo.png
  - Branding asset

### Data Pipeline and Assets

- scrape_ORCR.py (Selenium scraper)
- clean_and_merge.py (Pandas cleaning/merging)
- hbtu_all_rounds_orcr_2023.csv
- hbtu_all_rounds_orcr_2024.csv
- hbtu_all_rounds_orcr_2025.csv
- hbtu_combined_cleaned.csv
- seat_matrix_2025_normalized.csv

---

## 5. Data Pipeline and Dataset Status

### Scraping

The scraper automates the admissions.nic.in ORCR report page using Selenium, iterates through rounds, paginates via "Next", and exports a yearly CSV.

### Cleaning and Merge

The cleaning script:

- Standardizes columns
- Converts opening/closing ranks to numeric
- Drops rows with missing closing rank
- Adds year labels
- Produces one combined output CSV

### Reviewed Local Data (Current Workspace)

- Combined ORCR rows (hbtu_combined_cleaned.csv): 2021
- Seat matrix rows (seat_matrix_2025_normalized.csv): 374
- ORCR year coverage: 2023, 2024, 2025

Note: Raw ORCR branch naming is broader and inconsistent; the app resolves user queries through canonical branch aliases in backend logic.

---

## 6. System Architecture

### 6.1 Backend API Layer (FastAPI)

Implemented endpoints:

- GET /health
  - Verifies DB connectivity (SELECT 1)
  - Returns ok or degraded
- POST /predict
  - Direct prediction endpoint
- GET /seats
  - Direct seat lookup endpoint
- POST /chat
  - Primary conversational endpoint for UI
  - Accepts user_id, user_message, and optional session_id

### 6.2 Intent Routing Strategy

The conversational flow in main.py uses weighted keyword scoring for B.Tech intents:

- predict
- seats
- fees
- counselling_info

Additional layers:

- MBA intent detection runs early via detect_mba_intent
- AI fallback (ai_brain_response) handles unknown or ambiguous queries
- Token-safe short-keyword matching in intent scoring avoids false positives
  (example: "st" no longer matches inside "hostels")

### 6.3 Branch Prediction Logic

Prediction is SQL-driven over historical cutoffs data:

- Computes success per branch per year where closing_rank >= user_rank
- Aggregates success count across available years
- Converts to probability bands:
  - Very High (>=80%)
  - High (>=60%)
  - Moderate (>=40%)
  - Low (>=20%)
  - Very Low (<20%)

### 6.4 Seat Lookup Logic

Seat query (run_seat_lookup) reads from seats table by canonical branch and year, then returns:

- Total seats
- Quota-wise distribution
- Detailed rows

### 6.5 Memory and Resilience

Conversation memory design:

- Primary persistence in PostgreSQL (conversation_memory table)
- Auto-creation of memory table if missing
- In-process fallback store when DB memory operations fail
- Retry window for DB memory operations controlled by env config

This is a practical reliability feature: chat state can continue even when memory writes to DB are temporarily unavailable.

### 6.6 User Query Logging and Observability

The chatbot now logs user messages into PostgreSQL using a dedicated table:

- Table: user_queries
- Columns: id, user_id, message, detected_intent, session_id, created_at
- Table creation is automatic at runtime (CREATE TABLE IF NOT EXISTS)

Logging behavior:

- /chat resolves intent first, then schedules logging in the background
- Logging is non-blocking (chat response does not wait for DB insert)
- Failures are isolated (logging errors do not crash or block chat flow)

---

## 7. MBA Module (New Functional Area)

The codebase now includes a dedicated MBA admission assistant path:

- Knowledge base in backend/mba_knowledge.py
- Keyword intents for eligibility, registration, fees, rounds, seats, reservation, documents, withdrawal, medical, schedule
- Returns stream-type responses with MBA-specific action chips

This is a major expansion beyond only B.Tech counselling.

---

## 8. AI Fallback Layer

backend/ai_brain.py integrates Groq chat completions with a constrained system prompt:

- Focused domain: HBTU admissions and counselling
- Refuses out-of-scope content
- Advises not to fabricate cutoffs, fees, dates, or administrative designations
- Enforces canonical HBTU URL usage for official links
- Includes specific role responses for VC, Dean, Registrar, Pro VC, and Controller of Examinations

Configured model:

- llama-3.3-70b-versatile

Used when deterministic routing does not confidently match a structured intent path.

---

## 9. Frontend Implementation Review

The frontend is a single-page chat UI with a polished dark glassmorphism design.

Implemented UX features:

- Bot and user message bubbles with avatars and timestamps
- Rich cards for prediction and seat distribution
- Action chips and suggestion chips
- Typing indicator
- Streaming typewriter effect for long responses
- Clear chat and minimize controls
- API base selection via config.js or runtime origin fallback
- HTML escaping for safe rendering (escapeHtml, safeMultilineHtml)
- Automatic clickable URL conversion in message text (http/https/www)
- Link-only color styling for better readability

Deployment telemetry scripts are also present (Vercel insights/speed scripts).

---

## 10. Configuration, Environment, and Deployment

### Environment Variables (from backend/.env.example)

- DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
- DB_SSLMODE
- DB_MAX_CONNECTIONS
- ALLOWED_ORIGINS
- GROQ_API_KEY

### Backend Run Target

- Procfile command:
  - uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

### Frontend Runtime API

- backend/frontend/config.js currently points to a deployed Railway backend URL

---

## 11. Security and Robustness Observations

### Present in Current Code

- Input length caps for user_id and user_message
- Global exception handling for API failures
- Configurable CORS allowlist
- Connection pooling for PostgreSQL
- UI-side HTML escaping before rendering
- Background logging failure isolation (chat remains responsive)
- User query audit records (intent + session_id + timestamp)
- .env ignored in Git, with tracked .env.example

### Not Yet Implemented

- Authentication/authorization
- Rate limiting / abuse protection
- Structured audit logging and request tracing
- Automated test suite

---

## 12. Current Limitations

1. Static counselling content:
   Brochure-derived fee/date details are hardcoded and require manual updates each session.

2. Data provisioning gap:
   The app expects pre-populated cutoffs and seats tables, but repository code does not include a complete migration plus loader workflow for these tables.

3. Test coverage:
   No active automated tests are present in the current repository state.

4. Intent handling edge cases:
  Keyword scoring has been improved with token-safe checks, but highly ambiguous
  mixed-intent prompts can still be misrouted.

5. Logging observability gap:
  Query logging exists in DB, but no dashboard, retention policy, or analytics layer
  is currently implemented.

6. External dependency risk:
   AI fallback quality and availability depend on Groq API and valid API key configuration.

---

## 13. Recommendations and Next Steps

1. Add repeatable DB migrations and seed/load scripts for cutoffs and seats.
2. Add automated tests for intent classification, prediction flow transitions, and API response contracts.
3. Add admission-year versioning for counselling knowledge blocks.
4. Add backend rate limiting and request-level structured logging.
5. Add a simple admin/reporting view for user_queries analytics (intent trends,
   top query themes, session-level drill-down).
6. Add admin tooling for knowledge/data updates without code edits.

---

## 14. Conclusion

The project is now more than a basic B.Tech counselling bot. It is a multi-module admission assistant with:

- Deterministic data-backed prediction and seat lookups
- Counselling guidance with structured subtopics
- MBA support
- A robust conversational fallback path through LLM integration
- Non-blocking query logging for production observability
- Safer intent routing for non-counselling general queries
- Verified official-link governance in AI fallback responses
- A refined frontend experience designed for practical user guidance

With data loading automation, testing, and governance improvements, this can evolve into a maintainable production-grade admission advisory platform.

---

## 15. References

1. HBTU Official Website: https://hbtu.ac.in/
2. HBTU B.Tech Counselling Website: https://hbtu.admissions.nic.in/
3. HBTU Admissions Website: https://erp.hbtu.ac.in/HBTUAdmissions.html
4. HBTU Placement Statistics: https://hbtu.ac.in/training-placements/#PlacementStatistics
5. HBTU Academics Circular: https://hbtu.ac.in/academic-circular/
6. HBTU Academic Calendar: https://hbtu.ac.in/academic-calendar/
7. HBTU Classes Time Table: https://hbtu.ac.in/time-table/
8. FastAPI Documentation: https://fastapi.tiangolo.com
9. Psycopg2 Documentation: https://www.psycopg.org/docs/
10. Selenium Documentation: https://www.selenium.dev/documentation/
11. Pandas Documentation: https://pandas.pydata.org/docs/
12. Pydantic Documentation: https://docs.pydantic.dev
13. Groq API Documentation: https://console.groq.com/docs
