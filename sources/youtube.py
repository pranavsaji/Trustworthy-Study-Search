import requests, feedparser, urllib.parse
from typing import List
from utils.parsing import ResultItem
from utils.config import AppConfig

def _thumb_from_id(vid: str) -> str:
    # High-quality default thumbnail
    return f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"

def search_youtube(query: str, limit: int = 10, cfg: AppConfig | None = None) -> List[ResultItem]:
    key = (cfg.youtube_api_key if cfg else None)
    if key:
        try:
            r = requests.get("https://www.googleapis.com/youtube/v3/search", params={
                "key": key,
                "q": query,
                "part": "snippet",
                "type": "video",
                "maxResults": min(25, limit),
                "safeSearch": "strict",
            }, timeout=10)
            r.raise_for_status()
            data = r.json()
            out: List[ResultItem] = []
            for item in data.get("items", []):
                vid = item["id"]["videoId"]
                sn = item.get("snippet", {})
                title = sn.get("title")
                desc = sn.get("description") or ""
                url = f"https://www.youtube.com/watch?v={vid}"
                thumb = (sn.get("thumbnails", {}).get("high", {}) or {}).get("url") or _thumb_from_id(vid)
                out.append(ResultItem(
                    title=title,
                    url=url,
                    snippet=desc[:300] + ("..." if len(desc) > 300 else ""),
                    source="YouTube",
                    meta={"kind": "video", "video_id": vid},
                    image=thumb
                ))
            return out
        except Exception:
            pass
    # Fallback: YouTube RSS search (no API key)
    try:
        q = urllib.parse.quote_plus(query)
        feed_url = f"https://www.youtube.com/feeds/videos.xml?search_query={q}"
        feed = feedparser.parse(feed_url)
        out: List[ResultItem] = []
        for e in feed.entries[:limit]:
            title = e.title
            link = e.link
            vid = getattr(e, "yt_videoid", None) or (link.split("v=")[-1] if "v=" in link else "")
            summary = getattr(e, "summary", "")
            out.append(ResultItem(
                title=title,
                url=link,
                snippet=summary[:300] + ("..." if len(summary) > 300 else ""),
                source="YouTube (RSS)",
                meta={"kind": "video", "video_id": vid},
                image=_thumb_from_id(vid) if vid else None
            ))
        return out
    except Exception:
        return []
