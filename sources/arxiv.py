import requests, feedparser
from typing import List
from utils.parsing import ResultItem

def search_arxiv(query: str, limit: int = 8) -> List[ResultItem]:
    # Use arXiv API via Atom feed
    api = "http://export.arxiv.org/api/query"
    params = {"search_query": f"all:{query}", "start": 0, "max_results": limit}
    try:
        r = requests.get(api, params=params, timeout=15)
        r.raise_for_status()
        feed = feedparser.parse(r.text)
        out: List[ResultItem] = []
        for e in feed.entries:
            title = e.title
            url = e.link
            summary = e.summary if hasattr(e, "summary") else ""
            year = None
            if hasattr(e, "published"):
                year = int(e.published[:4])
            out.append(ResultItem(
                title=title,
                url=url,
                snippet=summary[:300] + ("..." if len(summary) > 300 else ""),
                source="arXiv",
                meta={"kind": "preprint", "year": year}
            ))
        return out
    except Exception:
        return []