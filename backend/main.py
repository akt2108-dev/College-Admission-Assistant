from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from collections import defaultdict
from db import execute_query, load_memory, save_memory, delete_memory
from utils import build_category
import os
import re


# ─────────────────────────────────────────────
#  Unified response builder
# ─────────────────────────────────────────────

def build_ui_response(
    response_type: str,
    message: str,
    data: dict = None,
    actions: list = None,
    suggestions: list = None
):
    return {
        "type": response_type,
        "message": message,
        "data": data or {},
        "actions": actions or [],
        "suggestions": suggestions or []
    }


# ─────────────────────────────────────────────
#  Branch alias map
# ─────────────────────────────────────────────

BRANCH_ALIASES = {
    "COMPUTER SC. & ENGG.": ["cse", "computer science", "computer", "cs", "comp sci."],
    "INFORMATION TECHNOLOGY": ["it", "information technology"],
    "ELECTRONICS ENGG.": ["electronics", "ece", "et"],
    "ELECTRICAL ENGG.": ["electrical", "ee", "elec"],
    "MECHANICAL ENGG.": ["mechanical", "mech"],
    "CIVIL ENGG.": ["civil"],
    "CHEMICAL ENGG.": ["chemical", "chem"],
    "FOOD TECHNOLOGY": ["food tech", "food"],
    "PLASTIC TECHNOLOGY": ["plastic", "pl"],
    "PAINT TECHNOLOGY": ["paint", "pt"],
    "LEATHER TECHNOLOGY": ["leather", "lft", "Leather & fashion technology", "leather and fashion technology"],
    "OIL TECHNOLOGY": ["oil", "ot"],
    "BIO CHEMICAL ENGG.": ["biochemical", "bio chemical", "biotech", "bio chem"],
}


def extract_branches(user_message: str) -> list[str]:
    """Detect one or more canonical branch names from message."""
    message = user_message.lower()
    detected = []
    for canonical, aliases in BRANCH_ALIASES.items():
        for alias in aliases:
            if alias in message:
                detected.append(canonical)
                break
    return list(set(detected))


def extract_rank(user_message: str) -> int | None:
    """
    Extract JEE CRL rank from message.
    Handles: 25000 / 42,135 / AIR 32000 / 58k / 2025 (when not in year-context)
    """
    message = user_message.lower().replace(",", "")

    # Handle "58k" format
    k_match = re.search(r'(\d+)\s*k\b', message)
    if k_match:
        return int(k_match.group(1)) * 1000

    # Handle "AIR 25000" or plain "25000"
    # Numbers in 2000–2099 are treated as rank UNLESS they appear in year-context
    # (e.g. "CSE 2025", "seats in 2025", "for 2025")
    rank_match = re.search(r'(?:air|rank)?\s*(\d{3,7})', message)
    if rank_match:
        val = int(rank_match.group(1))
        if 2000 <= val <= 2099:
            # If this number looks like a year (preceded by year-context words
            # or branch names), skip it as a rank
            year_context = re.search(
                r'(?:in|for|of|year|seats?|seat matrix|\b[a-z]{2,}\s+engg?\.?)\s*'
                + str(val),
                message
            )
            if year_context:
                return None
            # Otherwise treat it as a rank (e.g. user just typed "2025")
            return val
        return val

    return None


def extract_category(user_message: str) -> dict:
    """
    Extract base category and subcategory flags.
    Uses word-boundary matching to avoid false positives (e.g. 'first' → ST).
    """
    message = user_message.lower()

    base_category = None

    if any(word in message for word in ["general", "gen", "open"]):
        base_category = "OPEN"
    elif any(word in message for word in ["obc", "bc"]):
        base_category = "BC"
    elif re.search(r'\bsc\b', message):          # FIX: word boundary
        base_category = "SC"
    elif re.search(r'\bst\b', message):          # FIX: word boundary
        base_category = "ST"
    elif "ews" in message:
        base_category = "EWS"

    girl = any(word in message for word in ["girl", "female"])
    ph   = any(word in message for word in ["ph", "pwd", "disabled"])
    af   = "af" in message or "armed forces" in message
    ff   = "ff" in message or "freedom fighter" in message
    tf   = "tfw" in message or "tuition fee waiver" in message

    return {
        "base_category": base_category,
        "girl": girl,
        "ph": ph,
        "af": af,
        "ff": ff,
        "tf": tf,
    }


def extract_quota(user_message: str) -> str | None:
    """Extract quota: 'Home State' or 'All India'."""
    message = user_message.lower()

    if any(w in message for w in ["home state", "hs quota", "domicile"]):
        return "Home State"

    # FIX: avoid matching bare "hs" inside words; use word boundary
    if re.search(r'\bhs\b', message):
        return "Home State"

    if any(w in message for w in ["all india", "ai quota", "other state", "outside state"]):
        return "All India"

    # FIX: avoid matching bare "ai" inside words
    if re.search(r'\bai\b', message):
        return "All India"

    return None


def extract_year(user_message: str) -> int | None:
    """
    Extract a 4-digit year (2020–2099) from message, but ONLY when it
    appears in year-context (e.g. "CSE 2025", "seats in 2025", "for 2025").
    A bare "2025" with no context is treated as a rank, not a year.
    """
    message = user_message.lower()
    match = re.search(r'\b(20\d{2})\b', message)
    if not match:
        return None

    val = int(match.group(1))
    # Only return as year if preceded by year-context words or branch names
    year_context = re.search(
        r'(?:in|for|of|year|seats?|seat matrix|\b[a-z]{2,}\s+engg?\.?)\s*'
        + str(val),
        message
    )
    if year_context:
        return val

    return None


