"""
API 라우터 - Flexible (오디오 옵션 선택 가능)

- use_tts: 나래이션 포함 여부
- use_bgm: 배경음악 포함 여부
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from backend.app.core.logger import get_logger
from backend.app.core.config import settings
from backend.app.schemas import GenerateResponse

from backend.app.services.storage import make_job_dir, public_video_path
from backend.app.services.llm import generate_copy
from backend.app.services.tts import synthesize_voice_lines
from backend.app.services.video import (
    build_slideshow,
    burn_text_overlays,
    mix_audio,
)
from backend.app.utils.video_utils import project_root, normalize_for_tts, safe_segments
from backend.app.services.video_generator import generate_video

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["generator-flex"])



@router.post("/generate-flex", response_model=GenerateResponse)
async def generate_flex(
    images: list[UploadFile] = File(..., description="음식 사진들 (2~6장 권장)"),
    bgm_file: Optional[UploadFile] = File(None, description="사용자 지정 BGM 파일 (선택)"),
    menu_name: str = Form(..., description="메뉴 이름"),

    store_name: str = Form("", description="가게 이름(선택)"),
    tone: str = Form("감성", description="광고 톤(힙/감성/고급/가성비)"),

    price: str = Form("", description="가격(선택)"),
    location: str = Form("", description="위치(선택)"),
    benefit: str = Form("", description="혜택(선택)"),
    cta: str = Form("", description="콜투액션(선택)"),
    
    # 새로운 오디오 옵션
    use_tts: bool = Form(True, description="나래이션 포함 여부"),
    use_bgm: bool = Form(True, description="배경음악 포함 여부"),
):
    """오디오 옵션을 선택할 수 있는 영상 생성"""
    return await generate_video(
        images=images,
        menu_name=menu_name,
        store_name=store_name,
        tone=tone,
        price=price,
        location=location,
        benefit=benefit,
        cta=cta,
        use_tts=use_tts,
        use_bgm=use_bgm,
        bgm_file=bgm_file,
    )
