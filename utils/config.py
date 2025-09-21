import os
from dataclasses import dataclass

@dataclass
class AppConfig:
    serpapi_key: str | None = None
    google_cse_id: str | None = None
    google_cse_key: str | None = None
    youtube_api_key: str | None = None
    openai_api_key: str | None = None

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            serpapi_key=os.getenv("SERPAPI_KEY") or None,
            google_cse_id=os.getenv("GOOGLE_CSE_ID") or None,
            google_cse_key=os.getenv("GOOGLE_CSE_KEY") or None,
            youtube_api_key=os.getenv("YOUTUBE_DATA_API_KEY") or None,
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        )