def detect_intent(user_message: str) -> str:
    """
    Score-based intent detection.
    Each keyword hit adds to the intent's score. The intent with the highest
    score wins. This prevents conflicts when a message contains keywords from
    multiple intents (e.g. "seat distribution for each branch").
    """
    message = user_message.lower()

    # ── keyword → weight maps per intent ──────────────────────────────────
    # Higher-weight phrases are checked first via `in`; they are more specific.

    PREDICT_KEYWORDS = [
        # strong signals (2 pts)
        ("predict", 2), ("prediction", 2), ("chances", 2),
        ("probability", 2), ("expect", 2), ("likely", 2), ("possible", 2),
        ("options", 2),
        # weak signals (1 pt) — these appear in many contexts
        ("rank", 1), ("branch", 1),
    ]

    SEATS_KEYWORDS = [
        # strong signals (3 pts – multi-word phrases)
        ("seat matrix", 3), ("seat distribution", 3), ("seat count", 3),
        ("available seats", 3), ("total seats", 3),
        # moderate signals (2 pts)
        ("seat", 2), ("seats", 2), ("intake", 2), ("capacity", 2),
        ("how many", 2), ("reserved", 2),
    ]

    FEES_KEYWORDS = [
        ("fee structure", 3), ("tuition fee", 3),
        ("fee", 2), ("fees", 2), ("tuition", 2),
    ]

    COUNSELLING_KEYWORDS = [
        # strong signals (3 pts)
        ("counselling process", 3), ("counselling procedure", 3),
        ("counseling process", 3), ("counseling procedure", 3),
        ("freeze and float", 3), ("freeze or float", 3),
        ("choice filling", 3), ("spot round", 3), ("spot counselling", 3),
        ("seat allotment", 5), ("seat allocation", 5),
        ("internal sliding", 3), ("erp registration", 3),
        # eligibility / domicile / category (3 pts)
        ("academic eligibility", 3), ("eligibility criteria", 3),
        ("domicile", 3), ("home state", 3), ("other state", 3),
        ("category code", 3), ("category certificate", 3),
        ("reservation", 3), ("vertical reservation", 3), ("horizontal reservation", 3),
        ("medical standard", 3), ("medical fitness", 3), ("pwd", 3),
        ("fee structure", 3), ("fee waiver", 3), ("tuition fee waiver", 3),
        ("document checklist", 3), ("documents required", 3),
        # moderate signals (2 pts)
        ("counselling", 2), ("counseling", 2), ("freeze", 2), ("float", 2),
        ("withdraw", 2), ("refund", 2), ("document", 2), ("registration", 2),
        ("phase", 2), ("sliding", 2), ("allotment", 2), ("erp", 2),
        ("admission", 2), ("confirm", 2), ("submission", 2), ("announcement", 2),
        ("allotted", 2), ("don't get", 2), ("do not get", 2), ("not get a seat", 3),
        ("eligible", 2), ("qualify", 2), ("qualification", 2),
        ("category", 2), ("sc", 2), ("st", 2), ("obc", 2), ("ews", 2),
        ("upbc", 2), ("upsc", 2), ("upst", 2), ("upge", 2),
        ("subcategory", 2), ("sub-category", 2), ("handicapped", 2), ("disabled", 2),
        ("defence", 2), ("freedom fighter", 2), ("girl reservation", 2),
        ("medical", 2), ("vision", 2), ("physically", 2),
        # weak signals (1 pt)
        ("round", 1), ("process", 1), ("steps", 1), ("stages", 1),
        ("procedure", 1), ("timeline", 1), ("selection", 1),
        ("marks", 1), ("percentage", 1), ("physics", 1), ("mathematics", 1),
        ("certificate", 1), ("domicile", 1),
    ]

    def _score(keywords):
        total = 0
        for phrase, weight in keywords:
            if phrase in message:
                total += weight
        return total

    scores = {
        "predict":         _score(PREDICT_KEYWORDS),
        "seats":           _score(SEATS_KEYWORDS),
        "fees":            _score(FEES_KEYWORDS),
        "counselling_info": _score(COUNSELLING_KEYWORDS),
    }

    best_intent = max(scores, key=scores.get)
    if scores[best_intent] == 0:
        return "unknown"
    return best_intent


def detect_counselling_subtopic(user_message: str) -> str:
    """
    Detect which specific counselling subtopic the user is asking about.
    Returns a key into COUNSELLING_DATA, or 'overview' as default.
    """
    message = user_message.lower()

    # ── Eligibility / domicile / categories ────────────────────────────────
    if any(w in message for w in ["eligib", "qualify", "qualification", "10+2",
                                   "intermediate", "marks", "physics", "mathematics",
                                   "55%", "50%", "jee main"]):
        return "eligibility"
    if any(w in message for w in ["domicile", "home state", "other state", "up candidate",
                                   "uttar pradesh candidate", "permanent resident",
                                   "outside up", "outside uttar pradesh"]):
        return "domicile"
    if any(w in message for w in ["category code", "upge", "upbc", "upsc", "upst",
                                   "upgd", "gdsc", "gdst", "gdbc", "gdda",
                                   "osno", "ossc", "osst", "osbc",
                                   "which category", "category definition", "category type"]):
        return "categories"
    if any(w in message for w in ["reservation", "vertical reservation", "horizontal reservation",
                                   "upff", "upaf", "uphc", "upgl", "ews reservation",
                                   "21%", "27%", "sc reservation", "obc reservation",
                                   "sub-category", "subcategory", "freedom fighter",
                                   "defence reservation", "girl reservation", "girl quota",
                                   "handicapped reservation", "pwd reservation"]):
        return "reservation"
    if any(w in message for w in ["medical", "medical standard", "medical fitness",
                                   "physically handicapped", "disability", "vision",
                                   "hearing", "locomotor", "pwd", "disabled",
                                   "type i", "type ii", "type iii", "cmo"]):
        return "medical"
    # ── Fee structure ───────────────────────────────────────────────────────
    if any(w in message for w in ["fee structure", "fee breakdown", "how much fee",
                                   "total fee", "tuition fee", "fee waiver",
                                   "1,35,000", "135000", "75000", "annual fee"]):
        return "fee_structure"
    # ── Counselling procedure subtopics ─────────────────────────────────────
    if any(w in message for w in ["refund", "money back", "withdraw fee", "deduct",
                                   "5000", "rs 5000"]):
        return "refund"
    if any(w in message for w in ["freeze", "float", "upgrade", "upgradation"]):
        return "freeze_float"
    if any(w in message for w in ["internal sliding", "sliding result", "erp",
                                   "university erp", "erp registration"]):
        return "internal_sliding"
    if any(w in message for w in ["spot", "spot round", "spot counselling",
                                   "additional round", "offline in campus",
                                   "in campus counselling"]):
        return "spot_round"
    if any(w in message for w in ["register", "registration", "step 1", "step 2",
                                   "branch choice", "choice fill", "choice filling"]):
        return "registration"
    if any(w in message for w in ["round 1", "first round", "step 3", "1st round"]):
        return "round1"
    if any(w in message for w in ["round 2", "second round", "step 4", "2nd round"]):
        return "round2"
    if any(w in message for w in ["round 3", "third round", "step 5", "3rd round"]):
        return "round3"
    if any(w in message for w in ["round 4", "fourth round", "step 6", "4th round",
                                   "phase 2", "second phase"]):
        return "round4"
    if any(w in message for w in ["round 5", "fifth round", "step 7", "5th round",
                                   "last round", "final round"]):
        return "round5"
    if any(w in message for w in ["document", "verification", "offline", "visit",
                                   "checklist", "documents required", "bring documents"]):
        return "documents"

    return "overview"


# ─────────────────────────────────────────────
#  Counselling knowledge base (from official HBTU brochure)
# ─────────────────────────────────────────────

