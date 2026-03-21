# HBTU Counselling Assistant Chatbot — Project Report

---

## 1. Introduction

The **HBTU Counselling Assistant Chatbot** is an intelligent, web-based conversational system designed to assist students navigating the B.Tech admission counselling process at **Harcourt Butler Technical University (HBTU), Kanpur**. Every year, thousands of JEE Main aspirants face uncertainty about which engineering branches they are eligible for, how counselling rounds work, seat availability, fee structures, and document requirements. This information is typically scattered across lengthy PDF brochures, official websites, and social media — making it difficult for students and parents to find timely, accurate answers.

This project addresses that gap by providing an interactive chatbot that can:
- Predict branch allotment based on a student's JEE Main CRL (Common Rank List) rank, category, and quota.
- Display seat distribution data for any branch and year.
- Answer detailed questions about the counselling process, eligibility, reservation, fees, documents, and more — all through a natural, conversational interface.

The system combines a data pipeline (web scraping + data cleaning) with a backend API and a polished single-page frontend to deliver a seamless user experience.

---

## 2. Objectives

The primary objectives of this project are:

1. **Simplify the counselling process** — Provide students with a single point of contact to understand all aspects of HBTU B.Tech admissions, eliminating the need to read through lengthy official brochures.

2. **Enable data-driven branch prediction** — Use 3 years of historical ORCR (Opening & Closing Rank) data (2023, 2024, 2025) to predict branch allotment probability for a given rank, category, and quota combination.

3. **Provide real-time seat information** — Display seat matrix data with quota-wise and category-wise breakdowns for all 13 engineering branches.

4. **Answer counselling queries conversationally** — Handle questions about registration, choice filling, FREEZE/FLOAT/WITHDRAW options, round-wise procedures, internal sliding, refund policies, eligibility criteria, domicile requirements, category codes, reservation policies, medical standards, fee structures, and document checklists.

5. **Deliver an accessible, modern UI** — Build a responsive, visually appealing chat interface with rich cards, action chips, suggestion chips, and a streaming typewriter effect for long responses.

6. **Maintain conversation context** — Remember user inputs (rank, category, quota) across multiple messages using persistent database-backed memory, enabling a multi-turn conversational flow.

---

## 3. Scope

### In Scope
- **University coverage:** HBTU Kanpur — B.Tech programmes only.
- **Data years:** Historical ORCR data from 2023, 2024, and 2025 counselling sessions.
- **Branches covered:** All 13 B.Tech branches offered at HBTU — Computer Science & Engineering, Information Technology, Electronics Engineering, Electrical Engineering, Mechanical Engineering, Civil Engineering, Chemical Engineering, Food Technology, Plastic Technology, Paint Technology, Leather Technology, Oil Technology, and Bio Chemical Engineering.
- **Categories supported:** OPEN, BC (OBC-NCL), SC, ST, EWS — with sub-categories including Girl, PH (PwD), Armed Forces (AF), Freedom Fighter (FF), and Tuition Fee Waiver (TFW).
- **Quotas:** Home State (Uttar Pradesh) and All India.
- **Counselling topics:** Eligibility, domicile, category codes, reservation, medical standards, fee structure, round-wise procedures (Rounds 1–5), FREEZE/FLOAT/WITHDRAW, internal sliding, spot round, refund policy, and document checklist.
- **Prediction model:** Probability-based prediction using historical closing rank comparison across all available years.

### Out of Scope
- Other universities or colleges beyond HBTU.
- Post-graduate (M.Tech, MBA, MCA) admissions.
- Real-time integration with the official HBTU admissions portal.
- AI/LLM-based natural language understanding (the system uses rule-based NLP with score-based intent detection).
- Mobile application (native Android/iOS) — the current frontend is web-only.

---

## 4. Tech-Stack Used

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.11+** | Primary programming language |
| **FastAPI** | High-performance async web framework for REST APIs |
| **Pydantic** | Request/response validation and data modelling |
| **Uvicorn** | ASGI server for running the FastAPI application |
| **psycopg2-binary** | PostgreSQL database adapter for Python |
| **python-dotenv** | Environment variable management via `.env` files |

### Database
| Technology | Purpose |
|---|---|
| **PostgreSQL** | Relational database storing cutoff data, seat matrices, and conversation memory |
| **psycopg2 Connection Pooling** | Efficient connection reuse across concurrent requests |

### Frontend
| Technology | Purpose |
|---|---|
| **HTML5 / CSS3 / JavaScript (Vanilla)** | Single-page chat interface — no frameworks or build tools required |
| **Google Fonts (Fraunces + Instrument Sans)** | Typography for a polished, high-end UI |
| **CSS Animations & Transitions** | Smooth bubble pop-in, typing indicators, and bar chart animations |

### Data Pipeline
| Technology | Purpose |
|---|---|
| **Selenium WebDriver** | Automated web scraping of ORCR data from the official HBTU admissions portal |
| **Pandas** | Data cleaning, merging, and CSV processing |
| **ChromeDriver** | Browser automation for Selenium |

### DevOps / Tooling
| Technology | Purpose |
|---|---|
| **Git** | Version control |
| **CORS Middleware** | Cross-origin request handling (configurable via environment variable) |
| **Environment Variables** | Database credentials, allowed origins, connection pool sizing |

---

## 5. Features

