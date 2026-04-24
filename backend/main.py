from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from collections import defaultdict
from db import execute_query, load_memory, save_memory, delete_memory, log_user_query
from mba_knowledge import detect_mba_intent, get_mba_response
from mca_knowledge import detect_mca_intent, get_mca_response
from bsms_knowledge import detect_bsms_intent, get_bsms_response
from placements_stats import get_placement_response, get_placement_files_health
from ai_brain import ai_brain_response, localize_response_text
from language_utils import detect_language_style, normalize_multilingual_query
from utils import build_category
import asyncio
import logging
import os
import re
import time

logger = logging.getLogger(__name__)


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


HELPDESK_CONTACTS = {
    "ug_all": [
        {"name": "Prof. Lalit Kumar Singh", "designation": "Dy. Coordinator", "topic": "All UG Courses", "mobile": "7081300565"},
        {"name": "Prof. Vinay Pratap Singh", "designation": "Dy. Coordinator", "topic": "All UG Courses", "mobile": "9721456084"},
    ],
    "pg_all": [
        {"name": "Dr. Amit Kumar Rathoure", "designation": "Dy. Coordinator", "topic": "All PG Courses", "mobile": "6389950713"},
    ],
    "btech": [
        {"name": "Prof. Lalit Kumar Singh", "designation": "Dy. Coordinator", "topic": "All UG Courses", "mobile": "7081300565"},
        {"name": "Prof. Vinay Pratap Singh", "designation": "Dy. Coordinator", "topic": "All UG Courses", "mobile": "9721456084"},
        {"name": "Dr. Nand Kishore", "designation": "Asstt. Coordinator", "topic": "B.Tech & B.Tech (Working Professional)", "mobile": "8853038570"},
        {"name": "Dr. Rajkamal Kushwaha", "designation": "Asstt. Coordinator", "topic": "B.Tech", "mobile": "7081300606"},
    ],
    "btech_lateral": [
        {"name": "Mr. Gaurav Singh", "designation": "Asstt. Coordinator", "topic": "B.Tech Lateral Entry / NRI", "mobile": "7607489600"},
    ],
    "btech_wp": [
        {"name": "Dr. Nand Kishore", "designation": "Asstt. Coordinator", "topic": "B.Tech (Working Professional)", "mobile": "8853038570"},
    ],
    "bba": [
        {"name": "Dr. K.K. Bhartiya", "designation": "Asstt. Coordinator", "topic": "BBA", "mobile": "9696913773"},
    ],
    "bsms": [
        {"name": "Dr. Shivam Shreevastava", "designation": "Asstt. Coordinator", "topic": "BS-MS", "mobile": "8527904993"},
    ],
    "bpharma": [
        {"name": "Ms. Priyanka Mishra", "designation": "Asstt. Coordinator", "topic": "B.Pharma / B.Pharma Lateral Entry", "mobile": "9793886919"},
    ],
    "mca": [
        {"name": "Dr. Siddharth Srivastava", "designation": "Asstt. Coordinator", "topic": "MCA", "mobile": "9455280244"},
    ],
    "mba": [
        {"name": "Dr. Yogesh Puri", "designation": "Asstt. Coordinator", "topic": "MBA", "mobile": "8795838169"},
    ],
    "mtech": [
        {"name": "Dr. Rajkamal Kushwaha", "designation": "Asstt. Coordinator", "topic": "M.Tech & Ph.D", "mobile": "7081300606"},
        {"name": "Dr. Roma Agrahari", "designation": "Asstt. Coordinator", "topic": "M.Tech & Ph.D", "mobile": "7081300606"},
    ],
    "phd": [
        {"name": "Dr. Rajkamal Kushwaha", "designation": "Asstt. Coordinator", "topic": "M.Tech & Ph.D", "mobile": "7081300606"},
        {"name": "Dr. Roma Agrahari", "designation": "Asstt. Coordinator", "topic": "M.Tech & Ph.D", "mobile": "7081300606"},
    ],
    "msc": [
        {"name": "Dr. Abhinav Srivastav", "designation": "Asstt. Coordinator", "topic": "M.Sc. (Physics, Chemistry, Math)", "mobile": "6389950761"},
        {"name": "Dr. Neeraj Mishra", "designation": "Asstt. Coordinator", "topic": "M.Sc. (Biotechnology, Biochemistry)", "mobile": "8318891003"},
    ],
    "msc_physics": [{"name": "Dr. Abhinav Srivastav", "designation": "Asstt. Coordinator", "topic": "M.Sc. (Physics, Chemistry, Math)", "mobile": "6389950761"}],
    "msc_chemistry": [{"name": "Dr. Abhinav Srivastav", "designation": "Asstt. Coordinator", "topic": "M.Sc. (Physics, Chemistry, Math)", "mobile": "6389950761"}],
    "msc_maths": [{"name": "Dr. Abhinav Srivastav", "designation": "Asstt. Coordinator", "topic": "M.Sc. (Physics, Chemistry, Math)", "mobile": "6389950761"}],
    "msc_biotech": [{"name": "Dr. Neeraj Mishra", "designation": "Asstt. Coordinator", "topic": "M.Sc. (Biotechnology, Biochemistry)", "mobile": "8318891003"}],
    "international": [
        {"name": "Prof. Sanjiv Kumar", "designation": "Dean, International Student Affairs", "topic": "International / NRI Admission", "mobile": "7081300678"},
    ],
    "nri": [
        {"name": "Mr. Gaurav Singh", "designation": "Asstt. Coordinator", "topic": "B.Tech Lateral Entry / NRI", "mobile": "7607489600"},
        {"name": "Prof. Sanjiv Kumar", "designation": "Dean, International Student Affairs", "topic": "International / NRI Admission", "mobile": "7081300678"},
    ],
    "payment": [
        {"name": "Mr. Pranjal Nagayach", "designation": "F&AO", "topic": "Payment Related", "mobile": "9721456003"},
        {"name": "Mr. Sanjay Kumar Singh", "designation": "Assistant Accountant", "topic": "Payment Related", "mobile": "9721456070"},
        {"name": "Yash Singh", "designation": "", "topic": "Payment Related", "mobile": "8299197019"},
        {"name": "Kashika Sahil Taneja", "designation": "", "topic": "Payment Related", "mobile": "8303713728"},
    ],
    "admin": [
        {"name": "Registrar", "designation": "Registrar", "topic": "Registrar Office", "mobile": "9721456027"},
        {"name": "Mr. Sushil Kumar", "designation": "", "topic": "Administrative", "mobile": ""},
    ],
    "coordinator": [
        {
            "name": "Prof. Vandana Dixit Kaushik",
            "designation": "Dean of Academic Affairs & Coordinator Admissions 2026",
            "topic": "All Admission Queries",
            "mobile": "9721456057 / 9554449900",
            "email": "admission@hbtu.ac.in",
        },
    ],
}


ADMISSION_PROGRAMS_2026 = {
    "programs": [
        {"no": 1, "programme": "B.Tech.", "admission_through": "JEE Mains (2026)", "schedule": "May 2026"},
        {"no": 2, "programme": "BS-MS (Mathematics and Data Science)", "admission_through": "JEE Mains (2026) / CUET-UG 2026", "schedule": "May 2026"},
        {"no": 3, "programme": "B.Tech. (Lateral Entry)", "admission_through": "CUET-UG 2026", "schedule": "May 2026"},
        {"no": 4, "programme": "B.Tech. - Biotechnology & B.Tech. - Biotechnology (Lateral Entry)", "admission_through": "CUET-UG 2026", "schedule": "May 2026"},
        {"no": 5, "programme": "B.Pharm. & B.Pharm. (Lateral Entry)", "admission_through": "CUET-UG 2026", "schedule": "May 2026"},
        {"no": 6, "programme": "BBA", "admission_through": "CUET-UG 2026", "schedule": "May 2026"},
        {"no": 7, "programme": "MCA", "admission_through": "NIMCET 2026", "schedule": "May 2026"},
        {"no": 8, "programme": "B.Tech. (Working Professional)", "admission_through": "UET 2026", "schedule": "May 2026"},
        {"no": 9, "programme": "M.Tech.", "admission_through": "GATE / CUET-PG 2026 / UET 2026", "schedule": "Mid-April 2026"},
        {"no": 10, "programme": "M.Sc.", "admission_through": "IIT JAM 2026 / GAT-B 2026 / CUET-PG 2026 / UET 2026", "schedule": "Mid-April 2026"},
        {"no": 11, "programme": "PhD", "admission_through": "GATE / UGC (NET) / CSIR (NET) / UET 2026", "schedule": "Mid-April 2026"},
        {"no": 12, "programme": "MBA", "admission_through": "CAT 2025 / CMAT 2026 / AIMA-MAT 2025-26 / CUET-PG 2026 / UET 2026*", "schedule": "Open from March 2026"},
    ],
    "note": "* UET 2026: The University Entrance Test 2026 will be conducted only if seats remain vacant.",
    "apply_link": "https://erp.hbtu.ac.in/HBTUAdmissions.html",
    "info_website": "www.hbtu.ac.in",
    "contact_email": "admission@hbtu.ac.in",
}