COUNSELLING_DATA = {

    "overview": {
        "title": "B.Tech Counselling — Overview",
        "message": (
            "The HBTU B.Tech counselling for 2025-26 is split into 2 Phases and 5 Rounds:\n\n"
            "📋 PHASE 1 — Rounds 1, 2 & 3\n"
            "• Step 1: Online Registration at hbtu.admissions.nic.in + Rs. 2500 fee (non-refundable)\n"
            "• Step 2: Fill branch choices VERY CAREFULLY (locked for all rounds)\n"
            "• Rounds 1–3: Seat allotment → Document verification at HBTU, Kanpur → "
            "Pay Rs. 1,35,000 annual fee → Choose FREEZE or FLOAT\n"
            "  ↳ FREEZE = confirm seat | FLOAT = try for better branch\n"
            "  ↳ ⚠️ Round 3: NO FLOAT option\n\n"
            "📋 PHASE 2 — Rounds 4 & 5 (after Internal Sliding)\n"
            "• Round 4: Fresh re-registration allowed (Rs. 2500 again)\n"
            "• Round 5: NO FLOAT option\n\n"
            "🏫 Additional Round: Offline In-Campus (Spot) Counselling for remaining seats\n\n"
            "💰 Refund: Rs. 5000 processing fee deducted on withdrawal after fee payment\n\n"
            "📅 Registration: May 26, 2025 to June 20, 2025\n\n"
            "Ask me about any specific topic below 👇"
        ),
        "actions": [
            {"label": "Eligibility Criteria",  "value": "What is the eligibility criteria?"},
            {"label": "Round 1 Details",        "value": "Tell me about Round 1"},
            {"label": "Round 2 & 3",            "value": "Tell me about Round 2"},
            {"label": "Rounds 4 & 5",           "value": "Tell me about Round 4 and Round 5"},
            {"label": "FREEZE vs FLOAT",        "value": "What is the difference between Freeze and Float?"},
            {"label": "Refund Policy",          "value": "What is the refund policy?"},
            {"label": "Documents Needed",       "value": "What documents are needed for verification?"},
        ],
        "suggestions": [
            "Am I eligible for HBTU admission?",
            "What is domicile requirement?",
            "How does internal sliding work?",
            "What is the fee structure?",
        ],
    },

    "eligibility": {
        "title": "Academic Eligibility — HBTU B.Tech 2025-26",
        "message": (
            "📚 ACADEMIC ELIGIBILITY (as per official guidelines)\n\n"
            "✅ Qualifying Examination:\n"
            "  • Must have CLEARLY PASSED Intermediate / 10+2 from U.P. Board or equivalent\n"
            "  • Minimum of 5 subjects including:\n"
            "    → Physics & Mathematics (compulsory)\n"
            "    → Any ONE of: Chemistry / Bio-technology / Biology / Computer Science\n\n"
            "✅ Minimum Marks:\n"
            "  • OPEN / EWS candidates: at least 55% aggregate in the above 3 subjects\n"
            "  • SC / ST / OBC-NCL / PwD candidates: at least 50% aggregate\n\n"
            "✅ JEE Main 2025:\n"
            "  • Must have a valid JEE Main 2025 CRL rank (All India Rank)\n"
            "  • Seat allotment is strictly based on JEE Main 2025 rank and choice preference\n"
            "  • All eligibility conditions for appearing in JEE Mains 2025 also apply\n\n"
            "⚠️ Important:\n"
            "  • If your Board gives only grades (no percentage), get an equivalent marks certificate "
            "from the Board before document verification\n"
            "  • Any false documents will lead to cancellation of admission and legal action"
        ),
        "actions": [
            {"label": "Domicile Requirements", "value": "What is the domicile requirement?"},
            {"label": "Category & Reservation", "value": "Tell me about categories and reservation"},
            {"label": "Counselling Overview",   "value": "Explain the counselling process"},
        ],
        "suggestions": [
            "Can a student from outside UP apply?",
            "What is the minimum percentage for OBC candidates?",
        ],
    },

    "domicile": {
        "title": "Domicile & Home State Requirements",
        "message": (
            "🏠 DOMICILE REQUIREMENT (Session 2025-26)\n\n"
            "─── HOME STATE SEATS ───\n\n"
            "✅ Case A — Studied in U.P.:\n"
            "  • Passed 10+2 from an institution IN Uttar Pradesh\n"
            "  • Eligible for Home State quota\n"
            "  • ✅ No domicile certificate required [Code: UPGE / UPBC / UPSC / UPST]\n\n"
            "✅ Case B — Studied outside U.P. but parents are UP residents:\n"
            "  • Parents (Father or Mother) must be Permanent Resident of U.P.\n"
            "  • Submit Permanent Residence Certificate (Certificate No. 03)\n"
            "  • Issued on or after 01.04.2025 [Code: UPGD / GDBC / GDSC / GDST]\n\n"
            "✅ Case C — Defence Personnel:\n"
            "  • Wards of Defence Personnel settled/posted in U.P. on date of JEE Mains 2025\n"
            "  • Certificate No. 5 required [Code: GDDA → treated as UPGD]\n\n"
            "✅ Case D — All India Services (U.P. Cadre):\n"
            "  • Wards of Officers/Employees of All India Services belonging to U.P. Cadre\n"
            "  • Certificate No. 10 required [Code: GDDA]\n\n"
            "─── OTHER STATE SEATS ───\n\n"
            "  • Candidates & parents both domicile of a state OTHER than U.P.\n"
            "  • Eligible for 5% supernumerary seats only [Code: OSNO / OSSC / OSST / OSBC]\n"
            "  • Only vertical reservation (SC/ST/OBC-NCL as per Central Govt. list)\n"
            "  • No sub-category (horizontal) reservation for other state candidates"
        ),
        "actions": [
            {"label": "Category Codes",        "value": "What are the category codes?"},
            {"label": "Reservation Details",   "value": "Tell me about reservation of seats"},
            {"label": "Documents Needed",      "value": "What documents are needed?"},
        ],
        "suggestions": [
            "I studied outside UP but my parents are from UP. Am I eligible?",
            "What is Certificate No. 3?",
        ],
    },

    "categories": {
        "title": "Category Codes & Certificate Requirements",
        "message": (
            "🏷️ CATEGORY CODES (HBTU 2025-26)\n\n"
            "─── HOME STATE (U.P.) CANDIDATES ───\n"
            "  UPGE  → Studied in U.P., General/OPEN, no reserved category\n"
            "          Certificate: None required\n\n"
            "  UPBC  → Studied in U.P., OBC-NCL of U.P.\n"
            "  UPSC  → Studied in U.P., Scheduled Caste of U.P.\n"
            "  UPST  → Studied in U.P., Scheduled Tribe of U.P.\n"
            "          Certificate: No. 1 or 2 (as applicable), issued after 01.04.2025\n\n"
            "─── OUTSIDE U.P. — PARENTS ARE UP RESIDENTS ───\n"
            "  UPGD  → Studied outside U.P., parents UP domicile, General/OPEN\n"
            "          Certificate: No. 3 (Permanent Residence of parents)\n\n"
            "  GDBC  → Studied outside U.P., parents UP domicile, OBC-NCL\n"
            "  GDSC  → Studied outside U.P., parents UP domicile, SC\n"
            "  GDST  → Studied outside U.P., parents UP domicile, ST\n"
            "          Certificate: No. 3 + No. 1 or 2\n\n"
            "  GDDA  → Defence/All India Services ward (domicile relaxed)\n"
            "          Certificate: No. 5 or No. 10. Treated as UPGD for other benefits\n\n"
            "─── OTHER STATE CANDIDATES ───\n"
            "  OSNO  → Other state, General/OPEN → Certificate: None\n"
            "  OSBC  → Other state, OBC (Central Govt. list) → Certificate: No. 14\n"
            "  OSSC  → Other state, SC (Central Govt. list) → Certificate: No. 13\n"
            "  OSST  → Other state, ST (Central Govt. list) → Certificate: No. 13\n\n"
            "⚠️ Important: Category once filled in registration form CANNOT be changed"
        ),
        "actions": [
            {"label": "Reservation Percentages", "value": "What are the reservation percentages?"},
            {"label": "Domicile Requirements",   "value": "What is the domicile requirement?"},
            {"label": "Documents Needed",        "value": "What documents are needed?"},
        ],
    },

    "reservation": {
        "title": "Seat Reservation Details",
        "message": (
            "📊 RESERVATION OF SEATS (HBTU 2025-26)\n\n"
            "─── VERTICAL RESERVATION ───\n"
            "  SC (Scheduled Caste of U.P.)    → 21% of seats\n"
            "  ST (Scheduled Tribe of U.P.)    → 02% of seats\n"
            "  OBC-NCL (Other Backward Classes)→ 27% of seats\n"
            "  EWS (Economically Weaker Section)→ 10% of seats\n"
            "    (Certificate No. 12, issued after 01.04.2025 by Tehsildar or above)\n\n"
            "─── HORIZONTAL RESERVATION (Sub-categories) ───\n"
            "  Applicable only to candidates/parents with U.P. domicile:\n\n"
            "  UPFF → Dependents of Freedom Fighters from U.P.    — 02%\n"
            "  UPAF → Sons/Daughters of Defence Personnel of U.P. — 05%\n"
            "  UPHC → Handicapped/Disabled persons of U.P.        — 05%\n"
            "  UPGL → Girls of U.P.                               — 20%\n\n"
            "─── RULES ───\n"
            "  • A candidate can claim only ONE of UPFF / UPAF / UPHC\n"
            "  • Girl candidates can claim UPGL + any one of UPFF/UPAF/UPHC\n"
            "  • UPGL benefit is given automatically to all eligible female candidates\n"
            "  • Other state candidates: only vertical reservation (no horizontal)\n\n"
            "─── FEE WAIVER SEATS ───\n"
            "  • Tuition Fee Waiver (TFW): 5% supernumerary seats in each branch\n"
            "    Only Rs. 75,000 tuition fee waived; other charges still payable\n"
            "    Certificate No. 11 required (income ≤ Rs. 8 lakh/year)\n"
            "  • Full Fee Waiver: 2 seats per branch for SC/ST girls (merit basis)"
        ),
        "actions": [
            {"label": "Category Codes",       "value": "What are the category codes?"},
            {"label": "Fee Structure",        "value": "What is the fee structure?"},
            {"label": "Eligibility Criteria", "value": "What is the eligibility criteria?"},
        ],
    },

    "medical": {
        "title": "Medical Standards for Admission",
        "message": (
            "🏥 MEDICAL STANDARDS (HBTU B.Tech 2025-26)\n\n"
            "Candidates must be physically and mentally fit to pursue engineering studies.\n\n"
            "─── GENERAL STANDARDS ───\n"
            "  Heart & Lungs   → No abnormality\n"
            "  Hernia/Hydrocele/Piles → Must be corrected before joining\n"
            "  Vision          → Normal; if defective, corrected to 6/9 (better eye) "
            "and 6/12 (worse eye). Eyes must be free from congenital disease\n"
            "  Hearing         → Normal; if defective, must be corrected before joining\n\n"
            "─── PwD (PHYSICALLY HANDICAPPED/DISABLED) ───\n"
            "  5% reservation for PwD candidates of U.P. based on impairment type:\n\n"
            "  Type I   → Minimum 40% permanent Visual impairment\n"
            "  Type II  → Minimum 40% permanent Locomotors disability\n"
            "  Type III → Minimum 40% permanent Speech and Hearing impairment\n\n"
            "  ⚠️ PwD/Disability certificate must be issued by the CMO (Chief Medical "
            "Officer) of the district\n\n"
            "─── CERTIFICATES REQUIRED ───\n"
            "  • Certificate No. 8  → Medical Fitness certificate (from CMO or HBTU Medical Officer)\n"
            "  • Certificate No. 9  → Undertaking by candidate for medical fitness\n"
            "  • Certificate No. 6  → For PwD sub-category (UPHC) claim"
        ),
        "actions": [
            {"label": "Reservation Details",  "value": "Tell me about reservation of seats"},
            {"label": "Documents Needed",     "value": "What documents are needed?"},
            {"label": "Category Codes",       "value": "What are the category codes?"},
        ],
    },

    "fee_structure": {
        "title": "Fee Structure — B.Tech 2025-26",
        "message": (
            "💰 FEE STRUCTURE FOR B.TECH. (Session 2025-26)\n\n"
            "─── ANNUAL ACADEMIC FEE: Rs. 1,35,000 ───\n\n"
            "  A. Tuition Fee                          → Rs. 75,000\n\n"
            "  B. Other Fees:\n"
            "    • Registration, Exam & Certification  → Rs. 10,000\n"
            "    • Facility charges                    → Rs. 30,500\n"
            "    • Medical Fee                         → Rs.  3,000\n"
            "    • Training & Placement                → Rs.  4,000\n"
            "    • Activity Charges                    → Rs.  3,000\n"
            "    • Caution Money                       → Rs.  5,000\n"
            "    • University Alumni Fund              → Rs.  1,500\n"
            "    • Student Aid Fund                    → Rs.  1,500\n"
            "    • Contingency & Miscellaneous         → Rs.  1,500\n"
            "    Total (Other fees)                    → Rs. 60,000\n\n"
            "  GRAND TOTAL                             → Rs. 1,35,000\n\n"
            "─── PAYMENT MODES ───\n"
            "  • Demand Draft (in favour of 'Finance Controller, HBTU Kanpur', payable at Kanpur)\n"
            "  • Cash\n"
            "  • Online mode (check one-time payment limit of debit/credit card)\n"
            "  ⚠️ Full payment only — partial payment is NOT allowed\n\n"
            "─── REGISTRATION FEE ───\n"
            "  • Rs. 2500 (Non-Refundable) — paid online at hbtu.admissions.nic.in\n"
            "  • Phase 2 (Round 4) requires fresh registration + Rs. 2500 again\n\n"
            "─── FEE WAIVER ───\n"
            "  • Tuition Fee Waiver (5% seats): Rs. 75,000 waived; other Rs. 60,000 payable\n"
            "    Family income must be ≤ Rs. 8 lakh/year (Certificate No. 11)\n"
            "  • Full Fee Waiver: 2 seats/branch for SC/ST girls (merit basis)"
        ),
        "actions": [
            {"label": "Refund Policy",       "value": "What is the refund policy?"},
            {"label": "TFW / Fee Waiver",    "value": "Tell me about reservation of seats"},
            {"label": "Counselling Overview","value": "Explain the counselling process"},
        ],
    },

    "registration": {
        "title": "Registration & Choice Filling",
        "message": (
            "📝 STEP 1 — Online Registration\n"
            "  • Register at: https://hbtu.admissions.nic.in\n"
            "  • Pay Registration Fee: Rs. 2500 (Non-Refundable)\n"
            "  • 📅 Phase 1 Registration: May 26, 2025 to June 20, 2025\n\n"
            "📝 STEP 2 — Branch Choice Filling\n"
            "  • Fill your branch preferences VERY CAREFULLY\n"
            "  • ⚠️ Choices once locked CANNOT be changed between rounds\n"
            "  • Same choices used for ALL rounds and Internal Sliding\n\n"
            "─── PHASE 2 (Round 4) Registration ───\n"
            "  Who can register fresh in Round 4:\n"
            "  ✅ New candidates not registered in Rounds 1-3 (pay Rs. 2500 again)\n"
            "  ✅ Registered earlier but NO seat allotted in any round (no fee again)\n"
            "  ✅ Earlier allotted but seat cancelled (pay Rs. 2500 again)\n"
            "  ❌ Already admitted with paid fee and seat not cancelled — CANNOT participate\n\n"
            "⚠️ Key Rule: Once choices are submitted and locked, NO corrections allowed"
        ),
        "actions": [
            {"label": "Round 1 Process",  "value": "Tell me about Round 1"},
            {"label": "FREEZE vs FLOAT",  "value": "What is Freeze and Float?"},
            {"label": "Eligibility",      "value": "What is the eligibility criteria?"},
        ],
    },

    "round1": {
        "title": "Round 1 — First Round Counselling",
        "message": (
            "🔵 ROUND 1 (Step 3) — Starts after display of Seat Allotment Result\n\n"
            "3.1.1 → View your allotment result\n"
            "3.1.2 → If seat allotted:\n"
            "  • Visit HBTU, Kanpur with ALL original documents for Offline Document Verification\n"
            "  • ⚠️ If you don't visit in time → seat cancelled, out of counselling\n\n"
            "3.2 → After successful document verification:\n"
            "  • Deposit Full Academic Fee: Rs. 1,35,000 immediately\n"
            "  • ⚠️ Non-payment → seat cancelled (treated as vacant for next round)\n"
            "  • You will receive a Provisional Admission Letter after fee payment\n"
            "  • Choose one option:\n\n"
            "  🔒 FREEZE (confirm your seat):\n"
            "    → Do Academic Registration on University ERP\n"
            "    → Choose Yes/No for Internal Sliding (seat upgradation)\n\n"
            "  🌊 FLOAT (try for a better branch in Round 2):\n"
            "    → Keep current seat; wait for Round 2 result\n"
            "    → Pay Rs. 1,35,000 fee (seat held while floating)\n\n"
            "3.3 → Withdrawal / Cancellation:\n"
            "  • Fail to act in time = automatic removal from counselling\n"
            "  • Use WITHDRAW option and fill Withdrawal Form via same login for refund\n\n"
            "📌 If NO seat allotted: Wait for Round 2 result"
        ),
        "actions": [
            {"label": "Round 2 →",        "value": "Tell me about Round 2"},
            {"label": "FREEZE vs FLOAT",  "value": "What is Freeze and Float?"},
            {"label": "Refund Policy",    "value": "What is the refund policy?"},
            {"label": "Documents Needed", "value": "What documents are needed?"},
        ],
    },

    "round2": {
        "title": "Round 2 — Second Round Counselling",
        "message": (
            "🟢 ROUND 2 (Step 4) — Starts after display of Seat Allotment Result\n\n"
            "─── If seat allotted for FIRST TIME in Round 2 ───\n"
            "  4.1.2 → Visit HBTU, Kanpur for Offline Document Verification\n"
            "  4.1.3 → After verification: Deposit Full Academic Fee Rs. 1,35,000\n"
            "  4.1.4 → Choose FREEZE / FLOAT / Withdrawal\n\n"
            "  🔒 FREEZE: Register on University ERP + choose Yes/No for Internal Sliding\n"
            "  🌊 FLOAT: Wait for Round 3 result\n\n"
            "─── If seat was allotted in Round 1 (docs already verified) ───\n"
            "  • Do NOT visit HBTU again\n"
            "  • Choose FREEZE / FLOAT / WITHDRAW via login only\n"
            "  • If FLOAT chosen again → wait for Round 3 result\n\n"
            "4.2 → Withdrawal / Cancellation:\n"
            "  • Fail to act in time = automatic removal\n"
            "  • Fill WITHDRAWAL FORM via same login for refund"
        ),
        "actions": [
            {"label": "← Round 1",  "value": "Tell me about Round 1"},
            {"label": "Round 3 →",  "value": "Tell me about Round 3"},
            {"label": "Refund",     "value": "What is the refund policy?"},
        ],
    },

    "round3": {
        "title": "Round 3 — Third Round Counselling",
        "message": (
            "🟡 ROUND 3 (Step 5) — Starts after display of Seat Allotment Result\n\n"
            "─── If seat allotted for FIRST TIME in Round 3 ───\n"
            "  5.1.2 → Visit HBTU, Kanpur for Offline Document Verification\n"
            "  5.1.4 → After verification: Deposit Full Academic Fee Rs. 1,35,000\n"
            "  ⚠️ NO FLOAT option in Round 3 — only FREEZE or WITHDRAW\n\n"
            "  🔒 FREEZE: Register on University ERP + choose Yes/No for Internal Sliding\n\n"
            "─── If seat was allotted in earlier rounds (docs already verified) ───\n"
            "  • Do NOT visit HBTU again\n"
            "  • Choose FREEZE or WITHDRAW via login only\n"
            "  • Fill WITHDRAWAL FORM via same login if withdrawing\n\n"
            "5.3 → Declaration of Internal Sliding Result\n"
            "  → This marks the END of Phase 1 counselling\n\n"
            "📌 If NO seat allotted: Wait for Phase 2 (Round 4)"
        ),
        "actions": [
            {"label": "← Round 2",         "value": "Tell me about Round 2"},
            {"label": "Round 4 (Phase 2)", "value": "Tell me about Round 4 and Round 5"},
            {"label": "Internal Sliding",  "value": "How does internal sliding work?"},
            {"label": "Refund",            "value": "What is the refund policy?"},
        ],
    },

    "round4": {
        "title": "Round 4 — Phase 2 Counselling",
        "message": (
            "🟠 PHASE 2 — ROUND 4 (Step 6)\n"
            "Starts after display of Internal Sliding Result\n\n"
            "─── Registration (Fresh) ───\n"
            "  6.1.1 → Register at https://hbtu.admissions.nic.in\n"
            "    • New candidates: pay Rs. 2500 registration fee\n"
            "    • No seat in Rounds 1-3: no fresh fee (provide earlier registration proof)\n"
            "    • Earlier seat cancelled: re-register + pay Rs. 2500\n"
            "    • Already admitted with fee paid: CANNOT participate\n"
            "  6.1.2 → Re-fill branch choices VERY CAREFULLY (same locking rules apply)\n\n"
            "─── Seat Allotment ───\n"
            "  6.2.2 → If seat allotted: Visit HBTU, Kanpur for Offline Document Verification\n"
            "  6.2.3 → After verification:\n"
            "    • Deposit Full Academic Fee: Rs. 1,35,000\n"
            "    • Choose FREEZE / FLOAT / Withdraw\n\n"
            "  🔒 FREEZE: Register on ERP + wait for Internal Sliding\n"
            "  🌊 FLOAT: Wait for Round 5 results\n\n"
            "6.3 → Withdrawal: Fill WITHDRAWAL FORM via same login for refund"
        ),
        "actions": [
            {"label": "← Round 3",        "value": "Tell me about Round 3"},
            {"label": "Round 5 →",        "value": "Tell me about Round 5"},
            {"label": "Internal Sliding", "value": "How does internal sliding work?"},
            {"label": "Refund Policy",    "value": "What is the refund policy?"},
        ],
    },

    "round5": {
        "title": "Round 5 — Fifth Round Counselling",
        "message": (
            "🔴 ROUND 5 (Step 7) — Starts after Seat Allotment Result\n\n"
            "─── If seat allotted for FIRST TIME in Round 5 ───\n"
            "  7.1.2 → Visit HBTU for Offline Document Verification\n"
            "  7.1.3 → After verification:\n"
            "    • Deposit Full Academic Fee: Rs. 1,35,000\n"
            "    • Choose FREEZE or WITHDRAW\n"
            "  ⚠️ NO FLOAT option in Round 5\n\n"
            "  🔒 FREEZE: Register on University ERP + wait for Internal Sliding\n\n"
            "─── If seat was allotted in Round 4 (docs already verified) ───\n"
            "  • Do NOT visit HBTU again\n"
            "  • Choose FREEZE or WITHDRAW via login only\n\n"
            "7.1.5 → Withdrawal: You can opt out of counselling entirely\n\n"
            "STEP 8 → Declaration of Internal Sliding Result\n"
            "  (Final step of the entire counselling process)"
        ),
        "actions": [
            {"label": "← Round 4",        "value": "Tell me about Round 4"},
            {"label": "Spot Round",        "value": "Tell me about the spot counselling round"},
            {"label": "Internal Sliding",  "value": "How does internal sliding work?"},
            {"label": "Refund Policy",     "value": "What is the refund policy?"},
        ],
    },

    "internal_sliding": {
        "title": "Internal Sliding & ERP Registration",
        "message": (
            "🔄 INTERNAL SLIDING — What is it?\n\n"
            "Internal Sliding is a chance to UPGRADE your allotted seat as per your "
            "branch preferences, while keeping your current seat in hand.\n\n"
            "─── How it works ───\n"
            "  • After choosing FREEZE in any round, register on University ERP\n"
            "  • Give consent for Internal Sliding: choose YES or NO\n"
            "    → YES: system tries to upgrade you to a better branch (per your choices)\n"
            "    → NO: stay with your current allotted seat\n"
            "  • Sliding is based on vacant seats and your prefilled choices\n"
            "  • ⚠️ Category upgradation may also happen during sliding\n"
            "  • Internal Sliding result is FINAL and CANNOT be changed\n\n"
            "─── ERP Registration (MANDATORY) ───\n"
            "  • ALL candidates who have paid the full academic fee MUST register on ERP\n"
            "  • This confirms your admission\n"
            "  • ⚠️ Candidates who do NOT register on ERP will be considered not "
            "interested and their seat will be CANCELLED\n\n"
            "─── When it happens ───\n"
            "  • Phase 1: After Round 3 → Internal Sliding result declared (Step 5.3)\n"
            "  • Phase 2: After Round 5 → Internal Sliding result declared (Step 8)\n\n"
            "💡 Tip: Choose YES for Internal Sliding only if you want a higher-preference branch. "
            "Check the result carefully as it is final."
        ),
        "actions": [
            {"label": "FREEZE vs FLOAT",    "value": "What is Freeze and Float?"},
            {"label": "Round 3 Details",    "value": "Tell me about Round 3"},
            {"label": "Spot Round",         "value": "Tell me about the spot counselling round"},
        ],
    },

    "spot_round": {
        "title": "Additional Round — Offline In-Campus (Spot) Counselling",
        "message": (
            "🏫 ADDITIONAL ROUND — Offline In-Campus (Spot) Counselling\n\n"
            "This round is conducted for seats LEFT VACANT after all 5 rounds of "
            "counselling and Internal Sliding result publication.\n\n"
            "─── Who can participate ───\n"
            "  ✅ New candidates (not registered earlier):\n"
            "    → Register online as fresh candidate\n"
            "    → Pay Rs. 2500 registration fee (non-refundable)\n\n"
            "  ✅ Candidates registered earlier but could not find a seat:\n"
            "    → Can register without paying again\n"
            "    → Must provide proof of earlier registration fee payment\n\n"
            "─── How it works ───\n"
            "  • Conducted OFFLINE at HBTU, Kanpur campus\n"
            "  • Dates will be announced separately on the admission website\n"
            "  • Seats filled are those remaining after all previous rounds\n\n"
            "📌 Keep checking https://hbtu.admissions.nic.in for dates and announcements"
        ),
        "actions": [
            {"label": "← Round 5",          "value": "Tell me about Round 5"},
            {"label": "Counselling Overview","value": "Explain the counselling process"},
            {"label": "Refund Policy",       "value": "What is the refund policy?"},
        ],
    },

    "freeze_float": {
        "title": "FREEZE vs FLOAT vs WITHDRAW",
        "message": (
            "When a seat is allotted to you, you must choose one of these options:\n\n"
            "🔒 FREEZE — Confirm your current seat\n"
            "  • You are satisfied with the allotted branch\n"
            "  • Pay Rs. 1,35,000 Academic Fee (if not already paid)\n"
            "  • Register on University ERP (mandatory)\n"
            "  • Choose Yes/No for Internal Sliding\n"
            "  • Your seat is SECURED\n\n"
            "🌊 FLOAT — Try for a better branch in the next round\n"
            "  • You want a higher-preference branch\n"
            "  • Pay Rs. 1,35,000 Academic Fee (mandatory even for FLOAT)\n"
            "  • Current seat is held — you may get a better branch next round\n"
            "  • ⚠️ FLOAT is NOT available in Round 3 and Round 5\n"
            "  • ⚠️ If you get your first-choice branch, only FREEZE is available\n\n"
            "🚪 WITHDRAW — Exit the counselling process entirely\n"
            "  • Rs. 5000 deducted as processing fee if full academic fee already paid\n"
            "  • Remaining amount refunded as per UGC guidelines\n"
            "  • Rs. 2500 registration fee is NON-REFUNDABLE\n"
            "  • Must fill WITHDRAWAL FORM using same login\n\n"
            "💡 Tip: If you are happy with your branch, always FREEZE. "
            "FLOAT keeps your current seat but has risk if you don't get a better branch."
        ),
        "actions": [
            {"label": "Internal Sliding",   "value": "How does internal sliding work?"},
            {"label": "Refund Policy",      "value": "What is the refund policy?"},
            {"label": "Round 1 Process",    "value": "Tell me about Round 1"},
            {"label": "Start Prediction",   "value": "I want to predict my branch"},
        ],
    },

    "refund": {
        "title": "Refund Policy",
        "message": (
            "💰 REFUND POLICY (Official HBTU Guidelines 2025-26)\n\n"
            "─── If you WITHDRAW after paying Full Academic Fee ───\n"
            "  • Rs. 5000 deducted as processing fee (as per University norms)\n"
            "  • Additional deductions as per UGC guidelines\n"
            "  • Remaining amount refunded\n\n"
            "─── Registration Fee ───\n"
            "  • Rs. 2500 is NON-REFUNDABLE under all circumstances\n\n"
            "─── Important Notes ───\n"
            "  ⏳ All refunds processed AFTER last date of Admissions for session 2025-26\n"
            "  🏦 Fill BANK ACCOUNT details during Registration VERY CAREFULLY\n"
            "  ⚠️ If refund goes to wrong account due to incorrect info you provided, "
            "the University will NOT be responsible\n\n"
            "─── How to claim refund ───\n"
            "  1. Choose WITHDRAW option within the prescribed time\n"
            "  2. Fill the Withdrawal / Refund form\n"
            "  3. Use the SAME LOGIN used for the counselling process"
        ),
        "actions": [
            {"label": "FREEZE vs FLOAT",     "value": "What is Freeze and Float?"},
            {"label": "Fee Structure",       "value": "What is the fee structure?"},
            {"label": "Counselling Overview","value": "Explain the counselling process"},
        ],
    },

    "documents": {
        "title": "Document Checklist for Verification",
        "message": (
            "📄 OFFLINE DOCUMENT VERIFICATION\n\n"
            "─── When to visit HBTU, Kanpur ───\n"
            "  • ONLY if seat is allotted for the FIRST TIME in a round\n"
            "  • If documents already verified in a previous round → choose option via login only\n"
            "  • ⚠️ Not visiting in time = seat cancelled, out of counselling\n\n"
            "─── Official Document Checklist (Page 16 of guidelines) ───\n"
            "  1. Original Marksheet of 10+2 / Intermediate / qualifying examination\n"
            "  2. Original Class X (10th) certificate (for date of birth proof)\n"
            "  3. Original Category certificate [SC/ST/OBC/EWS/PwD etc.]\n"
            "  4. Original Domicile / Residence proof certificate (as applicable)\n"
            "  5. Original Income / Tuition Fee Waiver certificate (if applicable)\n"
            "  6. Original Sub-category certificate (UPFF/UPAF/UPHC etc. if applicable)\n"
            "  7. Medical certificate / undertaking for medical fitness (Cert. No. 8 & 9)\n"
            "  8. 4 Passport-size photographs\n"
            "  9. Self-attested photocopies of ALL above documents\n"
            " 10. Gap Affidavit (if applicable)\n\n"
            "─── Fee Payment at Document Verification ───\n"
            "  • Rs. 1,35,000 via Demand Draft / Cash / Online mode\n"
            "  • DD in favour of: 'Finance Controller, HBTU Kanpur' (payable at Kanpur)\n"
            "  • ⚠️ Partial payment NOT allowed — full amount only\n\n"
            "⚠️ If proper documents not produced in time → seat cancelled"
        ),
        "actions": [
            {"label": "Round 1 Process",    "value": "Tell me about Round 1"},
            {"label": "Category Codes",     "value": "What are the category codes?"},
            {"label": "Fee Structure",      "value": "What is the fee structure?"},
            {"label": "Medical Standards",  "value": "What are the medical standards?"},
        ],
    },

}


