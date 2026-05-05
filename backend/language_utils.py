import re


DEVANAGARI_RE = re.compile(r"[\u0900-\u097f]")

HINGLISH_CUES = {
    "hai", "hain", "hu", "ho", "kya", "kyu", "kyon", "kab", "kaise",
    "kitna", "kitni", "kitne", "batao", "bataye", "batana", "chahiye",
    "milega", "mil sakta", "hoga", "karna", "mera", "meri", "mere",
    "ka", "ki", "ke", "mein", "se", "tak", "liye", "wala",
    "chahiye", "puchna", "puchu", "puchhun", "dikhao", "bhejna",
}


def detect_language_style(user_message: str) -> str:
    """Return english, hindi, or hinglish based on the user's message."""
    message = (user_message or "").strip().lower()
    if not message:
        return "english"

    devanagari_chars = len(DEVANAGARI_RE.findall(message))
    if devanagari_chars >= 2:
        return "hindi"

    tokens = set(re.findall(r"[a-z]+", message))
    if tokens & HINGLISH_CUES:
        return "hinglish"

    return "english"


def _replace_phrases(message: str, replacements: dict[str, str]) -> str:
    for old in sorted(replacements, key=len, reverse=True):
        message = message.replace(old, replacements[old])
    return message


def normalize_multilingual_query(user_message: str) -> str:
    """Translate common Hindi/Hinglish admission phrases into routing keywords."""
    message = (user_message or "").lower()

    devanagari_replacements = {
        "\u092a\u094d\u0932\u0947\u0938\u092e\u0947\u0902\u091f": "placement",
        "\u0915\u0902\u092a\u0928\u0940": "company",
        "\u0915\u0902\u092a\u0928\u093f\u092f\u093e\u0902": "companies",
        "\u0915\u092e\u094d\u092a\u0928\u0940": "company",
        "\u0915\u092e\u094d\u092a\u0928\u093f\u092f\u093e\u0902": "companies",
        "\u0938\u092c\u0938\u0947 \u091c\u094d\u092f\u093e\u0926\u093e \u092a\u0948\u0915\u0947\u091c": "highest package",
        "\u0914\u0938\u0924 \u092a\u0948\u0915\u0947\u091c": "average package",
        "\u092e\u0940\u0921\u093f\u092f\u0928 \u092a\u0948\u0915\u0947\u091c": "median package",
        "\u092a\u0948\u0915\u0947\u091c": "package",
        "\u0930\u0948\u0902\u0915": "rank",
        "\u0930\u0948\u0902\u0915\u093f\u0902\u0917": "rank",
        "\u092b\u0940\u0938": "fees",
        "\u0936\u0941\u0932\u094d\u0915": "fees",
        "\u0938\u0940\u091f \u092e\u0948\u091f\u094d\u0930\u093f\u0915\u094d\u0938": "seat matrix",
        "\u0938\u0940\u091f\u0947\u0902": "seats",
        "\u0938\u0940\u091f": "seat",
        "\u0915\u093e\u0909\u0902\u0938\u0932\u093f\u0902\u0917": "counselling",
        "\u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c": "documents",
        "\u0921\u0949\u0915\u094d\u092f\u0942\u092e\u0947\u0902\u091f": "documents",
        "\u092f\u094b\u0917\u094d\u092f\u0924\u093e": "eligibility",
        "\u092a\u093e\u0924\u094d\u0930\u0924\u093e": "eligibility",
        "\u0936\u094d\u0930\u0947\u0923\u0940": "category",
        "\u0915\u0948\u091f\u0947\u0917\u0930\u0940": "category",
        "\u0906\u0930\u0915\u094d\u0937\u0923": "reservation",
        "\u0915\u094b\u091f\u093e": "quota",
        "\u0939\u094b\u092e \u0938\u094d\u091f\u0947\u091f": "home state",
        "\u0911\u0932 \u0907\u0902\u0921\u093f\u092f\u093e": "all india",
        "\u0913\u092c\u0940\u0938\u0940": "obc",
        "\u0905\u0928\u0941\u0938\u0942\u091a\u093f\u0924 \u091c\u093e\u0924\u093f": "sc",
        "\u0905\u0928\u0941\u0938\u0942\u091a\u093f\u0924 \u091c\u0928\u091c\u093e\u0924\u093f": "st",
        "\u092e\u0939\u093f\u0932\u093e": "girl",
        "\u0932\u0921\u093c\u0915\u0940": "girl",
        "\u0926\u093f\u0935\u094d\u092f\u093e\u0902\u0917": "pwd",
        "\u0906\u0935\u0947\u0926\u0928": "application",
        "\u0930\u091c\u093f\u0938\u094d\u091f\u094d\u0930\u0947\u0936\u0928": "registration",
        "\u0915\u092c": "date",
        "\u0915\u093f\u0924\u0928\u0940": "how many",
        "\u0915\u093f\u0924\u0928\u093e": "how many",
        "\u0915\u0948\u0938\u0947": "process",
        "\u092c\u0924\u093e\u0913": "tell me",
        "\u092c\u0924\u093e\u090f\u0902": "tell me",
        "\u0938\u0941\u0935\u093f\u0927\u093e": "facility",
        "\u0938\u0941\u0935\u093f\u0927\u093e\u090f\u0902": "facilities",
        "\u0938\u0941\u0935\u093f\u0927\u093e\u0913\u0902": "facilities",
        "\u0915\u0947\u0902\u0926\u094d\u0930\u0940\u092f \u0938\u0941\u0935\u093f\u0927\u093e": "central facilities",
        "\u0915\u0947\u0902\u0926\u094d\u0930\u0940\u092f \u0938\u0941\u0935\u093f\u0927\u093e\u090f\u0902": "central facilities",
        "\u091b\u093e\u0924\u094d\u0930\u093e\u0935\u093e\u0938": "hostel",
        "\u0939\u0949\u0938\u094d\u091f\u0932": "hostel",
        "\u092a\u0941\u0938\u094d\u0924\u0915\u093e\u0932\u092f": "library",
        "\u0932\u093e\u0907\u092c\u094d\u0930\u0947\u0930\u0940": "library",
        "\u0938\u094d\u0935\u093e\u0938\u094d\u0925\u094d\u092f \u0915\u0947\u0902\u0926\u094d\u0930": "health centre",
        "\u092c\u0948\u0902\u0915": "bank",
        "\u0916\u0947\u0932": "sports",
        "\u091c\u093f\u092e": "gym",
        "\u0905\u0924\u093f\u0925\u093f \u0917\u0943\u0939": "guest house",
        "\u0915\u0948\u0902\u091f\u0940\u0928": "canteen",
        "\u0938\u092d\u093e\u0917\u093e\u0930": "auditorium",
        "\u0935\u0930\u094d\u0915\u0936\u0949\u092a": "workshop",
        "\u0915\u0902\u092a\u094d\u092f\u0942\u091f\u0930 \u0915\u0947\u0902\u0926\u094d\u0930": "computer centre",
        "\u092c\u0940\u091f\u0947\u0915": "btech",
        "\u092c\u0940.\u091f\u0947\u0915": "btech",
        "\u090f\u092e\u092c\u0940\u090f": "mba",
        "\u090f\u092e.\u092c\u0940.\u090f": "mba",
        "\u090f\u092e\u0938\u0940\u090f": "mca",
        "\u090f\u092e.\u0938\u0940.\u090f": "mca",
        "\u090f\u092e\u090f\u0938\u0938\u0940": "msc",
        "\u090f\u092e.\u090f\u0938\u0938\u0940": "msc",
        "\u090f\u092e\u091f\u0947\u0915": "mtech",
        "\u090f\u092e.\u091f\u0947\u0915": "mtech",
        "\u092a\u0940\u090f\u091a\u0921\u0940": "phd",
        "\u092a\u0940.\u090f\u091a.\u0921\u0940": "phd",
    }

    hinglish_replacements = {
        "kitni fees": "fees",
        "fees kitni": "fees",
        "fee kitni": "fees",
        "kitna fee": "fees",
        "kitni seat": "seats",
        "kitni seats": "seats",
        "seat kitni": "seats",
        "seats kitni": "seats",
        "seat matrix dikhao": "seat matrix",
        "rank se branch": "predict branch rank",
        "branch milegi": "predict branch",
        "branch mil sakti": "predict branch",
        "kya branch milegi": "predict branch",
        "chance hai": "chances",
        "chances hai": "chances",
        "mera rank": "rank",
        "meri rank": "rank",
        "rank batao": "rank",
        "college milega": "predict",
        "admission milega": "predict admission",
        "counselling kab": "counselling schedule",
        "counselling kaise": "counselling process",
        "counselling process batao": "counselling process",
        "form kab": "form date",
        "registration kab": "registration date",
        "apply kaise": "application process",
        "documents kya": "documents required",
        "document kya": "documents required",
        "kya document": "documents required",
        "eligibility kya": "eligibility criteria",
        "eligible hu": "eligibility",
        "reservation kya": "reservation",
        "quota kya": "quota",
        "home state": "home state",
        "all india": "all india",
        "ladki": "girl",
        "female": "girl",
        "category": "category",
        "general": "general",
        "open": "open",
        "obc": "obc",
        "ews": "ews",
        "pwd": "pwd",
        "batao": "tell me",
        "bataye": "tell me",
        "kab hoga": "schedule",
        "kab hai": "date",
        "kya hai": "information",
        "kaise hoga": "process",
        "facility kya": "facility",
        "facilities kya": "facilities",
        "central facilities": "central facilities",
        "hostel kaisa": "hostel",
        "hostel facility": "hostel facility",
        "library timing": "library timings",
        "library timings": "library timings",
        "bank hai": "bank",
        "sports facility": "sports facility",
        "gym hai": "gym",
        "guest house": "guest house",
        "canteen hai": "canteen",
    }

    message = _replace_phrases(message, devanagari_replacements)
    message = _replace_phrases(message, hinglish_replacements)
    return re.sub(r"\s+", " ", message).strip()


def response_language_instruction(language_style: str) -> str:
    if language_style == "hindi":
        return (
            "Respond strictly in Hindi using Devanagari script only. Do not use "
            "Roman Hindi, Hinglish, or English sentences. Translate common words "
            "like fees, seats, documents, process, and schedule into Hindi. Keep "
            "official course names, category codes, ranks, URLs, and amounts unchanged."
        )
    if language_style == "hinglish":
        return (
            "Respond strictly in natural Hinglish using Roman script only. Do not "
            "use Devanagari script. Mix simple Hindi words with English admission "
            "terms where natural. Keep category codes, ranks, URLs, and amounts unchanged."
        )
    return "Respond in English."
