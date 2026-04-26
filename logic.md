# Chatbot Logic - End-to-End Routing and Decision Flow

This document summarizes the current runtime logic implemented in the backend, centered on `backend/main.py`.

## 1) Primary Modules

- `backend/main.py` - request routing, extraction, intent handling, and response composition
- `backend/db.py` - DB pool, memory persistence, async query logging
- `backend/mba_knowledge.py` - MBA KB + intent detection
- `backend/mca_knowledge.py` - MCA KB + intent detection
- `backend/bsms_knowledge.py` - BS-MS KB + intent detection
- `backend/placements_stats.py` - placement intent + computed responses from CSV
- `backend/ai_brain.py` - fallback LLM response generation
- `backend/language_utils.py` - language style detection + query normalization

---

## 2) Unified Response Contract

All chat responses are normalized through `build_ui_response()` with fields:

```json
{
  "type": "stream | question | prediction | seats | error",
  "message": "text/markdown",
  "data": {},
  "actions": [],
  "suggestions": []
}
```

This keeps frontend rendering deterministic despite multiple backend paths.

---

## 3) Preprocessing and Extraction

Before deep routing, the backend performs:

1. **Language style detection** (`english`, `hindi`, `hinglish`)
2. **Multilingual normalization** of Hindi/Hinglish variants to routing keywords
3. Entity extraction from message:
   - Branches (`extract_branches` via canonical alias map)
   - Rank (`extract_rank`, including `58k` format)
   - Category + subcategory flags (`extract_category`)
   - Quota (`extract_quota`)
   - Year (`extract_year`, only in year-context)

Important safety behavior:

- Short tokens like `st`, `sc`, `ai`, `hs` use boundary-safe matching to avoid accidental triggers.
- Years in the 2000-range are not blindly treated as rank if context indicates a year.

---

## 4) Intent and Course Scope Detection

## 4.1 Broad Intent (`detect_intent`)

Weighted scoring chooses the best of:

- `predict`
- `seats`
- `fees`
- `placement`
- `counselling_info`
- fallback `unknown`

Each intent has weighted keyword groups (strong phrases carry higher weight).

## 4.2 Course Scope (`detect_course_scope`)

Detects explicit course targeting:

- `mba`
- `mca`
- `bsms`
- `btech`
- `multiple`
- `unknown`

This prevents cross-course ambiguity and is central to safe routing.

---

## 5) High-Level Routing Priority in `/chat`

At runtime, `/chat` follows this precedence pattern:

1. **Immediate controls** (e.g., reset-style commands)
2. **Placement flow first** when placement intent is detected
3. **Course conflict guard** for mixed-course prompts
4. **MBA flow** (intent detector + fallback inferencer)
5. **MCA flow** (intent detector + fallback inferencer)
6. **BS-MS flow** (intent detector + fallback inferencer)
7. **B.Tech deterministic flow** for prediction, seats, fees, counselling
8. **Course clarification** for generic ambiguous asks
9. **AI fallback** for remaining queries

This sequence is intentionally conservative: deterministic modules are preferred before LLM fallback.

---

## 6) B.Tech Prediction Logic (State-Based)

Prediction depends on memory-backed slots:

- Required: `rank`, `base_category`, `quota`
- Optional subcategories: `girl`, `ph`, `af`, `ff`, `tf`
- Control: `subcategory_asked`, `awaiting`

### Conversation rules

- If rank missing -> ask rank
- If base category missing -> ask category
- If subcategory not asked yet -> ask subcategory
- If quota missing -> ask quota (supports `1`/`2` shortcuts in-context)
- Once complete -> run SQL prediction and return grouped results
- After result -> clear memory for next fresh prediction

### Memory reliability

- Primary storage: PostgreSQL `conversation_memory`
- Fallback: in-process dictionary if DB temporarily unavailable
- Retry gate via `MEMORY_DB_RETRY_SECONDS`

---

## 7) Seats Logic

- Requires branch detection from alias map
- Year is optional; defaults to **2025**
- Calls `run_seat_lookup(branch, year)`
- Returns structured seat data + formatted summary
- If branch absent, bot asks user to specify branch

---

## 8) Counselling / Fees Logic

- `fees` intent maps directly to `COUNSELLING_DATA["fee_structure"]`
- `counselling_info` uses subtopic classifier (`detect_counselling_subtopic`) and serves structured text blocks from `COUNSELLING_DATA`

Counselling subtopics cover eligibility, category/reservation, medical, rounds, internal sliding, spot round, refund, and required documents.

---

## 9) Course-Specific Knowledge Paths

### MBA

- `detect_mba_intent()` + confidence threshold
- fallback inferencer for low-confidence explicit MBA queries
- returns topic-specific response with MBA actions/suggestions

### MCA

- Same pattern as MBA
- includes explicit “based on 2025-26 guidelines” framing in responses

### BS-MS

- Same intent + fallback pattern
- includes BS-MS specific policy/schedule/fees/documents logic

---

## 10) Placement Logic

Placement is handled by `placements_stats.py`:

- Detects placement intent and dimensions (year/branch/course)
- Reads CSV-backed records
- Computes response metrics and formatted message
- Includes source attribution and actionable follow-ups
- `/health/startup` exposes placement file readiness

---

## 11) Helpdesk and Program Catalogue Logic

Additional deterministic knowledge helpers in `main.py`:

- **Helpdesk contact detection** -> topic-specific contact card
- **Programs/schedule query detection** -> structured 2026-27 program list response

These run as direct informational utilities, separate from prediction/seats math.

---

## 12) Fallback and Safety Behavior

If no deterministic branch resolves cleanly:

- `ai_brain_response()` is used with contextual hints (current rank/category/quota if known)
- Course clarification cards are shown for ambiguous multi-course terms
- Output can be localized based on detected language style

The system is designed to avoid fabricated deterministic facts where structured sources exist.

---

## 13) Logging and Observability

For each chat request, backend can log:

- `user_id`
- original `message`
- `detected_intent`
- `session_id`
- timestamp

Stored in `user_queries` table via non-blocking async insert.

