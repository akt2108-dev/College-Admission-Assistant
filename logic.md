# HBTU Chatbot Logic

This document explains how the backend interprets user queries and decides which chatbot response to return.

Primary implementation file: `backend/main.py`

Related modules:

- `backend/mba_knowledge.py`: MBA-specific knowledge base and intent detector.
- `backend/mca_knowledge.py`: MCA-specific knowledge base and intent detector.
- `backend/bsms_knowledge.py`: BS-MS-specific knowledge base and intent detector.
- `backend/placements_stats.py`: placement response handling.
- `backend/ai_brain.py`: AI fallback response generation.
- `backend/db.py`: database queries, conversation memory, and query logging.
- `backend/utils.py`: category formatting helper used elsewhere.

## Response Shape

All normal chatbot responses are built with `build_ui_response()`.

Returned object:

```json
{
  "type": "stream | question | prediction | seats | error",
  "message": "Markdown/plain text shown to user",
  "data": {},
  "actions": [],
  "suggestions": []
}
```

Response fields:

- `type`: tells the frontend how to render the answer.
- `message`: main chatbot answer.
- `data`: structured payload for predictions, seats, contacts, etc.
- `actions`: clickable follow-up options.
- `suggestions`: additional follow-up prompts.

## Core Knowledge Bases

### Branch Aliases

`BRANCH_ALIASES` maps canonical B.Tech branch names to user-friendly aliases.

Example:

- `COMPUTER SC. & ENGG.` matches `cse`, `computer science`, `computer`, `cs`.
- `INFORMATION TECHNOLOGY` matches `it`, `information technology`.

Used by `extract_branches()` to detect branch names in user messages.

### Helpdesk Contacts

`HELPDESK_CONTACTS` stores admission contact data for 2026-27.

Keys include:

- `btech`
- `btech_lateral`
- `btech_wp`
- `bsms`
- `bba`
- `bpharma`
- `mca`
- `mba`
- `mtech`
- `phd`
- `msc`
- `international`
- `nri`
- `payment`
- `admin`
- `coordinator`
- `ug_all`
- `pg_all`

Returned by:

- `detect_helpdesk_query()`
- `get_helpdesk_response()`

### Admission Programs 2026

`ADMISSION_PROGRAMS_2026` stores the 2026-27 program list, admission route, tentative schedule, application link, website, and email.

Returned by:

- `detect_programs_query()`
- `get_programs_response()`

### B.Tech Counselling Data

`COUNSELLING_DATA` stores B.Tech counselling responses.

Major keys include:

- `overview`
- `eligibility`
- `domicile`
- `categories`
- `reservation`
- `medical`
- `fee_structure`
- `registration`
- `round1`
- `round2`
- `round3`
- `round4`
- `round5`
- `internal_sliding`
- `spot_round`
- `refund`
- `documents`

Selected by `detect_counselling_subtopic()`.

## Extractors

These functions parse raw user text before routing.

### `extract_branches(user_message)`

Detects canonical B.Tech branch names using `BRANCH_ALIASES`.

Logic:

1. Lowercase the message.
2. Replace non-alphanumeric characters with spaces.
3. Match normalized aliases as full phrases.
4. Return a unique list of canonical branch names.

Used for:

- Seat lookup.
- B.Tech course scope detection.
- Avoiding rank/year confusion.

### `extract_rank(user_message)`

Extracts JEE CRL rank.

Supported formats:

- `25000`
- `42,135`
- `AIR 32000`
- `58k`

Special rule:

- Numbers from `2000` to `2099` can be ranks, but are skipped as ranks when they appear in year context such as `seats in 2025`.

### `extract_category(user_message)`

Extracts:

- Base category: `OPEN`, `BC`, `SC`, `ST`, `EWS`
- Subcategory flags: `girl`, `ph`, `af`, `ff`, `tf`

Base category logic:

- `general`, `gen`, `open` -> `OPEN`
- `obc`, `bc` -> `BC`
- whole word `sc` -> `SC`
- whole word `st` -> `ST`
- `ews` -> `EWS`

Subcategory logic:

- `girl`, `girls`, `female`, `woman` -> `girl`
- `ph`, `pwd`, `disabled`, `physically handicapped`, `handicapped` -> `ph`
- `af`, `armed forces`, `defence`, `defense` -> `af`
- `ff`, `freedom fighter` -> `ff`
- `tf`, `tfw`, `tuition fee waiver` -> `tf`

Important behavior:

