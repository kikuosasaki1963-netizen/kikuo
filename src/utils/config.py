"""Configuration management."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration."""

    google_credentials: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_refresh_token: str = ""
    default_voice: str = "ja-JP-Neural2-B"
    default_language: str = "ja-JP"
    default_speed: float = 1.0
    output_dir: Path = field(default_factory=lambda: Path("output"))

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment variables."""
        load_dotenv()

        return cls(
            google_credentials=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
            google_client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
            google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
            google_refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN", ""),
            default_voice=os.getenv("DEFAULT_VOICE", "ja-JP-Neural2-B"),
            default_language=os.getenv("DEFAULT_LANGUAGE", "ja-JP"),
            default_speed=float(os.getenv("DEFAULT_SPEED", "1.0")),
            output_dir=Path(os.getenv("OUTPUT_DIR", "output")),
        )

    def validate_tts(self) -> bool:
        """Validate TTS configuration."""
        return bool(self.google_credentials) or os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )

    def validate_google_docs(self) -> bool:
        """Validate Google Docs API configuration."""
        return all(
            [self.google_client_id, self.google_client_secret, self.google_refresh_token]
        )
