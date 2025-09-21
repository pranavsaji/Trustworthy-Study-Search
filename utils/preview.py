import requests
from bs4 import BeautifulSoup
from functools import lru_cache

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; StudySearchBot/1.0; +https://example.org/bot)"
}

@lru_cache(maxsize=256)
def fetch_og_image(url: str) -> str | None:
    """Fetch a page and try to extract og:image (quick, best-effort)."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # Common OG tags
        tag = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name":"twitter:image"})
        if tag:
            content = tag.get("content")
            if content and content.startswith(("http://", "https://")):
                return content
    except Exception:
        pass
    return None
