from pathlib import Path
import re
from backend.app.core.config import settings


def project_root() -> Path:
    """
    routes.py 위치: backend/app/api/routes.py
    parents[0]=api, [1]=app, [2]=backend, [3]=PROJECT_ROOT
    """
    return Path(__file__).resolve().parents[3]


def normalize_for_tts(s: str) -> str:
    """
    TTS가 또박또박 읽게끔 최소 보정
    - 너무 공격적으로 정리하면 감성(…/이모지)이 죽으니 최소만
    """
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("…", ".", 1) # Only replace the first occurrence of ellipsis to avoid altering valid text.
    s = s.replace("·", " ")
    return s.strip()


def safe_segments() -> int:
    """
    settings.VIDEO_SEGMENTS가 없거나 이상한 값이면 6으로 안전하게 보정
    """
    try:
        v = int(getattr(settings, "VIDEO_SEGMENTS", 6))
    except Exception:
        v = 6
    return max(1, min(12, v))  # 너무 많으면 오히려 산만해져서 상한 12
