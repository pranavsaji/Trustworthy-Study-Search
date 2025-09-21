import requests
from typing import List
from utils.parsing import ResultItem

def search_crossref(query: str, limit: int = 8) -> List[ResultItem]:
    url = "https://api.crossref.org/works"
    try:
        r = requests.get(url, params={"query": query, "rows": limit}, timeout=15)
        r.raise_for_status()
        data = r.json()
        out: List[ResultItem] = []
        for it in data.get("message", {}).get("items", []):
            title_list = it.get("title") or []
            title = title_list[0] if title_list else "(untitled)"
            link = None
            for l in it.get("link", []) or []:
                if l.get("URL"):
                    link = l["URL"]; break
            link = link or it.get("URL")
            year = None
            if it.get("issued", {}).get("date-parts"):
                year = it["issued"]["date-parts"][0][0]
            citations = it.get("is-referenced-by-count", 0)
            snippet = (it.get("container-title", [""])[0] or "") + (f" · DOI: {it.get('DOI')}" if it.get("DOI") else "")
            out.append(ResultItem(
                title=title,
                url=link,
                snippet=snippet.strip(),
                source="Crossref",
                meta={"kind": "journal", "year": year, "citations": citations}
            ))
        return out
    except Exception:
        return []