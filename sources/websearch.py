import requests
from typing import List
from utils.parsing import ResultItem
from utils.config import AppConfig
from utils.preview import fetch_og_image

WHITELIST_HINTS = [
    ".edu", ".gov", "nature.com", "science.org", "britannica.com",
    "sciencedirect.com", "springer.com", "acm.org", "ieee.org",
    "nasa.gov", "nih.gov", "who.int", "apnews.com", "reuters.com"
]

def _looks_trustworthy(url: str) -> bool:
    u = url.lower()
    return any(h in u for h in WHITELIST_HINTS)

def _serpapi(query: str, limit: int, key: str) -> List[ResultItem]:
    try:
        r = requests.get("https://serpapi.com/search.json", params={
            "engine": "google",
            "q": query,
            "num": min(20, limit),
            "api_key": key
        }, timeout=15)
        r.raise_for_status()
        data = r.json()
        out: List[ResultItem] = []
        for it in (data.get("organic_results") or [])[:limit]:
            link = it.get("link")
            if not link or not _looks_trustworthy(link):
                continue
            title = it.get("title")
            snippet = it.get("snippet") or ""
            thumb = fetch_og_image(link)
            out.append(ResultItem(
                title=title or "(untitled)",
                url=link,
                snippet=snippet,
                source="Web (SerpAPI)",
                meta={"kind": "article"},
                image=thumb
            ))
        return out
    except Exception:
        return []

def _google_cse(query: str, limit: int, cx: str, key: str) -> List[ResultItem]:
    try:
        r = requests.get("https://www.googleapis.com/customsearch/v1", params={
            "q": query, "cx": cx, "key": key, "num": min(10, limit)
        }, timeout=15)
        r.raise_for_status()
        data = r.json()
        out: List[ResultItem] = []
        for it in data.get("items", [])[:limit]:
            link = it.get("link")
            if not link or not _looks_trustworthy(link):
                continue
            title = it.get("title")
            snippet = it.get("snippet") or ""
            # Try pagemap thumbnail first, fallback to OG fetch
            pagemap = it.get("pagemap", {})
            thumb = None
            if "cse_image" in pagemap and pagemap["cse_image"]:
                thumb = pagemap["cse_image"][0].get("src")
            thumb = thumb or fetch_og_image(link)
            out.append(ResultItem(
                title=title or "(untitled)",
                url=link,
                snippet=snippet,
                source="Web (Google CSE)",
                meta={"kind": "article"},
                image=thumb
            ))
        return out
    except Exception:
        return []

def search_web(query: str, limit: int, cfg: AppConfig) -> List[ResultItem]:
    if cfg.serpapi_key:
        return _serpapi(query, limit, cfg.serpapi_key)
    if cfg.google_cse_id and cfg.google_cse_key:
        return _google_cse(query, limit, cfg.google_cse_id, cfg.google_cse_key)
    return []