# ─────────────────────────────────────────────
#  Prediction helpers
# ─────────────────────────────────────────────

def run_prediction(rank, base_category, girl, ph, af, ff, tf, quota):
    full_category = build_category(
        base=base_category, girl=girl, ph=ph, af=af, ff=ff, tf=tf
    )

    query = """
        WITH yearly_success AS (
            SELECT
                canonical_branch,
                year,
                MAX(
                    CASE
                        WHEN category = %s
                         AND quota = %s
                         AND closing_rank >= %s
                        THEN 1 ELSE 0
                    END
                ) AS success
            FROM cutoffs
            GROUP BY canonical_branch, year
        ),
        branch_years AS (
            SELECT
                canonical_branch,
                COUNT(DISTINCT year) AS total_years_available
            FROM cutoffs
            GROUP BY canonical_branch
        )
        SELECT
            b.canonical_branch AS branch,
            b.total_years_available,
            SUM(y.success) AS years_possible
        FROM branch_years b
        JOIN yearly_success y ON b.canonical_branch = y.canonical_branch
        GROUP BY b.canonical_branch, b.total_years_available
        ORDER BY years_possible DESC;
    """

    raw_results = execute_query(query, (full_category, quota, rank))

    grouped_results: dict[str, list] = {}
    for item in raw_results:
        total = item["total_years_available"]
        possible = item["years_possible"] or 0
        probability = (possible / total * 100) if total > 0 else 0

        if probability >= 80:
            level = "Very High"
        elif probability >= 60:
            level = "High"
        elif probability >= 40:
            level = "Moderate"
        elif probability >= 20:
            level = "Low"
        else:
            level = "Very Low"

        grouped_results.setdefault(level, []).append(item["branch"])

    return full_category, grouped_results


