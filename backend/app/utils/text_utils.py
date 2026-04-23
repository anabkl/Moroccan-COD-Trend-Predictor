"""
SoukAI Text Utilities
Handles cleaning and language detection for Darija / Arabic / French text.
All operations are UTF-8 safe.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional


# ---------------------------------------------------------------------------
# Arabic tashkeel (diacritics) range
# ---------------------------------------------------------------------------

_ARABIC_TASHKEEL = re.compile(
    r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8"
    r"\u06EA-\u06ED]"
)

# Tatweel (Arabic kashida/elongation character)
_ARABIC_TATWEEL = re.compile(r"\u0640")

# URLs
_URL_PATTERN = re.compile(
    r"https?://\S+|www\.\S+",
    re.IGNORECASE,
)

# Emojis – Unicode blocks covering most emoji ranges
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # geometric shapes extended
    "\U0001F800-\U0001F8FF"  # supplemental arrows-C
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA00-\U0001FA6F"  # chess symbols
    "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)

# Repeated punctuation / noise
_NOISE_PATTERN = re.compile(r"[^\w\s\u0600-\u06FF\u0750-\u077F]+", re.UNICODE)


# ---------------------------------------------------------------------------
# Language keyword sets (lowercase Darija transliteration + Arabic + French)
# ---------------------------------------------------------------------------

_ARABIC_SCRIPT_THRESHOLD = 0.25  # fraction of chars in Arabic Unicode block

_DARIJA_KEYWORDS: set[str] = {
    "wach", "kayen", "katwsl", "ncommandi", "bchhal", "thaman",
    "chri", "3afak", "afak", "kbira", "khadama", "mzyan", "zwin",
    "zwina", "tbarklah", "tbark", "3jbni", "ghali", "rkhis",
    "kifach", "fin", "walo", "bzzaf", "shwiya", "daba",
    "hadchi", "had", "chi", "fach", "ach", "wash",
}

_FRENCH_KEYWORDS: set[str] = {
    "prix", "livraison", "commande", "payer", "acheter", "disponible",
    "merci", "bonjour", "bonsoir", "magnifique", "superbe", "belle",
    "bon", "très", "trop", "comment", "où", "quand", "combien",
    "delivery", "nice", "beautiful", "good",
}

_ARABIC_WORDS: set[str] = {
    "بشحال", "ثمن", "واش", "كيفاش", "فين", "طلب", "توصيل",
    "غالي", "رخيص", "كاين", "مزيان", "زوين", "عجبني",
    "شحال", "كيتوصل", "كيفاش", "الثمن", "السعر",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Clean raw comment text:
    1. Remove URLs
    2. Remove emojis
    3. Remove Arabic tashkeel and tatweel
    4. Collapse noisy punctuation
    5. Normalise whitespace
    """
    if not text:
        return ""

    # Ensure UTF-8 safe string
    text = text.encode("utf-8", errors="replace").decode("utf-8")

    text = _URL_PATTERN.sub(" ", text)
    text = _EMOJI_PATTERN.sub(" ", text)
    text = _ARABIC_TASHKEEL.sub("", text)
    text = _ARABIC_TATWEEL.sub("", text)

    # Unicode normalise (NFC)
    text = unicodedata.normalize("NFC", text)

    # Remove stray punctuation but preserve Arabic, Latin, digits, and spaces
    text = _NOISE_PATTERN.sub(" ", text)

    # Collapse multiple whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_arabic(text: str) -> str:
    """Normalise common Arabic letter variants (alef forms, etc.)."""
    replacements = {
        "أ": "ا", "إ": "ا", "آ": "ا",
        "ة": "ه",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي",
    }
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)
    return text


def detect_language(text: str) -> str:
    """
    Heuristic language detection for Darija / Arabic / French / mixed.

    Returns: "arabic" | "darija" | "french" | "mixed"
    """
    if not text:
        return "mixed"

    text_lower = text.lower()
    tokens = set(re.findall(r"[\w\u0600-\u06FF]+", text_lower, re.UNICODE))

    # Count Arabic-script characters
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
    ratio_arabic = arabic_chars / max(len(text), 1)

    has_arabic_script = ratio_arabic >= _ARABIC_SCRIPT_THRESHOLD
    has_darija_kw = bool(tokens & _DARIJA_KEYWORDS)
    has_french_kw = bool(tokens & _FRENCH_KEYWORDS)
    has_arabic_words = bool(tokens & _ARABIC_WORDS)

    # Decision tree
    if has_arabic_script and has_arabic_words and not has_darija_kw and not has_french_kw:
        return "arabic"
    if has_arabic_script and (has_darija_kw or has_arabic_words):
        if has_french_kw:
            return "mixed"
        return "darija"
    if has_darija_kw and not has_french_kw:
        return "darija"
    if has_french_kw and not has_darija_kw:
        return "french"
    if has_darija_kw or has_french_kw:
        return "mixed"

    # Fallback: if mostly Arabic script → arabic
    if has_arabic_script:
        return "arabic"
    return "mixed"


def tokenize(text: str) -> list[str]:
    """Return a list of lowercase word tokens (Latin + Arabic)."""
    return re.findall(r"[\w\u0600-\u06FF]+", text.lower(), re.UNICODE)
