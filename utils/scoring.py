import tldextract
from datetime import datetime
from typing import List
from .parsing import ResultItem

EDU_GOV_BONUS = 25
JOURNAL_BONUS = 20
ENCYC_BONUS = 12
CITATION_BONUS_FACTOR = 0.02  # 50 citations -> +1, 500 -> +10 (cap later)

TRUSTED_DOMAINS = {
    "wikipedia.org", "britannica.com", "stanford.edu", "harvard.edu", "mit.edu",
    "nature.com", "science.org", "nih.gov", "ncbi.nlm.nih.gov", "arxiv.org",
    "acm.org", "ieee.org", "springer.com", "sciencedirect.com", "ox.ac.uk",
    "cam.ac.uk", "nasa.gov", "who.int"
}

def _domain(url: str | None) -> str | None:
    if not url:
        return None
    ext = tldextract.extract(url)
    return ".".join([p for p in [ext.domain, ext.suffix] if p])

def _year_penalty(year: int | None) -> float:
    if not year or year < 1900:
        return 0.0
    now = datetime.utcnow().year
    age = max(0, now - year)
    # Soft penalty after 8 years
    return min(20.0, max(0.0, (age - 8) * 1.5))

def score_items(items: List[ResultItem]) -> List[ResultItem]:
    for it in items:
        score = 40.0  # base
        dom = _domain(it.url)
        kind = it.meta.get("kind")
        year = it.meta.get("year")
        citations = float(it.meta.get("citations") or 0.0)

        if dom in TRUSTED_DOMAINS:
            score += 20
        if dom and (dom.endswith(".edu") or dom.endswith(".gov")):
            score += EDU_GOV_BONUS
        if kind in ("journal", "preprint", "research"):
            score += JOURNAL_BONUS
        if kind in ("encyclopedia", "reference"):
            score += ENCYC_BONUS

        score += min(20.0, citations * CITATION_BONUS_FACTOR)
        score -= _year_penalty(year)

        score = max(0.0, min(100.0, score))
        it.score = score
    return items

def sort_and_trim(items: List[ResultItem], n: int) -> List[ResultItem]:
    return sorted(items, key=lambda x: (x.score or 0.0), reverse=True)[:n]