def format_chatbot_response(rank, category, quota, grouped_results) -> str:
    if not grouped_results:
        return (
            f"Based on the previous few years of counselling data for {category} "
            f"category under {quota} quota, your JEE Main rank of {rank} "
            "may be higher than the closing ranks observed for most branches.\n\n"
            "You may consider participating in all counselling rounds and "
            "exploring related branches or alternate options."
        )

    return (
        f"Based on the previous few years of counselling data for {category} "
        f"category under {quota} quota, and your JEE Main rank of {rank}, "
        "here are the branches you are likely to get.\n\n"
        "These predictions are based on historical cutoff trends across all "
        "counselling rounds. Actual allotment may vary depending on seat "
        "availability and competition in the current year."
    )


# ─────────────────────────────────────────────
#  Seat lookup helpers
# ─────────────────────────────────────────────

def run_seat_lookup(branch: str, year: int) -> dict | None:
    query = """
        SELECT quota, category, seat_count
        FROM seats
        WHERE canonical_branch = %s AND year = %s
        ORDER BY quota, category;
    """
    results = execute_query(query, (branch, year))
    if not results:
        return None

    total_seats = sum(r["seat_count"] for r in results)
    quota_summary: dict[str, int] = {}
    for r in results:
        quota_summary[r["quota"]] = quota_summary.get(r["quota"], 0) + r["seat_count"]

    return {
        "branch": branch,
        "year": year,
        "total_seats": total_seats,
        "quota_distribution": quota_summary,
        "details": results,
    }