def extract_branches(user_message: str) -> list[str]:
    """Detect one or more canonical branch names from message using token-safe matching."""
    message = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", user_message.lower())).strip()
    padded_message = f" {message} "
    detected = []
    for canonical, aliases in BRANCH_ALIASES.items():
        for alias in aliases:
            norm_alias = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", alias.lower())).strip()
            if not norm_alias:
                continue
            if f" {norm_alias} " in padded_message:
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
    normalized = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", message)).strip()
    padded = f" {normalized} "

    def has_phrase(phrase: str) -> bool:
        norm_phrase = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", phrase.lower())).strip()
        return bool(norm_phrase) and f" {norm_phrase} " in padded

    base_category = None

    if any(has_phrase(word) for word in ["general", "gen", "open", "ur", "unreserved"]):
        base_category = "OPEN"
    elif any(has_phrase(word) for word in ["obc", "obc ncl", "bc", "backward class"]):
        base_category = "BC"
    elif any(has_phrase(word) for word in ["sc", "scheduled caste"]):
        base_category = "SC"
    elif any(has_phrase(word) for word in ["st", "scheduled tribe"]):
        base_category = "ST"
    elif any(has_phrase(word) for word in ["ews", "economically weaker section"]):
        base_category = "EWS"

    girl = any(word in message for word in ["girl", "girls", "female", "woman"])
    ph = (
        re.search(r"\bph\b|\bpwd\b", message) is not None
        or any(word in message for word in ["disabled", "physically handicapped", "handicapped"])
    )
    af = re.search(r"\baf\b", message) is not None or any(
        word in message for word in ["armed forces", "defence", "defense"]
    )
    ff = re.search(r"\bff\b", message) is not None or "freedom fighter" in message
    tf = re.search(r"\btf\b|\btfw\b", message) is not None or "tuition fee waiver" in message

    return {
        "base_category": base_category,
        "girl": girl,
        "ph": ph,
        "af": af,
        "ff": ff,
        "tf": tf,
    }


def has_subcategory(category_info: dict) -> bool:
    return any(category_info.get(key) for key in ["girl", "ph", "af", "ff", "tf"])


def memory_has_subcategory(memory: dict) -> bool:
    return any(memory.get(key) for key in ["girl", "ph", "af", "ff", "tf"])


def is_no_subcategory_reply(user_message: str) -> bool:
    message = re.sub(r"\s+", " ", user_message.lower()).strip()
    if message in {
        "no", "none", "nope", "na", "n/a", "not applicable",
        "no subcategory", "no sub category", "none of these",
        "not any", "normal", "only base category",
    }:
        return True

    return any(
        phrase in message for phrase in [
            "koi subcategory nahi", "koi sub category nahi", "sub category nahi",
            "subcategory nahi", "koi nahi", "nahi hai", "nhi hai",
            "sirf base category", "only base",
        ]
    )


def should_reset_prediction_memory(
    user_message: str,
    detection_message: str,
    memory: dict,
    extracted_rank: int | None,
    category_info: dict,
    extracted_quota: str | None,
) -> bool:
    """
    Reset stale prediction slots when user starts a fresh rank declaration
    (common in Hinglish, e.g. "meri rank 43045 hai") without category/quota.
    """
    if not extracted_rank:
        return False

    if category_info.get("base_category") or extracted_quota or has_subcategory(category_info):
        return False

    if not (memory.get("base_category") or memory.get("quota") or memory_has_subcategory(memory)):
        return False

    msg = user_message.lower()
    msg_norm = re.sub(r"\s+", " ", detection_message.lower()).strip()
    rank_decl_cues = [
        "my rank", "meri rank", "mera rank", "rank is", "rank hai", "air",
    ]
    short_rank_statement = len(msg_norm.split()) <= 8 and "rank" in msg_norm

    return any(cue in msg for cue in rank_decl_cues) or short_rank_statement


def prediction_prompt_text(prompt_key: str, language_style: str, **kwargs) -> str:
    """Deterministic short prompts so Hinglish follow-ups don't drift in person/tense."""
    rank = kwargs.get("rank")
    base_category = kwargs.get("base_category")

    if language_style == "hinglish":
        if prompt_key == "ask_rank":
            return (
                "Please apni JEE Main CRL rank batayein taaki prediction start kar saken.\n\n"
                "Note: category rank nahi, CRL rank bhejein."
            )
        if prompt_key == "ask_base_category":
            return (
                f"Aapki rank {rank} note ho gayi hai.\n\n"
                "Aapki base category kya hai? (OPEN / BC / SC / ST / EWS)"
            )
        if prompt_key == "ask_subcategory":
            return (
                f"Aapki rank {rank} aur base category {base_category} note ho gayi hai.\n\n"
                "Kya aap kisi sub-category se belong karte hain?"
                " Aap Girl, PH/PwD, AF, FF, TFW, ya None type kar sakte hain."
            )
        if prompt_key == "ask_quota":
            return (
                f"Aapki rank {rank} aur category {base_category} note ho gayi hai.\n\n"
                "Ab apna quota confirm karein:\n"
                "1) Home State\n"
                "2) All India\n\n"
                "Aap 'Home State', 'All India', ya sirf 1/2 type kar sakte hain."
            )

    # English default (also used when style is hindi to keep prompts stable).
    if prompt_key == "ask_rank":
        return (
            "Please tell me your JEE Main CRL (Common Rank List) rank to get started.\n\n"
            "Note: Please enter your CRL rank, not your category rank."
        )
    if prompt_key == "ask_base_category":
        return (
            f"I have your rank as {rank}.\n\n"
            "Please tell me your base category (OPEN / BC / SC / ST / EWS). "
            "After that, I will ask if any sub-category like Girl, PH, AF, FF, or TFW applies."
        )
    if prompt_key == "ask_subcategory":
        return (
            f"I have your rank as {rank} and base category as {base_category}.\n\n"
            "Do you belong to any sub-category? You can type Girl, PH/PwD, AF, FF, TFW, or None."
        )
    if prompt_key == "ask_quota":
        return (
            f"I have your rank as {rank} and category as {base_category}.\n\n"
            "Please confirm your quota:\n"
            "1) Home State\n"
            "2) All India\n\n"
            "You can type 'Home State', 'All India', or just 1 or 2."
        )
    return ""


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


