# College Admission Assistant - Project Report (Repository Review)

## 1) Executive Summary

This repository contains a FastAPI-based admission chatbot for HBTU that combines deterministic counselling logic with an AI fallback layer. The current system supports:

- **B.Tech rank-based branch prediction** (historical ORCR driven)
- **B.Tech seat matrix lookups** (normalized seat matrix data)
- **B.Tech counselling Q&A** (rule-based subtopic routing)
- **MBA, MCA, and BS-MS dedicated knowledge modules**
- **Placement statistics Q&A** across two academic sessions
- **Multilingual handling** (English/Hindi/Hinglish normalization + localized response behavior)
- **Persistent conversation memory + async query logging** in PostgreSQL

The implementation is modular, production-oriented for small deployments, and intentionally conservative for critical flows (prediction, seat lookup) by preferring deterministic logic over pure LLM generation.

---

## 2) Project Scope in Current Codebase

### In Scope

- Conversational admissions guidance through `/chat`
- Structured APIs for health, prediction, and seat lookups
- Multi-course admission guidance: **B.Tech, MBA, MCA, BS-MS**
- Placement insights from local CSV files
- Session memory for multi-turn prediction intake (rank/category/quota/subcategory)

### Out of Scope

- Authentication/authorization and user roles
- Real-time sync from official admission portals
- Automatic annual brochure ingestion
- Native mobile application
- End-to-end analytics dashboards (beyond DB query logging)

---

## 3) Repository Structure and Responsibilities

## Backend

- `backend/main.py`
  - FastAPI app setup, CORS, routes, error handling
  - Intent detection/routing orchestration
  - Prediction and seats flow integration
  - Course disambiguation (B.Tech vs MBA/MCA/BS-MS)
  - Memory-aware conversational flow (`awaiting` state)
- `backend/db.py`
  - PostgreSQL pooled connectivity
  - Query execution helpers
  - Conversation memory persistence
  - `user_queries` async logging
- `backend/placements_stats.py`
  - Placement CSV loading/validation
  - Placement intent parsing and metric responses
- `backend/mba_knowledge.py`, `backend/mca_knowledge.py`, `backend/bsms_knowledge.py`
  - Course-specific knowledge bases + intent detectors
- `backend/ai_brain.py`
  - LLM fallback and response shaping policy
- `backend/language_utils.py`
  - Hindi/Hinglish normalization + language-style detection
- `backend/frontend/index.html`, `backend/frontend/config.js`
  - Single-page web chat interface

## Data and Pipelines

- `scrape_ORCR.py` - Selenium ORCR scraping
- `clean_and_merge.py` - cleanup + merge of yearly ORCR files
- `hbtu_all_rounds_orcr_2023.csv`, `hbtu_all_rounds_orcr_2024.csv`, `hbtu_all_rounds_orcr_2025.csv`
- `hbtu_combined_cleaned.csv`
- `seat_matrix_2025_normalized.csv`
- Placement data files for 2024-25 and 2025-26 (root + backend copies)

---

## 4) API Surface (Observed)

- `GET /health`
  - DB connectivity probe (`SELECT 1`)
- `GET /health/startup`
  - Startup readiness with placement CSV file health
- `POST /predict`
  - Structured prediction endpoint
- `GET /seats`
  - Structured seats endpoint
- `POST /chat`
  - Main conversational endpoint

`/chat` is the primary product interface and includes most business logic.

---

## 5) Conversational Intelligence Design

### 5.1 Layered Routing Order

Routing is intentionally layered to reduce false positives:

1. Normalize multilingual query for detection
2. Detect broad intent (`predict`, `seats`, `fees`, `placement`, `counselling_info`, `unknown`)
3. Detect explicit course scope (MBA/MCA/BS-MS/B.Tech/multiple)
4. Handle high-priority flows first (placement and course-specialized modules)
5. Run B.Tech-specific deterministic flows (prediction/seats/counselling)
6. Use AI fallback for open-ended or unmatched asks

### 5.2 Prediction Conversation State Machine

The B.Tech prediction flow uses memory slots:

- `rank`
- `base_category`
- `girl`, `ph`, `af`, `ff`, `tf`
- `quota`
- `subcategory_asked`
- `awaiting` (`subcategory` / `quota`)

Key properties:

- Handles partial user replies across multiple turns
- Supports quota shortcuts (`1`=Home State, `2`=All India) only in relevant context
- Resets and avoids stale-state confusion in rank redeclaration scenarios
- Clears memory after completing prediction

### 5.3 Multi-Course Safety

The system prevents ambiguous cross-course answers by:

- Explicit **course scope detection**
- Returning clarification prompts when user asks generic terms (fees, seats, docs) without specifying course
- Rejecting mixed multi-course asks in one prompt with guided options

---

## 6) Data and Logic for Core Features

### 6.1 Branch Prediction

- SQL-based against historical cutoffs data
- Computes branch-wise chance levels by observed hit frequency across available years
- Outputs grouped branch recommendations with confidence labels

### 6.2 Seats

- Uses canonical branch aliases from user text
- Supports year extraction when in explicit year context
- Defaults seat lookup year to **2025** when not specified

### 6.3 Counselling Information

`COUNSELLING_DATA` in `main.py` provides structured subtopics, including:

- overview
- eligibility
- domicile
- categories and reservation
- medical standards
- fee structure
- registration + round details
- internal sliding / spot round
- refund and documents

### 6.4 Placement Statistics

- Reads placement CSVs for **2024-25** and **2025-26**
- Startup health endpoint reports file availability/readability
- Placement intent parser supports year-wise, branch-wise, and course-wise asks

### 6.5 Program/Helpdesk Knowledge

- Built-in 2026 admissions program list and routes
- Helpdesk lookup by topic with contacts and response cards

---

## 7) Reliability and Operations

### Strengths

- DB connection pooling with configurable limits/timeouts
- Automatic table creation for memory/query logs
- DB memory fallback to in-process store when DB temporarily fails
- Asynchronous query logging so chat responses are not blocked
- Global exception handler for API resilience

### Observed Operational Risks

- Heavy logic concentration in `backend/main.py` increases maintenance cost
- Static knowledge sections require manual yearly updates
- Placement statistics quality depends on CSV schema consistency
- No auth/rate-limiting layer in current backend

---

## 8) Frontend Review

Frontend is a single-page app (`backend/frontend/index.html`) with:

- chat bubbles + action chips
- response type-aware rendering (`stream`, `prediction`, `seats`, `question`, `error`)
- typing/typewriter UX
- safe multiline rendering + URL linkification
- runtime API base config via `config.js`

The UI is functionally rich for a single-file frontend and tightly aligned with backend response schema.

---

## 9) Overall Assessment

The project is a **rule-first admission assistant** with practical conversational behavior and strong domain specialization for HBTU. It is particularly good at:

- guided branch prediction intake
- deterministic factual modules for multiple courses
- balancing deterministic control with AI fallback

The next architectural improvement would be splitting `main.py` into dedicated routers/services while preserving the same response contract used by the frontend.

