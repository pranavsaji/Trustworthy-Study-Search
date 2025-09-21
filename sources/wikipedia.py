import requests
from typing import List
from utils.parsing import ResultItem

WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

HEADERS = {
    "User-Agent": "TrustworthyStudySearch/1.0 (https://github.com/; contact: example@example.com)"
}

def _search_api(query: str, limit: int) -> List[ResultItem]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": limit,
        "utf8": 1,
    }
    r = requests.get(WIKI_API, params=params, timeout=10, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    out: List[ResultItem] = []
    for hit in data.get("query", {}).get("search", []):
        title = hit.get("title", "")
        page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        snippet = (hit.get("snippet", "") or "").replace('<span class="searchmatch">', "").replace("</span>", "")
        out.append(ResultItem(
            title=title or "(untitled)",
            url=page_url,
            snippet=snippet,
            source="Wikipedia",
            meta={"kind": "encyclopedia"}
        ))
    return out

def _summary_api(query: str) -> List[ResultItem]:
    # Try the summary endpoint with the query as title
    title = query.strip().replace(" ", "_")
    r = requests.get(WIKI_SUMMARY.format(title=title), timeout=10, headers=HEADERS)
    if r.status_code != 200:
        return []
    js = r.json()
    if not js or "content_urls" not in js:
        return []
    url = js["content_urls"]["desktop"]["page"] if "desktop" in js.get("content_urls", {}) else js.get("content_urls", {}).get("page")
    if not url:
        url = f"https://en.wikipedia.org/wiki/{title}"
    snippet = js.get("extract") or ""
    display_title = js.get("title") or query
    thumb = (js.get("thumbnail") or {}).get("source")
    return [ResultItem(
        title=display_title,
        url=url,
        snippet=snippet[:300] + ("..." if len(snippet) > 300 else ""),
        source="Wikipedia",
        meta={"kind": "encyclopedia"},
        image=thumb
    )]

def _opensearch(query: str, limit: int) -> List[ResultItem]:
    params = {
        "action": "opensearch",
        "search": query,
        "limit": limit,
        "namespace": 0,
        "format": "json"
    }
    r = requests.get(WIKI_API, params=params, timeout=10, headers=HEADERS)
    r.raise_for_status()
    data = r.json()  # [query, titles[], descriptions[], urls[]]
    out: List[ResultItem] = []
    titles = data[1] if len(data) > 1 else []
    descs  = data[2] if len(data) > 2 else []
    urls   = data[3] if len(data) > 3 else []
    for t, d, u in zip(titles, descs, urls):
        out.append(ResultItem(
            title=t or "(untitled)",
            url=u,
            snippet=(d or "")[:300],
            source="Wikipedia",
            meta={"kind": "encyclopedia"}
        ))
    return out

def search_wikipedia(query: str, limit: int = 8) -> List[ResultItem]:
    try:
        items = _search_api(query, limit)
        if items:
            return items
        # fallback 1: summary (direct page title)
        items = _summary_api(query)
        if items:
            return items
        # fallback 2: opensearch
        items = _opensearch(query, limit)
        return items
    except Exception:
        return []