def detect_helpdesk_query(user_message: str) -> str | None:
    """
    Returns a HELPDESK_CONTACTS key if the user is asking for
    a contact/helpdesk person, else returns None.
    """
    message = re.sub(r"\s+", " ", user_message.lower()).strip()

    contact_triggers = [
        "contact", "helpdesk", "help desk", "whom to contact",
        "who to call", "phone number", "mobile number", "call",
        "coordinator", "who is", "email", "reach out", "get in touch",
        "admission office", "number for", "contact for", "contact of",
        "contact person", "contact details", "daa office", "dean",
        "vc", "vice chancellor", "head of", "where is",
    ]
    if not any(t in message for t in contact_triggers):
        return None

    if any(w in message for w in ["payment", "pay", "fee payment", "finance", "fao", "accountant", "refund query"]):
        return "payment"
    if any(w in message for w in ["daa office", "vc", "vice chancellor", "head of", "dean of", "registrar office"]):
        return "admin"
    if any(w in message for w in ["international", "foreign", "overseas"]):
        return "international"
    if any(w in message for w in ["nri"]):
        return "nri"
    if any(w in message for w in ["mba"]):
        return "mba"
    if re.search(r"\bmca\b", message):
        return "mca"
    if any(w in message for w in ["bs-ms", "bsms", "bs ms", "mathematics and data science", "mds"]):
        return "bsms"
    if any(w in message for w in ["b.pharma", "b pharma", "bpharma", "pharma"]):
        return "bpharma"
    if any(w in message for w in ["bba"]):
        return "bba"
    if any(w in message for w in ["working professional", "b.tech wp", "btech wp"]):
        return "btech_wp"
    if any(w in message for w in ["lateral entry", "lateral"]):
        return "btech_lateral"
    if any(w in message for w in ["m.tech", "mtech"]):
        return "mtech"
    if any(w in message for w in ["ph.d", "phd", "doctorate"]):
        return "phd"
    if re.search(r"\bm\.?sc\b|\bmaster of science\b", message):
        if any(w in message for w in ["biotech", "biochem"]):
            return "msc_biotech"
        if any(w in message for w in ["physics"]):
            return "msc_physics"
        if any(w in message for w in ["chemistry"]):
            return "msc_chemistry"
        if any(w in message for w in ["math", "maths"]):
            return "msc_maths"
        return "msc"
    if any(w in message for w in ["b.tech", "btech", "jee", "ug course", "undergraduate"]):
        return "btech"
    if any(w in message for w in ["pg course", "postgraduate", "post graduate"]):
        return "pg_all"
    if any(w in message for w in ["admin", "registrar", "administrative"]):
        return "admin"
    if any(w in message for w in ["admission", "coordinator", "dean"]):
        return "coordinator"
    if any(w in message for w in ["ug", "under graduate"]):
        return "ug_all"

    return "coordinator"


def _format_contacts(contacts: list[dict]) -> str:
    lines = []
    for c in contacts:
        name_line = f"**{c['name']}**"
        if c.get("designation"):
            name_line += f" - {c['designation']}"
        lines.append(name_line)
        lines.append(f"  Phone: {c['mobile']}")
        if c.get("email"):
            lines.append(f"  Email: {c['email']}")
        lines.append("")
    return "\n".join(lines).strip()


def get_helpdesk_response(key: str) -> dict:
    contacts = HELPDESK_CONTACTS.get(key, HELPDESK_CONTACTS["coordinator"])

    topic_labels = {
        "btech": "B.Tech Admission",
        "btech_lateral": "B.Tech Lateral Entry / NRI",
        "btech_wp": "B.Tech (Working Professional)",
        "bsms": "BS-MS (Mathematics & Data Science)",
        "bba": "BBA Admission",
        "bpharma": "B.Pharma Admission",
        "mca": "MCA Admission",
        "mba": "MBA Admission",
        "mtech": "M.Tech / Ph.D Admission",
        "phd": "Ph.D Admission",
        "msc": "M.Sc. Admission",
        "msc_physics": "M.Sc. Physics / Chemistry / Math",
        "msc_chemistry": "M.Sc. Physics / Chemistry / Math",
        "msc_maths": "M.Sc. Physics / Chemistry / Math",
        "msc_biotech": "M.Sc. Biotechnology / Biochemistry",
        "international": "International / NRI Admission",
        "nri": "NRI Admission",
        "payment": "Payment / Fee Related",
        "admin": "Administrative / Registrar",
        "coordinator": "Admissions 2026-27 (Overall)",
        "ug_all": "All UG Courses",
        "pg_all": "All PG Courses",
    }
    label = topic_labels.get(key, "Admissions 2026-27")

    message = (
        "## HBTU Admissions Helpdesk 2026-27\n"
        f"**Query: {label}**\n\n"
        f"{_format_contacts(contacts)}\n\n"
        "*Please contact during office hours: 10:00 AM - 5:00 PM*\n"
        "For email queries: **admission@hbtu.ac.in**"
    )

    return {
        "message": message,
        "data": {"contacts": contacts, "topic": label},
        "actions": [
            {"label": "B.Tech Contact", "value": "Who to contact for B.Tech admission?"},
            {"label": "MBA Contact", "value": "Who to contact for MBA admission?"},
            {"label": "MCA Contact", "value": "Who to contact for MCA admission?"},
            {"label": "Payment Help", "value": "Who to contact for payment issues?"},
        ],
        "suggestions": [
            "Who to contact for BS-MS admission?",
            "Who to contact for M.Tech admission?",
            "Who is the admission coordinator for 2026?",
        ],
    }


def detect_programs_query(user_message: str) -> bool:
    """
    Returns True when user is asking about the full list of programs,
    admission routes, or the overall 2026-27 schedule.
    """
    message = user_message.lower()
    triggers = [
        "all courses", "all programs", "all programmes",
        "programs offered", "programmes offered", "courses offered",
        "admission brochure", "2026 brochure", "2026-27 brochure",
        "which courses", "what courses", "list of courses",
        "admission schedule 2026", "admission process 2026",
        "how to apply 2026", "apply for admission 2026",
        "tentative schedule", "admission through",
        "jee mains 2026", "cuet 2026", "nimcet 2026",
    ]
    return any(t in message for t in triggers)


def get_programs_response() -> str:
    rows = []
    for p in ADMISSION_PROGRAMS_2026["programs"]:
        rows.append(
            f"| {p['no']} | {p['programme']} | {p['admission_through']} | {p['schedule']} |"
        )
    table = "\n".join(rows)

    return (
        "## HBTU Admission Brochure 2026-27\n\n"
        "| # | Programme | Admission Through | Tentative Schedule |\n"
        "|---|---|---|---|\n"
        f"{table}\n\n"
        f"**Note:** {ADMISSION_PROGRAMS_2026['note']}\n\n"
        f"**Apply at:** [{ADMISSION_PROGRAMS_2026['apply_link']}]({ADMISSION_PROGRAMS_2026['apply_link']})\n"
        f"**Info:** {ADMISSION_PROGRAMS_2026['info_website']}\n"
        f"**Email:** {ADMISSION_PROGRAMS_2026['contact_email']}"
    )


def normalize_query_for_detection(user_message: str) -> str:
    """Normalize common typos/Hinglish/Hindi terms before rule-based detection."""
    message = normalize_multilingual_query(user_message)

    replacements = {
        "placments": "placements",
        "placment": "placement",
        "comany": "company",
        "vists": "visits",
        "brouchere": "brochure",
        "registartion": "registration",
        "addmission": "admission",
        "cetogry": "category",
        "councelling": "counselling",
        "counceling": "counselling",
        "b.tec": "btech",
        "b-tech": "btech",
        "b tech": "btech",
        "bs ms": "bsms",
        "bs-ms": "bsms",
        "ओ बी सी": "obc",
        "ओबीसी": "obc",
        "होम स्टेट": "home state",
        "रैंक": "rank",
        "फीस": "fees",
        "btao": "tell me",
        "kab hoga": "schedule",
    }
    for old, new in replacements.items():
        message = message.replace(old, new)

    return re.sub(r"\s+", " ", message).strip()


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

    PLACEMENT_KEYWORDS = [
        ("placement statistics", 6), ("placement stats", 6),
        ("placements", 5), ("placement", 5),
        ("placement record", 6), ("recruiters", 5),
        ("median package", 6), ("average package", 6),
        ("highest package", 6), ("highest paying company", 6),
        ("highest package company", 6), ("highest package giving companies", 6),
        ("companies visited", 6), ("visited companies", 5),
        ("top companies", 6), ("companies come", 6), ("company visits", 6),
        ("ctc", 4), ("package", 3), ("offers", 2),
        ("stats", 2),
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
        ("brochure", 2), ("form date", 2), ("admission start", 2),
        # weak signals (1 pt)
        ("round", 1), ("process", 1), ("steps", 1), ("stages", 1),
        ("procedure", 1), ("timeline", 1), ("selection", 1),
        ("marks", 1), ("percentage", 1), ("physics", 1), ("mathematics", 1),
        ("certificate", 1), ("domicile", 1),
    ]

    def _phrase_present(phrase: str) -> bool:
        # Avoid false positives like "st" matching inside "hostels".
        if len(phrase) <= 3 and phrase.isalpha():
            return re.search(rf"\b{re.escape(phrase)}\b", message) is not None
        return phrase in message

    def _score(keywords):
        total = 0
        for phrase, weight in keywords:
            if _phrase_present(phrase):
                total += weight
        return total

    scores = {
        "predict":         _score(PREDICT_KEYWORDS),
        "seats":           _score(SEATS_KEYWORDS),
        "fees":            _score(FEES_KEYWORDS),
        "placement":       _score(PLACEMENT_KEYWORDS),
        "counselling_info": _score(COUNSELLING_KEYWORDS),
    }

    best_intent = max(scores, key=scores.get)
    if scores[best_intent] == 0:
        return "unknown"
    return best_intent


