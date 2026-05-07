import re

BROCHURE_DATA = {
    "btech": {
        "program": "B.Tech.",
        "admission_through": "JEE Mains 2026",
        "schedule": "May 2026",
    },
    "bsms": {
        "program": "BS-MS (Mathematics and Data Science)",
        "admission_through": "JEE Mains 2026 / CUET-UG 2026",
        "schedule": "May 2026",
    },
    "btech_lateral": {
        "program": "B.Tech. (Lateral Entry)",
        "admission_through": "CUET-UG 2026",
        "schedule": "May 2026",
    },
    "biotech": {
        "program": "B.Tech Biotechnology",
        "admission_through": "CUET-UG 2026",
        "schedule": "May 2026",
    },
    "bpharma": {
        "program": "B.Pharm",
        "admission_through": "CUET-UG 2026",
        "schedule": "May 2026",
    },
    "bba": {
        "program": "BBA",
        "admission_through": "CUET-UG 2026",
        "schedule": "May 2026",
    },
    "mca": {
        "program": "MCA",
        "admission_through": "NIMCET 2026",
        "schedule": "May 2026",
    },
    "mtech": {
        "program": "M.Tech",
        "admission_through": "GATE / CUET-PG 2026 / UET 2026",
        "schedule": "Mid-April 2026",
    },
    "msc": {
        "program": "M.Sc",
        "admission_through": "IIT JAM 2026 / GAT-B 2026 / CUET-PG 2026 / UET 2026",
        "schedule": "Mid-April 2026",
    },
    "phd": {
        "program": "PhD",
        "admission_through": "GATE / UGC-NET / CSIR-NET / UET 2026",
        "schedule": "Mid-April 2026",
    },
    "mba": {
        "program": "MBA",
        "admission_through": "CAT 2025 / CMAT 2026 / MAT / CUET-PG 2026 / UET 2026",
        "schedule": "March 2026",
    },
}

PROGRAM_ALIASES = {
    "btech": ["btech", "b tech", "b.tech", "b tech admission"],
    "bsms": ["bsms", "bs-ms", "bs ms", "mathematics and data science", "maths and data science"],
    "btech_lateral": ["lateral entry", "btech lateral", "b tech lateral", "b.tech lateral"],
    "biotech": ["biotech", "biotechnology"],
    "bpharma": ["bpharm", "b pharma", "b.pharm", "b.pharma", "pharmacy"],
    "bba": ["bba"],
    "mca": ["mca"],
    "mtech": ["mtech", "m tech", "m.tech"],
    "msc": ["msc", "m sc", "m.sc", "master of science"],
    "phd": ["phd", "ph d", "ph.d", "doctorate"],
    "mba": ["mba"],
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def _contains_phrase(normalized_message: str, phrase: str) -> bool:
    normalized_phrase = _normalize(phrase)
    if not normalized_phrase:
        return False
    return f" {normalized_phrase} " in f" {normalized_message} "


def _match_program_key(user_message: str) -> str | None:
    normalized_message = _normalize(user_message)
    for key, aliases in PROGRAM_ALIASES.items():
        if any(_contains_phrase(normalized_message, alias) for alias in aliases):
            return key
    return None


def detect_brochure_intent(user_message: str) -> bool:
    normalized_message = _normalize(user_message)

    keywords = [
        "admission brochure",
        "brochure",
        "2026 brochure",
        "2026 27 brochure",
        "all courses",
        "all programs",
        "all programmes",
        "which courses",
        "what courses",
        "list of courses",
        "courses offered",
        "programs offered",
        "programmes offered",
        "admission through",
        "how to apply",
        "application process",
        "admission schedule",
        "admission schedules",
        "tentative schedule",
        "tentative schedules",
        "when will admission",
        "when admission",
        "admission starts",
        "admission begins",
        "admission dates",
        "admission timing",
        "admission calendar",
        "application deadline",
        "jee mains 2026",
        "cuet 2026",
        "nimcet 2026",
        "gate 2026",
        "iit jam 2026",
        "cat 2025",
        "cmat 2026",
        "uet 2026",
    ]

    return any(_contains_phrase(normalized_message, keyword) for keyword in keywords)


def get_brochure_table_html() -> str:
    """Generate an HTML table for the admission brochure."""
    html = """
    <table style="border-collapse: collapse; width: 100%; margin: 20px 0; font-family: Arial, sans-serif;">
        <thead>
            <tr style="background-color: #2c3e50; color: white;">
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Program</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Admission Through</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Schedule</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for value in BROCHURE_DATA.values():
        html += f"""
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #ddd; padding: 12px;">{value['program']}</td>
                <td style="border: 1px solid #ddd; padding: 12px;">{value['admission_through']}</td>
                <td style="border: 1px solid #ddd; padding: 12px;">{value['schedule']}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    """
    return html


def get_brochure_table_markdown() -> str:
    """Generate a Markdown table for the admission brochure."""
    lines = [
        "| Program | Admission Through | Schedule |",
        "|---------|------------------|----------|",
    ]
    
    for value in BROCHURE_DATA.values():
        lines.append(
            f"| {value['program']} | {value['admission_through']} | {value['schedule']} |"
        )
    
    return "\n".join(lines)


def get_brochure_response(user_message: str):
    matched_key = _match_program_key(user_message)
    table_markdown = get_brochure_table_markdown()

    if matched_key:
        value = BROCHURE_DATA[matched_key]
        # Check if this is a timing-related question
        timing_keywords = ["when", "start", "begins", "schedule", "date"]
        is_timing_question = any(
            _contains_phrase(_normalize(user_message), kw) for kw in timing_keywords
        )
        
        if is_timing_question:
            # Show full table with specific course highlighted
            message = (
                f"## {value['program']} Admission Schedule\n\n"
                f"**Program:** {value['program']}\n"
                f"**Admission Through:** {value['admission_through']}\n"
                f"**Tentative Schedule:** {value['schedule']}\n\n"
                f"### Complete Admission Brochure 2026-27\n\n"
                f"{table_markdown}"
            )
            return {
                "message": message,
                "data": BROCHURE_DATA,
                "focused_course": value,
                "table_html": get_brochure_table_html(),
                "table_markdown": table_markdown,
            }
        else:
            # Generic course query
            return {
                "message": (
                    f"Program: {value['program']}\n"
                    f"Admission Through: {value['admission_through']}\n"
                    f"Tentative Schedule: {value['schedule']}"
                ),
                "data": value,
            }

    # No specific course mentioned - show full brochure
    return {
        "message": f"## HBTU Admission Brochure 2026-27\n\n{table_markdown}",
        "data": BROCHURE_DATA,
        "table_html": get_brochure_table_html(),
        "table_markdown": table_markdown,
    }
