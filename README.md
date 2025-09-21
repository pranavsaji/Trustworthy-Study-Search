# Trustworthy Study Search (Gradio)

A simple, extensible Gradio app that lets users search a topic and get
**trustworthy** learning materials: encyclopedic summaries (Wikipedia),
peer‑reviewed/academic sources (arXiv, PubMed, Crossref), and optionally
reputable web results and YouTube videos. Results are **scored** by a
credibility heuristic and shown in a clean UI.

## Features
- **No keys required** for: Wikipedia, arXiv, PubMed, Crossref, YouTube RSS.
- **Optional** keys for richer results:
  - Google Custom Search or SerpAPI for web results
  - YouTube Data API for video metadata
  - OpenAI key to generate concise summaries (optional)
- **Trust scoring** favoring `.edu`, `.gov`, journals, citations, and recency.
- **Deduplication** and domain whitelist/blacklist hooks.
- Simple modular sources you can extend.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then edit if you have keys
python app.py
```

Open the local URL Gradio prints (e.g., http://127.0.0.1:7860).

## Environment Variables (optional)
- `SERPAPI_KEY`: If set, uses SerpAPI Web Search for general web results.
- `GOOGLE_CSE_ID` & `GOOGLE_CSE_KEY`: Alternative to SerpAPI (Google CSE).
- `YOUTUBE_DATA_API_KEY`: If set, uses YouTube Data API v3; otherwise RSS.
- `OPENAI_API_KEY`: If set, generates concise summaries for results.

## Project Structure
```
trustworthy_study_search/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── sources/
│   ├── __init__.py
│   ├── wikipedia.py
│   ├── arxiv.py
│   ├── pubmed.py
│   ├── crossref.py
│   ├── youtube.py
│   └── websearch.py
└── utils/
    ├── config.py
    ├── scoring.py
    ├── parsing.py
    └── cache.py
```

## Notes on "Trustworthiness"
This project implements a heuristic score (0–100) combining:
- Domain quality (`.edu`, `.gov`, `.ac.*`, known journals)
- Source type (encyclopedia, peer‑reviewed, primary vs secondary)
- Citations (when available, e.g., Crossref counts)
- Recency (penalize very old material for fast‑moving topics)
- Basic domain allow/deny lists

You should still **apply judgement**. The app surfaces credible starting points,
but you are responsible for final verification.