def detect_course_scope(user_message: str, extracted_branches: list[str] | None = None) -> str:
    """
    Detect which course the user explicitly refers to.
    Returns one of: mba, mca, bsms, btech, multiple, unknown.
    """
    message = user_message.lower()
    message_norm = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", message)).strip()
    padded_message = f" {message_norm} "

    def _has_norm_phrase(phrase: str) -> bool:
        norm_phrase = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", phrase.lower())).strip()
        return bool(norm_phrase) and f" {norm_phrase} " in padded_message

    has_mba = re.search(r"\bmba\b", message) is not None
    has_mca = re.search(r"\bmca\b", message) is not None
    has_bsms = any(_has_norm_phrase(p) for p in [
        "bsms",
        "bs ms",
        "bs-ms",
        "bachelors in mathematics and data science",
        "bachelor in mathematics and data science",
        "mathematics and data science",
        "maths and data science",
        "math and data science",
        "mds program",
    ])
    has_explicit_btech = (
        re.search(r"\bb\.?\s*tech\b|\bbtech\b|\bb\.?\s*tec\b", message) is not None
        or re.search(r"\bjee\b|\bcrl\b", message) is not None
    )
    # Branch mentions imply B.Tech only when non-B.Tech courses are not explicitly requested.
    has_btech = has_explicit_btech or (bool(extracted_branches) and not (has_mba or has_mca or has_bsms))

    active = sum([has_mba, has_mca, has_bsms, has_btech])
    if active > 1:
        return "multiple"
    if has_mba:
        return "mba"
    if has_mca:
        return "mca"
    if has_bsms:
        return "bsms"
    if has_btech:
        return "btech"
    return "unknown"


def infer_course_specific_intent(course: str, user_message: str) -> str:
    """
    Lightweight fallback intent resolver when course is explicit but
    phrase-based detector confidence is low.
    """
    message_norm = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", user_message.lower())).strip()

    def _has_any(phrases: list[str]) -> bool:
        padded_message = f" {message_norm} "
        for phrase in phrases:
            norm_phrase = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", phrase.lower())).strip()
            if not norm_phrase:
                continue
            if f" {norm_phrase} " in padded_message:
                return True
        return False

    if course == "mba":
        if _has_any(["gd/pi", "gd pi", "gdpi", "group discussion", "personal interview", "weightage", "rank formula"]):
            return "mba_rank_gdpi"
        if _has_any(["document", "documents", "certificate", "verification"]):
            return "mba_documents"
        if _has_any(["fee", "fees", "tuition", "cost", "payment"]):
            return "mba_fees"
        if _has_any(["seat", "seats", "intake", "seat matrix", "vacancy"]):
            return "mba_seats"
        if _has_any(["reservation", "quota", "category", "obc", "sc", "st", "ews", "upgl", "upaf", "uphc", "upff"]):
            return "mba_reservation"
        if _has_any(["eligibility", "qualification", "criteria", "cat", "cmat", "cuet", "mat", "uet"]):
            return "mba_eligibility"
        if _has_any(["register", "registration", "apply", "application", "form"]):
            return "mba_registration"
        if _has_any(["withdraw", "refund", "cancel", "exit"]):
            return "mba_withdrawal"
        if _has_any(["medical", "fitness", "disability", "pwd", "hearing", "vision"]):
            return "mba_medical"
        if _has_any(["schedule", "date", "dates", "timeline", "round"]):
            return "mba_schedule"
        return "unknown"

    if course == "mca":
        if _has_any(["document", "documents", "certificate", "verification"]):
            return "mca_documents"
        if _has_any(["fee", "fees", "tuition", "cost", "payment"]):
            return "mca_fees"
        if _has_any(["seat", "seats", "intake", "seat matrix", "vacancy"]):
            return "mca_seats"
        if _has_any(["reservation", "quota", "category", "obc", "sc", "st", "ews", "gl", "af", "ph", "ff"]):
            return "mca_reservation"
        if _has_any(["eligibility", "qualification", "criteria", "nimcet", "bca", "maths"]):
            return "mca_eligibility"
        if _has_any(["register", "registration", "apply", "application", "form", "choice filling"]):
            return "mca_registration"
        if _has_any(["withdraw", "refund", "cancel", "exit"]):
            return "mca_withdrawal"
        if _has_any(["medical", "fitness", "disability", "pwd", "hearing", "vision"]):
            return "mca_medical"
        if _has_any(["schedule", "date", "dates", "timeline", "round"]):
            return "mca_schedule"
        return "unknown"

    if course == "bsms":
        if _has_any(["document", "documents", "certificate", "verification", "aadhar", "checklist"]):
            return "bsms_documents"
        if _has_any(["fee", "fees", "tuition", "cost", "payment", "80000", "80 000"]):
            return "bsms_fees"
        if _has_any(["seat", "seats", "intake", "seat matrix", "vacancy", "total seats", "60 seats"]):
            return "bsms_seats"
        if _has_any(["reservation", "quota", "category", "obc", "sc", "st", "ews", "gl", "af", "ph", "ff"]):
            return "bsms_reservation"
        if _has_any(["eligibility", "qualification", "criteria", "jee", "cuet", "10 2", "marks", "percentage"]):
            return "bsms_eligibility"
        if _has_any(["register", "registration", "apply", "application", "form", "choice filling", "choice locking"]):
            return "bsms_registration"
        if _has_any(["withdraw", "refund", "cancel", "exit", "processing fee"]):
            return "bsms_withdrawal"
        if _has_any(["medical", "fitness", "disability", "pwd", "hearing", "vision", "cmo"]):
            return "bsms_medical"
        if _has_any(["rank", "crl", "air", "normalised", "normalized", "tie break", "cuet 308", "cuet 319"]):
            return "bsms_rank_cuet"
        if _has_any(["schedule", "date", "dates", "timeline", "round", "phase", "july", "august"]):
            return "bsms_schedule"
        if _has_any(["round", "rounds", "phase 1", "phase 2", "phase 3", "counselling"]):
            return "bsms_rounds"
        return "unknown"

    return "unknown"


def should_clarify_course(
    user_message: str,
    intent: str,
    course_scope: str,
    extracted_branches: list[str],
) -> bool:
    """
    Ask user to specify course when query is common across programs
    and the message doesn't clearly target MBA/MCA/BSMS/B.Tech.
    """
    if course_scope != "unknown":
        return False
    if extracted_branches:
        return False

    message = user_message.lower()
    common_course_cues = [
        "seat", "seats", "intake", "capacity",
        "fee", "fees", "tuition", "cost",
        "document", "documents", "certificate", "verification",
        "reservation", "quota", "category",
        "eligibility", "eligible", "counselling", "counseling",
        "admission", "register", "registration", "schedule", "timeline",
    ]

    if intent in {"seats", "fees", "counselling_info"}:
        return True
    if intent == "unknown" and any(cue in message for cue in common_course_cues):
        return True
    return False