- Subcategories are saved independently.
- A user can type `girl`, `ph`, `af`, etc. as a follow-up and the bot will remember it.

### `has_subcategory(category_info)`

Returns `True` if extracted category info contains any subcategory flag.

### `memory_has_subcategory(memory)`

Returns `True` if stored conversation memory contains any subcategory flag.

### `is_no_subcategory_reply(user_message)`

Detects replies meaning no subcategory applies.

Examples:

- `no`
- `none`
- `nope`
- `na`
- `n/a`
- `not applicable`
- `no subcategory`
- `none of these`

### `extract_quota(user_message)`

Detects counselling quota.

Home State:

- `home state`
- `hs quota`
- `domicile`
- whole word `hs`

All India:

- `all india`
- `ai quota`
- `other state`
- `outside state`
- whole word `ai`

### `extract_year(user_message)`

Extracts a year only when it appears in year context.

Examples that count:

- `seats in 2025`
- `CSE 2025`
- `seat matrix for 2025`

A bare `2025` is treated as a possible rank, not a year.

## Intent Detection

### `detect_intent(user_message)`

Detects broad intent using weighted keyword scoring.

Possible intents:

- `predict`
- `seats`
- `fees`
- `placement`
- `counselling_info`
- `unknown`

Weighted keyword groups:

- Prediction: `predict`, `prediction`, `chances`, `rank`, `branch`, etc.
- Seats: `seat matrix`, `seat distribution`, `intake`, `capacity`, etc.
- Fees: `fee structure`, `tuition fee`, `fees`, etc.
- Placement: `placement`, `median package`, `average package`, `companies visited`, etc.
- Counselling: `counselling process`, `freeze`, `float`, `documents`, `eligibility`, `reservation`, etc.

The highest scoring intent wins. If all scores are zero, intent is `unknown`.

### `detect_course_scope(user_message, extracted_branches)`

Detects the course mentioned by the user.

Returns:

- `mba`
- `mca`
- `bsms`
- `btech`
- `multiple`
- `unknown`

Logic:

- `mba` is detected by whole word `mba`.
- `mca` is detected by whole word `mca`.
- `bsms` is detected by phrases like `bsms`, `bs-ms`, `mathematics and data science`.
- `btech` is detected by `b.tech`, `btech`, `jee`, `crl`, or branch names.
- If more than one course is detected, returns `multiple`.

### `infer_course_specific_intent(course, user_message)`

Used when the user clearly mentions MBA/MCA/BS-MS but the module-specific detector has low confidence.

It maps common terms to course-specific intents:

- `eligibility`
- `fees`
- `seats`
- `reservation`
- `documents`
- `registration`
- `withdrawal`
- `medical`
- `schedule`
- course-specific extras like MBA GD/PI and BS-MS rank/CUET handling

### `should_clarify_course(...)`

Asks the user to clarify which course they mean when the query is generic and no course is clear.

Example generic queries:

- `What are the fees?`
- `Tell me seat matrix`
- `What documents are required?`
- `What is reservation?`

If no course is clear, the bot returns actions for:

- B.Tech
- MBA
- MCA
- BS-MS

### `is_prediction_followup(...)`

Decides whether an otherwise unknown message should continue an active prediction flow.

Signals:

- Rank detected.
- Base category detected.
- Subcategory detected.
- Quota detected.
- User replies with `1`, `2`, `Home State`, `All India`, `none`, etc.
- Existing memory contains rank/category/quota or is awaiting quota/subcategory.

### `detect_counselling_subtopic(user_message)`

Maps B.Tech counselling queries to `COUNSELLING_DATA` keys.

Examples:

- Eligibility words -> `eligibility`
- Domicile words -> `domicile`
- Category code words -> `categories`
- Reservation words -> `reservation`
- Medical/PwD words -> `medical`
- Fee words -> `fee_structure`
- Refund words -> `refund`
- Freeze/float words -> `freeze_float`
- Internal sliding words -> `internal_sliding`
- Spot round words -> `spot_round`
- Round-specific words -> `round1` to `round5`
- Document words -> `documents`
- Default -> `overview`

## Helpdesk Query Handling

### `detect_helpdesk_query(user_message)`

Returns a `HELPDESK_CONTACTS` key if the user asks for a contact.

Trigger phrases include:

- `contact`
- `helpdesk`
- `who to call`
- `phone number`
- `mobile number`
- `coordinator`
- `email`
- `admission office`
- `contact person`

After a contact trigger is found, the function selects the most specific topic:

- Payment words -> `payment`
- International words -> `international`
- `nri` -> `nri`
- `mba` -> `mba`
- `mca` -> `mca`
- BS-MS phrases -> `bsms`
- B.Pharma phrases -> `bpharma`
- BBA -> `bba`
- Working professional -> `btech_wp`
- Lateral entry -> `btech_lateral`
- M.Tech -> `mtech`
- PhD -> `phd`
- M.Sc. subject phrases -> relevant M.Sc. key
- B.Tech/JEE/UG -> `btech`
- PG -> `pg_all`
- Admin/registrar -> `admin`
- Admission/coordinator/dean -> `coordinator`
- UG -> `ug_all`
- Fallback -> `coordinator`

### `get_helpdesk_response(key)`

Builds a contact response.

Returns:

- `message`: helpdesk title, query label, contacts, office hours, email.
- `data`: selected contacts and topic label.
- `actions`: B.Tech, MBA, MCA, Payment follow-ups.
- `suggestions`: BS-MS, M.Tech, coordinator follow-ups.

## Admission Programs Handling

### `detect_programs_query(user_message)`

Detects if the user asks for the full course list, admission brochure, admission routes, or overall schedule.

Trigger examples:

- `all courses`
- `all programs`
- `programs offered`
- `courses offered`
- `admission brochure`
- `which courses`
- `admission schedule 2026`
- `how to apply 2026`
- `admission through`
- `jee mains 2026`
- `cuet 2026`
- `nimcet 2026`

### `get_programs_response()`

Returns a Markdown table of all 2026-27 programs.

Includes:

- Program number
- Programme name
- Admission route
- Tentative schedule
- UET note
- Apply link
- Info website
- Admission email

## Prediction Logic

### Conversation Memory

Prediction is multi-turn and uses memory.

Memory fields:

```json
{
  "rank": null,
  "base_category": null,
  "girl": false,
  "ph": false,
  "af": false,
  "ff": false,
  "tf": false,
  "quota": null,
  "subcategory_asked": false,
  "awaiting": null
}
```

Memory is saved through:

- `_load_chat_memory(user_id)`
- `_save_chat_memory(user_id, memory)`
- `_delete_chat_memory(user_id)`

Database table:

- `conversation_memory`

Fallback:

- If DB memory is unavailable, in-process memory `_memory_fallback_store` is used.

### Prediction Required Fields

Prediction requires:

1. Rank
2. Base category
3. Subcategory answer or explicit skip
4. Quota

Subcategory is optional, but the bot asks once after rank and base category are known.

### Subcategory Flow

If memory has rank and base category but no subcategory answer yet:

1. Bot sets `memory["awaiting"] = "subcategory"`.
2. Bot asks whether the user belongs to:
   - Girl
   - PH/PwD
   - AF
   - FF
   - TFW
   - None

If user replies with a subcategory:

- The corresponding memory flag is set.
- `subcategory_asked` becomes `True`.
- Bot proceeds to quota if quota is missing.

If user replies `none`:

- `subcategory_asked` becomes `True`.
- Bot proceeds with base category only.

### Quota Flow

If rank, base category, and subcategory state are ready but quota is missing:

1. Bot sets `memory["awaiting"] = "quota"`.
2. Bot asks for:
   - `Home State`
   - `All India`
3. User can reply with:
   - `Home State`
   - `All India`
   - `1` for Home State
   - `2` for All India

### `build_category_lookup_values(...)`

Builds category labels that match the cutoff database/CSV.

Important CSV/database category formats:

- `OPEN`
- `BC`
- `SC`
- `ST`
- `EWS`
- `OPEN GIRL`
- `BC(GIRL)`
- `SC(GIRL)`
- `ST(GIRL)`
- `EWS(GIRL)`
- `OPEN(AF)`
- `OPEN(FF)`
- `OPEN(PH)`
- `OPEN (TF)`

Rules:

- PH -> `BASE(PH)`
- AF -> `BASE(AF)`
- FF -> `BASE(FF)`
- TFW + OPEN -> `OPEN (TF)` with fallback `OPEN(TF)`
- TFW + non-OPEN -> `BASE(TF)`
- Girl + OPEN -> `OPEN GIRL` with fallback `OPEN(GIRL)`
- Girl + non-OPEN -> `BASE(GIRL)`
- No subcategory -> `BASE`

### `run_prediction(rank, base_category, girl, ph, af, ff, tf, quota)`

Builds category lookup values, queries the `cutoffs` table, and groups branches by probability.

SQL behavior:

