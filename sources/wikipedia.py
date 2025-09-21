import requests
from typing import List
from utils.parsing import ResultItem

WIKI_SEARCH = "https://en.wikipedia.org/w/api.php"

def search_wikipedia(query: str, limit: int = 8) -> List[ResultItem]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": limit,
        "utf8": 1,
    }
    try:
        r = requests.get(WIKI_SEARCH, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        out = []
        for hit in data.get("query", {}).get("search", []):
            title = hit.get("title", "")
            page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            snippet = hit.get("snippet", "").replace("<span class=\"searchmatch\">","").replace("</span>","")
            out.append(ResultItem(
                title=title,
                url=page_url,
                snippet=snippet,
                source="Wikipedia",
                meta={"kind": "encyclopedia"}
            ))
        return out
    except Exception:
        return []