"""Severity/urgency badge shown next to AI answers.

Classification is a lightweight Bangla/English keyword heuristic run on the
AI response text — good enough to flag obviously urgent language without
needing a backend change or a model call of its own.
"""

from utils import theme
from utils.icons import icon

_URGENT_KEYWORDS = [
    "জরুরি", "অবিলম্বে", "এখনই", "দ্রুত ডাক্তার", "রক্তক্ষরণ", "শ্বাসকষ্ট",
    "অজ্ঞান", "বিষক্রিয়া", "মৃত্যু", "গুরুতর", "তীব্র ব্যথা",
    "emergency", "urgent", "critical",
]
_MONITOR_KEYWORDS = [
    "লক্ষ্য রাখুন", "পর্যবেক্ষণ", "নজর রাখুন", "যদি না কমে", "কয়েক দিন", "সতর্ক",
    "monitor", "watch",
]

_LEVELS = {
    "mild": {
        "label": "মৃদু সমস্যা",
        "color": theme.PRIMARY,
        "bg": theme.MINT,
        "icon": "check-shield",
    },
    "monitor": {
        "label": "লক্ষ্য রাখুন",
        "color": theme.AMBER,
        "bg": theme.AMBER_TINT,
        "icon": "eye",
    },
    "urgent": {
        "label": "জরুরি — ডাক্তার দেখান",
        "color": theme.RED,
        "bg": theme.RED_TINT,
        "icon": "alert-triangle",
    },
}


def classify_severity(text: str) -> str:
    """Return 'mild', 'monitor', or 'urgent' based on keywords in the response."""
    lowered = (text or "").lower()
    if any(word.lower() in lowered for word in _URGENT_KEYWORDS):
        return "urgent"
    if any(word.lower() in lowered for word in _MONITOR_KEYWORDS):
        return "monitor"
    return "mild"


def render_severity_badge(level: str) -> str:
    """Return an inline-styled HTML pill for the given severity level."""
    spec = _LEVELS.get(level, _LEVELS["mild"])
    return (
        f'<span style="display:inline-flex;align-items:center;gap:0.35rem;'
        f'background:{spec["bg"]};color:{spec["color"]};font-weight:700;'
        f'font-size:0.8rem;padding:0.35rem 0.75rem;border-radius:999px;">'
        f'{icon(spec["icon"], color=spec["color"], size=15)}{spec["label"]}</span>'
    )