- For each branch and year, mark success if:
  - `category = ANY(category_candidates)`
  - `quota = selected quota`
  - `closing_rank >= user rank`
- Count how many historical years were successful.
- Divide successful years by total years available.

Probability buckets:

- `Very High`: at least 80%
- `High`: at least 60%
- `Moderate`: at least 40%
- `Low`: at least 20%
- `Very Low`: below 20%

Returns:

- `full_category`
- `grouped_results`

### `format_chatbot_response(rank, category, quota, grouped_results)`

If no branches match:

- Explains that the rank may be higher than historical closing ranks.
- Suggests participating in all counselling rounds and exploring alternatives.

If branches match:

- Explains prediction is based on historical cutoff trends.
- Mentions category, quota, and rank.
- Notes actual allotment may vary.

### `/predict` Endpoint

Route: `POST /predict`

Input model:

- `rank`
- `base_category`
- `quota`
- `girl`
- `ph`
- `af`
- `ff`
- `tf`

Flow:

1. Calls `run_prediction()`.
2. On DB failure, returns `_db_unavailable_response()`.
3. Returns `type="prediction"`.
4. Data includes rank, category, quota, and grouped branches.

## Seat Lookup Logic

### `run_seat_lookup(branch, year)`

Queries `seats` table.

Filters:

- `canonical_branch`
- `year`

Returns:

- branch
- year
- total seats
- quota distribution
- raw details by quota/category

### `format_seat_response(seat_data)`

If no data:

- Returns `No seat data found...`

If data exists:

- Returns a formatted seat matrix summary.
- Includes total seats.
- Includes quota-wise distribution.
- Includes detailed category rows.

### `/seats` Endpoint

Route: `GET /seats`

Parameters:

- `branch`
- `year`

Flow:

1. Calls `run_seat_lookup()`.
2. Returns `error` if no rows.
3. Returns `type="seats"` if data exists.

## Health and Error Handling

### Global Exception Handler

`global_exception_handler()` catches unhandled exceptions.

Returns:

- HTTP 500
- `type="error"`
- generic user-facing message

### `/health`

Checks backend availability and DB status.

If DB works:

- `status="ok"`

If DB fails:

- `status="degraded"`
- DB unavailable details

### `/health/startup`

Checks placement CSV health through `get_placement_files_health()`.

If placement CSVs are okay:

- `status="ok"`

If not:

- HTTP 503
- `status="degraded"`

### `_db_unavailable_response()`

Returned when prediction or seat DB queries fail.

Response:

- `type="error"`
- message says admission data is temporarily unavailable
- data marks database as unavailable

## `/chat` Route Flow

Route: `POST /chat`

Input:

- `user_id`
- `user_message`
- optional `session_id`

### Step 0: Sanitize Input

Limits:

- `user_id`: max 64 chars
- `user_message`: max 500 chars
- `session_id`: max 100 chars

If user id or message is empty:

- returns `type="error"`

### Step 1: Load Memory

Loads DB-backed memory for the user.

If DB memory load fails:

- uses local fallback memory.

### Step 2: Extract Signals

The route extracts:

- rank
- category and subcategory
- quota
- branches
- year
- broad intent
- course scope

It also logs the user query asynchronously.

Current logging behavior:

- The chatbot logs the final handled route, not just the first rough intent.
- This makes query analysis more useful for follow-up messages like `OPEN`, `Girl`, `Home State`, or bare ranks.
- Examples of logged final routes:
  - `helpdesk`
  - `admission_programs`
  - `placement`
  - `ai_fallback_btech_unknown`
  - `prediction_ask_subcategory`
  - `prediction_ask_quota`
  - `prediction_result`
  - `seats_result`
  - `btech_counselling_documents`
  - `ai_fallback_general`

### Step 3: Helpdesk Routing

Runs before placement and course routing.

If `detect_helpdesk_query()` returns a key:

- returns helpdesk response immediately.

Response type:

- `stream`

### Step 4: Admission Programs Routing

If `detect_programs_query()` is true:

- returns program table immediately.

Response type:

- `stream`

### Step 5: Placement Routing

If intent is `placement`:

- calls `get_placement_response(user_message)`.
- returns placement payload.

This runs early so words like MBA/MCA inside placement questions do not route to admission knowledge bases.

### Step 6: Multiple Course Detection

If the message mentions multiple courses:

- bot asks the user to ask for one course at a time.

Response type:

- `question`

Actions:

- B.Tech
- MBA
- MCA
- BS-MS