### 5.1 Branch Prediction Engine
- Accepts JEE Main CRL rank, category (OPEN/BC/SC/ST/EWS with sub-categories), and quota (Home State / All India).
- Compares the user's rank against 3 years of historical closing ranks across all counselling rounds.
- Groups branches into 5 probability tiers: **Very High** (≥80%), **High** (≥60%), **Moderate** (≥40%), **Low** (≥20%), and **Very Low** (<20%).
- Results displayed in a rich prediction card with colour-coded branch tags.

### 5.2 Seat Distribution Viewer
- Retrieves seat matrix data for any branch and year from the database.
- Displays total seats, quota-wise distribution (Home State / All India), and animated horizontal bar charts.
- Supports natural language queries like "How many seats in CSE?" or "Show seat matrix for Mechanical 2025."

### 5.3 Counselling Information System
- Comprehensive knowledge base with 15+ topics derived from the official HBTU counselling brochure.
- Covers: overview, eligibility, domicile, category codes, reservation, medical standards, fee structure, registration & choice filling, Rounds 1–5, FREEZE/FLOAT/WITHDRAW, internal sliding, spot round, refund policy, and document checklist.
- Replies are streamed with a typewriter effect for a natural, engaging reading experience.

### 5.4 Score-Based Intent Detection
- Custom NLP engine using weighted keyword scoring across 4 intent categories: predict, seats, fees, and counselling_info.
- Resolves keyword conflicts (e.g., "branch" appears in both prediction and seat queries) by comparing cumulative scores rather than first-match.
- Subtopic detection routes counselling queries to the most relevant knowledge base entry.

### 5.5 Multi-Turn Conversational Memory
- Persistent, database-backed conversation state per user.
- Progressively collects rank → category → quota across multiple messages.
- Supports shortcut inputs (e.g., "1" for Home State, "2" for All India when prompted).
- Memory is automatically cleared after a successful prediction to start fresh.

### 5.6 Rich Interactive UI
- Dark-themed, glassmorphism-styled chat interface with ambient radial gradients.
- Message bubbles with avatar icons, timestamps, and smooth pop-in animations.
- Action chips (gold) for guided navigation and suggestion chips (muted) for discovery.
- Typing indicator with animated dots during response loading.
- Clear chat and minimize controls.

### 5.7 Data Pipeline (Scraping & Cleaning)
- Selenium-based scraper navigates the official HBTU ORCR portal, selects each counselling round from the dropdown, and extracts tabular data with pagination support.
- Pandas pipeline cleans column names, standardises data types, drops incomplete rows, and merges 3 years of data into a single CSV.
- Cleaned data is loaded into PostgreSQL for efficient querying.

### 5.8 Error Handling & Security
- Global exception handler returns user-friendly error messages.
- Input sanitisation: user IDs capped at 64 characters, messages at 500 characters.
- CORS origins configurable via environment variable (defaults to `*` for development).
- Database connection pooling (2–10 connections) prevents connection exhaustion.

---

## 6. Conclusions

The HBTU Counselling Assistant Chatbot successfully demonstrates how structured data, rule-based NLP, and a well-designed conversational interface can be combined to solve a real-world information accessibility problem for engineering aspirants.

**Key achievements:**
- **High intent detection accuracy (99%)** — The score-based approach correctly classifies 89 out of 90 test queries spanning prediction, seat distribution, and counselling process intents.
- **Comprehensive counselling coverage** — 15+ counselling subtopics sourced directly from the official HBTU brochure, ensuring accuracy and reliability.
- **Historical data-driven predictions** — 3 years of ORCR data (2023–2025) across 13 branches, multiple categories, and both quotas provide a robust basis for probability estimation.
- **Production-ready architecture** — Connection pooling, persistent memory, configurable CORS, input validation, and environment-based configuration make the system deployable beyond a local development environment.

**Future enhancements:**
- Integration of a Large Language Model (LLM) for handling open-ended, out-of-scope queries with natural language generation.
- Mobile-responsive design and Progressive Web App (PWA) support.
- Year-over-year cutoff trend visualisation charts.
- Branch comparison feature (side-by-side cutoffs, seats, and trends).
- Admin dashboard for data management and usage analytics.

The project serves as a practical, extensible foundation for building domain-specific educational chatbots, and has direct applicability for the thousands of students navigating HBTU admissions each year.

---

## 7. References

1. **HBTU Official Admissions Portal** — https://hbtu.admissions.nic.in  
   Source of ORCR (Opening & Closing Rank) data and counselling brochure.

2. **HBTU B.Tech Counselling Guidelines & Brochure (2025-26)**  
   Official document detailing eligibility criteria, counselling procedure, category codes, reservation policies, fee structure, document checklist, and refund policies.

3. **JEE Main — National Testing Agency (NTA)** — https://jeemain.nta.nic.in  
   The national-level entrance examination whose CRL ranks are used for HBTU seat allotment.

4. **FastAPI Documentation** — https://fastapi.tiangolo.com  
   Web framework used for building the backend REST API.

5. **Psycopg2 Documentation** — https://www.psycopg.org/docs/  
   PostgreSQL adapter for Python, including connection pooling.

6. **Selenium WebDriver Documentation** — https://www.selenium.dev/documentation/  
   Browser automation tool used for scraping ORCR data from the admissions portal.

7. **Pandas Documentation** — https://pandas.pydata.org/docs/  
   Data manipulation library used for cleaning and merging CSV datasets.

8. **Pydantic Documentation** — https://docs.pydantic.dev  
   Data validation library used with FastAPI for request/response models.
---

*Report generated for the HBTU Counselling Assistant Chatbot project.*
