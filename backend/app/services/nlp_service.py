"""
SoukAI NLP Service
Intent detection for Moroccan COD comments using keyword matching + TF-IDF scoring.
Handles Darija, Arabic, French, and mixed-language text.
"""

from __future__ import annotations

import logging
import re
from typing import List, Tuple

from app.utils.text_utils import clean_text, detect_language, tokenize

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Intent keyword lexicons
# ---------------------------------------------------------------------------

# High purchase-intent signals (Darija / Arabic / French)
HIGH_INTENT_KEYWORDS: List[str] = [
    # Darija transliteration – price / availability / ordering
    "bchhal", "bchhal had", "thaman", "wach katwsl", "kifach ncommandi",
    "commandi", "wach kayen", "fin kayen", "wach ghali", "kbira",
    "khadama", "chri", "3afak", "afak", "ndir commande",
    "wash kayen", "kifach", "delivery", "twassal", "nwassal",
    "kayen", "bghit", "bghit nchri", "rani bghit", "momkin",
    "wash momkin", "ash thaman", "wash ghali", "bshal",
    # French
    "prix", "livraison", "commande", "commander", "acheter",
    "payer", "disponible", "combien", "comment commander",
    # Arabic script
    "بشحال", "ثمن", "واش كاين", "كيفاش نطلب", "فين كاين",
    "كم الثمن", "السعر", "طلب", "كيتوصل", "توصيل",
]

# Low intent / pure admiration – does NOT indicate buying intent
LOW_INTENT_KEYWORDS: List[str] = [
    # Darija
    "zwin", "zwina", "tbarklah", "tbark allah", "3jbni", "mzyan",
    "mzyana", "waw", "safi", "hadi", "hadchi",
    # French
    "nice", "beautiful", "magnifique", "superbe", "beau", "belle",
    "parfait", "excellent",
    # Arabic
    "تبارك الله", "ما شاء الله", "زوين", "مزيان", "عجبني",
    "رائع", "جميل",
    # Generic English
    "wow", "great", "amazing", "love",
]

# Negative / rejection signals (reduce score)
NEGATIVE_KEYWORDS: List[str] = [
    "ghali", "bzzaf", "ghalia", "cher", "trop cher",
    "non merci", "pas intéressé",
    "غالي", "مش راني غادي نشري",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_matcher(keywords: List[str]) -> re.Pattern:
    """Build a single regex that matches any keyword (whole-word aware)."""
    sorted_kw = sorted(keywords, key=len, reverse=True)  # longest-first for greedy match
    escaped = [re.escape(kw.lower()) for kw in sorted_kw]
    pattern = r"(?<!\w)(" + "|".join(escaped) + r")(?!\w)"
    return re.compile(pattern, re.UNICODE | re.IGNORECASE)


_HIGH_PATTERN = _build_matcher(HIGH_INTENT_KEYWORDS)
_LOW_PATTERN = _build_matcher(LOW_INTENT_KEYWORDS)
_NEG_PATTERN = _build_matcher(NEGATIVE_KEYWORDS)


def _count_matches(pattern: re.Pattern, text: str) -> Tuple[int, List[str]]:
    matches = pattern.findall(text)
    unique = list(dict.fromkeys(m.lower() for m in matches))  # deduplicate, preserve order
    return len(matches), unique


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_intent(text: str) -> dict:
    """
    Analyse comment text for purchase intent.

    Returns:
        {
            "intent_score": float (0.0–1.0),
            "detected_language": str,
            "intent_keywords": list[str],
            "purchase_intent_level": str  # "high" | "medium" | "low"
        }
    """
    cleaned = clean_text(text)
    detected_language = detect_language(cleaned)

    high_count, high_kws = _count_matches(_HIGH_PATTERN, cleaned)
    low_count, low_kws = _count_matches(_LOW_PATTERN, cleaned)
    neg_count, _ = _count_matches(_NEG_PATTERN, cleaned)

    # Base score from keyword density
    total_tokens = max(len(tokenize(cleaned)), 1)

    # Weighted raw score: high intent carries more weight, low/negative reduce it
    raw_score = (high_count * 1.5 - low_count * 0.4 - neg_count * 0.8) / total_tokens

    # Normalise to 0–1 using a sigmoid-like clamp
    intent_score = max(0.0, min(1.0, raw_score))

    # Scale: at least 1 high-intent keyword → score ≥ 0.3
    if high_count >= 1 and intent_score < 0.3:
        intent_score = 0.3 + (high_count - 1) * 0.05

    # Hard cap
    intent_score = round(min(1.0, intent_score), 4)

    # Determine level
    if intent_score >= 0.55:
        level = "high"
    elif intent_score >= 0.25:
        level = "medium"
    else:
        level = "low"

    matched_keywords = list(dict.fromkeys(high_kws))  # only high-intent keywords reported

    logger.debug(
        "Intent analysis: lang=%s score=%.3f level=%s keywords=%s",
        detected_language, intent_score, level, matched_keywords,
    )

    return {
        "intent_score": intent_score,
        "detected_language": detected_language,
        "intent_keywords": matched_keywords,
        "purchase_intent_level": level,
    }


def batch_analyze_intents(texts: List[str]) -> List[dict]:
    """Analyse a batch of comment texts and return a list of analysis dicts."""
    return [analyze_intent(t) for t in texts]


def compute_avg_intent_score(texts: List[str]) -> float:
    """Return the mean intent score across a list of comment texts."""
    if not texts:
        return 0.0
    scores = [analyze_intent(t)["intent_score"] for t in texts]
    return round(sum(scores) / len(scores), 4)
