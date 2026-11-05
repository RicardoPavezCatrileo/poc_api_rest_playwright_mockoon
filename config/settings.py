"""Configuración centralizada, leída desde variables de entorno o un archivo .env."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@dataclass(frozen=True)
class Settings:
    base_url: str
    timeout_ms: int
    short_timeout_ms: int
    slow_endpoint_delay_ms: int
    max_response_time_ms: int


@dataclass(frozen=True)
class ConfiguracionTimeout:
    corto_ms: int
    suficiente_ms: int
    retardo_ms: int


settings = Settings(
    base_url=os.getenv("API_BASE_URL", "http://localhost:3001"),
    timeout_ms=int(os.getenv("API_TIMEOUT_MS", "20000")),
    short_timeout_ms=int(os.getenv("API_SHORT_TIMEOUT_MS", "5000")),
    slow_endpoint_delay_ms=int(os.getenv("SLOW_ENDPOINT_DELAY_MS", "15000")),
    max_response_time_ms=int(os.getenv("MAX_RESPONSE_TIME_MS", "2000")),
)