def format_seat_response(seat_data: dict | None) -> str:
    if not seat_data:
        return "Seat data not found for the requested branch and year."

    response = (
        f"Seat distribution for {seat_data['branch']} in {seat_data['year']}:\n\n"
        f"Total Seats: {seat_data['total_seats']}\n\n"
        "Quota Distribution:\n"
    )
    for quota, count in seat_data["quota_distribution"].items():
        response += f"- {quota}: {count}\n"
    response += "\nYou can ask for category-wise details if needed."
    return response


# ─────────────────────────────────────────────
#  Branch comparison helper
# ─────────────────────────────────────────────



# ─────────────────────────────────────────────
#  App setup
# ─────────────────────────────────────────────

app = FastAPI()

# CORS: use ALLOWED_ORIGINS env var (comma-separated) in production,
# falls back to ["*"] for local dev.
_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
_allowed_origins = (
    [o.strip() for o in _origins_env.split(",") if o.strip()]
    if _origins_env != "*" else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=build_ui_response(
            response_type="error",
            message="System temporarily unavailable. Please try again."
        )
    )


@app.get("/health")
def health_check():
    try:
        execute_query("SELECT 1 AS ok;")
        return {
            "status": "ok",
            "database": "connected",
        }
    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "database": "unavailable",
            },
        )