### Step 7: MBA Routing

If `course_scope == "mba"`:

1. Calls `detect_mba_intent()`.
2. If confidence is low, uses `infer_course_specific_intent("mba", user_message)`.
3. If still unknown, asks for a more specific MBA query.
4. Otherwise returns `get_mba_response(resolved_intent)`.

Response type:

- `stream`

Actions include MBA eligibility, fees, rounds, seats, reservation, documents.

### Step 8: MCA Routing

If `course_scope == "mca"`:

1. Calls `detect_mca_intent()`.
2. If confidence is low, uses `infer_course_specific_intent("mca", user_message)`.
3. If still unknown, asks for a more specific MCA query.
4. Otherwise returns `get_mca_response(resolved_intent)` plus a note about checking updated guidelines.

Response type:

- `stream`

Actions include MCA eligibility, fees, rounds, seats, reservation, documents.

### Step 9: BS-MS Routing

If `course_scope == "bsms"`:

1. Calls `detect_bsms_intent()`.
2. If confidence is low, uses `infer_course_specific_intent("bsms", user_message)`.
3. If still unknown, falls back to `bsms_general`.
4. Returns `get_bsms_response(resolved_intent)`.

Response type:

- `stream`

Actions include BS-MS eligibility, fees, rounds, seats, reservation, documents.

### Step 10: Broad B.Tech Query Guard

If user says B.Tech but no specific B.Tech intent is detected:

- asks user to be more specific.

Examples offered:

- B.Tech eligibility
- B.Tech fees
- B.Tech seat matrix
- B.Tech documents
- B.Tech counselling process

### Step 11: Context-Aware Follow-Up Handling

If memory is awaiting quota:

- `1` -> Home State
- `2` -> All India

If memory is awaiting subcategory:

- `none` and similar replies mark no subcategory.
- subcategory terms like `girl`, `ph`, `af`, `ff`, `tfw` are stored.

### Step 12: Update Memory

Updates memory from extracted values:

- rank
- base category
- subcategory flags
- quota

If a subcategory is detected, `subcategory_asked` becomes `True`.

If quota is detected, awaiting state is cleared.

### Step 13: Ask Subcategory

If rank and base category are known, but subcategory has not been asked and no subcategory exists:

- bot asks if any subcategory applies.

Response type:

- `question`

Actions:

- None
- Girl
- PH/PwD
- AF
- FF
- TFW

### Step 14: Persist Memory

Saves updated memory.

### Step 15: Run Prediction

If memory has:

- rank
- base category
- quota

Then:

1. Captures rank/category/subcategory/quota.
2. Deletes memory for the user.
3. Calls `run_prediction()`.
4. Returns prediction response.

Response type:

- `prediction`

Data:

- rank
- final category label
- quota
- grouped branches

### Step 16: Ask Quota

If rank and base category are known but quota is missing:

- sets `awaiting="quota"`
- asks user to confirm Home State or All India.

Response type:

- `question`

### Step 17: Branch-Only Seat Handling

If intent is unknown but a branch is detected:

- If message has seat cues, treat as seats.
- If message is short, like `cse`, treat as seats.

### Step 18: Continue Prediction Follow-Up

If message is unknown but prediction is in progress:

- `is_prediction_followup()` can convert intent to `predict`.

This lets users answer with short replies like:

- `50000`
- `open`
- `girl`
- `home state`
- `2`
- `none`

### Step 19: Clarify Generic Course Query

If query is generic and course is unclear:

- calls `ai_brain_response()` for a conversational clarification.
- returns course-specific action buttons based on query type.

Examples:

- Fees query -> B.Tech Fees, MBA Fees, MCA Fees, BS-MS Fees.
- Seats query -> B.Tech Seats, MBA Seats, MCA Seats, BS-MS Seats.
- Documents query -> document actions.
- Reservation query -> reservation actions.

### Step 20: Prediction Prompting

If intent is `predict`:

- If rank exists but base category is missing, asks for base category.
- If rank is missing, asks for JEE Main CRL rank.

If still not enough information:

- returns a prompt asking for rank, base category, subcategory if any, and quota.

### Step 21: Seats Intent

If intent is `seats`:

- If a branch is detected, uses extracted year or defaults to `2025`.
- Calls `run_seat_lookup()`.
- Returns `type="seats"`.
- If no branch is detected, asks which branch.

### Step 22: Fees Intent

If intent is `fees`:

- returns `COUNSELLING_DATA["fee_structure"]`.

Response type:

- `stream`

### Step 23: Counselling Intent

If intent is `counselling_info`:

- detects subtopic with `detect_counselling_subtopic()`.
- returns matching `COUNSELLING_DATA` entry.

Response type:

- `stream`

### Step 24: AI Brain Fallback

If no explicit route handles the message:

1. Builds lightweight user context from memory.
2. Calls `ai_brain_response()`.
3. Returns a generic stream response with actions:
   - Predict My Branch
   - B.Tech Counselling
   - Seat Matrix
   - Fee Structure

## Course Knowledge Modules

### MBA

File: `backend/mba_knowledge.py`

Data:

- `MBA_KB`
- `MBA_INTENT_KEYWORDS`

Functions:

- `detect_mba_intent(message)`
- `get_mba_response(intent)`

Intent examples:

- eligibility
- registration
- fees
- rounds
- rank/GD-PI
- seats
- reservation
- documents
- withdrawal
- medical
- schedule

### MCA

File: `backend/mca_knowledge.py`

Data:

- `MCA_KB`
- `MCA_INTENT_KEYWORDS`

Functions:

- `detect_mca_intent(message)`
- `get_mca_response(intent)`

Intent examples:

- eligibility
- registration
- fees
- rounds
- seats
- reservation
- documents
- withdrawal
- medical
- schedule

### BS-MS

File: `backend/bsms_knowledge.py`

Data:

- `BSMS_KB`
- `BSMS_INTENT_KEYWORDS`
- `BSMS_LATEST_GUIDELINES_NOTE`

Functions:

- `detect_bsms_intent(message)`
- `get_bsms_response(intent)`

Intent examples:

- eligibility
- registration
- fees
- rounds
- seats
- reservation
- documents
- withdrawal
- medical
- rank/CUET
- schedule
- general information

## Database Tables Used

### `cutoffs`

Used by prediction.

Expected fields:

- `canonical_branch`
- `year`
- `category`
- `quota`
- `closing_rank`

Prediction checks historical closing ranks by branch/year/category/quota.

### `seats`

Used by seat lookup.

Expected fields:

- `canonical_branch`
- `year`
- `quota`
- `category`
- `seat_count`

### `conversation_memory`

Used for multi-turn chat state.

Fields:

- `user_id`
- `memory`
- `updated_at`

### `user_queries`

Used for logging.

Fields:

- `user_id`
- `message`
- `detected_intent`
- `session_id`
- `created_at`

## Common Query Examples

### Prediction With Subcategory

User:

```text
predict my branch rank 50000 open
```

Bot:

```text
I have your rank as 50000 and base category as OPEN.
Do you belong to any sub-category?
```

User:

```text
girl
```

Bot asks quota.

User:

```text
home state
```

Bot predicts using category lookup:

```text
OPEN GIRL
```

### Prediction Without Subcategory

User:

```text
predict 50000 open
```

Bot asks subcategory.

User:

```text
none
```

Bot asks quota.

User:

```text
2
```

Bot predicts under:

```text
OPEN, All India
```

### Helpdesk

User:

```text
Who to contact for MBA admission?
```

Bot:

- Detects helpdesk query.
- Selects `mba`.
- Returns MBA contact details.

### Admission Programs

User:

```text
What courses are offered in 2026?
```

Bot:

- Detects programs query.
- Returns admission brochure table.

### Seats

User:

```text
Show seats for CSE
```

Bot:

- Detects CSE branch.
- Uses default year `2025`.
- Returns seat matrix.

### B.Tech Counselling

User:

```text
What documents are needed for B.Tech counselling?
```

Bot:

- Broad intent: `counselling_info`
- Subtopic: `documents`
- Returns `COUNSELLING_DATA["documents"]`

### Generic Course Clarification

User:

```text
What are the fees?
```

Bot:

- Course is unclear.
- Returns clarification with actions for B.Tech, MBA, MCA, BS-MS fees.

## Important Implementation Notes

- Helpdesk and admission program queries are routed before placement and course-specific admission logic.
- Placement queries are routed before MBA/MCA/BS-MS admission routing.
- MBA/MCA/BS-MS admission queries bypass B.Tech counselling logic when course scope is clear.
- Subcategory values are saved independently from base category.
- Prediction category labels are matched to the database/CSV format, not only display format.
- Seat lookup defaults to year `2025` when no year is provided.
- A bare `2025` can be treated as rank unless it appears in year context.
- Conversation memory is deleted after a successful prediction to avoid stale rank/category/quota in later chats.
