from groq import Groq
import os
import re
from language_utils import (
    detect_language_style,
    normalize_multilingual_query,
    response_language_instruction,
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _feedback_ack_response(user_message: str) -> str | None:
    """Return fixed acknowledgement text for passive feedback actions."""
    message = normalize_multilingual_query(user_message).strip()

    if message.startswith("report an issue") or " report an issue" in message:
        return (
            "Sorry you ran into this — I’m still in my testing phase, so issues can happen. Thanks for reporting it! I’ll make sure this gets looked into and improved soon."
        )

    if (
        message.startswith("suggest improvement")
        or message.startswith("suggest an improvement")
        or " suggest improvement" in message
        or " suggest an improvement" in message
    ):
        return (
            "Thanks a lot for your feedback! I really appreciate you taking the time to help improve me. I’ll definitely consider your suggestion and work on getting better."
        )

    return None


def _needs_course_clarification(user_message: str) -> bool:
    """Return True for common admission queries that don't specify course."""
    message = normalize_multilingual_query(user_message)

    has_bsms = (
        re.search(r"\bbs\s*[- ]?\s*ms\b", message) is not None
        or "mathematics and data science" in message
        or "maths and data science" in message
        or "math and data science" in message
        or "bachelors in mathematics and data science" in message
        or "bachelor in mathematics and data science" in message
    )

    has_explicit_course = (
        re.search(r"\bmba\b", message) is not None
        or re.search(r"\bmca\b", message) is not None
        or re.search(r"\bb\.?\s*tech\b", message) is not None
        or has_bsms
    )
    if has_explicit_course:
        return False

    common_query_cues = [
        "seat", "seats", "seat matrix", "intake",
        "fee", "fees", "tuition", "cost",
        "document", "documents", "certificate", "verification",
        "reservation", "quota", "category",
        "eligibility", "eligible", "admission", "counselling", "counseling",
        "schedule", "timeline", "dates", "register", "registration",
    ]
    return any(cue in message for cue in common_query_cues)

SYSTEM_PROMPT = """You are an Admission assistant for HBTU (Harcourt Butler Technical University), Kanpur.

STRICT RULES:
1. ONLY answer questions related to HBTU admissions, B.Tech/MBA counselling, entrance exams (JEE/CUET/CAT), seat matrix, fee structure, eligibility, reservation, documents, important dates, and HBTU academic administration relevant to admission (VC, Registrar, Controller of Examination, Deans, HoDs).
2. If the question is outside this scope, reply exactly: "I can only help with HBTU admissions and counselling queries."
3. NEVER fabricate rank cutoffs, seat numbers, fee amounts, deadlines, office-bearer names, or policy details.
4. If any critical fact is uncertain, outdated, or not verifiable, say: "I don't have reliable verified data for that detail right now — please check hbtu.ac.in."
5. Prefer detailed, structured answers (not too short). Use clear sections and bullet points where useful.
6. For admission/counselling questions, include practical detail: eligibility, process steps, documents, fee components, reservation/category notes, and what to do next.
7. For "latest" personnel queries (HoD, Controller of Examination, Dean, VC, Registrar, etc.), provide names ONLY when confidently verified from reliable context; otherwise clearly state that live designation data should be confirmed on official HBTU pages.
8. For HoD/department queries, provide department-wise guidance and tell users to verify from official Department/Administration pages because office assignments can change.
9. For date-sensitive topics (counselling schedule, notices, rounds, seat updates), explicitly mention that timelines may change and users must verify with the latest HBTU notice.
10. If asked for advice, provide realistic guidance with no guarantees, no overpromising, and no false certainty.
11. Keep tone professional, student-friendly, and actionable. Avoid vague one-line answers when user asks for explanation.
12. When sharing website links, use ONLY the exact official URLs below (do not invent or rewrite links):
    - HBTU official website: https://hbtu.ac.in/
    - HBTU B.Tech counselling website: https://hbtu.admissions.nic.in/
    - HBTU Admissions Website: https://erp.hbtu.ac.in/HBTUAdmissions.html
    - HBTU Placement Statistics: https://hbtu.ac.in/training-placements/#PlacementStatistics
    - Academics Circular: https://hbtu.ac.in/academic-circular/
    - Academic Calendar: https://hbtu.ac.in/academic-calendar/
    - Classes Time Table: https://hbtu.ac.in/time-table/
13. If user asks for page links, respond with page name + exact URL from the approved list above.
14. Do not provide outdated/non-canonical variants like http links, wrong subdomains, or guessed endpoints.
15. End important answers with a short verification reminder pointing to https://hbtu.ac.in/.
16. If asked about Vice Chancellor (VC) of HBTU, reply: "As per available information, the Vice Chancellor of HBTU is Prof. Samsher."
17. If asked about Dean of HBTU / Dean of Academic Affairs, reply: "As per available information, the Dean is Prof. Vandana Dixit Kaushik."
18. If asked about Registrar of HBTU, reply: "As per available information, the Registrar is Amit Kumar Rathore."
19. If asked about Pro Vice Chancellor of HBTU, reply: "As per available information, the Pro Vice Chancellor is Dipteek Parmar."
20. If asked about Controller of Examinations of HBTU, reply: "As per available information, the Controller of Examinations is Dr. Anita Yadav."
21. If asked about who created you, reply: "I was created by **Full stack gang** 
Aman Thakur, 
Hemant Singh, 
Parth Sharma, 
Information Technology'27 batch."
22. Understand English, Hindi, and Hinglish user messages. Match the user's language style unless the user explicitly asks for a different language.
"""


def localize_response_text(message: str, language_style: str) -> str:
    """Localize verified backend text without changing facts or markdown structure."""
    if language_style == "english" or not message:
        return message

    instruction = response_language_instruction(language_style)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You localize chatbot responses for HBTU admissions. "
                        "Preserve every fact, number, rank, category code, URL, Markdown table, "
                        "heading structure, and bullet structure. Do not add new information. "
                        f"{instruction}"
                    ),
                },
                {"role": "user", "content": message},
            ],
            max_tokens=1400,
            temperature=0.1,
        )
        return response.choices[0].message.content
    except Exception:
        return message


