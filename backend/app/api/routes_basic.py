"""
API 라우터 - Basic (TTS 없이 BGM만)

- 프론트(Streamlit)가 보내는 멀티파트(이미지 + 텍스트)를 받음
- LLM/Video 순서대로 실행 (TTS 생략)
- 결과 URL 반환
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.app.core.logger import get_logger
from backend.app.core.config import settings
from backend.app.schemas import GenerateResponse

from backend.app.services.storage import make_job_dir, public_video_path
from backend.app.services.llm import generate_copy
from backend.app.services.video import (
    build_slideshow,
    burn_text_overlays,
    mix_audio,
)
from backend.app.utils.video_utils import project_root, normalize_for_tts, safe_segments
from backend.app.services.video_generator import generate_video

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["generator-basic"])



@router.post("/generate-basic", response_model=GenerateResponse)
async def generate_basic(
    images: list[UploadFile] = File(..., description="음식 사진들 (2~6장 권장)"),
    menu_name: str = Form(..., description="메뉴 이름"),

    store_name: str = Form("", description="가게 이름(선택)"),
    tone: str = Form("감성", description="광고 톤(힙/감성/고급/가성비)"),

    price: str = Form("", description="가격(선택)"),
    location: str = Form("", description="위치(선택)"),
    benefit: str = Form("", description="혜택(선택)"),
    cta: str = Form("", description="콜투액션(선택)"),
):
    """TTS 없이 BGM만 포함된 영상 생성"""
    return await generate_video(
        images=images,
        menu_name=menu_name,
        store_name=store_name,
        tone=tone,
        price=price,
        location=location,
        benefit=benefit,
        cta=cta,
        use_tts=False,
        use_bgm=True,
        bgm_file=None, # No custom BGM for this route
    )
