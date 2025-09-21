import requests
from typing import List
from utils.parsing import ResultItem

def search_pubmed(query: str, limit: int = 8) -> List[ResultItem]:
    # E-Utilities esearch + esummary
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    try:
        es = requests.get(f"{base}/esearch.fcgi", params={
            "db": "pubmed", "term": query, "retmode": "json", "retmax": limit
        }, timeout=10).json()
        ids = es.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        summ = requests.get(f"{base}/esummary.fcgi", params={
            "db": "pubmed", "id": ",".join(ids), "retmode": "json"
        }, timeout=10).json()
        result = summ.get("result", {})
        out: List[ResultItem] = []
        for pid in ids:
            rec = result.get(pid, {})
            title = rec.get("title")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
            year = None
            if "pubdate" in rec and rec["pubdate"][:4].isdigit():
                year = int(rec["pubdate"][:4])
            snippet = (rec.get("source") or "") + " · " + (rec.get("pubtype", [""])[0] or "")
            out.append(ResultItem(
                title=title or "(untitled)",
                url=url,
                snippet=snippet.strip(),
                source="PubMed",
                meta={"kind": "journal", "year": year}
            ))
        return out
    except Exception:
        return []