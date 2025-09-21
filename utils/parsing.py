from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class ResultItem(BaseModel):
    title: str
    url: Optional[str] = None
    snippet: Optional[str] = None
    source: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    score: Optional[float] = None
    image: Optional[str] = None  # NEW: preview/thumbnail URL

def normalize_items(items: List["ResultItem"]) -> List["ResultItem"]:
    # Basic de-dup by URL/title
    seen = set()
    out = []
    for it in items:
        key = (it.url or it.title).strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out
