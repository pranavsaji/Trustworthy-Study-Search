import math
import requests
from typing import List
from utils.parsing import ResultItem
from utils.config import AppConfig
from utils.preview import fetch_og_image

# Expanded trusted hints so common, reputable docs/tutorial sites show up.
WHITELIST_HINTS = [
    # General reputable
    ".edu", ".gov", "britannica.com", "reuters.com", "apnews.com",
    # Science/health
    "nature.com", "science.org", "sciencedirect.com", "springer.com", "nih.gov", "who.int",
    # Developer documentation (common trustworthy sources)
    "developer.mozilla.org", "docs.python.org", "nodejs.org", "go.dev", "rust-lang.org",
    "kubernetes.io", "docker.com", "react.dev", "vuejs.org", "angular.io",
    "pytorch.org", "tensorflow.org", "scikit-learn.org", "numpy.org", "pandas.pydata.org",
    "cloud.google.com", "aws.amazon.com", "azure.microsoft.com", "learn.microsoft.com",
    "oracle.com", "ibm.com/docs", "vercel.com/docs", "postgresql.org", "mysql.com", "mariadb.org",
    # Learning sites with solid editorial vetting
    "khanacademy.org", "freecodecamp.org", "digitalocean.com"
]

def _looks_trustworthy(url: str) -> bool:
    u = (url or "").lower()
    return any(h in u for h in WHITELIST_HINTS)

def _serpapi(query: str, limit: int, key: str) -> List[ResultItem]:
    out: List[ResultItem] = []
    try:
        page_size = 10
        pages = math.ceil(min(limit, 100) / page_size)
        for page in range(pages):
            r = requests.get(
                "https://serpapi.com/search.json",
                params={"engine": "google", "q": query, "num": page_size, "start": page * page_size, "api_key": key},
                timeout=15,
            )
            r.raise_for_status()
            data = r.json()
            for it in (data.get("organic_results") or []):
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
                if len(out) >= limit:
                    return out
    except Exception:
        pass
    return out

def _google_cse(query: str, limit: int, cx: str, key: str) -> List[ResultItem]:
    out: List[ResultItem] = []
    try:
        page_size = 10  # CSE max per request
        pages = math.ceil(min(limit, 100) / page_size)
        for page in range(pages):
            start = page * page_size + 1
            r = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"q": query, "cx": cx, "key": key, "num": page_size, "start": start},
                timeout=15,
            )
            r.raise_for_status()
            data = r.json()
            for it in data.get("items", []) or []:
                link = it.get("link")
                if not link or not _looks_trustworthy(link):
                    continue
                title = it.get("title")
                snippet = it.get("snippet") or ""
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
                if len(out) >= limit:
                    return out
    except Exception:
        pass
    return out

def search_web(query: str, limit: int, cfg: AppConfig) -> List[ResultItem]:
    if cfg.serpapi_key:
        return _serpapi(query, limit, cfg.serpapi_key)
    if cfg.google_cse_id and cfg.google_cse_key:
        return _google_cse(query, limit, cfg.google_cse_id, cfg.google_cse_key)
    return []
