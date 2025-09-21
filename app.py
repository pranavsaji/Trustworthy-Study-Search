import os
import time
import gradio as gr
from dotenv import load_dotenv
from typing import List, Dict, Any
from utils.config import AppConfig
from utils.scoring import score_items, sort_and_trim
from utils.parsing import normalize_items, ResultItem
from utils.cache import timed_lru_cache
from sources.wikipedia import search_wikipedia
from sources.arxiv import search_arxiv
from sources.pubmed import search_pubmed
from sources.crossref import search_crossref
from sources.youtube import search_youtube
from sources.websearch import search_web

load_dotenv()
cfg = AppConfig.from_env()

@timed_lru_cache(seconds=300)
def aggregated_search(query: str, max_items: int, use_web: bool, use_videos: bool) -> Dict[str, List[ResultItem]]:
    items: List[ResultItem] = []
    items += search_wikipedia(query, limit=8)
    items += search_arxiv(query, limit=8)
    items += search_pubmed(query, limit=8)
    items += search_crossref(query, limit=8)
    if use_web:
        items += search_web(query, limit=10, cfg=cfg)
    if use_videos:
        items += search_youtube(query, limit=10, cfg=cfg)
    items = normalize_items(items)
    items = score_items(items)
    return {
        "Overview / Encyclopedic": sort_and_trim([i for i in items if i.meta.get("kind") in ["encyclopedia", "reference"]], max_items),
        "Peer-reviewed / Research": sort_and_trim([i for i in items if i.meta.get("kind") in ["journal", "preprint", "research"]], max_items),
        "Articles / Web":         sort_and_trim([i for i in items if i.meta.get("kind") in ["article", "news", "blog"]], max_items),
        "Videos / Lectures":      sort_and_trim([i for i in items if i.meta.get("kind") in ["video", "lecture"]], max_items),
    }

def _cards_html(section: str, items: List[ResultItem]) -> str:
    if not items:
        return f"<h3>{section}</h3><p><em>No results.</em></p>"
    # Simple responsive card grid with inline CSS (kept minimal for Gradio)
    html = [f"""
    <style>
      .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }}
      .card {{ background:#111; border:1px solid #2a2a2a; border-radius:14px; padding:12px; overflow:hidden; }}
      .card img {{ width:100%; height:150px; object-fit:cover; border-radius:10px; }}
      .title a {{ color:#c9d1d9; text-decoration:none; }}
      .meta {{ color:#9aa4b2; font-size:12px; margin-top:6px; }}
      .snippet {{ color:#d1d5db; font-size:13px; margin-top:6px; }}
      .score {{ font-weight:700; }}
    </style>
    <h3>{section}</h3>
    <div class="grid">
    """.strip()]
    for it in items:
        t = it.title or "(untitled)"
        url = it.url or "#"
        score = f"{it.score:.0f}/100" if isinstance(it.score, (int, float)) else ""
        src = it.source or ""
        year = it.meta.get("year")
        year_str = f" · {year}" if year else ""
        img = it.image or ""
        img_tag = f'<img src="{img}" alt="preview" loading="lazy" />' if img else ""
        snippet = (it.snippet or "")[:200]
        html.append(f"""
          <div class="card">
            {img_tag}
            <div class="title"><a href="{url}" target="_blank" rel="noopener">{t}</a></div>
            <div class="meta"><span class="score">{score}</span> · {src}{year_str}</div>
            <div class="snippet">{snippet}</div>
          </div>
        """)
    html.append("</div>")
    return "\n".join(html)

def do_search(query: str, use_web: bool, use_videos: bool, max_items: int):
    if not query or len(query.strip()) < 3:
        return "<p>Please enter a topic (≥ 3 characters).</p>"
    query = query.strip()
    t0 = time.time()
    bundles = aggregated_search(query, max_items=max(3, min(max_items, 20)), use_web=use_web, use_videos=use_videos)
    elapsed = time.time() - t0
    header = f"<h2>Results for <strong>{query}</strong></h2><p><em>Built sections in {elapsed:.2f}s (showing up to {max_items} per section).</em></p>"
    sections_html = []
    for title, lst in bundles.items():
        sections_html.append(_cards_html(title, lst))
    return header + "\n".join(sections_html)

with gr.Blocks(title="Trustworthy Study Search", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔎 Trustworthy Study Search\nFind credible learning materials across reputable sources.")
    with gr.Row():
        query = gr.Textbox(label="Topic", placeholder="e.g., reinforcement learning, CRISPR gene editing, HTTP/3...")
    with gr.Row():
        use_web = gr.Checkbox(label="Include reputable web articles (requires API key for best results)", value=False)
        use_videos = gr.Checkbox(label="Include videos / lectures", value=True)
        max_items = gr.Slider(3, 20, value=5, step=1, label="Max items per section")
    with gr.Row():
        btn = gr.Button("Search", variant="primary")
    out = gr.HTML("")  # switched to HTML to render cards with images
    btn.click(fn=do_search, inputs=[query, use_web, use_videos, max_items], outputs=[out])
    gr.Markdown("---\n**Tips:** Add API keys in `.env` to enable richer web and video results. Click any title to open the source.")

if __name__ == "__main__":
    demo.launch()