def is_prediction_followup(
    user_message: str,
    extracted_rank: int | None,
    category_info: dict,
    extracted_quota: str | None,
) -> bool:
    """
    Decide whether an ambiguous message should continue prediction flow.
    This prevents generic chatter from hijacking into rank/category prompts.
    """
    if (
        extracted_rank
        or category_info.get("base_category")
        or has_subcategory(category_info)
        or extracted_quota
    ):
        return True

    message = user_message.lower().strip()
    if message in {
        "1", "2", "home state", "all india", "hs", "ai",
        "no", "none", "nope", "na", "n/a", "not applicable",
    }:
        return True

    prediction_keywords = [
        "predict", "prediction", "rank", "quota", "category",
        "chance", "chances", "branch", "option", "options"
    ]
    return any(k in message for k in prediction_keywords)


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
            "## B.Tech Fee Structure (Session 2025-26)\n\n"
            "| Component | Amount (Rs.) |\n"
            "|---|---:|\n"
            "| Tuition Fee | 75,000 |\n"
            "| Registration, Exam & Certification | 10,000 |\n"
            "| Facility Charges | 30,500 |\n"
            "| Medical Fee | 3,000 |\n"
            "| Training & Placement | 4,000 |\n"
            "| Activity Charges | 3,000 |\n"
            "| Caution Money | 5,000 |\n"
            "| University Alumni Fund | 1,500 |\n"
            "| Student Aid Fund | 1,500 |\n"
            "| Contingency & Miscellaneous | 1,500 |\n"
            "| **Total Academic Fee** | **1,35,000** |\n\n"
            "### Registration Fee\n"
            "| Item | Amount (Rs.) | Notes |\n"
            "|---|---:|---|\n"
            "| Counselling Registration | 2,500 | Non-refundable; paid at hbtu.admissions.nic.in |\n"
            "| Phase 2 Re-registration (Round 4) | 2,500 | Fresh registration required in eligible cases |\n\n"
            "### Fee Waiver\n"
            "| Type | Benefit | Condition |\n"
            "|---|---|---|\n"
            "| Tuition Fee Waiver (TFW) | 75,000 tuition waived; other 60,000 payable | Family income <= 8 lakh/year (Certificate No. 11) |\n"
            "| Full Fee Waiver | 2 seats per branch for SC/ST girls | Merit basis |\n\n"
            "### Payment Modes\n"
            "- Demand Draft (in favour of 'Finance Controller, HBTU Kanpur', payable at Kanpur)\n"
            "- Cash\n"
            "- Online mode (check one-time payment limit of debit/credit card)\n"
            "\n"
            "⚠️ Full payment only; partial payment is not allowed."
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
    category_candidates = build_category_lookup_values(
        base=base_category, girl=girl, ph=ph, af=af, ff=ff, tf=tf
    )
    full_category = category_candidates[0]

    query = """
        WITH yearly_success AS (
            SELECT
                canonical_branch,
                year,
                MAX(
                    CASE
                        WHEN category = ANY(%s)
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

    raw_results = execute_query(query, (category_candidates, quota, rank))

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


def build_category_lookup_values(base, girl=False, ph=False, af=False, ff=False, tf=False) -> list[str]:
    """
    Return category labels in the same shape as the cutoff database.
    The source CSV stores OPEN+GIRL as "OPEN GIRL" and OPEN+TF as "OPEN (TF)",
    while most other subcategories use parentheses, e.g. "BC(GIRL)".
    """
    base = base.strip().upper()

    if ph:
        return [f"{base}(PH)"]
    if af:
        return [f"{base}(AF)"]
    if ff:
        return [f"{base}(FF)"]
    if tf:
        if base == "OPEN":
            return ["OPEN (TF)", "OPEN(TF)"]
        return [f"{base}(TF)"]
    if girl:
        if base == "OPEN":
            return ["OPEN GIRL", "OPEN(GIRL)"]
        return [f"{base}(GIRL)"]

    return [base]


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
    summary_lines = [
        "| Quota | Seats |",
        "|---|---:|",
    ]
    for quota, count in seat_data["quota_distribution"].items():
        summary_lines.append(f"| {quota} | {count} |")

    detail_lines = [
        "| Quota | Category | Seats |",
        "|---|---|---:|",
    ]
    for row in seat_data.get("details", []):
        detail_lines.append(
            f"| {row['quota']} | {row['category']} | {row['seat_count']} |"
        )

    return (
        f"## Seat Matrix — {seat_data['branch']} ({seat_data['year']})\n\n"
        f"**Total Seats:** {seat_data['total_seats']}\n\n"
        "### Quota-wise Summary\n"
        + "\n".join(summary_lines)
        + "\n\n### Category-wise Breakdown\n"
        + "\n".join(detail_lines)
    )


# ─────────────────────────────────────────────
#  Branch comparison helper
# ─────────────────────────────────────────────



# ─────────────────────────────────────────────
#  App setup
# ─────────────────────────────────────────────

app = FastAPI()

# CORS: use ALLOWED_ORIGINS env var (comma-separated) in production.
# Local default is explicit localhost origins to avoid wildcard+credentials issues.
_origins_env = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:5500,http://localhost:3000")
_allowed_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]
if not _allowed_origins:
    _allowed_origins = ["http://127.0.0.1:5500", "http://localhost:3000"]
_allow_credentials = "*" not in _allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=_allow_credentials,
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


@app.get("/health/startup")
def startup_health_check():
    placement_csv_health = get_placement_files_health()
    status_ok = placement_csv_health.get("ok", False)

    payload = {
        "status": "ok" if status_ok else "degraded",
        "checks": {
            "placement_csv": placement_csv_health,
        },
    }

    if status_ok:
        return payload

    return JSONResponse(status_code=503, content=payload)

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
    "subcategory_asked": False,
    # Tracks what we're waiting for so follow-up shortcuts are context-aware.
    "awaiting": None,
}

# ── Input limits ──────────────────────────────────
_memory_fallback_store: dict[str, dict] = {}
_memory_db_retry_after = 0.0
_MEMORY_DB_RETRY_SECONDS = int(os.getenv("MEMORY_DB_RETRY_SECONDS", "30"))


def _memory_db_attempt_allowed() -> bool:
    return time.time() >= _memory_db_retry_after


def _mark_memory_db_unavailable() -> None:
    global _memory_db_retry_after
    _memory_db_retry_after = time.time() + _MEMORY_DB_RETRY_SECONDS


def _mark_memory_db_available() -> None:
    global _memory_db_retry_after
    _memory_db_retry_after = 0.0


def _normalize_memory(memory: dict | None) -> dict:
    normalized = EMPTY_MEMORY()
    if isinstance(memory, dict):
        for key in normalized:
            if key in memory:
                normalized[key] = memory[key]
    return normalized


def _load_chat_memory(user_id: str) -> dict:
    if not _memory_db_attempt_allowed():
        return _normalize_memory(_memory_fallback_store.get(user_id))
    try:
        memory = _normalize_memory(load_memory(user_id, EMPTY_MEMORY))
        _mark_memory_db_available()
        return memory
    except Exception as exc:
        _mark_memory_db_unavailable()
        logger.warning(
            "DB memory load failed for user_id=%s. Falling back to in-process memory. Error: %s",
            user_id,
            exc,
        )
        return _normalize_memory(_memory_fallback_store.get(user_id))


def _save_chat_memory(user_id: str, memory: dict) -> None:
    normalized = _normalize_memory(memory)
    _memory_fallback_store[user_id] = normalized.copy()
    if not _memory_db_attempt_allowed():
        return
    try:
        save_memory(user_id, normalized)
        _mark_memory_db_available()
    except Exception as exc:
        _mark_memory_db_unavailable()
        logger.warning(
            "DB memory save failed for user_id=%s. Keeping in-process memory only. Error: %s",
            user_id,
            exc,
        )


def _delete_chat_memory(user_id: str) -> None:
    _memory_fallback_store.pop(user_id, None)
    if not _memory_db_attempt_allowed():
        return
    try:
        delete_memory(user_id)
        _mark_memory_db_available()
    except Exception as exc:
        _mark_memory_db_unavailable()
        logger.warning(
            "DB memory delete failed for user_id=%s. Cleared in-process memory only. Error: %s",
            user_id,
            exc,
        )


def _db_unavailable_response() -> dict:
    return build_ui_response(
        response_type="error",
        message="Database is temporarily unavailable. Please try again in a moment.",
    )


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
    try:
        full_category, grouped_results = run_prediction(
            data.rank, data.base_category,
            data.girl, data.ph, data.af, data.ff, data.tf,
            data.quota
        )
    except Exception as exc:
        logger.warning("Prediction query failed. Error: %s", exc)
        return _db_unavailable_response()
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
    try:
        seat_data = run_seat_lookup(branch.upper(), year)
    except Exception as exc:
        logger.warning("Seat lookup failed for branch=%s, year=%s. Error: %s", branch, year, exc)
        return _db_unavailable_response()
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
async def chat(
    user_id: str = Body(...),
    user_message: str = Body(...),
    session_id: str | None = Body(default=None),
):
    # ── Input sanitisation ───────────────────────────────────────────────────
    user_id = user_id.strip()[:MAX_USER_ID_LEN]
    user_message = user_message.strip()[:MAX_MESSAGE_LEN]
    session_id = session_id.strip()[:100] if session_id else None

    if not user_id or not user_message:
        return build_ui_response(
            response_type="error",
            message="Please provide a valid message.",
        )

    language_style = detect_language_style(user_message)

    # Load memory from DB (persists across restarts)
    memory = _load_chat_memory(user_id)

    # ── Step 1: extract everything from the message ──────────────────────────

    detection_message = normalize_query_for_detection(user_message)

    extracted_rank     = extract_rank(detection_message)
    category_info      = extract_category(detection_message)
    extracted_quota    = extract_quota(detection_message)
    extracted_branches = extract_branches(detection_message)
    extracted_year     = extract_year(detection_message)
    intent = detect_intent(detection_message)
    course_scope = detect_course_scope(detection_message, extracted_branches)

    if should_reset_prediction_memory(
        user_message=user_message,
        detection_message=detection_message,
        memory=memory,
        extracted_rank=extracted_rank,
        category_info=category_info,
        extracted_quota=extracted_quota,
    ):
        memory = EMPTY_MEMORY()
        memory["rank"] = extracted_rank

    def log_route(final_route: str) -> None:
        try:
            asyncio.create_task(log_user_query(user_id, user_message, final_route, session_id))
        except Exception:
            pass

    def respond(final_route: str, **kwargs):
        should_localize = kwargs.pop("localize", True)
        if should_localize and language_style != "english" and kwargs.get("response_type") != "error":
            kwargs["message"] = localize_response_text(kwargs.get("message", ""), language_style)
        log_route(final_route)
        return build_ui_response(**kwargs)

    def ai_fallback_response(final_route: str, actions: list | None = None):
        conversation_history = []
        user_context = {
            k: memory[k] for k in ("rank", "base_category", "quota")
            if memory.get(k)
        }
        ai_reply = ai_brain_response(
            user_message=user_message,
            conversation_history=conversation_history,
            user_context=user_context,
            language_style=language_style,
        )
        return respond(
            final_route,
            response_type="stream",
            message=ai_reply,
            localize=False,
            actions=actions or [
                {"label": "Predict My Branch", "value": "I want to predict my branch"},
                {"label": "Seat Distribution", "value": "Show seat distribution"},
                {"label": "Placement Stats", "value": "Show placement statistics year-wise"},
                {"label": "B.Tech Counselling", "value": "Explain the counselling process"},
                {"label": "MBA Admission", "value": "Tell me about MBA admission at HBTU"},
                {"label": "MCA Admission", "value": "Tell me about MCA admission at HBTU"},
                {"label": "BS-MS Admission", "value": "Tell me about BS-MS admission at HBTU"},
            ],
        )

    # Helpdesk/contact queries should answer before broader admission routing.
    helpdesk_key = detect_helpdesk_query(detection_message)
    if helpdesk_key:
        hd = get_helpdesk_response(helpdesk_key)
        return respond(
            "helpdesk",
            response_type="stream",
            message=hd["message"],
            data=hd["data"],
            actions=hd["actions"],
            suggestions=hd["suggestions"],
        )

    if detect_programs_query(detection_message):
        return respond(
            "admission_programs",
            response_type="stream",
            message=get_programs_response(),
            data={"source": "admission_brochure_2026_27"},
            actions=[
                {"label": "B.Tech Counselling", "value": "Explain the B.Tech counselling process"},
                {"label": "MBA Admission", "value": "Tell me about MBA admission"},
                {"label": "MCA Admission", "value": "Tell me about MCA admission"},
                {"label": "BS-MS Admission", "value": "Tell me about BS-MS admission"},
                {"label": "Admission Contacts", "value": "Who is the admission coordinator for 2026?"},
            ],
        )

    # Placement routing is independent of admission-course KB routing.
    # Handle it early so terms like MCA/MBA in placement queries don't divert.
    if intent == "placement":
        placement_payload = get_placement_response(user_message)
        return respond(
            "placement",
            response_type="stream",
            message=placement_payload.get("message", "Placement information is unavailable right now."),
            data=placement_payload.get("data", {}),
            actions=placement_payload.get("actions", []),
            suggestions=placement_payload.get("suggestions", []),
        )

    if course_scope == "multiple":
        return respond(
            "course_clarification_multiple",
            response_type="question",
            message=(
                "I found multiple courses in your message. "
                "Please ask for one course at a time: B.Tech, MBA, MCA, or BS-MS."
            ),
            actions=[
                {"label": "B.Tech", "value": "Tell me about B.Tech admission"},
                {"label": "MBA", "value": "Tell me about MBA admission"},
                {"label": "MCA", "value": "Tell me about MCA admission"},
                {"label": "BS-MS", "value": "Tell me about BS-MS admission"},
            ],
        )

# ── MBA intent check (runs before all B.Tech routing) ────────────────────
    if course_scope == "mba":
        mba_intent, mba_confidence = detect_mba_intent(detection_message)
        resolved_mba_intent = (
            mba_intent if (mba_intent and mba_confidence > 0.3)
            else infer_course_specific_intent("mba", detection_message)
        )
        if resolved_mba_intent == "unknown":
            return ai_fallback_response(
                "ai_fallback_mba_unknown",
                actions=[
                    {"label": "MBA Eligibility", "value": "What is MBA eligibility?"},
                    {"label": "MBA Fees", "value": "What are MBA fees?"},
                    {"label": "MBA Seats", "value": "Show MBA seat matrix"},
                    {"label": "MBA Schedule", "value": "Show MBA counselling schedule"},
                ],
            )
        return respond(
            f"mba_{resolved_mba_intent}",
            response_type="stream",
            message=get_mba_response(resolved_mba_intent),
            data={"subtopic": resolved_mba_intent, "title": "MBA Admission — HBTU"},
            actions=[
                {"label": "MBA Eligibility",    "value": "What is MBA eligibility?"},
                {"label": "MBA Fees",           "value": "What are MBA fees?"},
                {"label": "MBA Rounds",         "value": "Explain MBA counselling rounds"},
                {"label": "MBA Seats",          "value": "Show MBA seat matrix"},
                {"label": "MBA Reservation",    "value": "What is MBA reservation policy?"},
                {"label": "MBA Documents",      "value": "What documents are needed for MBA?"},
            ],
            suggestions=[
                "What is the MBA registration fee?",
                "When is the MBA Round 1 result?",
                "What is GD/PI weightage?",
            ],
        )

    # ── MCA intent check (runs before all B.Tech routing) ────────────────────
    if course_scope == "mca":
        mca_intent, mca_confidence = detect_mca_intent(detection_message)
        resolved_mca_intent = (
            mca_intent if (mca_intent and mca_confidence > 0.3)
            else infer_course_specific_intent("mca", detection_message)
        )
        if resolved_mca_intent == "unknown":
            return ai_fallback_response(
                "ai_fallback_mca_unknown",
                actions=[
                    {"label": "MCA Eligibility", "value": "What is MCA eligibility?"},
                    {"label": "MCA Fees", "value": "What are MCA fees?"},
                    {"label": "MCA Seats", "value": "Show MCA seat matrix"},
                    {"label": "MCA Schedule", "value": "Show MCA counselling schedule"},
                ],
            )
        mca_guidelines_note = (
            "\n\nThis MCA guidance is based on the 2025-26 admission guidelines. "
            "For updated guidelines, please check https://www.hbtu.ac.in and "
            "https://erp.hbtu.ac.in/HBTUAdmissions.html"
        )
        return respond(
            f"mca_{resolved_mca_intent}",
            response_type="stream",
            message=get_mca_response(resolved_mca_intent) + mca_guidelines_note,
            data={"subtopic": resolved_mca_intent, "title": "MCA Admission — HBTU"},
            actions=[
                {"label": "MCA Eligibility",  "value": "What is MCA eligibility?"},
                {"label": "MCA Fees",         "value": "What are MCA fees?"},
                {"label": "MCA Rounds",       "value": "Explain MCA counselling rounds"},
                {"label": "MCA Seats",        "value": "Show MCA seat matrix"},
                {"label": "MCA Reservation",  "value": "What is MCA reservation policy?"},
                {"label": "MCA Documents",    "value": "What documents are needed for MCA?"},
            ],
            suggestions=[
                "What is the MCA registration fee?",
                "When is the MCA Round 1 result?",
                "What is MCA total fee at HBTU?",
            ],
        )

    # ── BS-MS intent check (runs before all B.Tech routing) ─────────────────
    if course_scope == "bsms":
        bsms_intent, bsms_confidence = detect_bsms_intent(detection_message)
        resolved_bsms_intent = (
            bsms_intent if (bsms_intent and bsms_confidence > 0.3)
            else infer_course_specific_intent("bsms", detection_message)
        )
        if resolved_bsms_intent == "unknown":
            resolved_bsms_intent = "bsms_general"

        return respond(
            f"bsms_{resolved_bsms_intent}",
            response_type="stream",
            message=get_bsms_response(resolved_bsms_intent),
            data={
                "subtopic": resolved_bsms_intent,
                "title": "BS-MS (Mathematics and Data Science) Admission — HBTU",
            },
            actions=[
                {"label": "BS-MS Eligibility", "value": "What is BS-MS eligibility?"},
                {"label": "BS-MS Fees", "value": "What are BS-MS fees?"},
                {"label": "BS-MS Rounds", "value": "Explain BS-MS counselling rounds"},
                {"label": "BS-MS Seats", "value": "Show BS-MS seat matrix"},
                {"label": "BS-MS Reservation", "value": "What is BS-MS reservation policy?"},
                {"label": "BS-MS Documents", "value": "What documents are needed for BS-MS?"},
            ],
            suggestions=[
                "What is the BS-MS registration fee?",
                "Show BS-MS schedule for 2025-26",
            ],
        )

    if course_scope == "btech" and intent == "unknown" and not extracted_branches:
        return ai_fallback_response(
            "ai_fallback_btech_unknown",
            actions=[
                {"label": "B.Tech Eligibility", "value": "What is the eligibility criteria?"},
                {"label": "B.Tech Fees", "value": "What is the B.Tech fee structure?"},
                {"label": "B.Tech Seats", "value": "Show seat distribution for CSE 2025"},
                {"label": "B.Tech Counselling", "value": "Explain the counselling process"},
            ],
        )

    # ── Step 2: handle numbered shortcut ONLY when we are waiting for quota ──
    # FIX: quota shortcut was running unconditionally and being overwritten.
    # Now it only applies when we're specifically waiting for a quota answer.
    if memory["awaiting"] == "quota":
        stripped = detection_message.strip()
        if stripped == "1":
            extracted_quota = "Home State"
        elif stripped == "2":
            extracted_quota = "All India"
    elif memory["awaiting"] == "subcategory":
        if is_no_subcategory_reply(detection_message):
            memory["subcategory_asked"] = True
            memory["awaiting"] = None
        elif has_subcategory(category_info):
            memory["subcategory_asked"] = True
            memory["awaiting"] = None

    # ── Step 3: update memory with anything newly extracted ──────────────────

    if extracted_rank:
        memory["rank"] = extracted_rank

    if category_info["base_category"]:
        memory["base_category"] = category_info["base_category"]

    for subcategory_key in ["girl", "ph", "af", "ff", "tf"]:
        if category_info[subcategory_key]:
            memory[subcategory_key] = True
            memory["subcategory_asked"] = True
            if memory["awaiting"] == "subcategory":
                memory["awaiting"] = None

    if extracted_quota:
        memory["quota"] = extracted_quota
        memory["awaiting"] = None   # quota received, clear the wait flag

    if (
        memory["rank"]
        and memory["base_category"]
        and not memory["subcategory_asked"]
        and not memory_has_subcategory(memory)
    ):
        memory["awaiting"] = "subcategory"
        _save_chat_memory(user_id, memory)
        return respond(
            "prediction_ask_subcategory",
            response_type="question",
            message=prediction_prompt_text(
                "ask_subcategory",
                language_style,
                rank=memory["rank"],
                base_category=memory["base_category"],
            ),
            localize=False,
            actions=[
                {"label": "None", "value": "None"},
                {"label": "Girl", "value": "Girl"},
                {"label": "PH / PwD", "value": "PH"},
                {"label": "AF", "value": "AF"},
                {"label": "FF", "value": "FF"},
                {"label": "TFW", "value": "TFW"},
            ],
        )

    # Persist updated memory to DB
    _save_chat_memory(user_id, memory)

    # ── Step 4: run prediction when all three required fields are present ─────

    if memory["rank"] and memory["base_category"] and memory["quota"]:

        # Capture values before clearing memory
        rank          = memory["rank"]
        base_category = memory["base_category"]
        girl, ph, af  = memory["girl"], memory["ph"], memory["af"]
        ff, tf        = memory["ff"], memory["tf"]
        quota         = memory["quota"]

        # Reset for next conversation (clear from DB)
        _delete_chat_memory(user_id)

        try:
            full_category, grouped_results = run_prediction(
                rank, base_category, girl, ph, af, ff, tf, quota
            )
        except Exception as exc:
            logger.warning(
                "Prediction query failed in chat flow for user_id=%s. Error: %s",
                user_id,
                exc,
            )
            log_route("prediction_db_unavailable")
            return _db_unavailable_response()

        return respond(
            "prediction_result",
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
        _save_chat_memory(user_id, memory)
        return respond(
            "prediction_ask_quota",
            response_type="question",
            message=prediction_prompt_text(
                "ask_quota",
                language_style,
                rank=memory["rank"],
                base_category=memory["base_category"],
            ),
            localize=False,
            actions=[
                {"label": "Home State", "value": "Home State"},
                {"label": "All India",  "value": "All India"},
            ],
        )

    # ── Step 5b: only ask for missing prediction fields when user wants a prediction ─
    # FIX: these guards previously ran for ALL intents — now only for predict/unknown
    # and caused messages like "Tell me your rank" when user asked about counselling.
    # They now only trigger when intent is "predict" or unknown (no clear other intent).

    # If user typed just a branch name (e.g. "cse"), treat it as seats request.
    # Do not force unknown long queries (placements/facilities/etc.) into seats flow.
    if intent == "unknown" and extracted_branches:
        message_lc = detection_message.lower()
        seat_cues = [
            "seat", "seats", "seat matrix", "intake", "quota",
            "distribution", "available seats", "seat count",
        ]
        has_seat_cue = any(cue in message_lc for cue in seat_cues)
        short_branch_query = len(user_message.strip().split()) <= 3
        if has_seat_cue or short_branch_query:
            intent = "seats"

    # Continue prediction flow on follow-up messages even when the latest
    # message has no explicit prediction keywords (e.g. user replies "40000").
    prediction_in_progress = any([
        memory.get("rank"),
        memory.get("base_category"),
        memory_has_subcategory(memory),
        memory.get("quota"),
        memory.get("awaiting") == "subcategory",
        memory.get("awaiting") == "quota",
    ])
    if (
        intent == "unknown"
        and prediction_in_progress
        and is_prediction_followup(
            detection_message, extracted_rank, category_info, extracted_quota
        )
    ):
        intent = "predict"

    if should_clarify_course(detection_message, intent, course_scope, extracted_branches):
        conversation_history = []
        user_context = {
            k: memory[k] for k in ("rank", "base_category", "quota")
            if memory.get(k)
        }
        ai_reply = ai_brain_response(
            user_message=user_message,
            conversation_history=conversation_history,
            user_context=user_context,
            language_style=language_style,
        )

        message_lc = detection_message.lower()
        if any(k in message_lc for k in ["fee", "fees", "tuition", "cost"]):
            clarify_actions = [
                {"label": "B.Tech Fees", "value": "What is the B.Tech fee structure?"},
                {"label": "MBA Fees", "value": "What are MBA fees?"},
                {"label": "MCA Fees", "value": "What are MCA fees?"},
                {"label": "BS-MS Fees", "value": "What are BS-MS fees?"},
            ]
        elif any(k in message_lc for k in ["seat", "seats", "seat matrix", "intake", "capacity"]):
            clarify_actions = [
                {"label": "B.Tech Seats", "value": "Show B.Tech seat distribution"},
                {"label": "MBA Seats", "value": "Show MBA seat matrix"},
                {"label": "MCA Seats", "value": "Show MCA seat matrix"},
                {"label": "BS-MS Seats", "value": "Show BS-MS seat matrix"},
            ]
        elif any(k in message_lc for k in ["document", "documents", "certificate", "verification"]):
            clarify_actions = [
                {"label": "B.Tech Documents", "value": "What documents are needed for B.Tech?"},
                {"label": "MBA Documents", "value": "What documents are needed for MBA?"},
                {"label": "MCA Documents", "value": "What documents are needed for MCA?"},
                {"label": "BS-MS Documents", "value": "What documents are needed for BS-MS?"},
            ]
        elif any(k in message_lc for k in ["reservation", "quota", "category", "obc", "sc", "st", "ews"]):
            clarify_actions = [
                {"label": "B.Tech Reservation", "value": "Tell me B.Tech reservation policy"},
                {"label": "MBA Reservation", "value": "What is MBA reservation policy?"},
                {"label": "MCA Reservation", "value": "What is MCA reservation policy?"},
                {"label": "BS-MS Reservation", "value": "What is BS-MS reservation policy?"},
            ]
        elif any(k in message_lc for k in ["date", "dates", "schedule", "timeline", "start"]):
            clarify_actions = [
                {"label": "B.Tech Schedule", "value": "Show B.Tech counselling schedule"},
                {"label": "MBA Schedule", "value": "Show MBA counselling schedule"},
                {"label": "MCA Schedule", "value": "Show MCA counselling schedule"},
                {"label": "BS-MS Schedule", "value": "Show BS-MS counselling schedule"},
            ]
        elif any(k in message_lc for k in ["eligibility", "eligible", "criteria", "qualification"]):
            clarify_actions = [
                {"label": "B.Tech Eligibility", "value": "What is B.Tech eligibility criteria?"},
                {"label": "MBA Eligibility", "value": "What is MBA eligibility?"},
                {"label": "MCA Eligibility", "value": "What is MCA eligibility?"},
                {"label": "BS-MS Eligibility", "value": "What is BS-MS eligibility?"},
            ]
        else:
            clarify_actions = [
                {"label": "B.Tech", "value": "Tell me about B.Tech admission"},
                {"label": "MBA", "value": "Tell me about MBA admission"},
                {"label": "MCA", "value": "Tell me about MCA admission"},
                {"label": "BS-MS", "value": "Tell me about BS-MS admission"},
            ]

        return respond(
            "course_clarification_ai",
            response_type="stream",
            message=ai_reply,
            localize=False,
            actions=clarify_actions,
        )

    if intent == "predict":  # ← ONLY prompt for rank when user explicitly wants prediction

        if memory["rank"] and not memory["base_category"]:
            return respond(
                "prediction_ask_base_category",
                response_type="question",
                message=prediction_prompt_text(
                    "ask_base_category",
                    language_style,
                    rank=memory["rank"],
                ),
                localize=False,
                actions=[
                    {"label": "OPEN"}, {"label": "BC"},
                    {"label": "SC"},   {"label": "ST"}, {"label": "EWS"},
                ],
            )

        if not memory["rank"]:
            return respond(
                "prediction_ask_rank",
                response_type="question",
                message=prediction_prompt_text("ask_rank", language_style),
                localize=False,
            )

    # ── Step 6: intent-specific flows ─────────────────────────────────────────

    if intent == "predict":
        # Guide the user toward providing rank / category / sub-category / quota
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
                "Please tell me your base category (OPEN / BC / SC / ST / EWS), "
                "sub-category if any (Girl / PH / AF / FF / TFW), and quota."
            )
        else:
            msg = (
                "Please tell me your JEE Main CRL rank, base category, sub-category if any, and quota "
                "(Home State or All India).\n\n"
                "⚠️ Note: Please enter your CRL (Common Rank List) rank, not your category rank."
            )

        return respond("prediction_collect_missing", response_type="question", message=msg)

    # ── Seats intent ──────────────────────────────────────────────────────────
    # FIX: was split into two duplicate elif blocks — merged into one.

    elif intent == "seats":
        if extracted_branches:
            year = extracted_year or 2025   # default to 2025 if not specified
            try:
                seat_data = run_seat_lookup(extracted_branches[0], year)
            except Exception as exc:
                logger.warning(
                    "Seat lookup failed in chat flow for branch=%s, year=%s. Error: %s",
                    extracted_branches[0],
                    year,
                    exc,
                )
                log_route("seats_db_unavailable")
                return _db_unavailable_response()
            return respond(
                "seats_result",
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
            return respond(
                "seats_ask_branch",
                response_type="question",
                message="Please tell me which branch you want seat details for.",
            )


    elif intent == "fees":
        info = COUNSELLING_DATA["fee_structure"]
        return respond(
            "btech_fees",
            response_type="stream",
            message=info["message"],
            data={"subtopic": "fee_structure", "title": info["title"]},
            actions=info.get("actions", []),
        )

    elif intent == "counselling_info":
        subtopic = detect_counselling_subtopic(detection_message)
        info     = COUNSELLING_DATA.get(subtopic, COUNSELLING_DATA["overview"])

        return respond(
            f"btech_counselling_{subtopic}",
            response_type="stream",
            message=info["message"],
            data={"subtopic": subtopic, "title": info["title"]},
            actions=info.get("actions", []),
            suggestions=info.get("suggestions", []),
        )

    # ── Fallback ──────────────────────────────────────────────────────────────

    # ── AI Brain fallback — handles greetings, ambiguous, out-of-scope ────────
    # Build a lightweight history list from memory for context
    conversation_history = []  # extend this later if you persist chat history in DB

    user_context = {
        k: memory[k] for k in ("rank", "base_category", "quota")
        if memory.get(k)
    }

    ai_reply = ai_brain_response(
        user_message=user_message,
        conversation_history=conversation_history,
        user_context=user_context,
        language_style=language_style,
    )

    return respond(
        "ai_fallback_general",
        response_type="stream",
        message=ai_reply,
        localize=False,
        actions=[
            {"label": "🎯 Predict My Branch",   "value": "I want to predict my branch"},
            {"label": "💺 Seat Distribution",   "value": "Show seat distribution"},
            {"label": "📈 Placement Stats",     "value": "Show placement statistics year-wise"},
            {"label": "📋 B.Tech Counselling",  "value": "Explain the counselling process"},
            {"label": "🎓 MBA Admission",       "value": "Tell me about MBA admission at HBTU"},
            {"label": "🧑‍💻 MCA Admission",      "value": "Tell me about MCA admission at HBTU"},
            {"label": "📐 BS-MS Admission",      "value": "Tell me about BS-MS admission at HBTU"},
        ],
    )