# Conversation memory is now DB-backed (see db.py)
# EMPTY_MEMORY returns a fresh dict for new users.
EMPTY_MEMORY = lambda: {
    "rank": None,
    "base_category": None,
    "girl": False,
    "ph": False,
    "af": False,
    "ff": False,
    "tf": False,
    "quota": None,
    # Tracks what we're waiting for so quota shortcut "1"/"2" is context-aware
    "awaiting": None,
}

# ── Input limits ──────────────────────────────────
MAX_USER_ID_LEN = 64
MAX_MESSAGE_LEN = 500


# ─────────────────────────────────────────────
#  /predict  (direct REST endpoint)
# ─────────────────────────────────────────────

class PredictionRequest(BaseModel):
    rank: int
    base_category: str   # OPEN / SC / BC / ST / EWS
    quota: str           # "All India" or "Home State"
    girl: bool = False
    ph: bool = False
    af: bool = False
    ff: bool = False
    tf: bool = False


@app.post("/predict")
def predict_branch(data: PredictionRequest):
    full_category, grouped_results = run_prediction(
        data.rank, data.base_category,
        data.girl, data.ph, data.af, data.ff, data.tf,
        data.quota
    )
    return build_ui_response(
        response_type="prediction",
        message=format_chatbot_response(data.rank, full_category, data.quota, grouped_results),
        data={"rank": data.rank, "category": full_category, "quota": data.quota, "branches": grouped_results},
        actions=[
            {"label": "Check Seat Distribution", "intent": "seats"},
            {"label": "Start New Prediction", "intent": "reset"},
        ],
    )


# ─────────────────────────────────────────────
#  /seats  (direct REST endpoint)
# ─────────────────────────────────────────────

@app.get("/seats")
def get_seats(branch: str, year: int):
    seat_data = run_seat_lookup(branch.upper(), year)
    if not seat_data:
        return build_ui_response(
            response_type="error",
            message=f"No seat data found for {branch} in {year}."
        )

    return build_ui_response(
        response_type="seats",
        message=format_seat_response(seat_data),
        data=seat_data,
        actions=[
            {"label": "Check Another Branch", "intent": "seats"},
            {"label": "Go Back to Prediction", "intent": "predict"},
        ],
    )


# ─────────────────────────────────────────────
#  /chat  (conversational endpoint)
# ─────────────────────────────────────────────