def ai_brain_response(
    user_message: str,
    conversation_history: list,
    user_context: dict,
    language_style: str | None = None,
) -> str:
    language_style = language_style or detect_language_style(user_message)
    feedback_reply = _feedback_ack_response(user_message)
    if feedback_reply:
        return feedback_reply

    if _needs_course_clarification(user_message):
        return localize_response_text(
            "Please tell me which course you are asking about: B.Tech, MBA, MCA, or BSMS. "
            "I can then give exact seat details, fees, documents, and counselling steps for that course.",
            language_style,
        )

    context_note = f"\n[User context captured so far: {user_context}]" if user_context else ""
    language_note = f"\n[Response language/style instruction: {response_language_instruction(language_style)}]"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += conversation_history[-6:]  # last 3 turns
    messages.append({"role": "user", "content": user_message + context_note + language_note})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # free, very capable
            messages=messages,
            max_tokens=512,
            temperature=0.3   # lower = less creative = less hallucination
        )
        return response.choices[0].message.content

    except Exception:
        if language_style == "hindi":
            return (
                "\u092e\u0941\u091d\u0947 \u0905\u092d\u0940 \u0925\u094b\u0921\u093c\u0940 "
                "\u0926\u093f\u0915\u094d\u0915\u0924 \u0939\u094b \u0930\u0939\u0940 "
                "\u0939\u0948. \u0915\u0943\u092a\u092f\u093e rank prediction, seats, "
                "\u092f\u093e counselling process \u0915\u0947 \u092c\u093e\u0930\u0947 "
                "\u092e\u0947\u0902 \u092a\u0942\u091b\u0947\u0902."
            )
        if language_style == "hinglish":
            return "Mujhe abhi thodi dikkat ho rahi hai. Please rank prediction, seats, ya counselling process ke baare mein puchhein."
        return "I'm having trouble right now. Please ask about rank prediction, seats, or counselling process."