@app.post("/chat")
def chat(
    user_id: str = Body(...),
    user_message: str = Body(...)
):
    # ── Input sanitisation ───────────────────────────────────────────────────
    user_id = user_id.strip()[:MAX_USER_ID_LEN]
    user_message = user_message.strip()[:MAX_MESSAGE_LEN]

    if not user_id or not user_message:
        return build_ui_response(
            response_type="error",
            message="Please provide a valid message.",
        )

    # Load memory from DB (persists across restarts)
    memory = load_memory(user_id, EMPTY_MEMORY)

    # ── Step 1: extract everything from the message ──────────────────────────

    extracted_rank     = extract_rank(user_message)
    category_info      = extract_category(user_message)
    extracted_quota    = extract_quota(user_message)
    extracted_branches = extract_branches(user_message)
    extracted_year     = extract_year(user_message)
    intent             = detect_intent(user_message)

    # ── Step 2: handle numbered shortcut ONLY when we are waiting for quota ──
    # FIX: quota shortcut was running unconditionally and being overwritten.
    # Now it only applies when we're specifically waiting for a quota answer.
    if memory["awaiting"] == "quota":
        stripped = user_message.strip()
        if stripped == "1":
            extracted_quota = "Home State"
        elif stripped == "2":
            extracted_quota = "All India"

    # ── Step 3: update memory with anything newly extracted ──────────────────

    if extracted_rank:
        memory["rank"] = extracted_rank

    if category_info["base_category"]:
        memory["base_category"] = category_info["base_category"]
        memory["girl"] = category_info["girl"]
        memory["ph"]   = category_info["ph"]
        memory["af"]   = category_info["af"]
        memory["ff"]   = category_info["ff"]
        memory["tf"]   = category_info["tf"]

    if extracted_quota:
        memory["quota"] = extracted_quota
        memory["awaiting"] = None   # quota received, clear the wait flag

    # Persist updated memory to DB
    save_memory(user_id, memory)

    # ── Step 4: run prediction when all three required fields are present ─────

    if memory["rank"] and memory["base_category"] and memory["quota"]:

        # Capture values before clearing memory
        rank          = memory["rank"]
        base_category = memory["base_category"]
        girl, ph, af  = memory["girl"], memory["ph"], memory["af"]
        ff, tf        = memory["ff"], memory["tf"]
        quota         = memory["quota"]

        # Reset for next conversation (clear from DB)
        delete_memory(user_id)

        full_category, grouped_results = run_prediction(
            rank, base_category, girl, ph, af, ff, tf, quota
        )

        return build_ui_response(
            response_type="prediction",
            message=format_chatbot_response(rank, full_category, quota, grouped_results),
            data={
                "rank": rank,
                "category": full_category,
                "quota": quota,
                "branches": grouped_results,
            },
            actions=[
                {"label": "Check Seat Distribution", "intent": "seats"},
                {"label": "Start New Prediction",    "intent": "reset"},
            ],
            suggestions=[
                "Show seats for CSE 2025",
                "What is the counselling process?",
            ],
        )

    # ── Step 5: prompt for missing fields ─────────────────────────────────────
    # FIX: these were in the right place but now we also set memory["awaiting"]
    # so the quota shortcut ("1"/"2") is context-aware.

    if memory["rank"] and memory["base_category"] and not memory["quota"]:
        memory["awaiting"] = "quota"
        save_memory(user_id, memory)
        return build_ui_response(
            response_type="question",
            message=(
                f"I have your rank as {memory['rank']} and category as "
                f"{memory['base_category']}.\n\n"
                "Please confirm your quota:\n"
                "1️⃣ Home State\n"
                "2️⃣ All India\n\n"
                "You can type 'Home State', 'All India', or just 1 or 2."
            ),
            actions=[
                {"label": "Home State", "value": "Home State"},
                {"label": "All India",  "value": "All India"},
            ],
        )

    # ── Step 5b: only ask for missing prediction fields when user wants a prediction ─
    # FIX: these guards previously ran for ALL intents — now only for predict/unknown
    # and caused messages like "Tell me your rank" when user asked about counselling.
    # They now only trigger when intent is "predict" or unknown (no clear other intent).

    # If user typed just a branch name (e.g. "cse"), treat it as a seats request
    if intent == "unknown" and extracted_branches:
        intent = "seats"

    non_prediction_intents = {"counselling_info", "seats", "fees"}

    if intent not in non_prediction_intents:

        if memory["rank"] and not memory["base_category"]:
            return build_ui_response(
                response_type="question",
                message=(
                    f"I have your rank as {memory['rank']}.\n\n"
                    "Please tell me your category (OPEN / BC / SC / ST / EWS)."
                ),
                actions=[
                    {"label": "OPEN"}, {"label": "BC"},
                    {"label": "SC"},   {"label": "ST"}, {"label": "EWS"},
                ],
            )

        if not memory["rank"]:
            return build_ui_response(
                response_type="question",
                message="Please tell me your JEE Main CRL (Common Rank List) rank to get started.\n\n⚠️ Note: Please enter your CRL rank, not your category rank.",
            )

    # ── Step 6: intent-specific flows ─────────────────────────────────────────

    if intent == "predict":
        # Guide the user toward providing rank / category / quota
        if extracted_rank and category_info["base_category"] and extracted_quota:
            msg = (
                f"I detected your rank as {extracted_rank}, "
                f"category as {category_info['base_category']}, "
                f"and quota as {extracted_quota}. Running prediction…"
            )
        elif extracted_rank and category_info["base_category"]:
            msg = (
                f"I detected your rank as {extracted_rank} and category as "
                f"{category_info['base_category']}. "
                "Please confirm your quota (Home State or All India)."
            )
        elif extracted_rank:
            msg = (
                f"I detected your rank as {extracted_rank}. "
                "Please tell me your category and quota."
            )
        else:
            msg = (
                "Please tell me your JEE Main CRL rank, category, and quota "
                "(Home State or All India).\n\n"
                "⚠️ Note: Please enter your CRL (Common Rank List) rank, not your category rank."
            )

        return build_ui_response(response_type="question", message=msg)

    # ── Seats intent ──────────────────────────────────────────────────────────
    # FIX: was split into two duplicate elif blocks — merged into one.

    elif intent == "seats":
        if extracted_branches:
            year = extracted_year or 2025   # default to 2025 if not specified
            seat_data = run_seat_lookup(extracted_branches[0], year)
            return build_ui_response(
                response_type="seats",
                message=format_seat_response(seat_data),
                data=seat_data or {},
                actions=[
                    {"label": "Check Another Branch", "intent": "seats"},
                    {"label": "Go Back to Prediction", "intent": "predict"},
                ],
                suggestions=["Show seats for IT", "Show seats for Mechanical", "Show seats for ECE", "Show seats for Civil"],
            )
        else:
            return build_ui_response(
                response_type="question",
                message="Please tell me which branch you want seat details for.",
            )


    elif intent == "fees":
        info = COUNSELLING_DATA["fee_structure"]
        return build_ui_response(
            response_type="stream",
            message=info["message"],
            data={"subtopic": "fee_structure", "title": info["title"]},
            actions=info.get("actions", []),
        )

    elif intent == "counselling_info":
        subtopic = detect_counselling_subtopic(user_message)
        info     = COUNSELLING_DATA.get(subtopic, COUNSELLING_DATA["overview"])

        return build_ui_response(
            response_type="stream",
            message=info["message"],
            data={"subtopic": subtopic, "title": info["title"]},
            actions=info.get("actions", []),
            suggestions=info.get("suggestions", []),
        )

    # ── Fallback ──────────────────────────────────────────────────────────────

    return build_ui_response(
        response_type="unknown",
        message=(
            "I'm the HBTU Counselling Assistant — I can help you with:\n\n"
            "📊 **Branch Prediction** — Tell me your JEE Main CRL rank, category & quota "
            "and I'll predict which branches you're likely to get.\n"
            "💺 **Seat Distribution** — Ask about the seat matrix for any branch.\n"
            "📋 **Counselling Process** — Rounds, FREEZE/FLOAT, documents, refund & more.\n\n"
            "Try one of the options below or type your question!"
        ),
        actions=[
            {"label": "🎯 Predict My Branch",   "value": "I want to predict my branch"},
            {"label": "💺 Seat Distribution",   "value": "Show seat distribution"},
            {"label": "📋 Counselling Process", "value": "Explain the counselling process"},
        ],
    )
